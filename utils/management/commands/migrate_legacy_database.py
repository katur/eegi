import MySQLdb
import sys

from django.core.management.base import BaseCommand, CommandError

from eegi.local_settings import LEGACY_DATABASE, LEGACY_DATABASE_2

from migrate_legacy_database_steps import (update_LibraryPlate_table,
                                           update_Experiment_table,
                                           update_ManualScoreCode_table,
                                           update_ManualScore_table,
                                           update_DevstarScore_table,
                                           update_Clone_table,
                                           update_LibraryWell_table,
                                           update_ManualScore_table_secondary)


USAGE_MESSAGE = '''
USAGE:
\t./manage.py migrate_legacy_database [start end]

start is inclusive, end is exclusive, and the values for start and end
reference the steps below (dependencies in parentheses):
0: LibraryPlate
1: Experiment (WormStrain, 0)
2: ManualScoreCode
3: ManualScore_primary (1, 2)
4: DevstarScore (1)
5: Clone (named RNAiClone in database)
6: LibraryWell (0, 5)
7: ManualScore_secondary (1, 2)
'''


class Command(BaseCommand):
    """
    Command to update the new database according to the legacy database.

    REQUIREMENTS
    Some steps require that the WormStrain table is already populated
    (small enough that I populated it by hand).

    Steps 0-6 requires connection info for legacy database GenomeWideGI
    in local_settings.LEGACY_DATABASE, format:
    LEGACY_DATABASE = {
        'NAME': 'GenomeWideGI',
        'HOST': 'localhost',
        'USER': 'my_username',
        'PASSWORD': 'my_password',
    }

    Step 7 requires connection info for legacy database GWGI2
    in local_settings.LEGACY_DATABASE_2, same format as above.


    USAGE
    To update all tables, execute (from the project root):
    ./manage.py migrate_legacy_database

    To update a range of tables, execute (from the project root):
    ./manage.py migrate_legacy_database start end

    start is inclusive, end is exclusive, and the values for start and end
    reference the steps below (dependencies in parentheses):
    0: LibraryPlate
    1: Experiment (WormStrain, 0)
    2: ManualScoreCode
    3: ManualScore_primary (1, 2)
    4: DevstarScore (1)
    5: Clone (named RNAiClone in database)
    6: LibraryWell (0, 5)
    7: ManualScore_secondary (1, 2)


    OUTPUT
    Stdout reports whether or not a particular large step had changes.

    Stderr reports every change (such as an added row), and thus can get
        quite long; consider redirecting with 2> stderr.out.
    """
    help = ('Update the new database according to the legacy database.')

    def handle(self, *args, **options):
        if len(args) != 0 and len(args) != 2:
            sys.exit(USAGE_MESSAGE)

        steps = (
            update_LibraryPlate_table,
            update_Experiment_table,
            update_ManualScoreCode_table,
            update_ManualScore_table,
            update_DevstarScore_table,
            update_Clone_table,
            update_LibraryWell_table,
            update_ManualScore_table_secondary,
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

        if end == 8:
            step_seven = True
            end = 7
        else:
            step_seven = False

        for step in range(start, end):
            steps[step](cursor)

        if step_seven:
            legacy_db_2 = MySQLdb.connect(host=LEGACY_DATABASE_2['HOST'],
                                          user=LEGACY_DATABASE_2['USER'],
                                          passwd=LEGACY_DATABASE_2['PASSWORD'],
                                          db=LEGACY_DATABASE_2['NAME'])
            cursor = legacy_db_2.cursor()
            steps[7](cursor)
