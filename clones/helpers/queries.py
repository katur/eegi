from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q

from clones.models import Clone, CloneTarget, Gene


def get_clones(search_term):
    if not search_term:
        return Clone.objects.all()

    try:
        clone = Clone.objects.get(pk=search_term)
        clones = [clone]

    except ObjectDoesNotExist:
        genes = (Gene.objects
                 .filter(Q(id=search_term) |
                         Q(cosmid_id=search_term) |
                         Q(locus=search_term)))

        clone_ids = (CloneTarget.objects.filter(gene__in=genes)
                     .values_list('clone_id', flat=True))
        clones = Clone.objects.filter(id__in=clone_ids)

    return clones
