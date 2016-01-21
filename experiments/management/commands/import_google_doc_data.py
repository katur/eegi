import datetime
import re

from django.core.management.base import BaseCommand, CommandError

from eegi.settings import BATCH_DATA_ENTRY_GDOC_NAME
from experiments.models import ExperimentPlate
from library.helpers.naming import generate_library_plate_name
from library.models import LibraryPlate
from utils.google import connect_to_google_spreadsheets
from utils.scripting import require_db_write_acknowledgement
from worms.models import WormStrain


class Command(BaseCommand):
    help = 'Import batch experiments recorded in Google Doc'

    def handle(self, **options):
        try:
            count = _parse_batch_data_entry_gdoc(dry_run=True)
        except Exception as e:
            raise CommandError(e)

        self.stdout.write('Dry run complete. '
                          '{} experiment plates found in sheet.'
                          .format(count))

        require_db_write_acknowledgement('Proceed to actual run? '
                                         '(yes/no) ')

        try:
            count = _parse_batch_data_entry_gdoc()
        except Exception as e:
            raise CommandError(e)

        self.stdout.write('Actual run complete. '
                          '{} experiment plates added to database.'
                          .format(count))


def _parse_batch_data_entry_gdoc(dry_run=False):
    """
    Parse the Google Doc for batch data entry.

    Returns the number of experiments plates parsed from the sheet.

    By default, the parsed experiments are saved to the database.
    Set dry_run=True to instead do a dry run.
    """
    gc = connect_to_google_spreadsheets()
    sheet = gc.open(BATCH_DATA_ENTRY_GDOC_NAME).sheet1
    values = sheet.get_all_values()

    date, screen_stage = _parse_gdoc_global_info(values)
    worms, temperatures, screen_types = _parse_gdoc_column_headers(values)
    count = _parse_gdoc_experiment_rows(values[7:], screen_stage, date,
                                        worms, temperatures,
                                        dry_run=dry_run)
    return count


def _parse_gdoc_global_info(values):
    date = values[0][1]

    if re.match('^\d\d\d\d\d\d\d\d$', date):
        date = datetime.datetime.strptime(date, '%Y%m%d').date()
    elif re.match('^\d\d\d\d-\d\d-\d\d$', date):
        date = datetime.datetime.strptime(date, '%Y-%m-%d').date()
    else:
        raise ValueError('Date must be in format YYYYMMDD or YYYY-MM-DD')

    screen_stage = values[1][1]
    return (date, screen_stage)


def _parse_gdoc_column_headers(values):
    genes = values[3][1:]
    alleles = values[4][1:]
    worms = []

    for gene, allele in zip(genes, alleles):
        if allele == 'zc310':
            allele = 'zu310'

        try:
            worms.append(WormStrain.objects.get(gene=gene, allele=allele))
        except WormStrain.DoesNotExist:
            raise ValueError('Worm strain does not exist with gene {} '
                             'and allele {}'.format(gene, allele))

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
            raise ValueError('Screen {} and temperature {} do not agree '
                               'for worm strain {}'
                               .format(screen_type, temperature, worm))

    return (worms, temperatures, screen_types)


def _parse_gdoc_experiment_rows(rows, screen_stage, date, worms,
                                temperatures, dry_run=False):
    """Parse the rows with new experiments."""
    plate_count = 0

    for row in rows:
        library_plate_name = generate_library_plate_name(row[0])

        try:
            library_plate = LibraryPlate.objects.get(id=library_plate_name)
        except ObjectDoesNotExist:
            raise ValueError('Library Plate {} does not exist'
                             .format(library_plate))

        for i, experiment_plate_id in enumerate(row[1:]):
            if not experiment_plate_id:
                continue

            ExperimentPlate.create_plate_and_wells(
                experiment_plate_id, screen_stage, date,
                temperatures[i], worms[i], library_plate,
                dry_run=dry_run)

            plate_count += 1

    return plate_count
