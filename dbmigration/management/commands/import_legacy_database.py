import MySQLdb

from django.core.management.base import BaseCommand, CommandError

from dbmigration.helpers.sync_steps_library import (
    update_Clone_table, update_LibraryPlate_table, update_LibraryStock_table)

from dbmigration.helpers.sync_steps_experiments import (
    update_Experiment_tables, update_DevstarScore_table,
    update_ManualScoreCode_table, update_ManualScore_table_primary,
    update_ManualScore_table_secondary)

from eegi.local_settings import LEGACY_DATABASE, LEGACY_DATABASE_2
from utils.scripting import require_db_write_acknowledgement

STEPS = (
    update_Clone_table,
    update_LibraryPlate_table,
    update_LibraryStock_table,
    update_Experiment_tables,
    update_DevstarScore_table,
    update_ManualScoreCode_table,
    update_ManualScore_table_primary,
    update_ManualScore_table_secondary,
)

LAST_STEP = len(STEPS) - 1

ARG_HELP = '''
    Step to {} with, inclusive. If not provided, defaults to {}.
    The steps are (dependencies in parentheses):
        [0: Clone;
        1: LibraryPlate;
        2: LibraryStock (0,1);
        3: ExperimentWell&Experiment (WormStrain,1);
        4: DevstarScore (3);
        5: ManualScoreCode;
        6: ManualScore primary (3,5);
        7: ManualScore secondary (3,5);]
'''


class Command(BaseCommand):
    """Command to sync legacy databases to the new database.

    Summary:

        The synchronization is split into 8 steps. For each step,
        records are queried from the old database for a particular
        table. For each record, various conversions and validations
        are performed to make a Python object(s) that is compatible
        with the new database. This Python object(s) is inserted
        into the new database if not present, or used to update an
        existing record if changes have occurred.


    The steps are (dependencies in parentheses):

        0: Clone;
        1: LibraryPlate;
        2: LibraryStock (0,1);
        3: ExperimentPlate&Experiment (WormStrain,1);
        4: DevstarScore (3);
        5: ManualScoreCode;
        6: ManualScore primary (3,5);
        7: ManualScore secondary (3,5);

    Requirements:

        Step 3 requires that WormStrain table be populated
        (this table is small enough that I populated it by hand,
        referencing the Google Doc about the worms used in the screen).

        Steps 0-6 require that LEGACY_DATABASE be defined in local_settings.py,
        to connect to the GenomeWideGI legacy database.

        Step 7 requires that LEGACY_DATABASE_2 be defined in local_settings.py,
        to connect to the GWGI2 database.


    Output:

        Stdout reports whether or not a particular step had changes.

        Stderr reports every change (such as an added row), so can get
        quite long; consider redirecting with 2> stderr.out.

    """
    help = 'Sync the database according to any changes in the legacy database.'

    def add_arguments(self, parser):
        parser.add_argument('start', type=int, nargs='?', default=0,
                            help=(ARG_HELP.format('start', 0)))
        parser.add_argument('end', type=int, nargs='?', default=LAST_STEP,
                            help=(ARG_HELP.format('end', LAST_STEP)))

    def handle(self, **options):
        start = options['start']
        end = options['end']

        if start > end:
            raise CommandError('Start cannot be greater than end')

        if (start < 0) or (end > len(STEPS) - 1):
            raise CommandError('Start and end must be in range 0-{}'
                               .format(LAST_STEP))

        if end == LAST_STEP:
            do_last_step = True
            end = LAST_STEP - 1

        else:
            do_last_step = False

        require_db_write_acknowledgement()

        # Do the steps that involve connecting to Huey-Ling's legacy_db
        legacy_db = MySQLdb.connect(host=LEGACY_DATABASE['HOST'],
                                    user=LEGACY_DATABASE['USER'],
                                    passwd=LEGACY_DATABASE['PASSWORD'],
                                    db=LEGACY_DATABASE['NAME'])

        cursor = legacy_db.cursor()

        for step in range(start, end + 1):
            STEPS[step](self, cursor)

        # This step requires connecting to Kris's legacy_db_2
        if do_last_step:
            legacy_db_2 = MySQLdb.connect(host=LEGACY_DATABASE_2['HOST'],
                                          user=LEGACY_DATABASE_2['USER'],
                                          passwd=LEGACY_DATABASE_2['PASSWORD'],
                                          db=LEGACY_DATABASE_2['NAME'])
            cursor = legacy_db_2.cursor()
            STEPS[LAST_STEP](self, cursor)
