from django.db.models import Q

from worms.models import WormStrain


def get_worm_and_temperature(query, screen):
    """Get a tuple of (worm, temperature) capturing a search query and screen.

    Screen must be 'ENH' or 'SUP'; otherwise an exception is thrown.

    Query can be the allele, gene, or name of a worm strain.

    The combination of query/screen must uniquely identify a worm strain.
    Otherwise an exception is thrown.

    """
    if screen != 'ENH' and screen != 'SUP':
        raise Exception('screen must be ENH or SUP')

    if screen == 'ENH':
        worms = (WormStrain.objects
                 .filter(Q(gene=query) | Q(allele=query) | Q(id=query))
                 .exclude(permissive_temperature__isnull=True))
    else:
        worms = (WormStrain.objects
                 .filter(Q(gene=query) | Q(allele=query) | Q(id=query))
                 .exclude(restrictive_temperature__isnull=True))

    if len(worms) == 0:
        return None

    elif len(worms) > 1:
        raise Exception('Multiple worm strains match query.')

    else:
        worm = worms[0]

    if screen == 'ENH':
        temperature = worm.permissive_temperature
    else:
        temperature = worm.restrictive_temperature

    return (worm, temperature)
