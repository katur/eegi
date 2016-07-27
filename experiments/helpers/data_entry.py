import datetime
import re
from itertools import izip_longest

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

from experiments.models import Experiment, ExperimentPlate
from library.helpers.naming import generate_library_plate_name
from library.models import LibraryPlate
from utils.google import connect_to_google_spreadsheets
from worms.models import WormStrain

GENE_ROW = 3
ALLELE_ROW = 4
TEMPERATURE_ROW = 5
SCREEN_TYPE_ROW = 6
FIRST_EXP_ROW = 7


def parse_batch_data_entry_gdoc():
    """
    Parse the Google Doc for batch data entry.

    Returns the number of experiments plates parsed from the sheet.

    By default, the parsed experiments are saved to the database.
    Set dry_run=True to instead do a dry run.
    """
    gc = connect_to_google_spreadsheets()
    sheet = gc.open(settings.BATCH_DATA_ENTRY_GDOC_NAME).sheet1
    values = sheet.get_all_values()

    date, screen_stage = _parse_gdoc_global_info(values)
    worms, temperatures, screen_types = _parse_gdoc_column_headers(values)
    count = _parse_gdoc_experiment_rows(
        values[FIRST_EXP_ROW:], screen_stage, date, worms, temperatures)
    return count


def _parse_gdoc_global_info(values):
    try:
        date = values[0][1]
    except IndexError:
        raise IndexError('Date must be in first row, second col')

    if re.match('^\d\d\d\d\d\d\d\d$', date):
        date = datetime.datetime.strptime(date, '%Y%m%d').date()
    elif re.match('^\d\d\d\d-\d\d-\d\d$', date):
        date = datetime.datetime.strptime(date, '%Y-%m-%d').date()
    else:
        raise ValueError('Date must be in format YYYYMMDD or YYYY-MM-DD')

    try:
        screen_stage = int(values[1][1])
    except IndexError:
        raise IndexError('Screen stage must be in second row, second col')
    except ValueError:
        raise ValueError('Screen stage must be an integer')

    return (date, screen_stage)


def _parse_gdoc_column_headers(values):
    worms = []
    try:
        genes = values[GENE_ROW][1:]
        alleles = values[ALLELE_ROW][1:]
    except IndexError:
        raise IndexError('Genes should be listed in {}th row, '
                         'and alleles in {}th row.'
                         .format(GENE_ROW + 1, ALLELE_ROW + 1))

    # Use izip_longest in case genes is longer than alleles, in N2 case
    for gene, allele in izip_longest(genes, alleles):
        if allele == 'zc310':
            allele = 'zu310'

        try:
            worms.append(WormStrain.objects.get(gene=gene, allele=allele))
        except WormStrain.DoesNotExist:
            raise ValueError('Worm strain does not exist with gene "{}" '
                             'and allele "{}"'.format(gene, allele))

    try:
        temperatures = values[TEMPERATURE_ROW][1:]
        screen_types = values[SCREEN_TYPE_ROW][1:]
    except IndexError:
        raise IndexError('Temperatures should be in {}th row, '
                         'and screen types in {}th row.'
                         .format(TEMPERATURE_ROW + 1, SCREEN_TYPE_ROW + 1))

    if len(temperatures) != len(worms):
        raise ValueError('The temperatures row should be the same '
                         'length as the worms row')

    # Use izip_longest because screen_type is not always listed
    for i, tup in enumerate(izip_longest(temperatures, screen_types, worms)):
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
                                temperatures):
    """Parse the rows with new experiments."""
    all_new_plates = []
    all_new_wells = []

    for i, row in enumerate(rows):
        current_row_number = FIRST_EXP_ROW + i + 1  # gdoc 1-indexed
        library_plate_name = generate_library_plate_name(row[0])
        if not library_plate_name:
            raise ValueError('Library plate cannot be blank; see row {}'
                             .format(current_row_number))

        try:
            library_plate = LibraryPlate.objects.get(id=library_plate_name)
        except ObjectDoesNotExist:
            raise ValueError('Library Plate {} does not exist; see row {}'
                             .format(library_plate_name,
                                     current_row_number))

        for j, experiment_plate_id in enumerate(row[1:]):
            if not experiment_plate_id:
                continue

            # Do dry_run=True to save inserts for bulk queries at end
            plate, wells = ExperimentPlate.create_plate_and_wells(
                experiment_plate_id, screen_stage, date,
                temperatures[j], worms[j], library_plate, dry_run=True)

            all_new_plates.append(plate)
            all_new_wells.extend(wells)

    ExperimentPlate.objects.bulk_create(all_new_plates)
    Experiment.objects.bulk_create(all_new_wells)

    return len(all_new_plates)
