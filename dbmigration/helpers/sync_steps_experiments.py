"""This module contains the steps for the sync_legacy_database command
that involve the experiments app.

"""
from django.core.management.base import CommandError

from dbmigration.helpers.name_getters import get_experiment_name

from dbmigration.helpers.object_getters import (
    get_experiment, get_experiment_plate,
    get_worm_strain, get_library_well, get_score_code, get_user)

from dbmigration.helpers.sync_helpers import sync_rows, update_or_save_object

from experiments.models import (Experiment, ExperimentPlate, DevstarScore,
                                ManualScoreCode, ManualScore)

from utils.comparison import compare_floats_for_equality
from utils.plate_layout import get_well_list
from utils.time_conversion import get_timestamp, get_timestamp_from_ymd
from utils.well_tile_conversion import tile_to_well


def update_Experiment_tables(command, cursor):
    """Update the ExperimentPlate and Experiment tables according
    to legacy table RawData.

    Several datatype transforms occur from the old to the new schema:

        - recordDate string becomes a DATE
        - temperature string (suffixed 'C') becomes a decimal
        - plate-level mutant/mutantAllele becomes well-level FK to WormStrain
        - plate-level RNAiPlateID becomes becomes well-level pointers to
          LibraryWells
        - plate-level isJunk with three values (-1, 0, 1) becomes a boolean
          (with both 1 and -1 becoming 1), and and becomes well-level

    Also, experiments of Julie's (which were done with a line of spn-4 worms
    later deemed untrustworthy) are excluded.

    """
    recorded_plates = ExperimentPlate.objects.all()
    recorded_wells = Experiment.objects.all()

    plate_fields_to_compare = ('screen_stage', 'temperature', 'date',
                               'comment')

    well_fields_to_compare = ('plate', 'well', 'worm_strain',
                              'library_well', 'is_junk')

    legacy_query = ('SELECT expID, mutant, mutantAllele, RNAiPlateID, '
                    'CAST(SUBSTRING_INDEX(temperature, "C", 1) '
                    'AS DECIMAL(3,1)), '
                    'CAST(recordDate AS DATE), ABS(isJunk), comment '
                    'FROM RawData '
                    'WHERE (expID < 40000 OR expID >= 50000) '
                    'AND RNAiPlateID NOT LIKE "Julie%" '
                    'ORDER BY expID')

    def sync_experiment_row(legacy_row):
        experiment_plate_id = legacy_row[0]
        worm_strain = get_worm_strain(legacy_row[1], legacy_row[2])
        legacy_library_plate_name = legacy_row[3]
        temperature = legacy_row[4]
        date = legacy_row[5]
        is_junk = legacy_row[6]
        comment = legacy_row[7]

        all_match = True

        if experiment_plate_id < 40000:
            screen_stage = 1
        else:
            screen_stage = 2

        new_plate = ExperimentPlate(
            id=experiment_plate_id,
            screen_stage=screen_stage,
            temperature=temperature,
            date=date,
            comment=comment)

        all_match &= update_or_save_object(
            command, new_plate, recorded_plates, plate_fields_to_compare)

        experiment_plate = get_experiment_plate(experiment_plate_id)

        for well in get_well_list():
            new_well = Experiment(
                id=get_experiment_name(experiment_plate_id, well),
                plate=experiment_plate, well=well,
                worm_strain=worm_strain,
                library_well=get_library_well(
                    legacy_library_plate_name, well),
                is_junk=is_junk)

            all_match &= update_or_save_object(
                command, new_well, recorded_wells,
                well_fields_to_compare)

        return all_match

    sync_rows(command, cursor, legacy_query, sync_experiment_row)


