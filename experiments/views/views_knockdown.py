from collections import OrderedDict
from copy import copy
from django.shortcuts import render, get_object_or_404

from clones.models import Clone
from experiments.models import Experiment
from library.models import LibraryStock
from worms.models import WormStrain

from clones.helpers.queries import get_l4440
from worms.helpers.queries import get_n2
from experiments.helpers.queries import get_closest_temperature, get_all_dates
from utils.http import build_url


def rnai_knockdown(request, clones, temperature=None):
    """Render the page showing knockdown by RNAi only."""
    # data = {clone: {library_stock: [exp, exp, ...]}}
    data = OrderedDict()

    n2 = get_n2()
    clones = Clone.objects.filter(pk__in=clones.split(','))

    for clone in clones:
        filters = {
            'is_junk': False,
            'worm_strain': n2,
            'library_stock__intended_clone': clone,
        }

        if temperature:
            filters['plate__temperature'] = temperature

        # Do not join manual scores, since N2 not manually scored
        experiments = (Experiment.objects.filter(**filters)
                       .select_related('library_stock', 'plate')
                       .prefetch_related('devstarscore_set')
                       .order_by('-library_stock__plate__screen_stage',
                                 'library_stock', '-plate__date', 'id'))

        data_by_well = OrderedDict()

        for experiment in experiments:
            library_stock = experiment.library_stock
            if library_stock not in data_by_well:
                data_by_well[library_stock] = []
            data_by_well[library_stock].append(experiment)

        if data_by_well:
            data[clone] = data_by_well

    context = {
        'n2': n2,
        'clones': clones,
        'temperature': temperature,
        'data': data,
    }

    return render(request, 'rnai_knockdown.html', context)


def mutant_knockdown(request, mutant, temperature):
    """Render the page showing knockdown by mutation only."""
    # data = {date: {
    #   'link_to_all': url,
    #   'experiments': [experiments]}}
    data = OrderedDict()

    l4440 = get_l4440()
    mutant = get_object_or_404(WormStrain, pk=mutant)

    filters = {
        'is_junk': False,
        'worm_strain': mutant,
        'library_stock__intended_clone': l4440,
        'plate__temperature': temperature,
    }

    # Do not join manual scores, since L4440 not manually scored
    experiments = (Experiment.objects.filter(**filters)
                   .select_related('library_stock', 'plate')
                   .prefetch_related('devstarscore_set')
                   .order_by('-plate__date', 'id'))

    for experiment in experiments:
        date = experiment.plate.date
        if date not in data:
            data[date] = {'experiments': []}
        data[date]['experiments'].append(experiment)

        inner_filters = copy(filters)
        inner_filters['plate__date'] = date

        data[date]['link_to_all'] = build_url(
            'experiments.views.experiments', get=inner_filters)

    context = {
        'mutant': mutant,
        'l4440': l4440,
        'temperature': temperature,
        'data': data,
    }

    return render(request, 'mutant_knockdown.html', context)


def double_knockdown(request, mutant, clones, temperature):
    """Render the page showing knockdown by both mutation and RNAi."""
    # data = {clone: {library_stock: {date: {
    #   'mutant_rnai': {
    #       'link_to_all': url,
    #       'experiments': [exp, exp, ...]},
    #   'n2_rnai': {
    #       'link_to_all': url,
    #       'experiments': [exp, exp, ...]},
    #   'mutant_l4440': {
    #       'link_to_all': url,
    #       'experiments': [exp, exp, ...]},
    #   'n2_l4440': {
    #       'link_to_all': url,
    #       'experiments': [exp, exp, ...]}}}}}

    data = OrderedDict()

    n2 = get_n2()
    l4440 = get_l4440()
    mutant = get_object_or_404(WormStrain, pk=mutant)
    clones = Clone.objects.filter(pk__in=clones.split(','))

    for clone in clones:
        data_per_clone = OrderedDict()

        library_stocks = (LibraryStock.objects.filter(intended_clone=clone)
                          .order_by('-plate__screen_stage', 'id'))

        for library_stock in library_stocks:
            data_per_well = OrderedDict()

            date_filters = {
                'is_junk': False,
                'worm_strain': mutant,
                'library_stock': library_stock,
                'plate__temperature': temperature,
            }
            dates = get_all_dates(date_filters)

            for date in dates:
                # Add double knockdowns
                filters = {
                    'is_junk': False,
                    'plate__date': date,
                    'worm_strain': mutant,
                    'library_stock': library_stock,
                    'plate__temperature': temperature,
                }
                mutant_rnai = _create_inner_dictionary(
                    filters, join_manual=True)

                # Add mutant + L4440 controls
                filters = {
                    'is_junk': False,
                    'plate__date': date,
                    'worm_strain': mutant,
                    'library_stock__intended_clone': l4440,
                    'plate__temperature': temperature,
                }
                mutant_l4440 = _create_inner_dictionary(filters)

                # Add N2 + RNAi controls
                filters = {
                    'is_junk': False,
                    'plate__date': date,
                    'worm_strain': n2,
                    'library_stock': library_stock,
                }

                filters['plate__temperature'] = get_closest_temperature(
                    temperature, filters)

                n2_rnai = _create_inner_dictionary(filters)

                # Add N2 + L4440 controls
                filters = {
                    'is_junk': False,
                    'plate__date': date,
                    'worm_strain': n2,
                    'library_stock__intended_clone': l4440,
                }

                filters['plate__temperature'] = get_closest_temperature(
                    temperature, filters)

                n2_l4440 = _create_inner_dictionary(filters)

                data_per_well[date] = {
                    'mutant_rnai': mutant_rnai,
                    'mutant_l4440': mutant_l4440,
                    'n2_rnai': n2_rnai,
                    'n2_l4440': n2_l4440,
                }

            if data_per_well:
                data_per_clone[library_stock] = data_per_well

        data[clone] = data_per_clone

    context = {
        'mutant': mutant,
        'clones': clones,
        'temperature': temperature,
        'data': data,
    }

    return render(request, 'double_knockdown.html', context)


def _create_inner_dictionary(filters, join_devstar=True, join_manual=False,
                             order_by=None, limit=None):
    experiments = Experiment.objects.filter(**filters).select_related('plate')
    if join_devstar:
        experiments = experiments.prefetch_related('devstarscore_set')

    if join_manual:
        experiments = experiments.prefetch_related('manualscore_set')

    d = {}
    d['experiments'] = experiments
    d['link_to_all'] = build_url('experiments.views.experiments',
                                 get=filters)
    return d
