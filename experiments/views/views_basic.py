from collections import OrderedDict

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.shortcuts import render, get_object_or_404

from experiments.models import Experiment
from experiments.forms import ExperimentFilterForm
from library.models import LibraryWell, LibraryPlate
from utils.http import http_response_ok
from worms.models import WormStrain


EXPERIMENTS_PER_PAGE = 100


def experiment_plates(request, context=None):
    """Render the page to search for experiment plates."""
    total_results = None
    display_experiments = None
    link_to_vertical = None

    if len(request.GET):
        form = ExperimentFilterForm(request.GET)
        if form.is_valid():
            filters = form.cleaned_data
            for k, v in filters.items():
                # Retain 'False' as a legitimate filter
                if v is False:
                    continue

                # Ditch empty strings and None as filters
                if not v:
                    del filters[k]

            if filters:
                experiments = (
                    Experiment.objects.filter(**filters)
                    .values('id', 'worm_strain', 'worm_strain__genotype',
                            'library_plate', 'temperature', 'date',
                            'is_junk', 'comment'))
                total_results = len(experiments)

                if total_results > 0:
                    ids = experiments.values_list('id')
                    ids = (str(i[0]) for i in ids)
                    id_string = ','.join(ids)
                    link_to_vertical = reverse(
                        'experiment_plates_vertical_url', args=[id_string])

                paginator = Paginator(experiments, EXPERIMENTS_PER_PAGE)
                page = request.GET.get('page')
                try:
                    display_experiments = paginator.page(page)
                except PageNotAnInteger:
                    display_experiments = paginator.page(1)
                except EmptyPage:
                    display_experiments = paginator.page(paginator.num_pages)

    else:
        form = ExperimentFilterForm()

    context = {
        'form': form,
        'total_results': total_results,
        'display_experiments': display_experiments,
        'link_to_vertical': link_to_vertical,
    }

    return render(request, 'experiment_plates.html', context)


def experiment_plates_grid(request, screen_stage):
    """Render the page showing all experiments as a grid."""
    worms = WormStrain.objects.all()
    plates = LibraryPlate.objects.filter(
        Q(screen_stage=screen_stage) | Q(pk='L4440'))
    experiments = (Experiment.objects
                   .filter(screen_stage=screen_stage, is_junk=False)
                   .prefetch_related('library_plate', 'worm_strain'))

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
        experiment = get_object_or_404(Experiment, pk=id)
        experiment.library_wells = LibraryWell.objects.filter(
            plate=experiment.library_plate).order_by('well')
        experiments.append(experiment)

    context = {
        'experiments': experiments,

        # Default to thumbnail
        'mode': request.GET.get('mode', 'thumbnail')
    }

    return render(request, 'experiment_plates_vertical.html', context)


def experiment_plate(request, id):
    """Render the page to see a particular experiment plate."""
    experiment = get_object_or_404(Experiment, pk=id)
    experiment.worm_strain.url = experiment.worm_strain.get_url(request)

    library_wells = LibraryWell.objects.filter(
        plate=experiment.library_plate).order_by('well')

    # Add row attribute in order to use regroup template tag
    for library_well in library_wells:
        library_well.row = library_well.get_row()

    context = {
        'experiment': experiment,
        'library_wells': library_wells,

        # Default to thumbnail
        'mode': request.GET.get('mode', 'thumbnail'),
    }

    return render(request, 'experiment_plate.html', context)


def experiment_well(request, id, well):
    """Render the page to see a particular experiment well."""
    experiment = get_object_or_404(Experiment, pk=id)
    experiment.worm_strain.url = experiment.worm_strain.get_url(request)

    library_well = LibraryWell.objects.filter(
        plate=experiment.library_plate).filter(well=well)[0]

    devstar_url = experiment.get_devstar_image_url(well)
    devstar_available = http_response_ok(devstar_url)

    context = {
        'experiment': experiment,
        'well': well,
        'library_well': library_well,
        'devstar_available': devstar_available,

        # Default to full-size images
        'mode': request.GET.get('mode', 'big')
    }

    return render(request, 'experiment_well.html', context)
