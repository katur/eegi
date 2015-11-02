from django.db.models import Q

from worms.models import WormStrain


def get_worm_and_temperature_from_search_term(search_term, screen):
    """Get a tuple of (worm, temperature) matching search_term and screen.

    Screen must be 'ENH' or 'SUP'; otherwise an exception is thrown.

    search_term can be the allele, gene, or name of a worm strain.

    The combination of search_term/screen must uniquely identify a worm strain.
    Otherwise an exception is thrown.

    """
    if screen != 'ENH' and screen != 'SUP':
        raise Exception('screen must be ENH or SUP')

    if screen == 'ENH':
        worms = (WormStrain.objects
                 .filter(Q(gene=search_term) | Q(allele=search_term) |
                         Q(id=search_term))
                 .exclude(permissive_temperature__isnull=True))
    else:
        worms = (WormStrain.objects
                 .filter(Q(gene=search_term) | Q(allele=search_term) |
                         Q(id=search_term))
                 .exclude(restrictive_temperature__isnull=True))

    if not worms:
        return None

    elif len(worms) > 1:
        raise Exception('Multiple worm strains match search_term.')

    else:
        worm = worms[0]

    if screen == 'ENH':
        temperature = worm.permissive_temperature
    else:
        temperature = worm.restrictive_temperature

    return (worm, temperature)
