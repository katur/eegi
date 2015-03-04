from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect, get_object_or_404

from experiments.models import Experiment
from experiments.forms import ExperimentFilterForm
from library.models import LibraryWell


def experiments(request, context=None):
    """
    Render the page to navigate all experiments. Provides navigation
    by either a specific experiment id, or various filters.
    """
    exact_id_errors = []

    if 'exact_id' in request.GET:
        try:
            id = int(request.GET['exact_id'])
            if (id > 0):
                return redirect(experiment_plate, id)
            else:
                exact_id_errors.append('Experiment id must be positive')

        except ValueError:
            exact_id_errors.append('Experiment id must be a positive integer')

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

                if total_results > 0 and total_results < 25:
                    ids = experiments.values_list('id')
                    ids = (str(i[0]) for i in ids)
                    id_string = ','.join(ids)
                    link_to_vertical = reverse('experiment_plate_vertical_url',
                                               args=[id_string])

                paginator = Paginator(experiments, 100)
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
        'exact_id_errors': exact_id_errors,
        'form': form,
        'total_results': total_results,
        'display_experiments': display_experiments,
        'link_to_vertical': link_to_vertical,
    }

    return render(request, 'experiments.html', context)


def experiment_plate(request, id):
    """
    Render the page to see information about a specific experiment.
    """
    experiment = get_object_or_404(Experiment, pk=id)
    experiment.worm_strain.url = experiment.worm_strain.get_url(request)

    wells = LibraryWell.objects.filter(
        plate=experiment.library_plate).order_by('well')

    for well in wells:
        well.row = well.get_row()

    context = {
        'experiment': experiment,
        'wells': wells,
    }

    return render(request, 'experiment_plate.html', context)


def experiment_plate_vertical(request, ids):
    """
    Render the page to see information about a specific experiment.
    """
    ids = ids.split(',')
    experiments = []
    for id in ids:
        experiment = get_object_or_404(Experiment, pk=id)
        experiment.wells = LibraryWell.objects.filter(
            plate=experiment.library_plate).order_by('well')
        experiments.append(experiment)

    context = {
        'experiments': experiments,
    }

    return render(request, 'experiment_plate_vertical.html', context)


def experiment_well(request, id, well):
    experiment = get_object_or_404(Experiment, pk=id)
    experiment.worm_strain.url = experiment.worm_strain.get_url(request)

    well = LibraryWell.objects.filter(
        plate=experiment.library_plate).filter(well=well)[0]
    experiment.score_summary = experiment.get_score_summary(well)

    context = {
        'experiment': experiment,
        'well': well,
    }

    return render(request, 'experiment_well.html', context)
