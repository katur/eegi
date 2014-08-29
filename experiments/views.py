from django.shortcuts import render
from experiments.models import Experiment


def experiments(request, start, end):
    experiments = (
        Experiment.objects
        .filter(id__gte=start).filter(id__lt=end)
        .values('id', 'worm_strain', 'worm_strain__genotype',
                'library_plate', 'temperature', 'date', 'is_junk',
                'comment')
    )

    context = {'experiments': experiments}
    return render(request, 'experiments.html', context)
