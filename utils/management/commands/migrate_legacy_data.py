import MySQLdb
import sys

from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User

from eegi.local_settings import LEGACY_DATABASE
from utils.helpers.well_tile_conversion import (tile_to_well,
                                                get_three_character_well)
from utils.helpers.time_conversion import get_timestamp
from worms.models import WormStrain
from clones.models import Clone
from library.models import LibraryPlate
from experiments.models import (Experiment, ManualScoreCode, ManualScore,
                                DevstarScore)


class Command(BaseCommand):
    """
    Command to update this project's database according to the legacy database.

    Requires connection info for legacy database in local_settings, in format:
    LEGACY_DATABASE = {
        'NAME': 'GenomeWideGI',
        'HOST': 'localhost',
        'USER': 'my_username',
        'PASSWORD': 'my_password',
    }

    To update all tables, execute as so (from the project root):
    ./manage.py migrate_legacy_data

    To update just a range of tables, execute as so:
    ./manage.py migrate_legacy_data start end

    Stdout reports whether a particular step had no changes or had changes.
    Stderr reports every change (such as an added row), and thus can get
        quite long; consider redirecting with 2> stderr.out.

    Where start is inclusive, end is exclusive,
    and the values for start and end reference the steps below
    (dependencies in parentheses):
        0: LibraryPlate
        1: Experiment (WormStrain, 0)
        2: ManualScoreCode
        3: ManualScore (1, 2)
        4: DevstarScore (1)
        5: Clone (named RNAiClone in database)
        6: LibraryWell (0, 5)
        7: LibrarySequencing (6)
    """
    help = ('Update this database according to legacy database')

    def handle(self, *args, **options):
        """
        Main script to update the database according to the legacy database.
        """
        if len(args) != 0 and len(args) != 2:
            sys.exit(
                'Usage:\n'
                '\t./manage.py migrate_legacy_data\n'
                'or\n'
                '\t./manage.py migrate_legacy_data start end\n'
                '(where start is inclusive and end is exclusive)\n'
            )

        steps = (
            update_LibraryPlate_table,
            update_Experiment_table,
            update_ManualScoreCode_table,
            update_ManualScore_table,
            update_DevstarScore_table,
            update_Clone_table,
            update_LibraryWell_table,
            update_LibrarySequencing_table,
        )

        if args:
            try:
                start = int(args[0])
                end = int(args[1])
            except ValueError:
                raise CommandError('Start and endpoints must be integers')
            if start >= end:
                raise CommandError('Start must be less than end')
            if (start < 0) or (end > len(steps)):
                raise CommandError('Start and end must be in range 0-{}'
                                   .format(str(len(steps))))
        else:
            start = 0
            end = len(steps)

        proceed = False
        while not proceed:
            sys.stdout.write('This script modifies the database. '
                             'Proceed? (yes/no): ')
            response = raw_input()
            if response == 'no':
                sys.stdout.write('Okay. Goodbye!\n')
                sys.exit(0)
            elif response != 'yes':
                sys.stdout.write('Please try again, '
                                 'responding "yes" or "no"\n')
                continue
            else:
                proceed = True

        legacy_db = MySQLdb.connect(host=LEGACY_DATABASE['HOST'],
                                    user=LEGACY_DATABASE['USER'],
                                    passwd=LEGACY_DATABASE['PASSWORD'],
                                    db=LEGACY_DATABASE['NAME'])
        cursor = legacy_db.cursor()

        for step in range(start, end):
            steps[step](cursor)


