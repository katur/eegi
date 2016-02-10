import argparse
import csv
import os
import re
import requests
import shutil

from django.core.management.base import BaseCommand, CommandError

from utils.well_tile_conversion import well_to_tile
from eegi.settings import BASE_URL_IMG


class Command(BaseCommand):
    """
    Command to copy a set of images from the server to a local directory.

    Currently works only for the full-size, original .bmp images.

    Input is a csv in which each row is in format `experiment_id,well`
    or `experiment_id,tile`. For example, all these rows are okay:

        54034,A05
        12412,B12
        32412,H02
        22314,Tile000036
        25123,Tile000096.bmp

    Copied images will be prefixed with experiment_id,
    e.g. 54034_Tile000005.bmp.

    If the first element cannot be converted to an int, or if the second
    cannot be converted to a well, the row is skipped. So having a
    header row is okay.
    """

    help = 'Copy a set of images to a local directory.'

    def add_arguments(self, parser):
        parser.add_argument('input_file', type=argparse.FileType('r'),
                            help="CSV of experiment, wells to copy. "
                                 "See this command's docstring "
                                 "for more details.")

        parser.add_argument('output_dir',
                            help='Directory in which to write the images.')

    def handle(self, **options):
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

        for experiment_id, well in reader:
            try:
                experiment_id = int(experiment_id.strip())
            except ValueError:
                continue

            well = well.strip()

            if re.match('Tile0000\d\d\.bmp', well):
                tile = well.split('.bmp')[0]
            elif re.match('Tile0000\d\d', well):
                tile = well
            else:
                try:
                    tile = well_to_tile(well)
                except ValueError:
                    continue

            input_image_url = '{}/{}/{}.bmp'.format(
                BASE_URL_IMG, experiment_id, tile)
            output_image_path = '{}/{}_{}.bmp'.format(
                output_dir, experiment_id, tile)
            r = requests.get(input_image_url, stream=True)
            if r.status_code != 200:
                raise CommandError('non-ok GET status for {}'
                                   .format(input_image_url))

            with open(output_image_path, 'wb') as f:
                r.raw.decode_content = True
                shutil.copyfileobj(r.raw, f)

            self.stdout.write('{} written'.format(output_image_path))
