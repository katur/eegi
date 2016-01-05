import json
import gspread
from oauth2client.client import SignedJwtAssertionCredentials

from django.core.management.base import BaseCommand, CommandError

from dbmigration.helpers.name_getters import get_library_plate_name
from eegi.settings import GOOGLE_API_KEY
from experiments.models import ExperimentPlate
from library.models import LibraryPlate
from utils.scripting import require_db_write_acknowledgement
from worms.models import WormStrain


class Command(BaseCommand):
    help = 'Import batch experiments recorded in Google Doc'

    def handle(self, **options):
        require_db_write_acknowledgement()

        json_key = json.load(open(GOOGLE_API_KEY))
        scope = ['https://spreadsheets.google.com/feeds']

        credentials = SignedJwtAssertionCredentials(
                json_key['client_email'], json_key['private_key'].encode(),
                scope)

        gc = gspread.authorize(credentials)
        sheet = gc.open('eegi_batch_experiment_entry').sheet1
        values = sheet.get_all_values()

        # Get sheet-wide values
        date = values[0][1]
        screen_stage = values[1][1]

        # Get worm strains from genes and alleles
        genes = values[3][1:]
        alleles = values[4][1:]
        worms = []

        for gene, allele in zip(genes, alleles):
            if allele == 'zc310':
                allele = 'zu310'

            try:
                worm = WormStrain.objects.get(gene=gene, allele=allele)
            except WormStrain.DoesNotExist:
                raise CommandError('Worm strain does not exist with gene {} '
                                   'and allele {}'
                                   .format(gene, allele))

            worms.append(worm)

        # Get temperatures
        temperatures = values[5][1:]
        screen_types = values[6][1:]

        for i, tup in enumerate(zip(temperatures, screen_types, worms)):
            temperature, screen_type, worm = tup

            if temperature.endswith('C'):
                temperature = temperature[:-1]

            if temperature:
                temperature = float(temperature)
            else:
                temperature = None

            temperatures[i] = temperature

            # Sanity check that screen_type is correct
            if (
                    (screen_type == 'SUP' and
                    temperature != worm.restrictive_temperature) or
                    (screen_type == 'ENH' and
                    temperature != worm.permissive_temperature)):
                raise CommandError('Screen {} and temperature {} do not agree '
                                   'for worm strain {}'
                                   .format(screen_type, temperature, worm))

        for row in values[7:]:
            library_plate = get_library_plate_name(row[0])
            if not LibraryPlate.objects.filter(id=library_plate):
                raise CommandError('Library Plate {} does not exist'
                                   .format(library_plate))

            for i, experiment in enumerate(row[1:]):
                if not experiment:
                    continue

                if ExperimentPlate.objects.filter(id=experiment).count():
                    raise CommandError('Experiment Plate {} already '
                                       'exists'.format(experiment))

                print 'experiment {} is {}, {}, {}'.format(
                    experiment, library_plate, worms[i], temperatures[i])
