import os

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, get_object_or_404

from eegi.settings import MATERIALS_DIR
from experiments.models import Experiment, ExperimentPlate
from experiments.forms import ExperimentFilterForm, ExperimentPlateFilterForm
from utils.well_tile_conversion import tile_to_well
from utils.http import http_response_ok


EXPERIMENT_PLATES_PER_PAGE = 100
EXPERIMENTS_PER_PAGE = 10
DEVSTAR_SCORING_CATEGORIES_DIR = MATERIALS_DIR + '/devstar_scoring/categories'
DEVSTAR_SCORING_IMAGES_PER_PAGE = 10


def experiment(request, pk):
    """Render the page to see a particular experiment well."""
    experiment = get_object_or_404(Experiment, pk=pk)

    devstar_url = experiment.get_image_url(mode='devstar')
    devstar_available = http_response_ok(devstar_url)

    context = {
        'experiment': experiment,
        'devstar_available': devstar_available,

        # Default to full-size images
        'mode': request.GET.get('mode', 'big')
    }

    return render(request, 'experiment.html', context)


def experiment_plate(request, pk):
    """Render the page to see a particular experiment plate."""
    experiment_plate = get_object_or_404(ExperimentPlate, pk=pk)

    context = {
        'experiment_plate': experiment_plate,
        'experiments': experiment_plate.get_experiments(),

        # Default to thumbnail images
        'mode': request.GET.get('mode', 'thumbnail'),
    }

    return render(request, 'experiment_plate.html', context)


def experiment_plates_vertical(request, pks):
    """Render the page to view experiment plate images vertically."""
    pks = pks.split(',')

    # NOTE: To preserve order, do not do .filter(id__in=ids)
    plates = [get_object_or_404(ExperimentPlate, pk=pk) for pk in pks]

    context = {
        'experiment_plates': plates,

        # Default to thumbnail
        'mode': request.GET.get('mode', 'thumbnail')
    }

    return render(request, 'experiment_plates_vertical.html', context)


def experiment_plates(request, context=None):
    """Render the page to search for experiment plates."""
    experiment_plates = None
    display_plates = None

    if request.GET:
        form = ExperimentPlateFilterForm(request.GET)
        if form.is_valid():
            experiment_plates = form.cleaned_data['experiment_plates']

            paginator = Paginator(experiment_plates,
                                  EXPERIMENT_PLATES_PER_PAGE)
            page = request.GET.get('page')

            try:
                display_plates = paginator.page(page)
            except PageNotAnInteger:
                display_plates = paginator.page(1)
            except EmptyPage:
                display_plates = paginator.page(paginator.num_pages)

    else:
        form = ExperimentPlateFilterForm()

    context = {
        'form': form,
        'experiment_plates': experiment_plates,
        'display_plates': display_plates,
    }

    return render(request, 'experiment_plates.html', context)


def experiments(request):
    """Render the page showing experiments based on filters."""
    form = ExperimentFilterForm(request.GET)
    if form.is_valid():
        experiments = form.cleaned_data['experiments']

    paginator = Paginator(experiments, EXPERIMENTS_PER_PAGE)
    page = request.GET.get('page')

    try:
        display_expts = paginator.page(page)
    except PageNotAnInteger:
        display_expts = paginator.page(1)
    except EmptyPage:
        display_expts = paginator.page(paginator.num_pages)

    context = {
        'experiments': experiments,
        'display_experiments': display_expts,
    }

    return render(request, 'experiments.html', context)
def devstar_scoring_categories(request):
    categories = os.listdir(DEVSTAR_SCORING_CATEGORIES_DIR)

    context = {
        'categories': categories,
    }

    return render(request, 'devstar_scoring_categories.html', context)


def devstar_scoring_category(request, category):
    tuples = []

    f = open(DEVSTAR_SCORING_CATEGORIES_DIR + '/' + category, 'r')

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

    paginator = Paginator(tuples, DEVSTAR_SCORING_IMAGES_PER_PAGE)
    page = request.GET.get('page')

    try:
        display_tuples = paginator.page(page)
    except PageNotAnInteger:
        display_tuples = paginator.page(1)
    except EmptyPage:
        display_tuples = paginator.page(paginator.num_pages)

    context = {
        'category': category,
        'tuples': tuples,
        'display_tuples': display_tuples,
    }

    return render(request, 'devstar_scoring_category.html', context)
