from django.core.management.base import NoArgsCommand

from experiments.helpers.scores import (get_positives_across_all_worms,
                                        get_positives_specific_worm)
from experiments.helpers.criteria import (passes_sup_positive_criteria,
                                          passes_sup_high_confidence_criteria)
from library.models import LibrarySequencing
from library.helpers import (categorize_sequences_by_blat_results,
                             get_avg_crl,
                             get_avg_qs,
                             get_number_decent_quality,
                             NO_BLAT, NO_MATCH)
from worms.models import WormStrain

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

    def handle_noargs(self, **options):
        seq_starter = (LibrarySequencing.objects
                       .select_related('source_library_well',
                                       'source_library_well__intended_clone'))

        # Categorize all sequences by blat results and intended clone
        seqs = seq_starter.all()
        seqs_blat = categorize_sequences_by_blat_results(seqs)
        self.print_categories('ALL SEQUENCES', seqs_blat)

        # Categorize sequences for positives only
        positives = get_positives_across_all_worms(
            'SUP', 2, passes_sup_positive_criteria)
        seqs_pos = seq_starter.filter(source_library_well__in=positives)
        seqs_pos_blat = categorize_sequences_by_blat_results(seqs_pos)
        self.print_categories('SEQUENCES CORRESPONDING TO POSITIVES ONLY',
                              seqs_pos_blat)

        # Categorize sequences for high confidence only
        high_conf = get_positives_across_all_worms(
            'SUP', 2, passes_sup_high_confidence_criteria)
        seqs_high = seq_starter.filter(source_library_well__in=high_conf)
        seqs_high_blat = categorize_sequences_by_blat_results(seqs_high)
        self.print_categories('SEQUENCES CORRESPONDING TO HIGH CONFIDENCE '
                              'POSITIVES ONLY', seqs_high_blat)

        # Get set of "verified" wells (for now, just those for which the top
        # BLAT hit is an amplicon for the intended clone)
        verified = set(x.source_library_well for x in seqs_high_blat[1])
        self.stdout.write('Number library wells positive and "verified": {}'
                          .format(len(verified)))

        worms = WormStrain.objects.exclude(
            restrictive_temperature__isnull=True)

        unique_wells = set()
        num_interactions_by_well = 0
        num_interactions_by_clone = 0

        w = {}
        for worm in worms:
            positives = get_positives_specific_worm(
                worm, 'SUP', 2, passes_sup_high_confidence_criteria)
            pos_verified = positives.intersection(verified)

            unique_wells.update(pos_verified)
            num_interactions_by_well += len(pos_verified)

            pos_verified_clones = set()
            for well in pos_verified:
                clone = well.intended_clone_id
                if clone not in pos_verified:
                    pos_verified_clones.add(clone)

            num_interactions_by_clone += len(pos_verified_clones)
            w[worm] = pos_verified_clones

        self.stdout.write('Number unique library wells across clones that '
                          'are verified (should be the same as above): {}'
                          .format(len(unique_wells)))

        self.stdout.write('{} total interactions by well, {} by clone'
                          .format(num_interactions_by_well,
                                  num_interactions_by_clone))

        for worm in sorted(w):
            self.stdout.write('{}: {}'.format(worm.gene, len(w[worm])))

        for worm in sorted(w):
            for clone in sorted(w[worm]):
                self.stdout.write('{},{}'.format(worm.gene, clone))

        '''
        reseq_wells = get_wells_to_resequence(seqs_pos_blat)
        self.stdout.write('{} wells to resequence:\n'.format(len(reseq_wells)))
        for reseq_well in reseq_wells:
            self.stdout.write('{}\n'.format(reseq_well))
        '''


def get_wells_to_resequence(s):
    wells_to_resequence = []

    for key in s:
        if ((isinstance(key, int) and key > 1) or
                key == NO_BLAT or key == NO_MATCH):
            wells_to_resequence.extend(
                [x.source_library_well for x in s[key]])

    return sorted(wells_to_resequence)
