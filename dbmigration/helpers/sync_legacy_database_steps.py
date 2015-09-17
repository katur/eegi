"""This module contains the steps used to migrate data from the legacy
database to the new database.

Each step works more or less the same way. Records are queried from the old
database for a particular table. For each record, various conversions and
validations are performed to make a Python object that is compatible with
the new database. This Python object is inserted into the new database
if not present, or used to update an existing record if changes have occurred.

"""
import re
import sys

from django.core.exceptions import ObjectDoesNotExist

from clones.models import Clone
from dbmigration.helpers.name_getters import (get_ahringer_384_plate_name,
                                              get_vidal_clone_name,
                                              get_library_well_name)
from dbmigration.helpers.object_getters import (get_worm_strain, get_clone,
                                                get_library_plate,
                                                get_library_well, get_user,
                                                get_experiment, get_score_code)
from dbmigration.helpers.sync_objects import (update_or_save_object,
                                              compare_floats_for_equality)
from experiments.models import (Experiment, ManualScoreCode,
                                ManualScore, DevstarScore)
from library.models import LibraryPlate, LibraryWell
from utils.time_conversion import get_timestamp, get_timestamp_from_ymd
from utils.well_naming import get_three_character_well
from utils.well_tile_conversion import tile_to_well


def sync_rows(cursor, legacy_query, sync_row_function, **kwargs):
    """Sync the rows from a query to the legacy database to the current
    database, according to sync_row_function(legacy_row, **kwargs).

    """
    cursor.execute(legacy_query)
    legacy_rows = cursor.fetchall()
    all_match = True

    for legacy_row in legacy_rows:
        matches = sync_row_function(legacy_row, **kwargs)
        all_match &= matches

    if all_match:
        sys.stdout.write('All objects from legacy query:\n\n\t{}\n\n'
                         'were already represented in new database.\n\n'
                         .format(legacy_query))
    else:
        sys.stdout.write('Some objects from legacy query:\n\n\t{}\n\n'
                         'were just added or updated in new database'
                         '(individual changes printed to sys.stderr.)\n\n'
                         .format(legacy_query))


