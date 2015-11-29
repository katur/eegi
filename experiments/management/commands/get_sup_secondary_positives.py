from django.core.management.base import BaseCommand

from experiments.helpers.criteria import passes_sup_secondary_stringent
from library.helpers.sequencing import categorize_sequences_by_blat_results
from library.models import LibrarySequencing
from worms.models import WormStrain


class Command(BaseCommand):
    """Command to get the list of SUP secondary positives.

    Limited for now to just those that are sequence-verified, and to the
    most stringent 'high confidence criteria'.

    """
    help = 'Get the list of SUP secondary positives.'

    def add_arguments(self, parser):
        parser.add_argument('--summary',
                            dest='summary',
                            action='store_true',
                            default=False,
                            help='Print summary only')

    def handle(self, **options):
        if options['summary']:
            summary_mode = True
        else:
            summary_mode = False

        # Categorize sequences corresponding to high confidence positives
        seqs = (LibrarySequencing.objects
                .select_related('source_stock',
                                'source_stock__intended_clone'))
        seqs_blat = categorize_sequences_by_blat_results(seqs)

        # Get set of "verified" wells (for now, just those for which the top
        # BLAT hit is an amplicon for the intended clone)
        verified = set(x.source_stock for x in seqs_blat[1])

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
            positives = worm.get_positives('SUP', 2,
                                           passes_sup_secondary_stringent)

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

        if summary_mode:
            self.stdout.write('{} library wells both positive and verified\n'
                              '{} interactions by well\n'
                              '{} interactions by clone'
                              .format(len(verified_doublecheck),
                                      num_interactions_by_well,
                                      num_interactions_by_clone))

            self.stdout.write('Breakdown by worm:')
            for worm in sorted(w):
                self.stdout.write('\t{}: {}'.format(worm.gene, len(w[worm])))

        else:
            for worm in sorted(w):
                for clone in sorted(w[worm]):
                    self.stdout.write('{},{}'.format(worm.gene, clone))
