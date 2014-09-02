import MySQLdb
import sys

from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist

from eegi.local_settings import LEGACY_DATABASE

from worms.models import WormStrain
from library.models import LibraryPlate
from experiments.models import Experiment


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

    To run this command, from the project root:
    ./manage.py migrate_legacy_data
    """
    help = ('Update this database according to legacy database')

    def handle(self, *args, **options):
        """
        Main script to update the database according to the legacy database.
        """
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
        update_LibraryPlate_table(cursor)
        update_Experiment_table(cursor)


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

    original_384_plates = {
        'I': 8,
        'II': 9,
        'III': 7,
        'IV': 8,
        'V': 13,
        'X': 7,
    }

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
                             'temperature', 'date', 'is_junk', 'comment')
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


def update_or_save_object(legacy_object, recorded_objects, fields_to_compare):
    """
    Bring the new database up to speed regarding a particular legacy object.
    If the legacy object is not present, add it (and print to syserr).
    If the legacy object is present, confirm the provided fields match.
    If any fields do not match, update them (and print updates to syserr).

    Returns True if the legacy object was already present and matches
    on all provided fields. Returns False otherwise.
    """
    try:
        recorded_object = recorded_objects.get(pk=legacy_object.pk)
        return compare_fields(recorded_object, legacy_object,
                              fields_to_compare, update=True)
    except ObjectDoesNotExist:
        save_object(legacy_object)
        return False


def save_object(object):
    """
    Save an object to the database, printing a warning to syserr.
    """
    object.save()
    sys.stderr.write('WARNING: Added new object {} '
                     'to the database\n'
                     .format(str(object)))


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
