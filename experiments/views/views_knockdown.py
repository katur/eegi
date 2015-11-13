from collections import OrderedDict

from django.shortcuts import render, get_object_or_404

from clones.models import Clone
from experiments.models import ExperimentPlate, ExperimentWell
from library.models import LibraryWell, LibraryPlate
from worms.models import WormStrain


def rnai_knockdown(request, clones, temperature=None):
    """Render the page showing knockdown by RNAi only."""
    n2 = get_object_or_404(WormStrain, pk='N2')
    clones = Clone.objects.filter(pk__in=clones.split(','))

    # data = {clone: {library_well: [experiments]}}
    data = OrderedDict()

    for clone in clones:
        experiment_wells = (ExperimentWell.objects
                            .filter(is_junk=False, worm_strain=n2,
                                    library_well__intended_clone=clone))

        if temperature:
            experiment_wells = experiment_wells.filter(
                experiment_plate__temperature=temperature)

        experiment_wells = (
            experiment_wells
            .select_related('worm_strain', 'library_well__intended_clone',
                            'experiment_plate', 'library_well__library_plate')
            .prefetch_related('manualscore_set', 'devstarscore_set')
            .order_by('-library_well__library_plate__screen_stage',
                      'library_well', '-experiment_plate__date', 'id'))

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

    experiment_wells = (ExperimentWell.objects
                        .filter(is_junk=False, worm_strain=worm,
                                library_well__intended_clone=l4440,
                                experiment_plate__temperature=temperature)
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
    l4440_plate = get_object_or_404(LibraryPlate, pk='L4440')
    clones = Clone.objects.filter(pk__in=clones.split(','))

    # data[clone][[(library_well, date)] = {
    #       'mutant_rnai': [(exp, well), (exp, well), ...],
    #       'n2_rnai': [(exp, well), (exp, well), ...],
    #       'mutant_l4440': [(exp, well), (exp, well), ...],
    #       'n2_l4440': [(exp, well), (exp, well), ...]
    # })
    data = OrderedDict()

    for clone in clones:
        library_wells = (LibraryWell.objects
                         .filter(intended_clone=clone,
                                 plate__screen_stage__gt=0)
                         .order_by('-plate__screen_stage', 'id'))

        data_by_well = OrderedDict()

        for library_well in library_wells:
            dates = (ExperimentPlate.objects
                     .filter(is_junk=False)
                     .filter(worm_strain=worm)
                     .filter(temperature=temperature)
                     .filter(library_plate=library_well.plate)
                     .order_by('-date')
                     .values('date').distinct())

            for date in dates:
                # Create dictionary to hold info for this
                # library_well+date combo
                d = {}

                # Add mutant + RNAi experiments
                mutant_rnai_exps = (
                    ExperimentPlate.objects.filter(
                        is_junk=False, worm_strain=worm,
                        temperature=temperature,
                        date=date['date'],
                        library_plate=library_well.plate))

                d['mutant_rnai'] = (
                    [(e, library_well) for e in mutant_rnai_exps])

                # Add N2 + RNAi experiments
                n2_rnai_exps = (
                    ExperimentPlate.objects.filter(
                        is_junk=False, worm_strain=n2,
                        date=date['date'],
                        library_plate=library_well.plate))

                d['n2_rnai'] = [(e, library_well) for e in n2_rnai_exps]

                # For Primary, use separate L4440 plate
                if library_well.plate.screen_stage == 1:
                    mutant_l4440_exps = (
                        ExperimentPlate.objects.filter(
                            is_junk=False, worm_strain=worm,
                            temperature=temperature,
                            date=date['date'],
                            library_plate=l4440_plate))

                    n2_l4440_exps = (
                        ExperimentPlate.objects.filter(
                            is_junk=False, worm_strain=n2,
                            date=date['date'],
                            library_plate=l4440_plate))

                # For SUP Secondary, use L4440 wells from same plates as RNAi
                # TODO: will be different for ENH secondary
                # TODO: formally decide that these are the applicable controls,
                #   as opposed to all from the date.
                else:
                    mutant_l4440_exps = mutant_rnai_exps
                    n2_l4440_exps = n2_rnai_exps

                # Add mutant + L4440 experiments
                d['mutant_l4440'] = []
                for e in mutant_l4440_exps:
                    for w in e.library_plate.get_l4440_wells():
                        d['mutant_l4440'].append((e, w))

                # Add N2 + L4440 experiments
                d['n2_l4440'] = []
                for e in n2_l4440_exps:
                    for w in e.library_plate.get_l4440_wells():
                        d['n2_l4440'].append((e, w))

                # Add the finished dictionary for this date
                data_by_well[(library_well, date['date'])] = d

        # Add the finished dictionary for this library well
        if data_by_well:
            data[clone] = data_by_well

    context = {
        'worm': worm,
        'clones': clones,
        'temperature': temperature,
        'data': data,
    }

    return render(request, 'double_knockdown.html', context)