def update_LibraryPlate_table(cursor):
    """
    Update the LibraryPlate table by finding the distinct plates names in
    legacy tables RNAiPlate (defines the well-level contents of primary plates)
    and CherryPickRNAiPlate (well-level contents of secondary plates).

    Rows representing the 384-well plates and some miscellanous plates
    (such as the Eliana Rearray plates) are hardcoded into the script.
    """
    legacy_query = 'SELECT DISTINCT RNAiPlateID FROM {}'
    recorded_plates = LibraryPlate.objects.all()
    fields_to_compare = ('screen_stage', 'number_of_wells')

    def sync_library_plate_row(legacy_row, screen_stage, number_of_wells=96):
        legacy_plate = LibraryPlate(id=legacy_row[0],
                                    screen_stage=screen_stage,
                                    number_of_wells=number_of_wells)
        return update_or_save_object(legacy_plate, recorded_plates,
                                     fields_to_compare)

    original_384_plates = {'I': 8, 'II': 9, 'III': 7, 'IV': 8, 'V': 13, 'X': 7}

    for chromosome in original_384_plates:
        number = original_384_plates[chromosome]
        for i in range(1, number+1):
            sync_library_plate_row(['{}-{}'.format(chromosome, str(i))],
                                   0, 384)

    sync_library_plate_row(['Eliana_ReArray_1'], 1)
    sync_library_plate_row(['Eliana_ReArray_2'], 1)

    sync_rows(cursor, legacy_query.format('RNAiPlate'),
              sync_library_plate_row, screen_stage=1)
    sync_rows(cursor, legacy_query.format('CherryPickRNAiPlate'),
              sync_library_plate_row, screen_stage=2)


def update_Experiment_table(cursor):
    """
    Update the Experiment table according to legacy table RawData.

    Several datatype transforms occur from the old to the new schema:

        - mutant/mutantAllele become a FK to WormStrain
        - RNAiPlateID becomes a FK to LibraryPlate
        - temperature as string (with 'C') becomes a decimal
        - recordDate as string becomes a DATE
        - isJunk becomes a boolean (with both 1 and -1 becoming True)

    Also, experiments of Julie's (which were done with a line of spn-4 worms
    later deemed untrustworthy) are excluded.
    """
    legacy_query = ('SELECT expID, mutant, mutantAllele, RNAiPlateID, '
                    'CAST(SUBSTRING_INDEX(temperature, "C", 1) '
                    'AS DECIMAL(3,1)), '
                    'CAST(recordDate AS DATE), ABS(isJunk), comment '
                    'FROM RawData '
                    'WHERE (expID < 40000 OR expID>=50000) '
                    'AND RNAiPlateID NOT LIKE "Julie%"')

    recorded_experiments = Experiment.objects.all()
    fields_to_compare = ('worm_strain', 'library_plate', 'screen_level',
                         'temperature', 'date', 'is_junk', 'comment',)

    def sync_experiment_row(legacy_row):
        expID = legacy_row[0]
        if expID < 40000:
            screen_level = 1
        else:
            screen_level = 2
        legacy_experiment = Experiment(
            id=legacy_row[0],
            worm_strain=get_worm_strain(legacy_row[1], legacy_row[2]),
            library_plate=get_library_plate(legacy_row[3]),
            screen_level=screen_level,
            temperature=legacy_row[4],
            date=legacy_row[5],
            is_junk=legacy_row[6],
            comment=legacy_row[7]
        )
        return update_or_save_object(legacy_experiment, recorded_experiments,
                                     fields_to_compare)

    sync_rows(cursor, legacy_query, sync_experiment_row)


def update_ManualScoreCode_table(cursor):
    """
    Update the ManualScoreCode table according to the legacy table of the same
    name.

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
    legacy_query = ('SELECT code, definition FROM ManualScoreCode '
                    'WHERE code != -8 AND code != -1 AND code != 4 '
                    'AND code != 5 AND code != 6 AND code != -6')
    recorded_score_codes = ManualScoreCode.objects.all()
    fields_to_compare = ('legacy_description',)

    def sync_score_code_row(legacy_row):
        legacy_score_code = ManualScoreCode(
            id=legacy_row[0],
            legacy_description=legacy_row[1].decode('utf8'),
        )

        return update_or_save_object(legacy_score_code, recorded_score_codes,
                                     fields_to_compare)

    sync_rows(cursor, legacy_query, sync_score_code_row)


def update_ManualScore_table(cursor):
    """
    Update the ManualScore table according to the legacy table of the same
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
    legacy_query = ('SELECT ManualScore.expID, ImgName, score, scoreBy, '
                    'scoreYMD, ScoreYear, ScoreMonth, ScoreDate, ScoreTime, '
                    'mutant, screenFor '
                    'FROM ManualScore '
                    'LEFT JOIN RawData '
                    'ON ManualScore.expID = RawData.expID '
                    'WHERE score != -8 AND score != -1 AND score != 4 '
                    'AND score != 5 AND score != 6')
    recorded_scores = ManualScore.objects.all()
    fields_to_compare = None

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