def update_LibraryPlate_table(cursor):
    """Update the LibraryPlate table according to distinct plates recorded
    in legacy tables RNAiPlate and CherryPickRNAiPlate.

    Find original Ahringer 384-well plates through the chromosome and
    384PlateID fields of RNAiPlate (384PlateID NOT LIKE GHR-%, != 0).

    Find original Orfeome plates through the 384PlateID field of RNAiPlate
    (384PlateID LIKE GHR-%). Note that these original Orfeome plates
    are actually in 96-well format.

    Find the plates actually used in our primary experiments as the distinct
    RNAiPlateID from RNAiPlate, and the distinct RNAiPlateID LIKE Eliana%
    from ReArrayRNAiPlate.

    Find the plates actually used in our secondary experiments as the distinct
    RNAiPlateID from CherryPickRNAiPlates. Must also skip L4440 (because
    in order to get around some bizarities in the old database separating
    the primary and secondary screens into two tables, we have the same
    L4440 plate listed in both tables in the legacy database).

    """
    recorded_plates = LibraryPlate.objects.all()
    fields_to_compare = ('screen_stage', 'number_of_wells')

    legacy_query_384_plates = ('SELECT DISTINCT chromosome, 384PlateID '
                               'FROM RNAiPlate '
                               'WHERE 384PlateID NOT LIKE "GHR-%" '
                               'AND 384PlateID != 0')

    legacy_query_orfeome_plates = ('SELECT DISTINCT 384PlateID '
                                   'FROM RNAiPlate '
                                   'WHERE 384PlateID LIKE "GHR-%"')

    legacy_query_primary_plates = ('SELECT DISTINCT RNAiPlateID '
                                   'FROM RNAiPlate')

    legacy_query_eliana_rearrays = ('SELECT DISTINCT RNAiPlateID FROM '
                                    'ReArrayRNAiPlate WHERE RNAiPlateID '
                                    'LIKE "Eliana%"')

    legacy_query_secondary_plates = ('SELECT DISTINCT RNAiPlateID '
                                     'FROM CherryPickRNAiPlate '
                                     'WHERE RNAiPlateID != "L4440"')

    def sync_library_plate_row(legacy_row, screen_stage, number_of_wells=96):
        if len(legacy_row) > 1:
            legacy_plate_name = get_ahringer_384_plate_name(legacy_row[0],
                                                            legacy_row[1])
        else:
            legacy_plate_name = legacy_row[0]
        legacy_plate = LibraryPlate(id=legacy_plate_name,
                                    screen_stage=screen_stage,
                                    number_of_wells=number_of_wells)
        return update_or_save_object(legacy_plate, recorded_plates,
                                     fields_to_compare)

    # Sync the 384-well Ahringer plates from which our 96-well Ahringer plates
    # were arrayed
    sync_rows(cursor, legacy_query_384_plates, sync_library_plate_row,
              screen_stage=0, number_of_wells=384)

    # Sync the 96-well Orfeome plates from which our 96-well Vidal rearrays
    # were cherry-picked
    sync_rows(cursor, legacy_query_orfeome_plates, sync_library_plate_row,
              screen_stage=0)

    # Sync the 96-well plates used in our Primary experiments (includes
    # L4440 plate, Ahringer plates, and Vidal plates)
    sync_rows(cursor, legacy_query_primary_plates, sync_library_plate_row,
              screen_stage=1)

    # Sync the 96-well "Eliana Rearray" plates, which tried to salvage wells
    # that did not grow consistently in the other primary screen plates
    sync_rows(cursor, legacy_query_eliana_rearrays, sync_library_plate_row,
              screen_stage=1)

    # Sync the 96-well plates used for our Secondary experiments
    sync_rows(cursor, legacy_query_secondary_plates, sync_library_plate_row,
              screen_stage=2)


def update_Experiment_table(cursor):
    """Update the Experiment table according to legacy table RawData.

    Several datatype transforms occur from the old to the new schema:

        - mutant/mutantAllele become a FK to WormStrain
        - RNAiPlateID becomes a FK to LibraryPlate
        - temperature as string (with 'C') becomes a decimal
        - recordDate as string becomes a DATE
        - isJunk becomes a boolean (with both 1 and -1 becoming True)

    Also, experiments of Julie's (which were done with a line of spn-4 worms
    later deemed untrustworthy) are excluded.

    """
    recorded_experiments = Experiment.objects.all()
    fields_to_compare = ('worm_strain', 'library_plate', 'screen_stage',
                         'temperature', 'date', 'is_junk', 'comment',)

    legacy_query = ('SELECT expID, mutant, mutantAllele, RNAiPlateID, '
                    'CAST(SUBSTRING_INDEX(temperature, "C", 1) '
                    'AS DECIMAL(3,1)), '
                    'CAST(recordDate AS DATE), ABS(isJunk), comment '
                    'FROM RawData '
                    'WHERE (expID < 40000 OR expID >= 50000) '
                    'AND RNAiPlateID NOT LIKE "Julie%"')

    def sync_experiment_row(legacy_row):
        expID = legacy_row[0]

        if expID < 40000:
            screen_stage = 1
        else:
            screen_stage = 2

        legacy_experiment = Experiment(
            id=legacy_row[0],
            worm_strain=get_worm_strain(legacy_row[1], legacy_row[2]),
            library_plate=get_library_plate(legacy_row[3]),
            screen_stage=screen_stage,
            temperature=legacy_row[4],
            date=legacy_row[5],
            is_junk=legacy_row[6],
            comment=legacy_row[7]
        )

        return update_or_save_object(legacy_experiment, recorded_experiments,
                                     fields_to_compare)

    sync_rows(cursor, legacy_query, sync_experiment_row)


