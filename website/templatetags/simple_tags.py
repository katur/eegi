from decimal import Decimal

from django import template

register = template.Library()


@register.filter
def get_value(dictionary, key):
    """Get a dictionary value the normal way.

    Raises a KeyError if key is not present. So only use this when
    key being absent signifies a bug.

    """
    return dictionary[key]


@register.filter
def get_value_or_none(dictionary, key):
    """Get a dictionary value the safe way.

    Returns None if the key is not present.

    """
    return dictionary.get(key)


@register.filter
def is_key_present(dictionary, key):
    """Determine if a key is present in dictionary."""
    if dictionary.get(key):
        return True
    else:
        return False


@register.filter
def get_range(value):
    return range(value)


@register.simple_tag
def url_replace(request, field, value):
    query_dict = request.GET.copy()
    query_dict[field] = value
    return query_dict.urlencode()


@register.filter(is_safe=True)
def get_celsius_string(temperature):
    if temperature:
        return unicode(temperature) + u'\xb0' + 'C'
    else:
        return None


@register.filter(is_safe=True)
def concatenate_ids_with_commas(l):
    s = ''
    for item in l:
        s += str(item.id) + ','
    if len(s) > 0:
        s = s[:-1]

    return s


@register.simple_tag
def get_screen_type(temperature, strain):
    if Decimal(temperature) == strain.restrictive_temperature:
        return 'SUP screen temperature'
    elif Decimal(temperature) == strain.permissive_temperature:
        return 'ENH screen temperature'
    else:
        return 'neither SUP nor ENH screen temperature'
