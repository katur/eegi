import string
from decimal import Decimal

from django import template
from django.core.urlresolvers import reverse
from eegi.settings import IMG_PATH, THUMBNAIL_PATH, DEVSTAR_PATH
from library.helpers.tile_conversion import well_to_tile
from utils.http import http_response_ok

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


@register.simple_tag
def get_image_url(experiment, well):
    tile = well_to_tile(well)
    url = '/'.join((IMG_PATH, str(experiment.id), tile))
    return url


@register.simple_tag
def get_thumbnail_url(experiment, well):
    tile = well_to_tile(well)
    url = '/'.join((THUMBNAIL_PATH, str(experiment.id), tile))
    url = string.replace(url, 'bmp', 'jpg')
    return url


@register.assignment_tag
def get_devstar_image_url(experiment, well):
    tile = well_to_tile(well)
    url = '/'.join((DEVSTAR_PATH, str(experiment.id), tile))
    url = string.replace(url, '.bmp', 'res.png')
    if http_response_ok(url):
        return url
    else:
        return None


def get_image_title(experiment, well):
    url = reverse('experiment_well_url', args=[experiment.id, well])
    essentials = 'Experiment {}, well {}'.format(
        str(experiment.id), well)
    if experiment.worm_strain.is_control():
        essentials += ', ' + experiment.get_celsius_temperature()
    output = '''
    <span class="image-title">
      {} (<a href="{}">more info</a>)
    </span>
    '''.format(essentials, url)
    return output


def get_image_placement(current, length):
    return '<span class="placement">{} of {}</span>'.format(
        current, length)


@register.simple_tag
def get_image_html(experiment, library_well, current, length):
    well = library_well.well
    if library_well.is_control() or experiment.is_mutant_control():
        scores = ""
    else:
        scores = experiment.get_score_summary(well)

    output = '''
    <div class="individual-image">
      <span class="image-topbar">
        {}
        {}
      </span>

      <div class="image-frame"
        data-src="{}">
        <a href="#" class="image-frame-navigation image-frame-previous"></a>
        <a href="#" class="image-frame-navigation image-frame-next"></a>
      </div>

      <span class="image-caption">
        {}
      </span>
    </div>
    '''.format(
        get_image_title(experiment, well),
        get_image_placement(current, length),
        get_image_url(experiment, well),
        scores
    )
    return output