def update_ManualScoreCode_table(cursor):
    """Update the ManualScoreCode table according to the legacy table of
    the same name.

    We've made these decisions about migrating score codes and scores
        into the new database:

    - Scrap these antiquated codes, along with scores:
        -8: 2 degree pool (currently no scores; not used)
        -1: not sure (just Julie, whose scores are being deleted anyway)
        4: No Larvae (for a preliminary DevStaR test; no easy conversion)
        5: Larvae present ("")
        6: A lot of Larvae ("")

    - Scrap these antiquated codes, but convert scores:
        -6: Poor Image Quality (convert to -7)

    - Migrate these antiquated codes, but do not show in interface:
        -5: IA Error

    """
    recorded_score_codes = ManualScoreCode.objects.all()
    fields_to_compare = ('legacy_description',)

    legacy_query = ('SELECT code, definition FROM ManualScoreCode '
                    'WHERE code != -8 AND code != -1 AND code != 4 '
                    'AND code != 5 AND code != 6 AND code != -6')

    def sync_score_code_row(legacy_row):
        legacy_score_code = ManualScoreCode(
            id=legacy_row[0],
            legacy_description=legacy_row[1].decode('utf8'),
        )

        return update_or_save_object(legacy_score_code, recorded_score_codes,
                                     fields_to_compare)

    sync_rows(cursor, legacy_query, sync_score_code_row)


def update_ManualScore_table(cursor):
    """Update the ManualScore table according to the legacy table of the same
    name.

    Requires that ScoreYear, ScoreMonth, ScoreDate, and ScoreTime
    are valid fields for a python datetime.datetime.

    As described in update_ManualScoreCode_table, do not migrate scores
    with score code -8, -1, 4, 5, or 6.

    Also as described in update_ManualScoreCode_table, convert
    any -6 scores to -7 during migration.

    In addition, we've made these decisions about score migration:
        - *?*?* do not migrate isJunk = -1 scores, as we are probably trashing
          these experiments entirely *?*?*

        - scrap scorer Julie, treating her scores as follows:
            no bacteria (-2) scores: mark as scored by hueyling (hueyling did
                    populate these scores automatically, and Julie was simply
                    listed as the default scorer in the old database
            all other scores: do not migrate (all correspond to misbehaving
                    spn-4 line and have no bearing on our results)

        - scrap scorer expPeople, treating scores as hueyling

        - scrap alejandro and katy as scorers, not migrating any of their
          scores (all their scores were redundant; alejandro was not trained
          well, and katy's were done prior to other decisions)

        - scrap ENH scores only by eliana and lara

        - keep ENH scores by sherly, kelly, and patricia, but do not have
          these show in the interface

        - for sherly and patricia's ENH scores, ensure that any medium or
          strong enhancers were caught by official scorers

    """
    recorded_scores = ManualScore.objects.all()
    fields_to_compare = None

    legacy_query = ('SELECT ManualScore.expID, ImgName, score, scoreBy, '
                    'scoreYMD, ScoreYear, ScoreMonth, ScoreDate, ScoreTime, '
                    'mutant, screenFor '
                    'FROM ManualScore '
                    'LEFT JOIN RawData '
                    'ON ManualScore.expID = RawData.expID '
                    'WHERE score != -8 AND score != -1 AND score != 4 '
                    'AND score != 5 AND score != 6')

    def sync_score_row(legacy_row):
        legacy_score_code = legacy_row[2]
        legacy_scorer = legacy_row[3]
        gene = legacy_row[9]
        screen = legacy_row[10]

        # Skip some scores entirely (see criteria above)
        skip_entirely = ('alejandro', 'katy')
        skip_ENH = ('eliana', 'lara')

        if ((legacy_scorer == 'Julie' and legacy_score_code != -2) or
                (legacy_scorer in skip_entirely) or
                (screen == 'ENH' and legacy_scorer in skip_ENH)):
            sys.stderr.write('Skipping a {} {} score of {} by {}\n'
                             .format(gene, screen, legacy_score_code,
                                     legacy_scorer))
            return True

        # Convert some scorers to hueyling (see criteria above)
        if legacy_scorer == 'Julie' or legacy_scorer == 'expPeople':
            sys.stderr.write('Converting a {} score by {} to hueyling\n'
                             .format(legacy_score_code, legacy_scorer))
            legacy_scorer = 'hueyling'

        # Convert some score codes to other score codes (see criteria above)
        if legacy_score_code == -6:
            sys.stderr.write('Converting score from -6 to -7\n')
            legacy_score_code = -7

        # The following raise exceptions if improperly formatted or not found
        experiment = get_experiment(legacy_row[0])
        well = tile_to_well(legacy_row[1])
        score_code = get_score_code(legacy_score_code)
        scorer = get_user(legacy_scorer)

        timestamp = get_timestamp(legacy_row[5], legacy_row[6], legacy_row[7],
                                  legacy_row[8], legacy_row[4])
        if not timestamp:
            sys.exit('ERROR: score of experiment {}, well {} '
                     'could not be converted to a proper '
                     'datetime'.format(legacy_row[0], legacy_row[1]))

        legacy_score = ManualScore(
            experiment=experiment,
            well=well,
            score_code=score_code,
            scorer=scorer,
            timestamp=timestamp,
        )

        return update_or_save_object(
            legacy_score, recorded_scores, fields_to_compare,
            alternate_pk={'experiment': legacy_score.experiment,
                          'well': legacy_score.well,
                          'score_code': legacy_score.score_code,
                          'scorer': legacy_score.scorer,
                          'timestamp': timestamp}
        )

    sync_rows(cursor, legacy_query, sync_score_row)


