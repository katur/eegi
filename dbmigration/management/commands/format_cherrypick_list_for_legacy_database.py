import argparse
import MySQLdb

from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand, CommandError

from eegi.local_settings import LEGACY_DATABASE
from library.models import LibraryPlate, LibraryStock
from utils.well_tile_conversion import well_to_tile
from worms.models import WormStrain


class Command(BaseCommand):
    """
    Command to format a cherrypick list to import into legacy database.

    Import into GenomeWideGI.CherryPickRNAiPlate.

    This script requires that LEGACY_DATABASE be defined in
    local_settings.py.

    Output
        Prints to stdout

    Arguments
        - cherrypick_list should be a comma-separated file, including
          header row, where each row is in format:

            source_plate,source_well,destination_plate,destination_well
    """

    help = 'Format a cherrypick list for legacy database.'

    def add_arguments(self, parser):
        parser.add_argument('cherrypick_list', type=argparse.FileType('r'),
                            help="CSV file of cherry-pick list. "
                                 "See this command's docstring "
                                 "for more details.")

    def handle(self, **options):
        ######################################################
        # FIRST STAGE
        #
        #   Connect to legacy database and create a dictionary to
        #   translate from new canonical clones names to legacy
        #   clone information.
        #
        ######################################################
        legacy_db = MySQLdb.connect(host=LEGACY_DATABASE['HOST'],
                                    user=LEGACY_DATABASE['USER'],
                                    passwd=LEGACY_DATABASE['PASSWORD'],
                                    db=LEGACY_DATABASE['NAME'])
        cursor = legacy_db.cursor()

        cursor.execute('SELECT clone, node_primary_name, 384PlateID, '
                       '384Well FROM RNAiPlate '
                       'WHERE RNAiPlateID != "L4440"')

        new_to_old = {}

        for row in cursor.fetchall():
            old_clone_name = row[0].strip()
            node_primary_name = row[1]
            if isinstance(node_primary_name, str):
                node_primary_name = node_primary_name.strip()
            plate_384 = row[2].strip()
            well_384 = row[3].strip()

            if plate_384[0:3] == 'GHR':
                new_clone_name = plate_384 + '@' + well_384
            else:
                new_clone_name = old_clone_name

            new_to_old[new_clone_name] = {
                'old_clone_name': old_clone_name,
                'node_primary_name': node_primary_name,
            }

        ######################################################
        # SECOND STAGE
        #
        #   For each row in cherrypick_list, create a corresponding
        #   row for the legacy database, with fields:
        #   ('mutant', 'mutantAllele', 'RNAiPlateID', '96well',
        #    'ImgName', 'clone', 'node_primary_name',
        #    'seq_node_primary_name')
        #
        ######################################################
        cherrypick_list = options['cherrypick_list']

        # Skip header row
        next(cherrypick_list)

        '''
        # Uncomment this to add header row with fieldnames
        legacy_fields = ('mutant', 'mutantAllele', 'RNAiPlateID',
                         '96well', 'ImgName', 'clone',
                         'node_primary_name', 'seq_node_primary_name')

        self.stdout.write(','.join(legacy_fields))
        '''

        for line in cherrypick_list:
            row = line.split(',')
            source_plate_name = row[0].strip()

            # Since legacy database did not represent empty wells
            if not source_plate_name or source_plate_name == "None":
                continue

            source_well = row[1].strip()
            destination_plate_name = row[2].strip()
            destination_well = row[3].strip()
            destination_tile = well_to_tile(destination_well) + '.bmp'

            try:
                source_plate = LibraryPlate.objects.get(
                    id=source_plate_name)
                source_stock = LibraryStock.objects.get(
                    plate=source_plate, well=source_well)

            except ObjectDoesNotExist:
                raise CommandError('{} at {} not found'
                                   .format(source_plate_name, source_well))

            allele = destination_plate_name.split('-')[0]

            if allele == 'universal':
                # For universal plates, allele == gene == 'universal'
                gene = 'universal'

            else:
                # Otherwise, gene can be retrieved from WormStrain
                gene = WormStrain.objects.get(allele=allele).gene

            # Account for legacy database using mispelled allele 'zc310'
            if allele == 'zu310':
                allele = 'zc310'
                destination_plate_chars = list(destination_plate_name)
                destination_plate_chars[1] = 'c'
                destination_plate_name = ''.join(destination_plate_chars)

            if source_stock.intended_clone:
                new_clone_name = source_stock.intended_clone.id
                old_clone_name = new_to_old[new_clone_name]['old_clone_name']
                node_primary_name = (
                    new_to_old[new_clone_name]['node_primary_name'])
                if node_primary_name == 'NULL':
                    node_primary_name = ''

            else:
                old_clone_name = ''
                node_primary_name = ''

            output = [
                gene, allele,
                destination_plate_name, destination_well, destination_tile,
                old_clone_name, node_primary_name, 'X'
            ]

            self.stdout.write(','.join([str(x) for x in output]))