def update_DevstarScore_table(cursor):
    """
    Update the DevstarScore table according to legacy table RawDataWithScore.

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
        - machineCall becomes a boolean
    """
    legacy_query = ('SELECT expID, 96well, '
                    'mutantAllele, targetRNAiClone, RNAiPlateID, '
                    'areaWorm, areaLarvae, areaEmbryo, '
                    'AdultCount, LarvaeCount, EggCount, '
                    'EggPerWorm, LarvaePerWorm, survival, lethality, '
                    'machineCall, machineDetectBac, '
                    'GIscoreLarvaePerWorm, GIscoreSurvival '
                    'FROM RawDataWithScore '
                    'LIMIT 25000')

    recorded_scores = DevstarScore.objects.all()
    fields_to_compare = ('area_adult', 'area_larva', 'area_embryo',
                         'count_adult', 'count_larva', 'is_bacteria_present',
                         'count_embryo', 'larva_per_adult',
                         'embryo_per_adult', 'survival', 'lethality',)

    def sync_score_row(legacy_row):
        # Build the object using the minimimum fields
        count_adult = legacy_row[8]
        count_larva = legacy_row[9]
        if count_adult == -1:
            count_adult = None
        if count_larva == -1:
            count_larva = None

        legacy_score = DevstarScore(
            experiment=get_experiment(legacy_row[0]),
            well=legacy_row[1],
            area_adult=legacy_row[5],
            area_larva=legacy_row[6],
            area_embryo=legacy_row[7],
            count_adult=count_adult,
            count_larva=count_larva,
            is_bacteria_present=legacy_row[16],
        )

        # Clean the object to populate the fields derived from other fields
        legacy_score.clean()

        errors = []
        if legacy_score.experiment.worm_strain.allele != legacy_row[2]:
            errors.append('allele mismatch')
        if legacy_score.experiment.library_plate.id != legacy_row[4]:
            errors.append('RNAi plate mismatch')
        if legacy_score.count_embryo != legacy_row[10]:
            errors.append('embryo count mismatch')

        if (legacy_row[8] and legacy_row[8] != -1 and
                int(legacy_score.embryo_per_adult) != legacy_row[11]):
            errors.append('embryo per adult mismatch')
        if (legacy_row[9] and legacy_row[9] != -1 and
                int(legacy_score.larva_per_adult) != legacy_row[12]):
            errors.append('larva per adult mismatch')

        if (not compare_floats_for_equality(
                legacy_score.survival, legacy_row[13]) and
                legacy_row[13] != 0):
            errors.append('invalid survival')
        if (not compare_floats_for_equality(
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
    """
    Update the Clone table by finding the distinct Ahringer clone names
    (prefixed 'sjj') and the L4440 empty vector clone from RNAiPlate,
    and getting the Vidal clone names from the CSV from John Kim
    (since we want to migrate away from RNAiPlate's use of mv_X names).
    """
    legacy_query = ('SELECT DISTINCT clone FROM RNAiPlate '
                    'WHERE clone LIKE "sjj%" OR clone = "L4440"')
    recorded_clones = Clone.objects.all()
    fields_to_compare = None

    def sync_clone_row(legacy_row):
        legacy_clone = Clone(id=legacy_row[0])
        return update_or_save_object(legacy_clone, recorded_clones,
                                     fields_to_compare)

    sync_rows(cursor, legacy_query, sync_clone_row)


def update_LibraryWell_table(cursor):
    pass


def update_LibrarySequencing_table(cursor):
    pass


def sync_rows(cursor, legacy_query, sync_row_function, **kwargs):
    """
    Sync the rows resulting from a query to the legacy database
    to the current database, according to
    sync_row_function(legacy_row, **kwargs).
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


def update_or_save_object(legacy_object, recorded_objects, fields_to_compare,
                          alternate_pk=False):
    """
    Bring the new database up to speed with a particular legacy object.

    If the legacy object is not present, add it (and print to syserr).

    If the legacy object is present, confirm the provided fields match.
    If any fields do not match, update them (and print updates to syserr).

    Returns True if the legacy object was already present and matches
    on all provided fields. Returns False otherwise.
    """
    try:
        if alternate_pk:
            recorded_object = recorded_objects.get(**alternate_pk)
        else:
            recorded_object = recorded_objects.get(pk=legacy_object.pk)
        if fields_to_compare:
            return compare_fields(recorded_object, legacy_object,
                                  fields_to_compare, update=True)
        else:
            return True

    except ObjectDoesNotExist:
        legacy_object.save()
        sys.stderr.write('Added new record {} to the database\n'
                         .format(str(legacy_object)))
        return False


def compare_fields(object, legacy_object, fields, update=False):
    """
    Compare two objects on the provided fields.
    Any differences are printed to stderr.
    If 'update' is True, object is updated to match
    legacy_object on these fields.

    Used to bring an object already recorded in this project's database
    up to date with the corresponding object in the legacy database.
    """
    differences = []
    for field in fields:
        if not compare_fields_for_equality(getattr(object, field),
                                           getattr(legacy_object, field)):
            differences.append('{} was previously recorded as {}, '
                               'but is now {} in legacy database\n'
                               .format(field,
                                       str(getattr(object, field)),
                                       str(getattr(legacy_object, field))))
            if update:
                setattr(object, field, getattr(legacy_object, field))
                object.save()

    if differences:
        sys.stderr.write('WARNING: Record {} had these changes: {}\n'
                         .format(str(object),
                                 str([d for d in differences])))
        if update:
            sys.stderr.write('The new database was updated to reflect '
                             'the changes\n\n')
        else:
            sys.stderr.write('The new database was NOT updated to reflect '
                             'the changes\n\n')
        return False
    else:
        return True


def get_worm_strain(mutant, mutantAllele):
    """
    Get a worm strain from new database,
    from its mutant gene and mutant allele.

    Exists with an error if the worm strain is not present.
    """
    try:
        if mutant == 'N2':
            gene = None
            allele = None
            worm_strain = WormStrain.objects.get(id='N2')
        else:
            gene = mutant
            allele = mutantAllele
            if allele == 'zc310':
                allele = 'zu310'
            worm_strain = WormStrain.objects.get(gene=gene, allele=allele)
        return worm_strain

    except ObjectDoesNotExist:
        sys.exit('ERROR: Strain with mutant: ' + mutant +
                 ', mutantAllele: ' + mutantAllele +
                 ' in the legacy database does not match any '
                 'worm strain in the new database\n')


def get_library_plate(library_plate_as_string):
    """
    Get a library plate from the new database, from its plate name.

    Exits with an error if the plate is not present.
    """
    try:
        return LibraryPlate.objects.get(id=library_plate_as_string)

    except ObjectDoesNotExist:
        sys.exit('ERROR: RNAiPlateID ' + library_plate_as_string +
                 ' in the legacy database does not match any library '
                 'plate in the new database\n')


def get_experiment(id):
    try:
        return Experiment.objects.get(id=id)
    except ObjectDoesNotExist:
        sys.exit('ERROR: Experiment ' + str(id) +
                 'not found in the new database\n')


def get_score_code(id):
    try:
        return ManualScoreCode.objects.get(id=id)
    except ObjectDoesNotExist:
        sys.exit('ERROR: ManualScoreCode with id ' + str(id) +
                 'not found in the new database\n')


def get_user(username):
    if username == 'Julie':
        username = 'julie'
    if username == 'patricia':
        username = 'giselle'

    try:
        return User.objects.get(username=username)
    except ObjectDoesNotExist:
        sys.exit('ERROR: User with username ' + str(username) +
                 'not found in the new database\n')


def compare_floats_for_equality(x, y):
    if x is None and y is None:
        return True
    elif x is None or y is None:
        return False
    elif abs(x - y) < 0.001:
        return True
    else:
        return False


def compare_fields_for_equality(x, y):
    if isinstance(x, float) or isinstance(x, long):
        return compare_floats_for_equality(x, y)
    else:
        return x == y
