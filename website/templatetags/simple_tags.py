from decimal import Decimal

from django import template

register = template.Library()


@register.filter
def keyvalue(dict, key):
        return dict[key]


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