def update_DevstarScore_table(command, cursor):
    """Update the DevstarScore table according to legacy table
    RawDataWithScore.

    Redundant fields (mutantAllele, targetRNAiClone, RNAiPlateID) are
    excluded.

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
        - division by 0 in embryo/larva per adult remain 0, but when
          adult=0 we DO now calculate survival and lethality
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
                    'AND expID >= 460 '
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

        new_score = DevstarScore(
            experiment=get_experiment(legacy_row[0], legacy_row[1]),
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
        new_score.clean()

        errors = []

        new_allele = new_score.experiment.worm_strain.allele
        if (new_allele != legacy_row[2]):
            # Deal with case of legacy database using zc310 instead of zu310
            if (legacy_row[2] == 'zc310' and
                    new_allele == 'zu310'):
                pass

            # Deal with some case sensitivity issues in legacy database
            # (e.g. see experiment 32405, where the allele is capitalized).
            # Can't do lower() in all cases because "N2" should always be
            # capitalized.
            elif new_allele == legacy_row[2].lower():
                pass

            else:
                errors.append('allele mismatch')

        # Deal with case of some experiments having the wrong RNAiPlateID
        # in the legacy database's RawDataWithScore table. This field is
        # redundant with the RawData table, and RawData is more trustworthy;
        # however it is still worthwhile to perform this check in order
        # to find the mismatches, and to confirm manually that each one
        # makes sense.
        new_lp = new_score.experiment.library_well.library_plate_id
        legacy_lp = legacy_row[4]
        if (legacy_lp != new_lp and
                new_score.experiment.plate_id not in (461, 8345) and
                legacy_lp != new_lp.replace('-', '_') and
                legacy_lp != new_lp.replace('zu310', 'zc310') and
                ('vidal-' not in new_lp or
                    legacy_lp != new_lp.split('vidal-')[1])):
            errors.append('RNAi plate mismatch')

        if new_score.count_embryo != legacy_row[10]:
            errors.append('embryo count mismatch')

        if (new_score.embryo_per_adult and legacy_row[8] and
                legacy_row[8] != -1 and
                int(new_score.embryo_per_adult) != legacy_row[11]):
            errors.append('embryo per adult mismatch')

        if (new_score.larva_per_adult and legacy_row[9] and
                legacy_row[9] != -1 and
                int(new_score.larva_per_adult) != legacy_row[12]):
            errors.append('larva per adult mismatch')

        if (new_score.survival and not compare_floats_for_equality(
                new_score.survival, legacy_row[13]) and
                legacy_row[13] != 0):
            errors.append('invalid survival')

        if (new_score.lethality and not compare_floats_for_equality(
                new_score.lethality, legacy_row[14]) and
                legacy_row[13] != 0):
            errors.append('invalid lethality')

        if errors:
            raise CommandError(
                'DevstarScore for {}:{} had these errors: {}'
                .format(legacy_row[0], legacy_row[1], errors))

        return update_or_save_object(
            command, new_score, recorded_scores, fields_to_compare,
            alternate_pk={'experiment': new_score.experiment})

    sync_rows(command, cursor, legacy_query, sync_score_row)


def update_ManualScoreCode_table(command, cursor):
    """Update the ManualScoreCode table according to the legacy table.

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
        new_score_code = ManualScoreCode(
            id=legacy_row[0],
            legacy_description=legacy_row[1].decode('utf8'))

        return update_or_save_object(
            command, new_score_code, recorded_score_codes, fields_to_compare)

    sync_rows(command, cursor, legacy_query, sync_score_code_row)


def update_ManualScore_table_primary(command, cursor):
    """Update the ManualScore table according to the legacy table.

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
                    'scoreYMD, ScoreYear, ScoreMonth, ScoreDate, '
                    'ScoreTime, mutant, screenFor '
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
            command.stderr.write(
                'FYI: Skipping a {} {} score of {} by {}\n'
                .format(gene, screen, legacy_score_code, legacy_scorer))

            return True

        # Convert some scorers to hueyling (see criteria above)
        if legacy_scorer == 'Julie' or legacy_scorer == 'expPeople':
            command.stderr.write(
                'FYI: Converting a {} score by {} to hueyling\n'
                .format(legacy_score_code, legacy_scorer))

            legacy_scorer = 'hueyling'

        # Convert some score codes (see criteria above)
        if legacy_score_code == -6:
            command.stderr.write('FYI: Converting score from -6 to -7\n')
            legacy_score_code = -7

        # Following raise exceptions if improperly formatted or not found
        experiment = get_experiment(legacy_row[0], tile_to_well(legacy_row[1]))
        score_code = get_score_code(legacy_score_code)
        scorer = get_user(legacy_scorer)

        timestamp = get_timestamp(legacy_row[5], legacy_row[6], legacy_row[7],
                                  legacy_row[8], legacy_row[4])
        if not timestamp:
            raise CommandError(
                'ERROR: score of {} could  not be converted to a proper '
                'datetime'.format(experiment))

        new_score = ManualScore(
            experiment=experiment,
            score_code=score_code,
            scorer=scorer,
            timestamp=timestamp)

        return update_or_save_object(
            command, new_score, recorded_scores, fields_to_compare,
            alternate_pk={'experiment': new_score.experiment,
                          'score_code': new_score.score_code,
                          'scorer': new_score.scorer,
                          'timestamp': new_score.timestamp})

    sync_rows(command, cursor, legacy_query, sync_score_row)


def update_ManualScore_table_secondary(command, cursor):
    recorded_scores = ManualScore.objects.all()
    fields_to_compare = None
    legacy_query = ('SELECT expID, ImgName, score, '
                    'scoreBy, scoreYMD, ScoreTime '
                    'FROM ScoreResultsManual')

    def sync_score_row(legacy_row):
        legacy_score_code = legacy_row[2]
        legacy_scorer = legacy_row[3]
        experiment = get_experiment(legacy_row[0], tile_to_well(legacy_row[1]))
        score_code = get_score_code(legacy_score_code)
        scorer = get_user(legacy_scorer)

        timestamp = get_timestamp_from_ymd(legacy_row[4], legacy_row[5])
        if not timestamp:
            raise CommandError(
                'ERROR: score of experiment {}, well {} '
                'could not be converted to a proper datetime'
                .format(legacy_row[0], legacy_row[1]))

        new_score = ManualScore(
            experiment=experiment,
            score_code=score_code,
            scorer=scorer,
            timestamp=timestamp)

        return update_or_save_object(
            command, new_score, recorded_scores, fields_to_compare,
            alternate_pk={'experiment': new_score.experiment,
                          'score_code': new_score.score_code,
                          'scorer': new_score.scorer,
                          'timestamp': new_score.timestamp})

    sync_rows(command, cursor, legacy_query, sync_score_row)
