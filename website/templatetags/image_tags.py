from django import template
from django.core.urlresolvers import reverse

register = template.Library()


@register.simple_tag
def get_image(experiment, well, settings):
    """Get an image.

    Returns the HTML img tag along with a surrounding div
    to preserve the aspect ratio while loading.

    """
    mode = settings.get('mode', None)
    if mode == 'thumbnail':
        image_url = experiment.get_thumbnail_url(well)
    elif mode == 'devstar':
        image_url = experiment.get_devstar_image_url(well)
    else:
        image_url = experiment.get_image_url(well)

    return '''
        <div class="image-frame">
          <img src="{}"/>
        </div>
    '''.format(image_url)


@register.simple_tag
def get_image_td(experiment, library_well, settings):
    """Get an HTML td element with an image and minimal information.

    "Minimal information" is a top bar identifying the well's position,
    and a lower caption identifying the clone name.
    Clicking the image links to more details about that experiment well.
    This function is meant for displaying a well in the context of
    displaying the entire plate.

    """

    well = library_well.well
    image = get_image(experiment, well, settings)
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
        '''.format(experiment.get_image_url(well))

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
        experiment.get_devstar_image_url(well)
    )
