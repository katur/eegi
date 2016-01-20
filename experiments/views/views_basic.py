from django.shortcuts import render, get_object_or_404

from experiments.models import Experiment, ExperimentPlate
from experiments.forms import (ExperimentWellFilterForm,
                               ExperimentPlateFilterForm)
from utils.http import http_response_ok
from utils.pagination import get_paginated


EXPERIMENT_PLATES_PER_PAGE = 100
EXPERIMENT_WELLS_PER_PAGE = 10


def experiment_well(request, pk):
    """Render the page to see a particular experiment well."""
    experiment = get_object_or_404(Experiment, pk=pk)

    devstar_url = experiment.get_image_url(mode='devstar')
    devstar_available = http_response_ok(devstar_url)

    if (request.POST.get('toggle-junk') and
            request.user.has_perm('experiments.change_experiment')):
        experiment.toggle_junk()

    context = {
        'experiment': experiment,
        'devstar_available': devstar_available,

        # Default to full-size images
        'mode': request.GET.get('mode', 'big')
    }

    return render(request, 'experiment_well.html', context)


def experiment_wells(request):
    """Render the page showing experiments based on filters."""
    experiments = None
    display_experiments = None

    if request.GET:
        form = ExperimentWellFilterForm(request.GET)

        if form.is_valid():
            experiments = form.cleaned_data['experiments']
            display_experiments = get_paginated(request, experiments,
                                                EXPERIMENT_WELLS_PER_PAGE)

    else:
        form = ExperimentWellFilterForm()

    context = {
        'form': form,
        'experiments': experiments,
        'display_experiments': display_experiments,
    }

    return render(request, 'experiment_wells.html', context)


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


def experiment_plates(request, context=None):
    """Render the page to search for experiment plates."""
    experiment_plates = None
    display_plates = None

    if request.GET:
        form = ExperimentPlateFilterForm(request.GET)

        if form.is_valid():
            experiment_plates = form.cleaned_data['experiment_plates']
            display_plates = get_paginated(request, experiment_plates,
                                           EXPERIMENT_PLATES_PER_PAGE)

    else:
        form = ExperimentPlateFilterForm()

    context = {
        'form': form,
        'experiment_plates': experiment_plates,
        'display_plates': display_plates,
    }

    return render(request, 'experiment_plates.html', context)


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
