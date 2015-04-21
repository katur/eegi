from django.core.management.base import NoArgsCommand

from experiments.helpers.criteria import (
    passes_sup_positive_percentage_criteria)
from experiments.helpers.scores import get_positives_across_all_worms
from library.helpers.plate_design import (assign_to_plates,
                                          get_plate_assignment_rows)
from library.helpers.sequencing import (categorize_sequences_by_blat_results,
                                        NO_BLAT, NO_MATCH)
from library.models import LibrarySequencing

HELP = '''
Get list of SUP Secondary wells to resequence.

We are resequencing all wells for which the sequencing result
corresponds to a positive, and for which the top hit of the sequencing result
does not agree with the intended clone.

'''


class Command(NoArgsCommand):
    help = HELP

    def handle_noargs(self, **options):
        positives = get_positives_across_all_worms(
            'SUP', 2, passes_sup_positive_percentage_criteria)
        seqs = (LibrarySequencing.objects
                .filter(source_library_well__in=positives)
                .select_related('source_library_well',
                                'source_library_well__intended_clone'))
        seqs_blat = categorize_sequences_by_blat_results(seqs)

        reseq_wells = get_wells_to_resequence(seqs_blat)
        assigned = assign_to_plates(reseq_wells)
        assignment_rows = get_plate_assignment_rows(assigned)

        self.stdout.write('source_plate, source_well, destination_plate, '
                          'destination_well')
        for row in assignment_rows:
            self.stdout.write('{},{},{},{}\n'
                              .format(row[0].plate, row[0].well,
                                      row[1], row[2]))

        # TODO: add new seq plates to database


def get_wells_to_resequence(s):
    wells_to_resequence = []

    for key in s:
        if ((isinstance(key, int) and key > 1) or
                key == NO_BLAT or key == NO_MATCH):
            wells_to_resequence.extend(
                [x.source_library_well for x in s[key]])

    return sorted(wells_to_resequence)
