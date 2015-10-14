from collections import OrderedDict

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404

from clones.models import Clone
from experiments.forms import (
    DoubleKnockdownForm, RNAiKnockdownForm, MutantKnockdownForm)
from experiments.models import Experiment
from library.models import LibraryWell, LibraryPlate
from worms.models import WormStrain


def double_knockdown(request, worm, clone, temperature):
    """Render the double knockdown page."""
    worm = get_object_or_404(WormStrain, pk=worm)
    clone = get_object_or_404(Clone, pk=clone)
    n2 = get_object_or_404(WormStrain, pk='N2')
    l4440_plate = get_object_or_404(LibraryPlate, pk='L4440')
    library_wells = (LibraryWell.objects
                     .filter(intended_clone=clone,
                             plate__screen_stage__gt=0)
                     .order_by('-plate__screen_stage'))

    # data[(library_well, date)] = {
    #       'mutant_rnai': [(exp, well), (exp, well), ...],
    #       'n2_rnai': [(exp, well), (exp, well), ...],
    #       'mutant_l4440': [(exp, well), (exp, well), ...],
    #       'n2_l4440': [(exp, well), (exp, well), ...]
    # })
    data = OrderedDict()

    for library_well in library_wells:
        dates = (Experiment.objects
                 .filter(is_junk=False)
                 .filter(worm_strain=worm)
                 .filter(temperature=temperature)
                 .filter(library_plate=library_well.plate)
                 .order_by('-date')
                 .values('date').distinct())

        for date in dates:
            # Create dictionary to hold info for this library_well+date combo
            d = {}

            # Add mutant + RNAi experiments
            mutant_rnai_exps = (
                Experiment.objects.filter(
                    Q(is_junk=False),
                    Q(worm_strain=worm),
                    Q(temperature=temperature),
                    Q(date=date['date']),
                    Q(library_plate=library_well.plate)))

            d['mutant_rnai'] = [(e, library_well) for e in mutant_rnai_exps]

            # Add N2 + RNAi experiments
            n2_rnai_exps = (
                Experiment.objects.filter(
                    Q(is_junk=False),
                    Q(worm_strain=n2),
                    Q(date=date['date']),
                    Q(library_plate=library_well.plate)))

            d['n2_rnai'] = [(e, library_well) for e in n2_rnai_exps]

            # For Primary, use separate L4440 plate
            if library_well.plate.screen_stage == 1:
                mutant_l4440_exps = (
                    Experiment.objects.filter(
                        Q(is_junk=False),
                        Q(worm_strain=worm),
                        Q(temperature=temperature),
                        Q(date=date['date']),
                        Q(library_plate=l4440_plate)))

                n2_l4440_exps = (
                    Experiment.objects.filter(
                        Q(is_junk=False),
                        Q(worm_strain=n2),
                        Q(date=date['date']),
                        Q(library_plate=l4440_plate)))

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

            # Add the finished dictionary to overall data
            data[(library_well, date['date'])] = d

    context = {
        'worm': worm,
        'clone': clone,
        'temperature': temperature,
        'data': data,
    }

    return render(request, 'double_knockdown.html', context)


def mutant_knockdown(request, worm, temperature):
    """Render the mutant knockdown page."""
    worm = get_object_or_404(WormStrain, pk=worm)
    l4440 = get_object_or_404(Clone, pk='L4440')

    # data[date] = [(exp, well), (exp, well), ... ]
    data = {}

    plates = (LibraryWell.objects.filter(intended_clone=l4440)
              .order_by('plate').values('plate').distinct())

    experiments = (Experiment.objects
                   .filter(is_junk=False,
                           worm_strain=worm,
                           temperature=temperature,
                           library_plate__in=plates))

    for experiment in experiments:
        l4440_wells = experiment.library_plate.get_l4440_wells()
        if not l4440_wells:
            continue

        date = experiment.date
        if date not in data:
            data[date] = []

        for l4440_well in l4440_wells:
            data[date].append((experiment, l4440_well))

    sorted_data = OrderedDict()
    for key in sorted(data.keys(), reverse=True):
        sorted_data[key] = data[key]

    context = {
        'worm': worm,
        'clone': l4440,
        'temperature': temperature,
        'data': sorted_data,
    }

    return render(request, 'mutant_knockdown.html', context)


def rnai_knockdown(request, clone, temperature=None):
    """Render the RNAi knockdown page."""
    n2 = get_object_or_404(WormStrain, pk='N2')
    clone = get_object_or_404(Clone, pk=clone)
    library_wells = (LibraryWell.objects
                     .filter(intended_clone=clone,
                             plate__screen_stage__gt=0)
                     .order_by('-plate__screen_stage', 'id'))

    # data[library_well] = [(exp, well), (exp, well), ...]
    data = OrderedDict()

    for library_well in library_wells:
        experiments = Experiment.objects.filter(
            is_junk=False, worm_strain=n2,
            library_plate=library_well.plate)

        if temperature:
            experiments = experiments.filter(temperature=temperature)

        experiments = experiments.order_by('-date', '-id')

        if experiments:
            data[library_well] = [(e, library_well) for e in experiments]

    context = {
        'worm': n2,
        'clone': clone,
        'temperature': temperature,
        'data': data,
    }

    return render(request, 'rnai_knockdown.html', context)


