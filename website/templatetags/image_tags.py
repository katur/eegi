import string

from django import template
from django.core.urlresolvers import reverse
from eegi.settings import IMG_PATH, THUMBNAIL_PATH, DEVSTAR_PATH
from utils.http import http_response_ok
from utils.well_tile_conversion import well_to_tile

register = template.Library()


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
    return '{} (<a href="{}">more info</a>)'.format(essentials, url)


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
        <span class="image-title">{}</span>
        <span class="placement">{} of {}</span>
      </span>

      <div class="image-frame"
        data-src="{}">
        <a href="#" class="image-frame-navigation image-frame-previous">
          <span>&laquo;</span>
        </a>
        <a href="#" class="image-frame-navigation image-frame-next">
          <span>&raquo;</span>
        </a>
      </div>

      <span class="image-caption">
        {}
      </span>
    </div>
    '''.format(
        get_image_title(experiment, well),
        current,
        length,
        get_image_url(experiment, well),
        scores
    )
    return output
