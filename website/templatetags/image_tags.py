import string

from django import template
from django.core.urlresolvers import reverse
from eegi.settings import IMG_PATH, THUMBNAIL_PATH, DEVSTAR_PATH
from utils.http import http_response_ok
from utils.well_tile_conversion import well_to_tile

register = template.Library()


@register.simple_tag
def get_image_url(experiment, well):
    """Get the url of an experiment image.

    Accepts an Experiment object, and well as a string.

    """
    tile = well_to_tile(well)
    url = '/'.join((IMG_PATH, str(experiment.id), tile))
    return url


@register.simple_tag
def get_thumbnail_url(experiment, well):
    """Get the url of an experiment thumbnail image.

    Accepts an Experiment object, and well as a string.

    """
    tile = well_to_tile(well)
    url = '/'.join((THUMBNAIL_PATH, str(experiment.id), tile))
    url = string.replace(url, 'bmp', 'jpg')
    return url


@register.simple_tag
def get_devstar_image_url(experiment, well):
    """Get the url of a DevStaR output image.

    Accepts an Experiment object, and well as a string.

    """
    tile = well_to_tile(well)
    url = '/'.join((DEVSTAR_PATH, str(experiment.id), tile))
    url = string.replace(url, '.bmp', 'res.png')
    return url


@register.assignment_tag
def get_devstar_image_url_if_exists(experiment, well):
    """Get the url of a DevStaR output image, or None if it doesn't exist.

    Checks that the url returns an HTTP 200 status code, meaning "ok".
    Be careful not to use this on too many images at once; making
    many HTTP requests can be slow.

    """
    url = get_devstar_image_url(experiment, well)
    if http_response_ok(url):
        return url
    else:
        return None


@register.simple_tag
def get_thumbnail_td(experiment, library_well):
    return get_image_td(experiment, library_well, is_thumbnail=True)


@register.simple_tag
def get_devstar_image_td(experiment, library_well):
    return get_image_td(experiment, library_well, is_devstar=True)


@register.simple_tag
def get_image_td(experiment, library_well, is_thumbnail=False,
                 is_devstar=False):
    """Get a td element with an experiment image and some simple information.

    This is used when printing the wells of an entire plate as a table
    (e.g with 8 rows and 12 columns for a normal 96-well plate, or 96 rows
    and 1 column for "vertical view" of a 96-well plate, etc).

    The top bar contains minimal info to identify the well (well and tile).

    The lower caption contains the clone name.

    Clicking the image links to more details about that experiment well.

    """

    well = library_well.well
    experiment_url = reverse('experiment_well_url', args=[experiment.id, well])

    if is_thumbnail:
        image_url = get_thumbnail_url(experiment, well)
    elif is_devstar:
        image_url = get_devstar_image_url(experiment, well)
    else:
        image_url = get_image_url(experiment, well)

    if not library_well.intended_clone:
        td_style = 'class="empty-well"'
    else:
        td_style = ''

    return '''
        <td {0}>
          <div class="well-title">
            {1}
            <span class="parenthetical">({2})</span>
          </div>

          <a class="image-frame" href="{3}">
            <img src="{4}">
          </a>

          <div class="well-caption">{5}</div>
        </td>
    '''.format(td_style, well, library_well.get_tile(), experiment_url,
               image_url, library_well.intended_clone)


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