def update_ManualScore_table_secondary(cursor):
    recorded_scores = ManualScore.objects.all()
    fields_to_compare = None
    legacy_query = ('SELECT expID, ImgName, score, '
                    'scoreBy, scoreYMD, ScoreTime '
                    'FROM ScoreResultsManual')

    def sync_score_row(legacy_row):
        legacy_score_code = legacy_row[2]
        legacy_scorer = legacy_row[3]

        # The following raise exceptions if improperly formatted or not found
        experiment = get_experiment(legacy_row[0])
        well = tile_to_well(legacy_row[1])
        score_code = get_score_code(legacy_score_code)
        scorer = get_user(legacy_scorer)

        timestamp = get_timestamp_from_ymd(legacy_row[4], legacy_row[5])
        if not timestamp:
            sys.exit('ERROR: score of experiment {}, well {} '
                     'could not be converted to a proper '
                     'datetime'.format(legacy_row[0], legacy_row[1]))

        legacy_score = ManualScore(
            experiment=experiment,
            well=well,
            score_code=score_code,
            scorer=scorer,
            timestamp=timestamp,
        )

        return update_or_save_object(
            legacy_score, recorded_scores, fields_to_compare,
            alternate_pk={'experiment': legacy_score.experiment,
                          'well': legacy_score.well,
                          'score_code': legacy_score.score_code,
                          'scorer': legacy_score.scorer,
                          'timestamp': timestamp}
        )

    sync_rows(cursor, legacy_query, sync_score_row)


