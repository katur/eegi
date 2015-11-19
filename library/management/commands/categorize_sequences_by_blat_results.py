from django.core.management.base import BaseCommand

from experiments.helpers.criteria import (
    passes_sup_positive_percentage_criteria, passes_sup_stringent_criteria)
from experiments.helpers.scores import get_positives_any_worm
from library.helpers.sequencing import (categorize_sequences_by_blat_results,
                                        get_avg_crl, get_avg_qs,
                                        get_number_decent_quality)
from library.models import LibrarySequencing


class Command(BaseCommand):
    """Command to summarize our sequencing results.

    Writes to stdout a categorized summary of our sequencing results,
    according to how high up the intended clone appears in the BLAT hits.

    The purpose of this script is to get a general sense of the quality of the
    sequencing and BLAT hits.


    Categories:

        - "Category X" (where X is an integer)
            The blat result for this sequencing result includes the intended
            clone, at hit rank X (see Firoz's documentation for meaning of
            hit rank).

        - "Category intended clone, does not match BLAT results"
            There are blat results for this sequencing result, but they do not
            include the intended clone.

        - "Category intended clone, no BLAT results"
            There are no blat results for this sequencing result.

        - other categories
            There are more categories included as controls / for curiosity's
            sake, e.g., sequences of L4440 wells and supposedly empty wells.


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
            'SUP', 2, passes_sup_positive_percentage_criteria)
        seqs_pos = seq_starter.filter(source_stock__in=positives)
        seqs_pos_blat = categorize_sequences_by_blat_results(seqs_pos)
        self.print_categories('SEQUENCES CORRESPONDING TO POSITIVES ONLY',
                              seqs_pos_blat)

        # Categorize sequences for SUP high confidence positives
        high_conf = get_positives_any_worm(
            'SUP', 2, passes_sup_stringent_criteria)
        seqs_high = seq_starter.filter(source_stock__in=high_conf)
        seqs_high_blat = categorize_sequences_by_blat_results(seqs_high)
        self.print_categories('SEQUENCES CORRESPONDING TO HIGH CONFIDENCE '
                              'POSITIVES ONLY', seqs_high_blat)

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
                '\t\t{} avg CRL, {} avg quality score\n'
                .format(category,
                        number_in_category,
                        get_number_decent_quality(seqs),
                        get_avg_crl(seqs),
                        get_avg_qs(seqs))
            )

        self.stdout.write('(TOTAL: {})\n\n'.format(running_total))
