import sys

from django.core.management.base import BaseCommand

from clones.models import Clone
from library.models import LibrarySequencing, LibrarySequencingBlatResult


class Command(BaseCommand):
    """
    Command to compare the BLAT results to the intended clones.

    USAGE
    From the project root:
        ./manage.py analyze_blat_results
    """
    help = ('Compare BLAT results to intended clones.')

    def handle(self, *args, **options):
        seqs = (LibrarySequencing.objects.all()
                .select_related('source_library_well',
                                'source_library_well__intended_clone'))
        blats = (LibrarySequencingBlatResult.objects.all()
                 .select_related('library_sequencing', 'clone_hit'))

        b = {}
        for blat in blats:
            seq = blat.library_sequencing
            if seq not in b:
                b[seq] = []
            b[seq].append(blat)

        num_no_clone = 0
        num_no_clone_yes_blat = 0

        num_l4440 = 0
        num_l4440_yes_blat = 0

        num_other = 0
        num_other_no_blat = 0
        num_other_no_match = 0
        num_other_match = {}
        num_other_match[1] = 0
        num_other_match[2] = 0
        num_other_match[3] = 0

        for seq in seqs:
            if seq.source_library_well:
                intended_clone = seq.source_library_well.intended_clone
            else:
                intended_clone = None

            if not intended_clone:
                num_no_clone += 1
                if seq in b:
                    num_no_clone_yes_blat += 1

            elif intended_clone.is_control():
                num_l4440 += 1
                if seq in b:
                    num_l4440_yes_blat += 1

            else:
                num_other += 1
                if seq not in b:
                    num_other_no_blat += 1
                else:
                    match = get_match(b[seq], intended_clone)
                    if not match:
                        num_other_no_match += 1
                    else:
                        rank = match.hit_rank
                        num_other_match[rank] += 1

        sys.stdout.write('{} seq results with no intended clone '
                         '({} of these have BLAT results)\n'
                         '{} seq results for L4440 '
                         '({} of these have BLAT results)\n'
                         '\n'
                         '{} seq results with (non-L4440) intended clones\n'
                         'Of these, {} have no BLAT, {} have no match.\n'
                         'Of matches, {} rank 1, {} rank 2, {} rank 3.\n'
                         .format(num_no_clone, num_no_clone_yes_blat,
                                 num_l4440, num_l4440_yes_blat,
                                 num_other, num_other_no_blat,
                                 num_other_no_match, num_other_match[1],
                                 num_other_match[2], num_other_match[3]))


def get_match(blat_results, intended_clone):
    for x in blat_results:
        if x.clone_hit == intended_clone:
            return x
    return None
