import string

from django import template

register = template.Library()


@register.filter(is_safe=True)
def get_celsius_string(temperature):
    if temperature:
        return unicode(temperature) + u'\xb0' + 'C'
    else:
        return None


@register.filter
def get_range(value):
    return range(value)


@register.simple_tag
def url_replace(request, field, value):
    query_dict = request.GET.copy()
    query_dict[field] = value
    return query_dict.urlencode()


@register.simple_tag
def get_image(experiment, well):
    prefix = 'http://pleiades.bio.nyu.edu/GI_IMG/'
    tile = well.get_tile()
    url = '{}{}/{}'.format(prefix, experiment.id, tile)
    return url


@register.simple_tag
def get_thumbnail_image(experiment, well):
    prefix = 'http://pleiades.bio.nyu.edu/GI_IMG/convertedImg/'
    tile = well.get_tile()
    url = '{}{}/{}'.format(prefix, experiment.id, tile)
    url = string.replace(url, 'bmp', 'jpg')
    return url
