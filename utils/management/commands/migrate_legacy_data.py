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
    Script to update this project's database according to the legacy database.

    Include connection info for legacy database in local_settings, in format:
    LEGACY_DATABASE = {
        'NAME': 'GenomeWideGI',
        'HOST': 'localhost',
        'USER': 'my_username',
        'PASSWORD': 'my_password',
    }

    To run program:
    ./manage.py migrate_legacy_data
    """
    help = ('Update this database according to legacy database')

    def handle(self, *args, **options):
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
        sync_LibraryPlate_table(cursor)
        # sync_Experiment_table(cursor)


def compare_fields(recorded, new, fields, update=False):
    differences = []
    for field in fields:
        if getattr(recorded, field) != getattr(new, field):
            differences.append(field + ' is ' +
                               str(getattr(recorded, field)) + ' in recorded, '
                               'and ' + str(getattr(new, field)) + ' in new\n')
            if update:
                setattr(recorded, field, getattr(new, field))
    return differences


def sync_LibraryPlate_table(cursor):
    """
    Sync the LibraryPlate table.

    Specifically, makes sure all distinct RNAiPlateID from
    RNAiPlate and CherryPickRNAiPlate tables are included in the new database.
    """
    def sync_row(row, screen_stage, number_of_wells=96):
        plate_name = row[0]
        new_entry = LibraryPlate(id=plate_name,
                                 screen_stage=screen_stage,
                                 number_of_wells=number_of_wells)
        pk = new_entry.pk

        try:
            recorded_entry = recorded_plates.get(pk=pk)
            fields_to_compare = ('screen_stage', 'number_of_wells')
            differences = compare_fields(recorded_entry, new_entry,
                                         fields_to_compare,
                                         update=True)
            if differences:
                sys.stderr.write('WARNING: These updates to library plate ' +
                                 '{} occurred: {}\n'
                                 .format(plate_name,
                                         [d for d in differences]))
                return False
            else:
                return True

        except ObjectDoesNotExist:
            new_entry.save()
            sys.stderr.write('WARNING: Added new plate {} '
                             'to the database\n'
                             .format(plate_name))
            return False

    def sync_all_rows(legacy_table_name, screen_stage):
        cursor.execute('SELECT DISTINCT RNAiPlateID FROM ' + legacy_table_name)
        plates = cursor.fetchall()
        all_plates_present_and_match = True

        for row in plates:
            present_and_matches = sync_row(row, screen_stage)
            all_plates_present_and_match &= present_and_matches

        if all_plates_present_and_match:
            sys.stdout.write('LibraryPlate contained all plates from ' +
                             'table {} in the legacy database\n'
                             .format(legacy_table_name))
        else:
            sys.stdout.write('Some library plates added or updated from {}. '
                             '(Printed changes to sys.stderr.)\n'
                             .format(legacy_table_name))

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
            sync_row(['{}-{}'.format(chromosome, str(i))], 0, 384)

    sync_row(['Eliana_ReArray_1'], 1)
    sync_row(['Eliana_ReArray_2'], 1)
    sync_all_rows('RNAiPlate', 1)
    sync_all_rows('CherryPickRNAiPlate', 2)


def sync_Experiment_table(cursor):
    """
    Sync the Experiment table.

    Specifically, makes sure all experiments in RawData are included
    and synced in the new database.
    """
    def get_worm_strain(mutant, mutantAllele):
        try:
            if mutant == 'N2':
                gene = None
                allele = None
                worm_strain = worm_strains.get(id='N2')
            else:
                gene = mutant
                allele = mutantAllele
                if allele == 'zc310':
                    allele = 'zu310'
                worm_strain = worm_strains.get(gene=gene, allele=allele)
            return worm_strain

        except WormStrain.DoesNotExist:
            sys.exit('Strain with mutant: ' + mutant +
                     ', mutantAllele: ' + mutantAllele +
                     ' in the legacy database does not match any '
                     'worm strain in the new database\n')

    def get_library_plate(library_plate_as_string):
        try:
            return library_plates.get(id=library_plate_as_string)

        except LibraryPlate.DoesNotExist:
            sys.exit('RNAiPlateID ' + library_plate_as_string +
                     ' in the legacy database does not match any library '
                     'plate in the new database')

    def sync_row(row):
        id = row[0]
        worm_strain = get_worm_strain(row[1], row[2])
        library_plate = get_library_plate(row[3])
        temperature = row[4]
        date = row[5]
        is_junk = row[6]
        comment = row[7]

        new_experiment = Experiment(
            id=id,
            worm_strain=worm_strain,
            library_plate=library_plate,
            temperature=temperature,
            date=date,
            is_junk=is_junk,
            comment=comment
        )

        try:
            recorded_experiment = recorded_experiments.get(id=id)
            fields_to_compare = ('worm_strain', 'library_plate',
                                 'temperature', 'date', 'is_junk', 'comment')
            differences = compare_fields(recorded_experiment, new_experiment,
                                         fields_to_compare, update=True)
            if differences:
                sys.stdout.write('Updates to library plate {}: {}\n'
                                 .format(id, [d for d in differences]))
                return False
            else:
                return True

        except Experiment.DoesNotExist:
            new_experiment.save()
            sys.stdout.write('Added new experiment {} to the database\n'
                             .format(new_experiment))
            return False

    def sync_all_rows():
        all_experiments_present_and_match = True
        cursor.execute('SELECT '
                       'expID, mutant, mutantAllele, RNAiPlateID, '
                       'CAST(SUBSTRING_INDEX(temperature, "C", 1) '
                       'AS DECIMAL(3,1)), '
                       'CAST(recordDate AS DATE), '
                       'ABS(isJunk), '
                       'comment FROM RawData '
                       'WHERE (expID < 40000 OR expID>=50000) '
                       'AND RNAiPlateID NOT LIKE "Julie%"')
        experiments = cursor.fetchall()
        for row in experiments:
            present_and_matches = sync_row(row)
            all_experiments_present_and_match &= present_and_matches

        if all_experiments_present_and_match:
            sys.stdout.write('Experiment contained all experiments from '
                             'legacy database\n')
        else:
            sys.stdout.write('Some experiments added or updated.\n')

    worm_strains = WormStrain.objects.all()
    library_plates = LibraryPlate.objects.all()
    recorded_experiments = Experiment.objects.all()
    sync_all_rows()
