from django.shortcuts import render, redirect, get_object_or_404
from experiments.models import Experiment


def experiments(request, context=None):
    if 'id' in request.GET:
        try:
            id = int(request.GET['id'])
            if (id < 1):
                error_message = 'Experiment id must be positive'
            else:
                return redirect(experiment, id=id)

        except ValueError:
            error_message = 'Experiment id must be a positive integer'

        context = {'id_error_message': error_message}
        return render(request, 'experiments.html', context)

    elif 'start' in request.GET and 'end' in request.GET:
        try:
            start = int(request.GET['start'])
            end = int(request.GET['end'])

            if (start < 1) or (end < 1):
                error_message = ('Start and end experiment ids '
                                 'must be positive')
            elif start > end:
                error_message = ('Start must be greater than '
                                 'or equal to end')
            elif (end - start) > 1001:
                error_message = ('Range must be 1000 items or less')
            else:
                return redirect(experiment_range, start=start, end=end)

        except ValueError:
            error_message = ('Start and end experiment ids '
                             'must be positive integers')

        context = {'range_error_message': error_message}
        return render(request, 'experiments.html', context)

    else:
        return render(request, 'experiments.html', context)


def experiment(request, id):
    experiment = get_object_or_404(Experiment, pk=id)
    context = {'experiment': experiment}
    return render(request, 'experiment.html', context)


def experiment_range(request, start, end):
    experiments = (
        Experiment.objects
        .filter(id__gte=start).filter(id__lte=end)
        .values('id', 'worm_strain', 'worm_strain__genotype',
                'library_plate', 'temperature', 'date', 'is_junk',
                'comment')
    )

    context = {'experiments': experiments, 'start': start, 'end': end}
    return render(request, 'experiments_range.html', context)
