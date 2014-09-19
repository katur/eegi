from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from experiments.models import Experiment
from experiments.forms import ExperimentFilterForm
from utils.helpers import well_tile_conversion


def experiment(request, id):
    """
    Render the page to see information about a specific experiment.
    """
    experiment = get_object_or_404(Experiment, pk=id)
    plate_template = well_tile_conversion.get_96_grid()
    context = {'experiment': experiment, 'plate_template': plate_template}
    return render(request, 'experiment.html', context)


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
                return redirect(experiment, id=id)
            else:
                exact_id_errors.append('Experiment id must be positive')

        except ValueError:
            exact_id_errors.append('Experiment id must be a positive integer')

    total_results = None
    display_experiments = None

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
    }
    return render(request, 'experiments.html', context)
