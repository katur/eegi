from django.core.management.base import BaseCommand

from experiments.helpers.criteria import (
    shows_any_suppression as criteria)
from experiments.helpers.scores import get_positives_any_worm
from experiments.models import Experiment
from library.helpers.sequencing import (
    categorize_sequences_by_blat_results, NO_BLAT, NO_MATCH, NO_CLONE_BLAT)
from library.models import LibrarySequencing
from utils.google import connect_to_google_spreadsheets
from utils.plates import assign_to_plates, get_plate_assignment_rows


class Command(BaseCommand):
    """
    Command to get list of SUP secondary stocks to resequence.

    We are resequencing all SUP secondary stocks for which:
        1) top BLAT result of sequence does not match intended clone, and
        2) the stock passes a criteria
    """

    help = 'Get list of SUP secondary stocks to resequence.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--first-plate-number', type=int,
            help='Number of the first output plate')

        parser.add_argument(
            '--empties-per-plate', type=int, default=0,
            help='Number of empty wells per output plate')

    def handle(self, **options):
        positives = get_positives_any_worm('SUP', 2, criteria)
        additional_positives = get_additional_positives_from_google_doc()
        positives = positives | additional_positives

        seqs = (LibrarySequencing.objects
                .filter(source_stock__in=positives)
                .select_related('source_stock',
                                'source_stock__intended_clone'))
        categorized_seqs = categorize_sequences_by_blat_results(seqs)

        stocks_to_resequence = []
        for category, values in categorized_seqs.items():
            if is_bad_sequence(category):
                stocks_to_resequence.extend(
                    [x.source_stock for x in values])

        stocks_to_resequence = sorted(stocks_to_resequence,
                                      key=lambda stock: stock.id)

        assigned = assign_to_plates(
            stocks_to_resequence, vertical=True,
            empties_per_plate=options['empties_per_plate'])
        rows = get_plate_assignment_rows(assigned)

        # Write output
        self.stdout.write('source_plate,source_well,'
                          'destination_plate,destination_well')
        for row in rows:
            destination_plate = get_destination_plate(
                row[0], options['first_plate_number'])
            destination_well = row[1]
            source = row[2]

            if hasattr(source, 'plate'):
                source_plate = source.plate
            else:
                source_plate = None

            if hasattr(source, 'well'):
                source_well = source.well
            else:
                source_well = None

            self.stdout.write('{},{},{},{}'.format(
                source_plate, source_well,
                destination_plate, destination_well))


def is_bad_sequence(category):
    return ((isinstance(category, int) and category > 1) or
            category == NO_BLAT or category == NO_MATCH or
            category == NO_CLONE_BLAT)


def get_destination_plate(index, first_plate_number=None):
    """
    Get the name of the destination plate.

    If first_plate_number is supplied, returns a plate name
    in format 'JL%', where % is first_plate_number + index.

    If first_plate_number is None, returns a plate name of just
    the index (assumed that the above convention is not being used).
    """
    if first_plate_number:
        plate_number = first_plate_number + index
        return 'JL{}'.format(plate_number)
    else:
        return str(index)


def get_additional_positives_from_google_doc():
    """
    One-off function to add positives from Noah's Google Doc,
    since these scores have not yet been added to the database.
    """
    gc = connect_to_google_spreadsheets()
    sheet = (gc.open('SUP_secondary_rescores_due_to_all_0_interface_bug')
             .sheet1)
    values = sheet.get_all_values()

    positive_stocks = set()

    for row in values[1:]:
        experiment_id, score = row[0:2]

        try:
            experiment_id = experiment_id.strip()
            experiment = Experiment.objects.get(id=experiment_id)
            score = int(score.strip())
            if score >= 1 and score <= 3:
                positive_stocks.add(experiment.library_stock)

        except Exception:
            continue

    return positive_stocks