def update_DevstarScore_table(cursor):
    """Update the DevstarScore table according to legacy table
    RawDataWithScore.

    Redundant fields (mutantAllele, targetRNAiClone, RNAiPlateID) are excluded.

    The DevStaR output is simply 6 fields (adult/larva/embryo area,
    adult/larva count, and whether bacteria is present).
    Several other fields are simply calculations on these fields
    (embryo per adult, larva per adult, survival, lethality).
    I redo these calculations, but compare to the legacy value to make sure
    it is equal or almost equal. We also have some datatype conversions:
        - embryo/larva per adult become Float
        - survival and lethality become higher precision Floats
        - counts of -1 become NULL (this happens when part of the DevStaR
          program did not run)
        - division by 0 in embryo/larva per adult remain 0, but when adult=0
          we DO now calculate survival and lethality
        - machineCall becomes a Boolean

    """
    recorded_scores = DevstarScore.objects.all()
    fields_to_compare = ('area_adult', 'area_larva', 'area_embryo',
                         'count_adult', 'count_larva', 'is_bacteria_present',
                         'count_embryo', 'larva_per_adult',
                         'embryo_per_adult', 'survival', 'lethality',
                         'selected_for_scoring', 'gi_score_larva_per_adult',
                         'gi_score_survival')

    legacy_query = ('SELECT expID, 96well, '
                    'mutantAllele, targetRNAiClone, RNAiPlateID, '
                    'areaWorm, areaLarvae, areaEmbryo, '
                    'AdultCount, LarvaeCount, EggCount, '
                    'EggPerWorm, LarvaePerWorm, survival, lethality, '
                    'machineCall, machineDetectBac, '
                    'GIscoreLarvaePerWorm, GIscoreSurvival '
                    'FROM RawDataWithScore '
                    'WHERE (expID < 40000 OR expID >= 50000) '
                    'AND RNAiPlateID NOT LIKE "Julie%" '
                    'ORDER BY expID, 96well')

    def sync_score_row(legacy_row):
        # Build the object using the minimimum fields
        count_adult = legacy_row[8]
        count_larva = legacy_row[9]
        if count_adult == -1:
            count_adult = None
        if count_larva == -1:
            count_larva = None

        machine_call = legacy_row[15]
        if machine_call:
            selected_for_scoring = True
        else:
            selected_for_scoring = False

        legacy_score = DevstarScore(
            experiment=get_experiment(legacy_row[0]),
            well=get_three_character_well(legacy_row[1]),
            area_adult=legacy_row[5],
            area_larva=legacy_row[6],
            area_embryo=legacy_row[7],
            count_adult=count_adult,
            count_larva=count_larva,
            is_bacteria_present=legacy_row[16],
            selected_for_scoring=selected_for_scoring,
            gi_score_larva_per_adult=legacy_row[17],
            gi_score_survival=legacy_row[18]
        )

        # Clean the object to populate the fields derived from other fields
        legacy_score.clean()

        errors = []

        legacy_allele = legacy_score.experiment.worm_strain.allele
        if (legacy_allele != legacy_row[2]):
            # Deal with case of legacy database using zc310 instead of zu310
            if (legacy_row[2] == 'zc310' and
                    legacy_allele == 'zu310'):
                pass

            # Deal with some case sensitivity issues in legacy database
            # (e.g. see experiment 32405, where the allele is capitalized).
            # Can't do lower() in all cases because "N2" should always be
            # capitalized.
            elif legacy_allele == legacy_row[2].lower():
                pass

            else:
                errors.append('allele mismatch')

        # Deal with case of some experiments having the wrong RNAiPlateID
        # in the legacy database's RawDataWithScore table. This field is
        # redundant with the RawData table, and RawData is more trustworthy;
        # however it is still worthwhile to perform this check in order
        # to find the mismatches, and to confirm manually that each one
        # makes sense.
        if legacy_score.experiment.library_plate.id != legacy_row[4]:
            if (legacy_score.experiment.id == 461 or
                    legacy_score.experiment.id == 8345):
                pass
            else:
                errors.append('RNAi plate mismatch')

        if legacy_score.count_embryo != legacy_row[10]:
            errors.append('embryo count mismatch')

        if (legacy_score.embryo_per_adult and legacy_row[8] and
                legacy_row[8] != -1 and
                int(legacy_score.embryo_per_adult) != legacy_row[11]):
            errors.append('embryo per adult mismatch')

        if (legacy_score.larva_per_adult and legacy_row[9] and
                legacy_row[9] != -1 and
                int(legacy_score.larva_per_adult) != legacy_row[12]):
            errors.append('larva per adult mismatch')

        if (legacy_score.survival and not compare_floats_for_equality(
                legacy_score.survival, legacy_row[13]) and
                legacy_row[13] != 0):
            errors.append('invalid survival')
        if (legacy_score.lethality and not compare_floats_for_equality(
                legacy_score.lethality, legacy_row[14]) and
                legacy_row[13] != 0):
            errors.append('invalid lethality')

        if errors:
            sys.exit('DevstarScore for {}:{} had these errors: {}'
                     .format(legacy_row[0], legacy_row[1], errors))

        return update_or_save_object(
            legacy_score, recorded_scores, fields_to_compare,
            alternate_pk={'experiment': legacy_score.experiment,
                          'well': legacy_score.well})

    sync_rows(cursor, legacy_query, sync_score_row)


