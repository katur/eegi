import string

from eegi.settings import IMG_PATH, THUMBNAIL_PATH, DEVSTAR_PATH
from utils.well_tile_conversion import well_to_tile


def get_image_url(experiment, well):
    """Get the url of an experiment image.

    Accepts an Experiment object, and well as a string.

    """
    tile = well_to_tile(well)
    url = '/'.join((IMG_PATH, str(experiment.id), tile))
    return url


def get_thumbnail_url(experiment, well):
    """Get the url of an experiment thumbnail image.

    Accepts an Experiment object, and well as a string.

    """
    tile = well_to_tile(well)
    url = '/'.join((THUMBNAIL_PATH, str(experiment.id), tile))
    url = string.replace(url, 'bmp', 'jpg')
    return url


def get_devstar_image_url(experiment, well):
    """Get the url of a DevStaR output image.

    Accepts an Experiment object, and well as a string.

    """
    tile = well_to_tile(well)
    url = '/'.join((DEVSTAR_PATH, str(experiment.id), tile))
    url = string.replace(url, '.bmp', 'res.png')
    return url
