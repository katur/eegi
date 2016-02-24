import argparse
import csv
import MySQLdb
import os.path

from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand, CommandError

from dbmigration.helpers.object_getters import get_library_stock
from library.management.commands.import_sequencing_data import (
    process_tracking_number)
from eegi.localsettings import LEGACY_DATABASE
from utils.scripting import require_db_write_acknowledgement


class Command(BaseCommand):
    """
    Command to import sequencing results that were partially
    represented in the legacy database.

    This script requires that LEGACY_DATABASE be defined in localsettings,
    since it uses the legacy database to determine which library stocks
    correspond to which sequencing wells for our old sequencing data.

    Arguments

    - tracking_numbers is a csv containing the genewiz orders to be
      added. Only two columns are relevant for this script (since
      translating between sequencing ids and library stocks can
      be done through the legacy database): `order_date` and
      `tracking_number`. This file currently lives at:

          materials/sequencing/genewiz_dump/tracking_numbers_2012.csv

    - genewiz_output_root is the root directory where Genewiz dumps our
      sequencing data. See the `import_sequencing_data` script
      for more details. This directory currently lives at:

          materials/sequencing/genewiz_dump/genewiz_data
    """

    help = 'Import legacy sequencing data (from 2012)'

    def add_arguments(self, parser):
        parser.add_argument('tracking_numbers',
                            type=argparse.FileType('r'),
                            help="CSV of Genewiz tracking numbers. "
                                 "See this command's docstring "
                                 "for more details.")

        parser.add_argument('genewiz_output_root',
                            help="Root Genewiz output directory. "
                                 "See this command's docstring "
                                 "for more details.")

    def handle(self, **options):
        require_db_write_acknowledgement()

        tracking_numbers = options['tracking_numbers']
        genewiz_root = options['genewiz_output_root']

        if not os.path.isdir(genewiz_root):
            raise CommandError('genewiz_root directory not found')

        legacy_db = MySQLdb.connect(host=LEGACY_DATABASE['HOST'],
                                    user=LEGACY_DATABASE['USER'],
                                    passwd=LEGACY_DATABASE['PASSWORD'],
                                    db=LEGACY_DATABASE['NAME'])

        cursor = legacy_db.cursor()

        ####################################################
        # FIRST STAGE: Create a dictionary of which
        #   sequences correspond to which library stocks
        #
        # This information is stored in the legacy database.
        ####################################################
        seq_to_source = {}

        cursor.execute(
            'SELECT SeqPlateID, Seq96Well, RNAiPlateID, 96well, oriClone '
            'FROM SeqPlate WHERE SeqPlateID <= 55')

        for row in cursor.fetchall():
            seq_plate_number, seq_well = row[0:2]
            seq_plate = 'JL' + str(seq_plate_number)

            try:
                library_stock = get_library_stock(row[2], row[3])

            except ObjectDoesNotExist:
                raise CommandError('LibraryStock not found for {} {}\n'
                                   .format(row[0], row[1]))

            # Sanity check that clone matches
            legacy_clone = row[4]
            if legacy_clone:
                clone = library_stock.intended_clone
                if (not clone or (legacy_clone != clone.id and
                                  'GHR' not in clone.id)):
                    self.stderr.write(
                        'WARNING: Legacy clone mismatch for {}: {} {}\n'
                        .format(library_stock, clone, legacy_clone))

            seq_to_source[seq_plate + '_' + seq_well] = library_stock

        ####################################
        # SECOND STAGE: Add raw genewiz data
        #   (sequences and quality scores)
        ####################################

        reader = csv.DictReader(tracking_numbers)

        for row in reader:
            tracking_number = row['tracking_number'].strip()
            order_date = row['order_date'].strip()
            process_tracking_number(tracking_number, order_date,
                                    genewiz_root, seq_to_source)
