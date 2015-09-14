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
        parser.add_argument('file', type=argparse.FileType('r'))

    def handle(self, **options):
        f = options['file']

        legacy_fields = ['mutant', 'mutantAllele',
                         'RNAiPlateID', '96well', 'ImgName',
                         'clone', 'node_primary_name', 'seq_node_primary_name']

        for line in f:
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

            clone = source_library_well.intended_clone.id

            if clone[0:3] == 'GHR':
                clone = source_library_well.intended_clone.legacy_id

            output = [
                worm.gene, worm.allele,
                destination_plate_name, destination_well, destination_tile,
                clone, None, 'X'
            ]

            self.stdout.write(','.join([str(x) for x in output]))
