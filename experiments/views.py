from django.shortcuts import render, redirect, get_object_or_404
from experiments.models import Experiment
from experiments.forms import ExperimentFilterForm


def experiments(request, context=None):
    errors = []
    experiments = None

    if 'exact_id' in request.GET:
        try:
            id = int(request.GET['exact_id'])
            if (id > 0):
                return redirect(experiment, id=id)
            else:
                errors.append('Experiment id must be positive')

        except ValueError:
            errors.append('Experiment id must be a positive integer')

    if request.method == 'GET' and len(request.GET):
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
                            'is_junk', 'comment')
                )

    else:
        form = ExperimentFilterForm()

    context = {
        'experiments': experiments,
        'errors': errors,
        'form': form,
    }
    return render(request, 'experiments.html', context)


def experiment(request, id):
    experiment = get_object_or_404(Experiment, pk=id)
    context = {'experiment': experiment}
    return render(request, 'experiment.html', context)
