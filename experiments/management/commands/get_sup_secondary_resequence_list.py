from django.core.management.base import BaseCommand

from experiments.helpers.criteria import (
    shows_any_suppression as criteria)
from experiments.helpers.scores import get_positives_any_worm
from library.helpers.sequencing import (
    categorize_sequences_by_blat_results,
    NO_BLAT, NO_MATCH, NO_CLONE_BLAT)
from library.models import LibrarySequencing
from utils.plates import assign_to_plates, get_plate_assignment_rows


class Command(BaseCommand):
    """
    Command to get list of SUP secondary stocks to resequence.

    We are resequencing all SUP secondary stocks for which:
        1) top BLAT result of sequence does not match intended clone, and
        2) the stock passes a criteria
    """

    help = 'Get list of SUP secondary stocks to resequence.'

    def handle(self, **options):
        positives = get_positives_any_worm('SUP', 2, criteria)

        seqs = (LibrarySequencing.objects
                .filter(source_stock__in=positives)
                .select_related('source_stock',
                                'source_stock__intended_clone'))

        categorized_seqs = categorize_sequences_by_blat_results(seqs)

        stocks_to_resequence = []

        for key, values in categorized_seqs.items():
            if ((isinstance(key, int) and key > 1) or
                    key == NO_BLAT or key == NO_MATCH or key == NO_CLONE_BLAT):
                stocks_to_resequence.extend(
                    [x.source_stock for x in values])

        stocks_to_resequence = sorted(stocks_to_resequence,
                                      key=lambda stock: stock.id)

        assigned = assign_to_plates(stocks_to_resequence)

        rows = get_plate_assignment_rows(assigned)

        self.stdout.write('source_plate,source_well,'
                          'destination_plate,destination_well')
        for row in rows:
            source = row[2]

            if hasattr(source, 'plate'):
                plate = source.plate
            else:
                plate = None

            if hasattr(source, 'well'):
                well = source.well
            else:
                well = None

            self.stdout.write('{},{},{},{}'
                              .format(plate, well, row[0], row[1]))
