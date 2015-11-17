from collections import OrderedDict

from django.shortcuts import render, get_object_or_404

from clones.models import Clone
from experiments.models import Experiment
from library.models import LibraryStock
from worms.models import WormStrain


def rnai_knockdown(request, clones, temperature=None):
    """Render the page showing knockdown by RNAi only."""
    n2 = get_object_or_404(WormStrain, pk='N2')
    clones = Clone.objects.filter(pk__in=clones.split(','))

    # data = {clone: {library_stock: [experiments]}}
    data = OrderedDict()

    for clone in clones:
        experiments = Experiment.objects.filter(
            is_junk=False, worm_strain=n2,
            library_stock__intended_clone=clone)

        if temperature:
            experiments = experiments.filter(plate__temperature=temperature)

        # No need to prefetch manual scores, since N2 not manually scored
        experiments = (
            experiments
            .select_related('library_stock', 'plate')
            .prefetch_related('devstarscore_set')
            .order_by('-library_stock__plate__screen_stage',
                      'library_stock', '-plate__date', 'plate__id', 'well'))

        data_by_well = OrderedDict()

        for experiment in experiments:
            library_stock = experiment.library_stock
            if library_stock not in data_by_well:
                data_by_well[library_stock] = []
            data_by_well[library_stock].append(experiment)

        if data_by_well:
            data[clone] = data_by_well

    context = {
        'worm': n2,
        'clones': clones,
        'temperature': temperature,
        'data': data,
    }

    return render(request, 'rnai_knockdown.html', context)


def mutant_knockdown(request, worm, temperature):
    """Render the page showing knockdown by mutation only."""
    worm = get_object_or_404(WormStrain, pk=worm)
    l4440 = get_object_or_404(Clone, pk='L4440')

    experiments = (
        Experiment.objects
        .filter(is_junk=False, worm_strain=worm,
                library_stock__intended_clone=l4440,
                plate__temperature=temperature)
        .order_by('-plate__date', 'library_stock', 'plate__id', 'well'))

    # data = {date: [experiments]}
    data = OrderedDict()

    for experiment in experiments:
        date = experiment.plate.date
        if date not in data:
            data[date] = []
        data[date].append(experiment)

    context = {
        'worm': worm,
        'clone': l4440,
        'temperature': temperature,
        'data': data,
    }

    return render(request, 'mutant_knockdown.html', context)


def double_knockdown(request, worm, clones, temperature):
    """Render the page showing knockdown by both mutation and RNAi."""
    n2 = get_object_or_404(WormStrain, pk='N2')
    worm = get_object_or_404(WormStrain, pk=worm)
    l4440 = get_object_or_404(Clone, pk='L4440')
    clones = Clone.objects.filter(pk__in=clones.split(','))

    # data = {clone: {
    #   library_stock: {
    #       date: {
    #           'mutant_rnai': [exp_well, exp_well, ...],
    #           'n2_rnai': [exp_well, exp_well, ...],
    #           'mutant_l4440': [(exp, well), (exp, well), ...],
    #           'n2_l4440': [(exp, well), (exp, well), ...]}}}}

    data = OrderedDict()

    for clone in clones:
        data_per_clone = OrderedDict()

        library_stocks = (LibraryStock.objects.filter(intended_clone=clone)
                          .order_by('-plate__screen_stage', 'id'))

        for library_stock in library_stocks:
            data_per_well = OrderedDict()

            dates = (
                Experiment.objects
                .filter(is_junk=False, worm_strain=worm,
                        plate__temperature=temperature,
                        library_stock=library_stock)
                .order_by('-plate__date')
                .values_list('plate__date', flat=True)
                .distinct())

            for date in dates:
                data_per_date = {}

                # The part common to all queries
                common = (Experiment.objects
                          .filter(is_junk=False, plate__date=date)
                          .select_related('plate')
                          .prefetch_related('devstarscore_set'))

                # Add double knockdowns
                data_per_date['mutant_rnai'] = (common.filter(
                    worm_strain=worm, plate__temperature=temperature,
                    library_stock=library_stock)
                    .prefetch_related('manualscore_set'))

                # Add mutant + L4440 controls
                data_per_date['mutant_l4440'] = common.filter(
                    worm_strain=worm, plate__temperature=temperature,
                    library_stock__intended_clone=l4440)

                # TODO: N2 controls should be limited to closest temperature

                # Add N2 + RNAi controls
                data_per_date['n2_rnai'] = common.filter(
                    worm_strain=n2, library_stock=library_stock)

                # Add N2 + L4440 controls
                data_per_date['n2_l4440'] = common.filter(
                    worm_strain=n2, library_stock__intended_clone=l4440)

                data_per_well[date] = data_per_date

            if data_per_well:
                data_per_clone[library_stock] = data_per_well

        data[clone] = data_per_clone

    context = {
        'worm': worm,
        'clones': clones,
        'temperature': temperature,
        'data': data,
    }

    return render(request, 'double_knockdown.html', context)
