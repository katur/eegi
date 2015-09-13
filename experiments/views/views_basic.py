from collections import OrderedDict

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.urlresolvers import reverse
from django.shortcuts import render, get_object_or_404

from experiments.models import Experiment
from experiments.forms import ExperimentFilterForm
from library.models import LibraryWell, LibraryPlate
from worms.models import WormStrain


EXPERIMENTS_PER_PAGE = 100


def experiments(request, context=None):
    """Render the page to search for experiments."""
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
                    link_to_vertical = reverse('experiment_plate_vertical_url',
                                               args=[id_string])

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

    return render(request, 'experiments.html', context)


def experiment_grid(request, screen_stage):
    """Render the page showing all experiments as a grid."""
    worms = WormStrain.objects.all()
    plates = LibraryPlate.objects.filter(screen_stage=screen_stage)
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

    return render(request, 'experiment_grid.html', context)


def experiment_plate(request, id):
    """Render the page to see the images and information for a particular
    experiment.
    """
    experiment = get_object_or_404(Experiment, pk=id)
    experiment.worm_strain.url = experiment.worm_strain.get_url(request)

    library_wells = LibraryWell.objects.filter(
        plate=experiment.library_plate).order_by('well')

    for library_well in library_wells:
        library_well.row = library_well.get_row()

    context = {
        'experiment': experiment,
        'library_wells': library_wells,
    }

    return render(request, 'experiment_plate.html', context)


def experiment_plate_vertical(request, ids):
    """Render the page to view the images of experiments vertically."""
    ids = ids.split(',')
    experiments = []
    for id in ids:
        experiment = get_object_or_404(Experiment, pk=id)
        experiment.library_wells = LibraryWell.objects.filter(
            plate=experiment.library_plate).order_by('well')
        experiments.append(experiment)

    context = {
        'experiments': experiments,
    }

    return render(request, 'experiment_plate_vertical.html', context)


def experiment_well(request, id, well):
    """Render the page to see the image and information for a particular
    experiment well.
    """
    experiment = get_object_or_404(Experiment, pk=id)
    experiment.worm_strain.url = experiment.worm_strain.get_url(request)

    library_well = LibraryWell.objects.filter(
        plate=experiment.library_plate).filter(well=well)[0]

    context = {
        'experiment': experiment,
        'well': well,
        'library_well': library_well,
    }

    return render(request, 'experiment_well.html', context)
