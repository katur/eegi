import MySQLdb
import sys
import datetime


from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone

from eegi.local_settings import LEGACY_DATABASE

from worms.models import WormStrain
from library.models import LibraryPlate
from experiments.models import Experiment, ManualScoreCode, ManualScore
from utils.helpers import well_tile_conversion


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

    Where start is inclusive, end is exclusive,
    and the values for start and end reference the steps below
    (dependencies in parentheses):
    0: LibraryPlate
    1: Experiment (WormStrain, 0)
    2: ManualScoreCode
    3: ManualScore (1, 2)
    4: DevstarScore (1)
    5: Clone
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
                './manage.py migrate_legacy_data\n'
                'OR\n'
                './manage.py migrate_legacy_data start end\n'
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
    Update the LibraryPlate table, primarily against distinct RNAiPlateID in
    legacy tables RNAiPlate and CherryPickRNAiPlate.
    """
    def sync_legacy_library_plate_table(legacy_table_name, screen_stage):
        cursor.execute('SELECT DISTINCT RNAiPlateID FROM ' + legacy_table_name)
        legacy_rows = cursor.fetchall()
        all_match = True

        for legacy_row in legacy_rows:
            matches = sync_legacy_library_plate(legacy_row, screen_stage)
            all_match &= matches

        report_table_sync_outcome(all_match, legacy_table_name)

    def sync_legacy_library_plate(legacy_row, screen_stage,
                                  number_of_wells=96):
        legacy_plate = LibraryPlate(id=legacy_row[0],
                                    screen_stage=screen_stage,
                                    number_of_wells=number_of_wells)
        fields_to_compare = ('screen_stage', 'number_of_wells')
        return update_or_save_object(legacy_plate, recorded_plates,
                                     fields_to_compare)

    recorded_plates = LibraryPlate.objects.all()

    original_384_plates = {'I': 8, 'II': 9, 'III': 7, 'IV': 8, 'V': 13, 'X': 7}

    for chromosome in original_384_plates:
        number = original_384_plates[chromosome]
        for i in range(1, number+1):
            sync_legacy_library_plate(['{}-{}'.format(chromosome, str(i))], 0,
                                      384)

    sync_legacy_library_plate(['Eliana_ReArray_1'], 1)
    sync_legacy_library_plate(['Eliana_ReArray_2'], 1)
    sync_legacy_library_plate_table('RNAiPlate', 1)
    sync_legacy_library_plate_table('CherryPickRNAiPlate', 2)


def update_Experiment_table(cursor):
    """
    Update the Experiment table, primary against legacy table RawData.
    """
    def sync_legacy_experiment(legacy_row):
        legacy_experiment = Experiment(
            id=legacy_row[0],
            worm_strain=get_worm_strain(legacy_row[1], legacy_row[2]),
            library_plate=get_library_plate(legacy_row[3]),
            temperature=legacy_row[4],
            date=legacy_row[5],
            is_junk=legacy_row[6],
            comment=legacy_row[7]
        )

        fields_to_compare = ('worm_strain', 'library_plate',
                             'temperature', 'date', 'is_junk', 'comment',)
        return update_or_save_object(legacy_experiment, recorded_experiments,
                                     fields_to_compare)

    recorded_experiments = Experiment.objects.all()
    cursor.execute('SELECT expID, mutant, mutantAllele, RNAiPlateID, '
                   'CAST(SUBSTRING_INDEX(temperature, "C", 1) '
                   'AS DECIMAL(3,1)), '
                   'CAST(recordDate AS DATE), ABS(isJunk), comment '
                   'FROM RawData '
                   'WHERE (expID < 40000 OR expID>=50000) '
                   'AND RNAiPlateID NOT LIKE "Julie%"')
    legacy_rows = cursor.fetchall()
    all_match = True
    for legacy_row in legacy_rows:
        match = sync_legacy_experiment(legacy_row)
        all_match &= match

    report_table_sync_outcome(all_match, 'RNAiPlateID')


def update_ManualScoreCode_table(cursor):
    """
    Update the ManualScoreCode table, against the legacy table of the same
    name.
    """
    def sync_legacy_score_code(legacy_row):
        legacy_score_code = ManualScoreCode(
            id=legacy_row[0],
            legacy_description=legacy_row[1].decode('utf8'),
        )

        fields_to_compare = ('legacy_description',)
        return update_or_save_object(legacy_score_code, recorded_score_codes,
                                     fields_to_compare)

    recorded_score_codes = ManualScoreCode.objects.all()
    cursor.execute('SELECT code, definition FROM ManualScoreCode')
    legacy_rows = cursor.fetchall()
    all_match = True
    for legacy_row in legacy_rows:
        match = sync_legacy_score_code(legacy_row)
        all_match &= match

    report_table_sync_outcome(all_match, 'ManualScoreCode')


def update_ManualScore_table(cursor):
    """
    Requires that ScoreYear, ScoreMonth, ScoreDate, and ScoreTime
    are valid fields for a python datetime.datetime.
    """

    def sync_legacy_score(legacy_row):
        scorer = get_user(legacy_row[3])
        if not scorer:
            sys.stderr.write('WARNING: skipping a score '
                             'scored by non-User {}\n'
                             .format(legacy_row[3]))
            return True

        timestamp = get_timestamp(legacy_row[5], legacy_row[6], legacy_row[7],
                                  legacy_row[8], legacy_row[4])
        if not timestamp:
            sys.exit('ERROR: score of {}({}), '
                     'could not be converted to a proper '
                     'datetime'.format(legacy_row[0], legacy_row[1]))
        legacy_score = ManualScore(
            experiment=get_experiment(legacy_row[0]),
            well=well_tile_conversion.get_well(legacy_row[1]),
            score_code=get_score_code(legacy_row[2]),
            scorer=scorer,
            timestamp=timestamp,
        )

        return update_or_save_object(
            legacy_score, recorded_scores, None,
            alternate_pk={'experiment': legacy_score.experiment,
                          'well': legacy_score.well,
                          'score_code': legacy_score.score_code,
                          'scorer': legacy_score.scorer,
                          'timestamp': timestamp}
        )

    recorded_scores = ManualScore.objects.all()
    cursor.execute('SELECT expID, ImgName, score, scoreBy, scoreYMD, '
                   'ScoreYear, ScoreMonth, ScoreDate, ScoreTime '
                   'FROM ManualScore')
    legacy_rows = cursor.fetchall()
    all_match = True
    for legacy_row in legacy_rows:
        match = sync_legacy_score(legacy_row)
        all_match &= match


def update_DevstarScore_table(cursor):
    pass


def update_Clone_table(cursor):
    pass


def update_LibraryWell_table(cursor):
    pass


def update_LibrarySequencing_table(cursor):
    pass


def update_or_save_object(legacy_object, recorded_objects, fields_to_compare,
                          alternate_pk=False):
    """
    Bring the new database up to speed regarding a particular legacy object.
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
        save_object(legacy_object)
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
        if getattr(object, field) != getattr(legacy_object, field):
            differences.append('{} was previously recorded as {}, '
                               'but is now {} in legacy database\n'
                               .format(field,
                                       str(getattr(object, field)),
                                       str(getattr(legacy_object, field))))
            if update:
                setattr(object, field, getattr(legacy_object, field))
                object.save()

    if differences:
        sys.stderr.write('WARNING: Object {} had these changes: {}\n'
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


def save_object(object):
    """
    Save an object to the database, printing a warning to syserr.
    """
    object.save()
    '''
    sys.stderr.write('WARNING: Added new object {} '
                     'to the database\n'
                     .format(str(object)))
    '''


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
    if username == 'katy' or username == 'expPeople':
        return None

    try:
        return User.objects.get(username=username)
    except ObjectDoesNotExist:
        sys.exit('ERROR: User with username ' + str(username) +
                 'not found in the new database\n')


def get_timestamp(year, month, day, time, ymd):
    """
    Return a datetime.datetime object from an int year,
    a 3-letter-string month (e.g. 'Jan'), an int day,
    and a string time in format '00:00:00'.

    If a ymd is passed in, it is simply confirmed to match the date derived
    from the year/month/day/time.

    If the year/month/day/time or ymd are not in the expected format,
    or if both exist and are in the expected format yet they do not match
    each other, returns None.
    """
    try:
        string = '{}-{}-{}::{}'.format(year, month, day, time)
        timestamp = timezone.make_aware(
            datetime.datetime.strptime(string, '%Y-%b-%d::%H:%M:%S'),
            timezone.get_default_timezone())
    except Exception:
        return None

    if ymd:
        try:
            hour, minute, second = time.split(':')
            timestamp_from_ymd = timezone.make_aware(
                datetime.datetime(ymd.year, ymd.month, ymd.day,
                                  int(hour), int(minute), int(second)),
                timezone.get_default_timezone())

            if timestamp != timestamp_from_ymd:
                return None

        except Exception:
            return None

    return timestamp


def report_table_sync_outcome(all_match, legacy_table_name):
    """
    Print to stdout whether all legacy objects from a particular table
    were already present and match the new database.
    """
    if all_match:
        sys.stdout.write('All objects from legacy table {} already present\n'
                         .format(legacy_table_name))
    else:
        sys.stdout.write('Some objects added or updated from legacy table {} '
                         '(individual changes printed to sys.stderr.)\n'
                         .format(legacy_table_name))
