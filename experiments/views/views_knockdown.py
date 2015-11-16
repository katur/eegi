from collections import OrderedDict

from django.shortcuts import render, get_object_or_404

from clones.models import Clone
from experiments.models import ExperimentWell
from library.models import LibraryWell
from worms.models import WormStrain


def rnai_knockdown(request, clones, temperature=None):
    """Render the page showing knockdown by RNAi only."""
    n2 = get_object_or_404(WormStrain, pk='N2')
    clones = Clone.objects.filter(pk__in=clones.split(','))

    # data = {clone: {library_well: [experiments]}}
    data = OrderedDict()

    for clone in clones:
        experiment_wells = (
            ExperimentWell.objects
            .filter(is_junk=False, worm_strain=n2,
                    library_well__intended_clone=clone))

        if temperature:
            experiment_wells = experiment_wells.filter(
                experiment_plate__temperature=temperature)

        experiment_wells = (
            experiment_wells
            .order_by('-library_well__plate__screen_stage', 'library_well',
                      '-experiment_plate__date', 'id'))

        data_by_well = OrderedDict()

        for e in experiment_wells:
            if e.library_well not in data_by_well:
                data_by_well[e.library_well] = []
            data_by_well[e.library_well].append(e)

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

    experiment_wells = (
        ExperimentWell.objects
        .filter(is_junk=False, worm_strain=worm,
                library_well__intended_clone=l4440,
                experiment_plate__temperature=temperature)
        # .select_related('experiment_plate')
        .order_by('-experiment_plate__date', 'library_well'))

    # data = {date: [experiments]}
    data = OrderedDict()

    for e in experiment_wells:
        date = e.experiment_plate.date
        if date not in data:
            data[date] = []

        data[date].append(e)

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
    #   library_well: {
    #       date: {
    #           'mutant_rnai': [exp_well, exp_well, ...],
    #           'n2_rnai': [exp_well, exp_well, ...],
    #           'mutant_l4440': [(exp, well), (exp, well), ...],
    #           'n2_l4440': [(exp, well), (exp, well), ...]}}}}

    data = OrderedDict()

    for clone in clones:
        data_per_clone = OrderedDict()

        library_wells = (LibraryWell.objects
                         .filter(intended_clone=clone)
                         .order_by('-plate__screen_stage', 'id'))

        for library_well in library_wells:
            data_per_well = OrderedDict()

            dates = (ExperimentWell.objects.filter(
                     is_junk=False, worm_strain=worm,
                     experiment_plate__temperature=temperature,
                     library_well=library_well)
                     .order_by('-experiment_plate__date')
                     .values_list('experiment_plate__date', flat=True)
                     .distinct())

            for date in dates:
                data_per_date = {}

                # Add double knockdowns
                data_per_date['mutant_rnai'] = (
                    ExperimentWell.objects.filter(
                        is_junk=False, worm_strain=worm,
                        experiment_plate__temperature=temperature,
                        library_well=library_well,
                        experiment_plate__date=date)
                    .order_by('id'))

                # Add mutant + L4440 controls
                data_per_date['mutant_l4440'] = (
                    ExperimentWell.objects.filter(
                        is_junk=False, worm_strain=worm,
                        experiment_plate__temperature=temperature,
                        library_well__intended_clone=l4440,
                        experiment_plate__date=date))

                # TODO: N2 controls should be limited to closest temperature

                # Add N2 + RNAi controls
                data_per_date['n2_rnai'] = (
                    ExperimentWell.objects.filter(
                        is_junk=False, worm_strain=n2,
                        library_well=library_well,
                        experiment_plate__date=date))

                # Add N2 + L4440 controls
                data_per_date['n2_l4440'] = (
                    ExperimentWell.objects.filter(
                        is_junk=False, worm_strain=n2,
                        library_well__intended_clone=l4440,
                        experiment_plate__date=date))

                data_per_well[date] = data_per_date

            if data_per_well:
                data_per_clone[library_well] = data_per_well

        data[clone] = data_per_clone

    context = {
        'worm': worm,
        'clones': clones,
        'temperature': temperature,
        'data': data,
    }

    return render(request, 'double_knockdown.html', context)
