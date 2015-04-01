import MySQLdb

from django.core.management.base import BaseCommand, CommandError

from dbmigration.helpers.sync_legacy_database_steps import (
    update_LibraryPlate_table, update_Experiment_table,
    update_ManualScoreCode_table, update_ManualScore_table,
    update_DevstarScore_table, update_Clone_table,
    update_LibraryWell_table, update_ManualScore_table_secondary)
from eegi.local_settings import LEGACY_DATABASE, LEGACY_DATABASE_2
from utils.helpers.scripting import require_db_write_acknowledgement

HELP = '''
Sync the database according to any changes in the legacy database.

Optionally provide start and end args to limit which tables are synced.
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


Requirements:
    Several steps require that the WormStrain table is already populated
    (this table is small enough that I populated it by hand, referencing
    written records about the worm strains used in the screen).

    Steps 0-6 require that LEGACY_DATABASE be defined in local_settings.py,
    to connect to the GenomeWideGI legacy database.

    Step 7 requires that LEGACY_DATABASE_2 be defined in local_settings.py,
    to connect to the GWGI2 database.


Output:
    Stdout reports whether or not a particular large step had changes.

    Stderr reports every change (such as an added row), and thus can get
        quite long; consider redirecting with 2> stderr.out.
'''


class Command(BaseCommand):
    args = '[start end]'
    help = HELP

    def handle(self, *args, **options):
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
            if len(args) != 2:
                raise CommandError('Command requires 0 or 2 arguments')
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

        require_db_write_acknowledgement()

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
