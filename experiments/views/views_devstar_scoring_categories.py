import os

from django.shortcuts import render, get_object_or_404

from eegi.settings import BASE_DIR_DEVSTAR_SCORING_CATEGORIES
from experiments.models import Experiment
from utils.pagination import get_paginated
from utils.well_tile_conversion import tile_to_well

DEVSTAR_SCORING_IMAGES_PER_PAGE = 10


def devstar_scoring_categories(request):
    categories = os.listdir(BASE_DIR_DEVSTAR_SCORING_CATEGORIES)

    context = {
        'categories': categories,
    }

    return render(request, 'devstar_scoring_categories.html', context)


def devstar_scoring_category(request, category):
    tuples = []

    f = open(BASE_DIR_DEVSTAR_SCORING_CATEGORIES + '/' + category, 'r')

    rows = f.readlines()

    for row in rows:
        experiment_plate_id, tile = row.split('_')
        tile = tile.split('.')[0]
        well = tile_to_well(tile)
        experiment = get_object_or_404(Experiment,
                                       plate=experiment_plate_id,
                                       well=well)
        tuples.append((experiment, tile))

    f.close()

    display_tuples = get_paginated(request, tuples,
                                   DEVSTAR_SCORING_IMAGES_PER_PAGE)

    context = {
        'category': category,
        'tuples': tuples,
        'display_tuples': display_tuples,
    }

    return render(request, 'devstar_scoring_category.html', context)