def update_Clone_table(cursor):
    """Update the Clone table, according to the distinct clones in legacy
    table RNAiPlate.

    Find the distinct Ahringer clone names (in 'sjj_X' format) and
    the L4440 empty vector clone (just called 'L4440')
    from the clone field of RNAiPlate.

    Find the distinct Vidal clone names (in 'GHR-X@X' format)
    from the 384PlateID and 384Well fields of RNAiPlate
    (note that we are no longer using the 'mv_X'-style Vidal clone names,
    and our PK for Vidal clones will now be in 'GHR-X@X' style).

    """
    recorded_clones = Clone.objects.all()
    fields_to_compare = None

    legacy_query = ('SELECT DISTINCT clone FROM RNAiPlate '
                    'WHERE clone LIKE "sjj%" OR clone = "L4440"')

    def sync_clone_row(legacy_row):
        legacy_clone = Clone(id=legacy_row[0])
        return update_or_save_object(legacy_clone, recorded_clones,
                                     fields_to_compare)

    legacy_query_vidal = ('SELECT DISTINCT 384PlateID, 384Well FROM RNAiPlate '
                          'WHERE clone LIKE "mv%"')

    def sync_clone_row_vidal(legacy_row):
        vidal_clone_name = get_vidal_clone_name(legacy_row[0], legacy_row[1])
        legacy_clone = Clone(id=vidal_clone_name)
        return update_or_save_object(legacy_clone, recorded_clones,
                                     fields_to_compare)

    sync_rows(cursor, legacy_query, sync_clone_row)
    sync_rows(cursor, legacy_query_vidal, sync_clone_row_vidal)


