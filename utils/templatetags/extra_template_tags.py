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
def get_image_url(experiment, tile_number):
    prefix = 'http://pleiades.bio.nyu.edu/GI_IMG/'
    tile = 'Tile0000{}.bmp'.format(str(tile_number).zfill(2))
    url = '{}{}/{}'.format(prefix, experiment.id, tile)
    return url
