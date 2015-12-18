from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q

from clones.models import Clone, CloneTarget, Gene


def get_l4440():
    """Get the L4440 control RNAi clone."""
    return Clone.objects.get(pk='L4440')


def get_clones_from_search_term(search_term):
    """
    Get list of clones matching a search term.

    If no search_term is provided, raises a ValueError. This is
    to distinguish the case of no search term from the case of
    no match.

    Matching is defined as a perfect match between search_term and
    clone.pk, or if that does not exist, a perfect match between
    search_term and the gene.locus, gene.cosmid, or gene.pk of
    one of the clone's targets.
    """
    if not search_term:
        raise ValueError('Search term is required')

    try:
        clone = Clone.objects.get(pk=search_term)
        return [clone]

    except ObjectDoesNotExist:
        genes = (Gene.objects
                 .filter(Q(id=search_term) |
                         Q(cosmid_id=search_term) |
                         Q(locus=search_term)))

        clone_ids = (CloneTarget.objects.filter(gene__in=genes)
                     .values_list('clone_id', flat=True))
        return Clone.objects.filter(id__in=clone_ids)
