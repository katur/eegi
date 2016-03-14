from django.db.models import Q

from worms.models import WormStrain


def get_n2():
    """Get the N2 control worm strain."""
    return WormStrain.objects.get(pk='N2')


def get_worms_for_screen_type(screen_type):
    """
    Get the worm strains involved in a particular screen.

    screen_type must be 'ENH' or 'SUP'.
    """
    if screen_type not in ('ENH', 'SUP'):
        raise Exception('screen_type must be ENH or SUP')

    worms = WormStrain.objects

    if screen_type == 'ENH':
        return worms.exclude(permissive_temperature__isnull=True)
    else:
        return worms.exclude(restrictive_temperature__isnull=True)


def get_worm_and_temperature_from_search_term(search_term, screen_type):
    """
    Get a tuple of (worm, temperature) matching search_term and screen_type.

    screen_type must be 'ENH' or 'SUP'; otherwise an exception is thrown.

    search_term can be the allele, gene, or name of a worm strain.

    The combination of search_term/screen_type must uniquely identify a worm
    strain. Otherwise an exception is thrown.
    """
    worms = get_worms_for_screen_type(screen_type)

    worms = worms.filter(Q(gene=search_term) | Q(allele=search_term) |
                         Q(id=search_term))

    if not worms:
        return None
    elif len(worms) > 1:
        raise Exception('Multiple worm strains match search_term.')
    else:
        worm = worms.first()

    if screen_type == 'ENH':
        temperature = worm.permissive_temperature
    else:
        temperature = worm.restrictive_temperature

    return (worm, temperature)