def update_LibraryWell_table(cursor):
    """Update the LibraryWell table to reflect the clone layout of all plates:
    source plates (Ahringer 384 and original Orfeome plates e.g. GHR-10001),
    primary plates, and secondary plates. Also update the parent LibraryWells
    of primary and secondary plates.

    This information comes from a variety of queries of
    primarily according to legacy tables RNAiPlate and CherryPickRNAiPlate.
    Detailed comments inline.

    """
    recorded_wells = LibraryWell.objects.all()
    fields_to_compare = ('plate', 'well', 'parent_library_well',
                         'intended_clone')

    # 'Source' plates are Ahringer 384 plates and original Orfeome
    # plates (e.g. GHR-10001). Plate names are captured as they
    # were in update_LibraryPlate_table (i.e., using fields 384PlateID and
    # chromosome). Well is captured in field 384Well. Clone is captured
    # as described in update_Clone_table (i.e., using clone field for
    # sjj clones, and source plate@well for mv clones).
    legacy_query_source = ('SELECT DISTINCT 384PlateID, 384Well, '
                           'chromosome, clone FROM RNAiPlate '
                           'WHERE clone LIKE "sjj%" OR clone LIKE "mv%"')

    def sync_source_row(legacy_row):
        plate_name = legacy_row[0]
        clone_name = legacy_row[3]

        if re.match('sjj', clone_name):
            chromosome = legacy_row[2]
            plate_name = get_ahringer_384_plate_name(chromosome, plate_name)

        well_improper = legacy_row[1]
        well_proper = get_three_character_well(well_improper)

        if re.match('mv', clone_name):
            clone_name = get_vidal_clone_name(plate_name, well_improper)

        legacy_well = LibraryWell(
            id=get_library_well_name(plate_name, well_proper),
            plate=get_library_plate(plate_name),
            well=well_proper,
            parent_library_well=None,
            intended_clone=get_clone(clone_name))

        return update_or_save_object(legacy_well, recorded_wells,
                                     fields_to_compare)

    # Primary well layout is captured in RNAiPlate (fields RNAiPlateID
    # and 96well). Clone is determined the same way as described in
    # update_Clone_table (i.e., clone column for sjj clones, and source
    # plate@well for mv clones). No parent for L4440 wells. Parent for other
    # plates determined using fields 384PlateID, chromosome, and 384Well.
    legacy_query_primary = ('SELECT RNAiPlateID, 96well, clone, '
                            'chromosome, 384PlateID, 384Well '
                            'FROM RNAiPlate')

    def sync_primary_row(legacy_row):
        plate_name = legacy_row[0]
        well_improper = legacy_row[1]
        well_proper = get_three_character_well(well_improper)

        clone_name = legacy_row[2]
        parent_plate_name = legacy_row[4]

        if re.match('sjj', clone_name):
            parent_chromosome = legacy_row[3]
            parent_plate_name = get_ahringer_384_plate_name(parent_chromosome,
                                                            parent_plate_name)
        parent_well_improper = legacy_row[5]
        if re.match('mv', clone_name):
            clone_name = get_vidal_clone_name(parent_plate_name,
                                              parent_well_improper)

        intended_clone = get_clone(clone_name)

        if re.match('L4440', clone_name):
            parent_library_well = None
        else:
            parent_well_proper = get_three_character_well(parent_well_improper)
            parent_library_well_name = get_library_well_name(
                parent_plate_name, parent_well_proper)
            parent_library_well = get_library_well(parent_library_well_name)

            # Confirm that this intended clone matches parent's clone
            if parent_library_well.intended_clone != intended_clone:
                sys.exit('Clone {} does not match parent\n'
                         .format(clone_name))

        legacy_well = LibraryWell(
            id=get_library_well_name(plate_name, well_proper),
            plate=get_library_plate(plate_name),
            well=well_proper,
            parent_library_well=parent_library_well,
            intended_clone=intended_clone)

        return update_or_save_object(legacy_well, recorded_wells,
                                     fields_to_compare)

    # L4440 wells from secondary screen are treated specially (since
    # the complicated join used to resolve parents below complicates things
    # for L4440). L4440 wells have no recorded parent.
    legacy_query_secondary_L4440 = ('SELECT RNAiPlateID, 96well '
                                    'FROM CherryPickRNAiPlate '
                                    'WHERE clone = "L4440"')

    def sync_secondary_L4440_row(legacy_row):
        plate_name = legacy_row[0]
        well_improper = legacy_row[1]
        well_proper = get_three_character_well(well_improper)

        legacy_well = LibraryWell(
            id=get_library_well_name(plate_name, well_proper),
            plate=get_library_plate(plate_name),
            well=well_proper,
            parent_library_well=None,
            intended_clone=get_clone('L4440'))

        return update_or_save_object(legacy_well, recorded_wells,
                                     fields_to_compare)

    # Secondary well layout is captured in CherryPickRNAiPlate (fields
    # RNAiPlate and 96well). However, there are no columns in this table
    # for origin. CherryPickTemplate captures MOST parent relationships,
    # but not all. Therefore, we rely on CherryPickTemplate where available
    # to define parent relationship. Otherwise, we guess based on clone name
    # (which almost always uniquely defines the source well). In the handful
    # of cases not in CherryPickTemplate and where there is ambiguity,
    # we leave the parent undefined (and we will need go back through physical
    # notes to resolve these).
    legacy_query_secondary = (
        'SELECT C.RNAiPlateID as plate, C.96well as well, C.clone, '
        'T.RNAiPlateID as definite_parent_plate, '
        'T.96well as definite_parent_well, '
        'R.RNAiPlateID as likely_parent_plate, '
        'R.96well as likely_parent_well, '
        'R.clone as likely_parent_clone '
        'FROM CherryPickRNAiPlate AS C '
        'LEFT JOIN CherryPickTemplate AS T '
        'ON finalRNAiPlateID = C.RNAiPlateID AND final96well = C.96well '
        'LEFT JOIN RNAiPlate AS R ON C.clone=R.clone AND '
        '(T.RNAiPlateID IS NULL OR '
        '(T.RNAiPlateID=R.RNAiPlateID AND T.96well=R.96well)) '
        'WHERE C.clone != "L4440" '
        'ORDER BY C.RNAiPlateID, C.96well')

    def sync_secondary_row(legacy_row):
        plate_name = legacy_row[0]
        well_improper = legacy_row[1]
        well_proper = get_three_character_well(well_improper)
        clone_name = legacy_row[2]

        definite_parent_plate_name = legacy_row[3]
        definite_parent_well = legacy_row[4]
        if definite_parent_well:
            definite_parent_well = get_three_character_well(
                definite_parent_well)

        likely_parent_plate_name = legacy_row[5]
        likely_parent_well = legacy_row[6]
        if likely_parent_well:
            likely_parent_well = get_three_character_well(likely_parent_well)
        likely_parent_clone_name = legacy_row[7]

        if (definite_parent_plate_name and likely_parent_plate_name and
                definite_parent_plate_name != likely_parent_plate_name):
            sys.exit('ERROR: definite and likely parent plates disagree '
                     'for {} {}\n'.format(plate_name, well_proper))

        if (definite_parent_well and likely_parent_well and
                definite_parent_well != likely_parent_well):
            sys.exit('ERROR: definite and likely parent wells disagree '
                     'for {} {}\n'.format(plate_name, well_proper))

        if definite_parent_plate_name and definite_parent_well:
            parent_library_well_name = get_library_well_name(
                definite_parent_plate_name, definite_parent_well)
        else:
            parent_library_well_name = get_library_well_name(
                likely_parent_plate_name, likely_parent_well)

        try:
            parent_library_well = get_library_well(parent_library_well_name)
            intended_clone = parent_library_well.intended_clone
        except ObjectDoesNotExist:
            sys.stdout.write('WARNING for LibraryWell {} {}: parent not '
                             'found in LibraryWell\n'
                             .format(plate_name, well_proper))
            parent_library_well = None
            intended_clone = None

        if clone_name and (clone_name != likely_parent_clone_name):
            sys.stdout.write('WARNING for LibraryWell {} {}: clone recorded '
                             'in CherryPickRNAiPlate is inconsistent with '
                             'CherryPickTemplate source/destination records\n'
                             .format(plate_name, well_proper))

        if re.match('sjj', clone_name):
            try:
                recorded_clone = get_clone(clone_name)
                if recorded_clone != intended_clone:
                    sys.stdout.write('WARNING for LibraryWell {} {}: '
                                     'clone recorded in CherryPickRNAiPlate '
                                     'does not match its parent\'s clone\n'
                                     .format(plate_name, well_proper))
            except ObjectDoesNotExist:
                sys.stdout.write('WARNING for LibraryWell {} {}: clone '
                                 'recorded in CherryPickRNAiPlate not found '
                                 'at all in RNAiPlate\n'
                                 .format(plate_name, well_proper))

        legacy_well = LibraryWell(
            id=get_library_well_name(plate_name, well_proper),
            plate=get_library_plate(plate_name),
            well=well_proper,
            parent_library_well=parent_library_well,
            intended_clone=intended_clone)

        return update_or_save_object(legacy_well, recorded_wells,
                                     fields_to_compare)
    sync_rows(cursor, legacy_query_source, sync_source_row)
    sync_rows(cursor, legacy_query_primary, sync_primary_row)
    sync_rows(cursor, legacy_query_secondary_L4440,
              sync_secondary_L4440_row)
    sync_rows(cursor, legacy_query_secondary, sync_secondary_row)