def double_knockdown_search(request):
    """Render the page to search for a double knockdown."""
    error = ''
    if request.method == 'POST':
        form = DoubleKnockdownForm(request.POST)
        if form.is_valid():
            try:
                data = form.cleaned_data
                query = data['query']
                target = data['target']
                screen = data['screen']

                if screen != 'ENH' and screen != 'SUP':
                    raise Exception('screen must be ENH or SUP')

                if query == 'N2':
                    raise Exception('query must be a mutant, not N2')

                if target == 'L4440':
                    raise Exception('target must be an RNAi clone, not L4440')

                if screen == 'ENH':
                    worms = (WormStrain.objects
                             .filter(Q(gene=query) | Q(allele=query) |
                                     Q(id=query))
                             .exclude(permissive_temperature__isnull=True))
                else:
                    worms = (WormStrain.objects
                             .filter(Q(gene=query) | Q(allele=query) |
                                     Q(id=query))
                             .exclude(restrictive_temperature__isnull=True))

                if len(worms) == 0:
                    raise Exception('No worm strain matches query.')
                elif len(worms) > 1:
                    raise Exception('Multiple worm strains match query.')
                else:
                    worm = worms[0]

                if screen == 'ENH':
                    temperature = worm.permissive_temperature
                else:
                    temperature = worm.restrictive_temperature

                try:
                    clone = Clone.objects.get(pk=target)
                except ObjectDoesNotExist:
                    raise ObjectDoesNotExist('No clone matches target.')

                return redirect(double_knockdown, worm, clone, temperature)

            except Exception as e:
                error = e.message

    else:
        form = DoubleKnockdownForm(initial={'screen': 'SUP'})

    context = {
        'form': form,
        'error': error,
    }

    return render(request, 'double_knockdown_search.html', context)


def single_knockdown_search(request):
    """Render the page to search for a single knockdown."""
    error = ''
    if request.method == 'POST':
        if 'rnai' in request.POST:
            mutant_form = MutantKnockdownForm(prefix='mutant',
                                              initial={'screen': 'SUP'})
            rnai_form = RNAiKnockdownForm(request.POST, prefix='rnai')
            if rnai_form.is_valid():
                try:
                    data = rnai_form.cleaned_data
                    target = data['target']
                    temperature = data['temperature']

                    try:
                        clone = Clone.objects.get(pk=target)
                    except ObjectDoesNotExist:
                        raise ObjectDoesNotExist('No clone matches target.')

                    if temperature:
                        return redirect(rnai_knockdown, clone, temperature)
                    else:
                        return redirect(rnai_knockdown, clone)

                except Exception as e:
                    error = e.message

        elif 'mutant' in request.POST:
            rnai_form = RNAiKnockdownForm(prefix='rnai')
            mutant_form = MutantKnockdownForm(request.POST, prefix='mutant')
            if mutant_form.is_valid():
                try:
                    data = mutant_form.cleaned_data
                    query = data['query']
                    screen = data['screen']

                    if screen != 'ENH' and screen != 'SUP':
                        raise Exception('screen must be ENH or SUP')

                    if screen == 'ENH':
                        worms = (WormStrain.objects
                                 .filter(Q(gene=query) | Q(allele=query) |
                                         Q(id=query))
                                 .exclude(permissive_temperature__isnull=True))
                    else:
                        worms = (WormStrain.objects
                                 .filter(Q(gene=query) | Q(allele=query) |
                                         Q(id=query))
                                 .exclude(
                                     restrictive_temperature__isnull=True))

                    if len(worms) == 0:
                        raise Exception('No worm strain matches query.')
                    elif len(worms) > 1:
                        raise Exception('Multiple worm strains match query.')
                    else:
                        worm = worms[0]

                    if screen == 'ENH':
                        temperature = worm.permissive_temperature
                    else:
                        temperature = worm.restrictive_temperature

                    return redirect(mutant_knockdown, worm, temperature)

                except Exception as e:
                    error = e.message

    else:
        rnai_form = RNAiKnockdownForm(prefix='rnai')
        mutant_form = MutantKnockdownForm(prefix='mutant',
                                          initial={'screen': 'SUP'})

    context = {
        'rnai_form': rnai_form,
        'mutant_form': mutant_form,
        'error': error,
    }

    return render(request, 'single_knockdown_search.html', context)
