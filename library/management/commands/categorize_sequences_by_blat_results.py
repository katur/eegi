from django.core.management.base import BaseCommand

from experiments.helpers.criteria import (passes_sup_secondary_percent,
                                          passes_sup_secondary_stringent)
from experiments.helpers.scores import get_positives_any_worm
from library.helpers.sequencing import (categorize_sequences_by_blat_results,
                                        get_average_crl, get_average_qs,
                                        get_number_decent_quality)
from library.models import LibrarySequencing


class Command(BaseCommand):
    """Command to summarize our sequencing results.

    Writes to stdout a categorized summary of our sequencing results,
    according to how high up the intended clone appears in the BLAT hits.

    The purpose of this script is to get a general sense of the quality
    of the sequencing and BLAT hits.


    Categories:

        - "Category X" (where X is an integer)
            The blat result for this sequencing result includes the
            intended clone, at hit rank X (see Firoz's documentation
            for meaning of hit rank).

        - "Category intended clone, does not match BLAT results"
            There are blat results for this sequencing result, but
            they do not include the intended clone.

        - "Category intended clone, no BLAT results"
            There are no blat results for this sequencing result.

        - other categories
            There are more categories included as controls / for
            curiosity's sake. E.g., sequences of L4440 wells and
            supposedly empty wells.


    The categorization is done for:

        1) all sequences
        2) sequences corresponding to positives only
        3) sequences corresponding to high confidence positives only

    """
    help = ('Summarize sequencing results. '
            'See command docstring for more details.')

    def handle(self, **options):
        seq_starter = (LibrarySequencing.objects
                       .select_related('source_stock',
                                       'source_stock__intended_clone'))

        # Categorize all sequences by blat results and intended clone
        seqs = seq_starter.all()
        seqs_blat = categorize_sequences_by_blat_results(seqs)
        self.print_categories('ALL SEQUENCES', seqs_blat)

        # Categorize sequences for SUP positives
        positives = get_positives_any_worm(
            'SUP', 2, passes_sup_secondary_percent)
        seqs_pos = seq_starter.filter(source_stock__in=positives)
        seqs_pos_blat = categorize_sequences_by_blat_results(seqs_pos)
        self.print_categories('SEQUENCES CORRESPONDING TO SUP SECONDARY '
                              'PERCENT POSITIVES ONLY',
                              seqs_pos_blat)

        # Categorize sequences for SUP high confidence positives
        high_conf = get_positives_any_worm(
            'SUP', 2, passes_sup_secondary_stringent)
        seqs_high = seq_starter.filter(source_stock__in=high_conf)
        seqs_high_blat = categorize_sequences_by_blat_results(seqs_high)
        self.print_categories('SEQUENCES CORRESPONDING TO SUP SECONDARY '
                              'STRINGENT POSITIVES ONLY',
                              seqs_high_blat)

    def print_categories(self, header, s):
        self.stdout.write('=========='
                          ' {} '
                          '=========='
                          .format(header))
        running_total = 0

        for category, seqs in sorted(s.iteritems()):
            number_in_category = len(seqs)
            running_total += number_in_category
            self.stdout.write(
                'Category {}:\n'
                '\t{} total\n'
                '\t\t{} "decent"\n'
                '\t\t{} average CRL; {} average quality score\n'
                .format(category,
                        number_in_category,
                        get_number_decent_quality(seqs),
                        get_average_crl(seqs),
                        get_average_qs(seqs))
            )

        self.stdout.write('(TOTAL: {})\n\n'.format(running_total))
