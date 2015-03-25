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

        NO_BLAT = 'intended clone, but no BLAT results (bad)'
        NO_MATCH = 'intended clone does not match BLAT results (bad)'
        L4440_BLAT = 'L4440 with BLAT results (bad)'
        L4440_NO_BLAT = 'L4440, no BLAT results (good)'
        NO_CLONE_BLAT = 'no intended clone with BLAT results (bad)'
        NO_CLONE_NO_BLAT = 'no intended clone, no BLAT results (good)'

        s = {
            1: [],
            2: [],
            3: [],
            L4440_NO_BLAT: [],
            NO_CLONE_NO_BLAT: [],
            NO_BLAT: [],
            NO_MATCH: [],
            L4440_BLAT: [],
            NO_CLONE_BLAT: [],
        }

        for seq in seqs:
            if seq.source_library_well:
                intended_clone = seq.source_library_well.intended_clone
            else:
                intended_clone = None

            if not intended_clone:
                if seq in b:
                    s[NO_CLONE_BLAT].append(seq)
                else:
                    s[NO_CLONE_NO_BLAT].append(seq)

            elif intended_clone.is_control():
                if seq in b:
                    s[L4440_BLAT].append(seq)
                else:
                    s[L4440_NO_BLAT].append(seq)

            else:
                if seq not in b:
                    s[NO_BLAT].append(seq)
                else:
                    match = get_match(b[seq], intended_clone)
                    if not match:
                        s[NO_MATCH].append(seq)
                    else:
                        rank = match.hit_rank
                        s[rank].append(seq)

        for name, l in s.iteritems():
            sys.stdout.write(
                'Category {}:\n'
                '\t{} total\n'
                '\t{} "decent"\n'
                '\t{} average CRL\n'
                '\t{} average quality score\n\n'
                .format(name, len(l), get_number_decent(l),
                        get_avg_crl(l), get_avg_qs(l))
            )


def get_match(blat_results, intended_clone):
    for x in blat_results:
        if x.clone_hit == intended_clone:
            return x
    return None


def avg(l):
    if l:
        return sum(l) / len(l)
    else:
        return 0


def get_avg_crl(l):
    return avg([x.crl for x in l])


def get_avg_qs(l):
    return avg([x.quality_score for x in l])


def get_number_decent(l):
    return sum([x.is_decent_quality() for x in l])
