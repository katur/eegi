from django import template
from django.core.urlresolvers import reverse

from experiments.helpers.urls import (get_image_url, get_thumbnail_url,
                                      get_devstar_image_url)
from utils.http import http_response_ok

register = template.Library()


@register.simple_tag
def get_thumbnail(experiment, well):
    """Get a thumbnail image.

    See get_image() for more details.

    """
    return get_image(experiment, well, is_thumbnail=True)


@register.simple_tag
def get_devstar_image(experiment, well):
    """Get a DevStaR-labelled image.

    See get_image() for more details.

    """
    return get_image(experiment, well, is_devstar=True)


@register.simple_tag
def get_devstar_image_if_exists(experiment, well):
    """Get a DevStaR-labelled image, or None if it doesn't exist.

    Like get_devstar_image(), but checks that the image url returns an
    HTTP 200 status code (which means "ok").

    Be careful not to use this on too many images at once; making
    many HTTP requests can be slow.

    """
    url = get_devstar_image_url(experiment, well)
    if http_response_ok(url):
        return get_devstar_image(experiment, well)
    else:
        return None


@register.simple_tag
def get_image(experiment, well, is_thumbnail=False, is_devstar=False):
    """Get an image.

    Returns the HTML img tag along with a surrounding div
    to preserve the aspect ratio while loading.

    """
    if is_thumbnail:
        image_url = get_thumbnail_url(experiment, well)
    elif is_devstar:
        image_url = get_devstar_image_url(experiment, well)
    else:
        image_url = get_image_url(experiment, well)

    return '''
        <div class="image-frame">
          <img src="{}"/>
        </div>
    '''.format(image_url)


@register.simple_tag
def get_thumbnail_td(experiment, library_well):
    """Get an HTML td element with a thumbnail and minimal information.

    See get_image_td() for more details.

    """
    return get_image_td(experiment, library_well, is_thumbnail=True)


@register.simple_tag
def get_devstar_image_td(experiment, library_well):
    """Get an HTML td element with a DevStaR-labelled image and minimal
    information.

    See get_image_td() for more details.

    """
    return get_image_td(experiment, library_well, is_devstar=True)


@register.simple_tag
def get_image_td(experiment, library_well, is_thumbnail=False,
                 is_devstar=False):
    """Get an HTML td element with an image and minimal information.

    "Minimal information" is a top bar identifying the well's position,
    and a lower caption identifying the clone name.
    Clicking the image links to more details about that experiment well.
    This function is meant for displaying a well in the context of
    displaying the entire plate.

    """

    well = library_well.well
    image = get_image(experiment, well, is_thumbnail=is_thumbnail,
                      is_devstar=is_devstar)
    experiment_url = reverse('experiment_well_url', args=[experiment.id, well])

    if not library_well.intended_clone:
        td_style = 'class="empty-well"'
    else:
        td_style = ''

    return '''
        <td {}>
          <div class="well-title">
            {}
            <span class="parenthetical">({})</span>
          </div>

          <a href="{}">
            {}
          </a>

          <div class="well-caption">{}</div>
        </td>
    '''.format(td_style, well, library_well.get_tile(), experiment_url,
               image, library_well.intended_clone)


@register.simple_tag
def get_image_wrapper(experiment, library_well, current, length):
    """Get an image along with the surrounding carousel information.

    Surrounding information includes which experiment and well it is,
    its position in the carousel, manual scores, a link to devstar, etc.

    """
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
            <span class="image-title">{}</span>
            <span class="placement">{} of {}</span>
          </span>

          {}

          <span class="image-caption">
            <span class="image-scores">{}</span>
            <a class="devstar-link" href="{}">View DevStaR image</a>
        </div>
    '''.format(
        get_image_title(experiment, well),
        current, length,
        get_image_frame(experiment, well),
        scores,
        get_devstar_image_url(experiment, well)
    )
