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


@register.simple_tag
def get_devstar_image_url(experiment, well):
    tile = well_to_tile(well)
    url = '/'.join((DEVSTAR_PATH, str(experiment.id), tile))
    url = string.replace(url, '.bmp', 'res.png')
    return url


@register.assignment_tag
def get_devstar_image_url_if_exists(experiment, well):
    """Returns the DevStaR image output, or None if the url does not return
    a 200 HTTP response.

    Be careful not to use this on too many images at once (making
    many HTTP requests can be slow).

    """
    url = get_devstar_image_url(experiment, well)
    if http_response_ok(url):
        return url
    else:
        return None


def get_image_frame(experiment, well):
    return '''
        <div class="image-frame"
          data-src="{}">
        <a href="#" class="image-frame-navigation image-frame-previous">
          <span>&laquo;</span>
        </a>
        <a href="#" class="image-frame-navigation image-frame-next">
          <span>&raquo;</span>
        </a>
        </div>
    '''.format(get_image_url(experiment, well))


@register.simple_tag
def get_image_wrapper(experiment, library_well, current, length):

    def get_image_title(experiment, well):
        url = reverse('experiment_well_url', args=[experiment.id, well])
        essentials = 'Experiment {}, well {}'.format(
            str(experiment.id), well)
        if experiment.worm_strain.is_control():
            essentials += ', ' + experiment.get_celsius_temperature()
        return '{} (<a href="{}">more info</a>)'.format(essentials, url)

    well = library_well.well

    if library_well.is_control() or experiment.is_mutant_control():
        scores = ""
    else:
        scores = experiment.get_score_summary(well)

    return '''
        <div class="individual-image">
          <span class="image-topbar">
            <span class="image-title">{0}</span>
            <span class="placement">{1} of {2}</span>
          </span>

          {3}

          <span class="image-caption">
            <span class="image-scores">{4}</span>
            <a class="devstar-link" href="{5}">View DevStaR image</a>
        </div>
    '''.format(
        get_image_title(experiment, well),
        current, length,
        get_image_frame(experiment, well),
        scores,
        get_devstar_image_url(experiment, well)
    )
