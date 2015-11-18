import os
from collections import OrderedDict

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, get_object_or_404

from eegi.settings import MATERIALS_DIR
from experiments.models import Experiment, ExperimentPlate
from experiments.forms import ExperimentPlateFilterForm
from library.models import LibraryStock, LibraryPlate
from utils.well_tile_conversion import tile_to_well
from utils.http import http_response_ok
from worms.models import WormStrain


EXPERIMENT_PLATES_PER_PAGE = 100


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
        'experiments': (experiment_plate.experiment_set
                        .select_related(
                            'library_stock',
                            'library_stock__intended_clone')
                        .order_by('well')),

        # Default to thumbnail images
        'mode': request.GET.get('mode', 'thumbnail'),
    }

    return render(request, 'experiment_plate.html', context)


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


def experiment_plates_grid(request, screen_stage):
    """Render the page showing all experiments as a grid."""
    worms = WormStrain.objects.all()
    experiments = (ExperimentPlate.objects
                   .filter(screen_stage=screen_stage, is_junk=False)
                   .select_related('library_plate', 'worm_strain'))

    plate_pks = (experiments.order_by('library_plate')
                 .values_list('library_plate', flat=True)
                 .distinct())
    plates = LibraryPlate.objects.filter(pk__in=plate_pks)

    header = []
    for worm in worms:
        if worm.permissive_temperature:
            header.append((worm, worm.permissive_temperature))
        if worm.restrictive_temperature:
            header.append((worm, worm.restrictive_temperature))

    e = OrderedDict()
    for plate in plates:
        e[plate] = OrderedDict()
        for worm in worms:
            if worm not in e[plate]:
                e[plate][worm] = OrderedDict()
            if worm.permissive_temperature:
                e[plate][worm][worm.permissive_temperature] = []
            if worm.restrictive_temperature:
                e[plate][worm][worm.restrictive_temperature] = []

    for experiment in experiments:
        plate = experiment.library_plate
        worm = experiment.worm_strain
        temp = experiment.temperature

        if temp in e[plate][worm]:
            e[plate][worm][temp].append(experiment)

    context = {
        'screen_stage': screen_stage,
        'header': header,
        'e': e,
    }

    return render(request, 'experiment_plates_grid.html', context)


def experiment_plates_vertical(request, ids):
    """Render the page to view vertical images of one or more experiments."""
    ids = ids.split(',')
    experiments = []
    for id in ids:
        experiment = get_object_or_404(ExperimentPlate, pk=id)
        experiment.library_stocks = LibraryStock.objects.filter(
            plate=experiment.library_plate).order_by('well')
        experiments.append(experiment)

    context = {
        'experiments': experiments,

        # Default to thumbnail
        'mode': request.GET.get('mode', 'thumbnail')
    }

    return render(request, 'experiment_plates_vertical.html', context)


DEVSTAR_SCORING_CATEGORIES_DIR = MATERIALS_DIR + '/devstar_scoring/categories'
DEVSTAR_SCORING_IMAGES_PER_PAGE = 10


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
        tile = tile.split('.bmp')[0]
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
