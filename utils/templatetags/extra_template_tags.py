import string
from decimal import Decimal

from django import template
from django.core.urlresolvers import reverse

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


@register.simple_tag
def get_screen_type(temperature, strain):
    if Decimal(temperature) == strain.restrictive_temperature:
        return 'SUP screen temperature'
    elif Decimal(temperature) == strain.permissive_temperature:
        return 'ENH screen temperature'
    else:
        return 'not SUP or ENH screening temperature for this strain'


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


@register.simple_tag
def get_image_title(experiment, well):
    url = reverse('experiment_well_url', args=[experiment.id, well.well])
    output = '''
    <span class="image-title">
      Experiment {}, well {} (<a href="{}">click to zoom</a>)
    </span>
    '''.format(str(experiment.id), well.well, url)
    print output
    return output


@register.simple_tag
def get_image_placement(current, length):
    return '<span class="placement">{} of {}</span>'.format(current, length)


@register.simple_tag
def get_image_html(experiment, well, current, length):
    output = '''
    <div class="individual-image">
      <span class="image-topbar">
        {}
        {}
      </span>

      <div class="experiment-image-wrapper"
        data-src="{}">
      </div>

      <span class="image-caption">
        {}
      </span>
    </div>
    '''.format(
        get_image_title(experiment, well),
        get_image_placement(current, length),
        get_image(experiment, well),
        experiment.score_summary
    )
    return output
