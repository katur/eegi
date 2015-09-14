import argparse

from django.core.management.base import BaseCommand
from library.models import LibraryPlate, LibraryWell
from worms.models import WormStrain
from utils.well_to_tile import well_to_tile


HELP = '''
Format the Enhancer Secondary screen cherry-picking list such that it
is can be imported into the legacy database GenomeWideGI
(into table CherryPickRNAiPlate)

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

        # Iterate over the dump of the legacy clone information to populate
        # the dictionary
        for line in options['legacy_clones']:
            row = line.split(',')
            old_clone_name = row[0]
            node_primary_name = row[1]
            plate_384 = row[2]
            well_384 = row[3]

            if plate_384[0:3] == 'GHR':
                new_clone_name = plate_384 + '@' + well_384
            else:
                new_clone_name = old_clone_name

            new_to_old[new_clone_name] = {
                'old_clone_name': old_clone_name,
                'node_primary_name': node_primary_name,
            }

        # Iterate over the cherry pick list, translating each row
        # to the correct format for importing into the CherryPickRNAi
        # table in the legacy database. The fields in CherryPickRNAi
        # are: ('mutant', 'mutantAllele', 'RNAiPlateID', '96well', 'ImgName',
        # 'clone', 'node_primary_name', 'seq_node_primary_name']
        for line in options['cherrypick_list']:
            row = line.split(',')
            source_plate_name = row[0]
            source_well = row[1]
            destination_plate_name = row[2]
            destination_well = row[3]
            destination_tile = well_to_tile(destination_well)

            source_plate = LibraryPlate.objects.get(id=source_plate_name)
            source_library_well = LibraryWell.objects.get(
                plate=source_plate, well=source_well)

            allele = destination_plate_name.split('_')[0]
            worm = WormStrain.objects.get(allele=allele)

            new_clone_name = source_library_well.intended_clone.id
            old_clone_name = new_to_old[new_clone_name]['old_clone_name']
            node_primary_name = new_to_old[new_clone_name]

            output = [
                worm.gene, worm.allele,
                destination_plate_name, destination_well, destination_tile,
                old_clone_name, node_primary_name, 'X'
            ]

            self.stdout.write(','.join([str(x) for x in output]))
