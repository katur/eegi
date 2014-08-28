import MySQLdb
import sys

from django.core.management.base import BaseCommand, CommandError

from eegi.local_settings import LEGACY_DATABASE
from library.models import LibraryPlate


class Command(BaseCommand):
    """
    Script to update LibraryPlate table according to the legacy database.
    Specifically, makes sure all distinct RNAiPlateID from
    RNAiPlate and CherryPickRNAiPlate tables are included in the new database.

    Include connection info for legacy database in local_settings, in format:
    LEGACY_DATABASE = {
        'NAME': 'GenomeWideGI',
        'HOST': 'localhost',
        'USER': 'my_username',
        'PASSWORD': 'my_password',
    }

    To run program:
    ./manage.py migrate_LibraryPlate_data
    """
    help = ('Update rows in LibraryPlate table according to legacy database')

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

        update_plates(cursor, 1, 'primary', 'RNAiPlate')
        update_plates(cursor, 2, 'secondary', 'CherryPickRNAiPlate')


def update_plates(cursor, screen_stage, screen_stage_as_string, legacy_table):
    cursor.execute('SELECT DISTINCT RNAiPlateID FROM ' + legacy_table)
    plates = cursor.fetchall()
    recorded_plates = LibraryPlate.objects.filter(screen_stage=screen_stage)
    all_match = True

    for row in plates:
        plate_name = row[0]
        plate = LibraryPlate(id=plate_name, screen_stage=screen_stage,
                             number_of_wells=96)

        if plate in recorded_plates:
            # __eq__ in Django tests for primary key only, not other fields
            matches = check_other_fields(plate)
            if not matches:
                all_match = False
        else:
            sys.stdout.write('Adding new plate {} '
                             'to the database\n'
                             .format(plate_name))
            plate.save()
            all_match = False

    alert_if_all_match(all_match, screen_stage_as_string)


def check_other_fields(plate):
    recorded_plate = LibraryPlate.objects.get(id=plate.id)
    matches = True
    if recorded_plate.screen_stage != plate.screen_stage:
        sys.stdout.write('Warning: screen stage mismatch on plate {}\n'
                         .format(plate.id))
        matches = False

    if recorded_plate.number_of_wells != 96:
        sys.stdout.write('Warning: number of wells not 96 on plate {}\n'
                         .format(plate.id))
        matches = False

    return matches


def alert_if_all_match(all_match, stage):
    if all_match:
        sys.stdout.write('All {} plates present and match\n'.format(stage))
