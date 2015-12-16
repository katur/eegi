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
    """Command to get list of SUP secondary stocks to resequence.

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

        seqs_blat = categorize_sequences_by_blat_results(seqs)

        reseq_wells = _get_wells_to_resequence(seqs_blat)

        assigned = assign_to_plates(reseq_wells)

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


def _get_wells_to_resequence(s):
    wells_to_resequence = []

    for key in s:
        if ((isinstance(key, int) and key > 1) or
                key == NO_BLAT or key == NO_MATCH or key == NO_CLONE_BLAT):
            wells_to_resequence.extend(
                [x.source_stock for x in s[key]])

    return sorted(wells_to_resequence)
