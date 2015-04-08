import time

from django.core.management.base import NoArgsCommand

from experiments.helpers.scores import get_positives_specific_worm
from experiments.helpers.criteria import passes_sup_high_confidence_criteria
from library.models import LibrarySequencing
from library.helpers import categorize_sequences_by_blat_results
from worms.models import WormStrain

HELP = '''
Get the list of SUP secondary positives, limiting it for now to
just those that are sequence-verified, and to the more stringent
'high confidence criteria'.

'''


class Command(NoArgsCommand):
    help = HELP

    def handle_noargs(self, **options):
        start = time.time()
        # Get and categorize the sequences corresponding to high confidence
        # positives
        seqs = (LibrarySequencing.objects
                .select_related('source_library_well',
                                'source_library_well__intended_clone'))
        seqs_blat = categorize_sequences_by_blat_results(seqs)

        # Get set of "verified" wells (for now, just those for which the top
        # BLAT hit is an amplicon for the intended clone)
        verified = set(x.source_library_well for x in seqs_blat[1])

        # Get all SUP worm strains
        worms = WormStrain.objects.exclude(
            restrictive_temperature__isnull=True)

        verified_doublecheck = set()
        num_interactions_by_well = 0
        num_interactions_by_clone = 0

        # For each worm, find the intersection of verified positives,
        # and add to the list of interactions
        w = {}
        for worm in worms:
            positives = get_positives_specific_worm(
                worm, 'SUP', 2, passes_sup_high_confidence_criteria)
            pos_verified = positives.intersection(verified)

            verified_doublecheck.update(pos_verified)
            num_interactions_by_well += len(pos_verified)

            pos_verified_clones = set()
            for well in pos_verified:
                clone = well.intended_clone_id
                if clone not in pos_verified:
                    pos_verified_clones.add(clone)

            num_interactions_by_clone += len(pos_verified_clones)
            w[worm] = pos_verified_clones

        self.stdout.write('{} library wells both positive and verified; '
                          '{} when calculated across worm strains '
                          '(should be equal)'
                          .format(len(verified), len(verified_doublecheck)))

        self.stdout.write('{} interactions by well\n'
                          '{} interactions by clone'
                          .format(num_interactions_by_well,
                                  num_interactions_by_clone))

        self.stdout.write('Breakdown by worm:')
        for worm in sorted(w):
            self.stdout.write('\t{}: {}'.format(worm.gene, len(w[worm])))

        self.stdout.write('\n')

        for worm in sorted(w):
            for clone in sorted(w[worm]):
                self.stdout.write('{},{}'.format(worm.gene, clone))

        end = time.time()
        self.stdout.write(str(end - start))
