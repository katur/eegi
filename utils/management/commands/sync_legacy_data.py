import MySQLdb
import sys

from django.core.management.base import BaseCommand, CommandError

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
    ./manage.py sync_legacy_data
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
        sync_Experiment_table(cursor)


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
    def sync_screen_plates(cursor, screen_stage, screen_stage_string,
                           legacy_table):
        cursor.execute('SELECT DISTINCT RNAiPlateID FROM ' + legacy_table)
        plates = cursor.fetchall()
        recorded_plates = LibraryPlate.objects.filter(
            screen_stage=screen_stage)
        all_plates_present = True

        for row in plates:
            plate_name = row[0]
            new_plate = LibraryPlate(id=plate_name,
                                     screen_stage=screen_stage,
                                     number_of_wells=96)
            try:
                recorded_plate = recorded_plates.get(id=plate_name)
                fields_to_compare = ('screen_stage', 'number_of_wells')
                differences = compare_fields(recorded_plate, new_plate,
                                             fields_to_compare,
                                             update=False)
                if differences:
                    sys.stdout.write('Updates to library plate ' +
                                     '{}: {}\n'
                                     .format(plate_name,
                                             [d for d in differences]))
            except LibraryPlate.DoesNotExist:
                sys.stdout.write('Adding new plate {} '
                                 'to the database\n'
                                 .format(plate_name))
                new_plate.save()
                all_plates_present = False

        if all_plates_present:
            sys.stdout.write('LibraryPlate contained all {} plates from '
                             'legacy database\n'
                             .format(screen_stage_string))

    sync_screen_plates(cursor, 1, 'primary', 'RNAiPlate')
    sync_screen_plates(cursor, 2, 'secondary', 'CherryPickRNAiPlate')


def sync_Experiment_table(cursor):
    """
    Sync the Experiment table.

    Specifically, makes sure all experiments in RawData are included
    and synced in the new database.
    """
    worm_strains = WormStrain.objects.all()
    library_plates = LibraryPlate.objects.all()

    def get_worm_strain(mutant, mutantAllele):
        try:
            if mutant == 'N2':
                gene = None
                allele = None
                worm_strain = worm_strains.get(id='N2')
            else:
                gene = row[1]
                allele = row[2]
                if allele == 'zc310':
                    allele = 'zu310'
                worm_strain = worm_strains.get(gene=gene, allele=allele)
            return worm_strain

        except WormStrain.DoesNotExist:
            sys.stdout.write('Strain with mutant: ' + row[1] +
                             ', mutantAllele: ' + row[2] +
                             ' in the legacy database does not match any '
                             'worm strain in the new database\n')
            sys.exit(1)

    def get_library_plate(library_plate_as_string):
        try:
            return library_plates.get(id=row[3])

        except LibraryPlate.DoesNotExist:
            sys.stdout.write('RNAiPlateID ' + row[3] + ' in the legacy '
                             'database does not match any library plate '
                             'in the new database')
            sys.exit(1)

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
    recorded_experiments = Experiment.objects.all()
    all_experiments_present = True

    for row in experiments:
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
                                         fields_to_compare, update=False)
            if differences:
                sys.stdout.write('Updates to library plate {}: {}\n'
                                 .format(id, [d for d in differences]))

        except Experiment.DoesNotExist:
            sys.stdout.write('Adding new experiment {} to the database'
                             .format(new_experiment))
            new_experiment.save()
            all_experiments_present = False

    if all_experiments_present:
        sys.stdout.write('Experiment contained all experiments from '
                         'legacy database\n')
