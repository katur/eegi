from django.shortcuts import render, redirect, get_object_or_404
from experiments.models import Experiment


def experiments(request, context=None):
    errors = []
    if 'exact_id' in request.GET:
        try:
            id = int(request.GET['exact_id'])
            if (id > 0):
                return redirect(experiment, id=id)
            else:
                errors.append('Experiment id must be positive')

        except ValueError:
            errors.append('Experiment id must be a positive integer')

    filters = {
        'id__gte': request.GET.get('min_id', None),
        'id__lte': request.GET.get('max_id', None),
        'worm_strain': request.GET.get('worm_strain', None),
        'worm_strain__gene': request.GET.get('gene', None),
        'worm_strain__allele': request.GET.get('allele', None),
        'library_plate': request.GET.get('library_plate', None),
        'temperature': request.GET.get('temperature', None),
        'permissive': request.GET.get('permissive', None),
        'restrictive': request.GET.get('restrictive', None),
        'date': request.GET.get('date', None),
        'is_junk': request.GET.get('is_junk', None),
    }

    for k, v in filters.items():
        if not v:
            del filters[k]

    if filters:
        experiments = (
            Experiment.objects.filter(**filters)
            .values('id', 'worm_strain', 'worm_strain__genotype',
                    'library_plate', 'temperature', 'date', 'is_junk',
                    'comment')
        )

    else:
        experiments = None

    context = {'experiments': experiments, 'errors': errors}
    return render(request, 'experiments.html', context)


def experiment(request, id):
    experiment = get_object_or_404(Experiment, pk=id)
    context = {'experiment': experiment}
    return render(request, 'experiment.html', context)
