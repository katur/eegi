from django.core.management.base import NoArgsCommand

from experiments.helpers.scores import get_sup_secondary_positive_library_wells
from library.models import LibrarySequencing
from library.helpers import (categorize_sequences_by_blat_results,
                             get_avg_crl,
                             get_avg_qs,
                             get_number_decent_quality,
                             get_wells_to_resequence)

HELP = '''
Compare BLAT hits of our sequencing results to the intended clones.

The purpose do of this is that intended clones that are not found in the
BLAT results will be resequenced.
'''


class Command(NoArgsCommand):
    help = HELP

    def print_categories(self, header, s):
        self.stdout.write('============='
                          ' {} '
                          '============='
                          .format(header))
        for category, seqs in sorted(s.iteritems()):
            self.stdout.write(
                'Category {}:\n'
                '\t{} total\n'
                '\t\t{} "decent"\n'
                '\t\t{} average CRL\n'
                '\t\t{} average quality score\n\n'
                .format(category,
                        len(seqs),
                        get_number_decent_quality(seqs),
                        get_avg_crl(seqs),
                        get_avg_qs(seqs))
            )

    def handle_noargs(self, **options):
        seq_starter = (LibrarySequencing.objects
                       .select_related('source_library_well',
                                       'source_library_well__intended_clone'))
        seqs_all = seq_starter.all()
        s_all = categorize_sequences_by_blat_results(seqs_all)
        self.print_categories('ALL SEQUENCES', s_all)

        positives = get_sup_secondary_positive_library_wells()
        seqs_pos = seq_starter.filter(source_library_well__in=positives)
        s_pos = categorize_sequences_by_blat_results(seqs_pos)
        self.print_categories('POSITIVES ONLY', s_pos)

        reseq_wells = get_wells_to_resequence(s_pos)
        self.stdout.write('{} wells to resequence:\n'.format(len(reseq_wells)))
        for reseq_well in reseq_wells:
            self.stdout.write('{}\n'.format(reseq_well))
