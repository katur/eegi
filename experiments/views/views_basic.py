from django.conf import settings
from django.contrib.auth.decorators import permission_required
from django.shortcuts import redirect, render, get_object_or_404

from experiments.helpers.data_entry import parse_batch_data_entry_gdoc
from experiments.models import Experiment, ExperimentPlate
from experiments.forms import (
    FilterExperimentWellsForm, FilterExperimentPlatesForm,
    AddExperimentPlateForm, ChangeExperimentPlatesForm,
    process_ChangeExperimentPlatesForm_data,
)
from utils.http import http_response_ok
from utils.pagination import get_paginated


EXPERIMENT_PLATES_PER_PAGE = 30
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


def experiment_plate(request, pk):
    """Render the page to see a particular experiment plate."""
    experiment_plate = get_object_or_404(ExperimentPlate, pk=pk)

    context = {
        'experiment_plate': experiment_plate,
        'experiments': experiment_plate.get_experiment_wells(),

        # Default to thumbnail images
        'mode': request.GET.get('mode', 'thumbnail'),
    }

    return render(request, 'experiment_plate.html', context)


def vertical_experiment_plates(request, pks):
    """Render the page to view experiment plate images vertically."""
    pks = pks.split(',')

    # NOTE: To preserve order, do not do .filter(pk__in=pks)
    plates = [get_object_or_404(ExperimentPlate, pk=pk) for pk in pks]

    context = {
        'experiment_plates': plates,

        # Default to thumbnail
        'mode': request.GET.get('mode', 'thumbnail')
    }

    return render(request, 'vertical_experiment_plates.html', context)


def find_experiment_wells(request):
    """Render the page to find experiment wells based on filters."""
    experiments = None
    display_experiments = None

    if request.GET:
        form = FilterExperimentWellsForm(request.GET)

        if form.is_valid():
            experiments = form.cleaned_data['experiments']
            display_experiments = get_paginated(request, experiments,
                                                EXPERIMENT_WELLS_PER_PAGE)

    else:
        form = FilterExperimentWellsForm()

    context = {
        'form': form,
        'experiments': experiments,
        'display_experiments': display_experiments,
    }

    return render(request, 'find_experiment_wells.html', context)


def find_experiment_plates(request, context=None):
    """Render the page to find experiment plates based on filters."""
    experiment_plates = None
    display_plates = None

    if request.GET:
        form = FilterExperimentPlatesForm(request.GET)

        if form.is_valid():
            experiment_plates = form.cleaned_data['experiment_plates']
            display_plates = get_paginated(request, experiment_plates,
                                           EXPERIMENT_PLATES_PER_PAGE)

    else:
        form = FilterExperimentPlatesForm()

    context = {
        'form': form,
        'experiment_plates': experiment_plates,
        'display_plates': display_plates,
    }

    return render(request, 'find_experiment_plates.html', context)


@permission_required(['experiments.add_experiment',
                      'experiments.add_experimentplate'])
def add_experiment_plate(request):
    """
    Render the page to add a new experiment plate.

    Adding an experiment plate also adds the corresponding experiment wells.
    """
    if request.POST:
        form = AddExperimentPlateForm(request.POST)

        if form.is_valid():
            data = form.cleaned_data
            experiment_plate_id = data['experiment_plate_id']

            ExperimentPlate.create_plate_and_wells(
                experiment_plate_id, data['screen_stage'], data['date'],
                data['temperature'], data['worm_strain'],
                data['library_plate'], is_junk=data['is_junk'],
                plate_comment=data['plate_comment'])

            return redirect('experiment_plate_url', experiment_plate_id)

    else:
        form = AddExperimentPlateForm()

    context = {
        'form': form,
    }

    return render(request, 'add_experiment_plate.html', context)


@permission_required(['experiments.add_experiment',
                      'experiments.add_experimentplate'])
def add_experiment_plates_gdoc(request):
    """
    Render the page to import Google Doc experiment data.
    """
    errors = []
    success = False
    count = 0

    if request.POST:
        try:
            count = parse_batch_data_entry_gdoc()
            success = True

        except Exception as e:
            errors.append(e)

    context = {
        'batch_data_entry_gdoc_url': settings.BATCH_DATA_ENTRY_GDOC_URL,
        'batch_data_entry_gdoc_name': settings.BATCH_DATA_ENTRY_GDOC_NAME,
        'errors': errors,
        'success': success,
        'count': count,
    }

    return render(request, 'add_experiment_plates_gdoc.html', context)


@permission_required(['experiments.change_experiment',
                      'experiments.change_experimentplate'])
def change_experiment_plates(request, pks):
    """
    Render the page to update bulk experiment plates.

    When bulk updating experiment plates, the corresponding experiment
    wells might change too.
    """
    split_pks = pks.split(',')
    experiment_plates = ExperimentPlate.objects.filter(pk__in=split_pks)
    display_plates = get_paginated(request, experiment_plates,
                                   EXPERIMENT_PLATES_PER_PAGE)

    if request.POST:
        form = ChangeExperimentPlatesForm(request.POST)

        if form.is_valid():
            for plate in experiment_plates:
                process_ChangeExperimentPlatesForm_data(
                    plate, form.cleaned_data)

            return redirect('change_experiment_plates_url', pks)

    else:
        form = ChangeExperimentPlatesForm()

    context = {
        'experiment_plates': experiment_plates,
        'display_plates': display_plates,
        'form': form,
    }

    return render(request, 'change_experiment_plates.html', context)
