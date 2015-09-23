import argparse
import csv
import os
import requests
import shutil

from django.core.management.base import BaseCommand, CommandError

from utils.well_tile_conversion import well_to_tile
from eegi.settings import IMG_PATH


HELP = '''
Copy a set of images from the server to a local directory.

Input is a csv, including header row, in which each row
is in format: experiment_id, well. For example:

    54034,A05
    12412,B12
    32412,H02
'''


class Command(BaseCommand):
    help = HELP

    def add_arguments(self, parser):
        parser.add_argument('input_file', type=argparse.FileType('r'))
        parser.add_argument('output_dir')

    def handle(self, *args, **options):
        input_file = options['input_file']
        output_dir = options['output_dir']

        # Create output directory, exiting if already exists
        if os.path.exists(output_dir):
            raise CommandError('Output directory {} already exists'
                               .format(output_dir))
        else:
            os.makedirs(output_dir)

        # Parse input
        reader = csv.reader(input_file, delimiter=',')

        # Skip header
        next(reader)

        for experiment_id, well in reader:
            tile = well_to_tile(well)
            input_image_url = '{}/{}/{}'.format(IMG_PATH, experiment_id, tile)
            output_image_path = '{}/{}_{}'.format(output_dir, experiment_id,
                                                  tile)
            r = requests.get(input_image_url, stream=True)
            if r.status_code != 200:
                raise CommandError('non-ok GET status for {}'
                                   .format(input_image_url))

            with open(output_image_path, 'wb') as f:
                r.raw.decode_content = True
                shutil.copyfileobj(r.raw, f)

            print '{} written'.format(output_image_path)
