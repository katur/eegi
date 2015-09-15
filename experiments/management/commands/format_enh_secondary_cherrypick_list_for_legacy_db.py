import argparse

from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand, CommandError
from library.models import LibraryPlate, LibraryWell
from worms.models import WormStrain
from utils.well_tile_conversion import well_to_tile


HELP = '''
Format the Enhancer Secondary screen cherry-picking list such that it
is can be imported into the legacy database GenomeWideGI
(into table CherryPickRNAiPlate).

'''


class Command(BaseCommand):
    help = HELP

    def add_arguments(self, parser):
        parser.add_argument('cherrypick_list', type=argparse.FileType('r'))
        parser.add_argument('legacy_clones', type=argparse.FileType('r'))

    def handle(self, **options):

        # Create a dictionary to translate from new canonical clones names
        # to the various fields which need to be entered into the legacy
        # database

        new_to_old = {}

        # Iterate over the dump of legacy clone information to populate
        # the dictionary. This dump can be gotten with the query:
        # SELECT clone, node_primary_name, 384PlateID, 384Well
        # FROM RNAiPlate WHERE RNAiPlateID != "L4440"

        for line in options['legacy_clones']:
            row = line.split(',')
            old_clone_name = row[0].strip()
            node_primary_name = row[1].strip()
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

        cherrypick_list = options['cherrypick_list']

        # skip header row
        next(cherrypick_list)

        # Iterate over the cherry pick list, translating each row
        # to the correct format for importing into the CherryPickRNAi
        # table in the legacy database. The fields in CherryPickRNAi
        # are: ('mutant', 'mutantAllele', 'RNAiPlateID', '96well', 'ImgName',
        # 'clone', 'node_primary_name', 'seq_node_primary_name']
        legacy_fields = ('mutant', 'mutantAllele', 'RNAiPlateID', '96well',
                         'ImgName', 'clone', 'node_primary_name',
                         'seq_node_primary_name')
        self.stdout.write(','.join(legacy_fields))

        for line in cherrypick_list:
            row = line.split(',')
            source_plate_name = row[0].strip()

            # Skip "None", since legacy database did not represent
            # empty wells
            if not source_plate_name or source_plate_name == "None":
                continue

            source_well = row[1].strip()
            destination_plate_name = row[2].strip()
            destination_well = row[3].strip()
            destination_tile = well_to_tile(destination_well)

            try:
                source_plate = LibraryPlate.objects.get(id=source_plate_name)
                source_library_well = LibraryWell.objects.get(
                    plate=source_plate, well=source_well)
            except ObjectDoesNotExist:
                raise CommandError('{} at {} not found'
                                   .format(source_plate, source_well))

            allele = destination_plate_name.split('_')[0]

            if allele == 'universal':
                # For universal plates, allele == gene == 'universal'
                gene = 'universal'

            else:
                # Otherwise, gene can be retrieved from WormStrain
                gene = WormStrain.objects.get(allele=allele).gene

            # Account for legacy database using mispelled allele 'zc310'
            if allele == 'zu310':
                allele_chars = list(allele)
                allele_chars[1] = 'c'
                allele = ''.join(allele_chars)

                destination_plate_chars = list(destination_plate_name)
                destination_plate_chars[1] = 'c'
                destination_plate_name = ''.join(destination_plate_chars)

            new_clone_name = source_library_well.intended_clone.id
            old_clone_name = new_to_old[new_clone_name]['old_clone_name']
            node_primary_name = new_to_old[new_clone_name]['node_primary_name']

            output = [
                gene, allele,
                destination_plate_name, destination_well, destination_tile,
                old_clone_name, node_primary_name, 'X'
            ]

            self.stdout.write(','.join([str(x) for x in output]))
