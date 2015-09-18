from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404

from clones.models import Clone
from experiments.forms import (DoubleKnockdownForm, RNAiKnockdownForm,
                               MutantKnockdownForm)
from experiments.models import Experiment
from library.models import LibraryWell, LibraryPlate
from worms.models import WormStrain


def double_knockdown(request, worm, clone, temperature):
    """Render the page displaying the images of a double knockdown search."""
    worm = get_object_or_404(WormStrain, pk=worm)
    clone = get_object_or_404(Clone, pk=clone)
    n2 = get_object_or_404(WormStrain, pk='N2')
    l4440_plate = get_object_or_404(LibraryPlate, pk='L4440')
    library_wells = (LibraryWell.objects
                     .filter(intended_clone=clone,
                             plate__screen_stage__gt=0)
                     .order_by('-plate__screen_stage'))

    # Each element of 'data' is in format (as needed by the template):
    #   (library_well, date, {
    #       'mutant_rnai': [experiments],
    #       'n2_rnai': [experiments],
    #       'mutant_l4440': [experiments],
    #       'n2_l4440': [experiments]
    #   })
    data = []

    for library_well in library_wells:
        dates = (Experiment.objects
                 .filter(is_junk=False)
                 .filter(worm_strain=worm)
                 .filter(temperature=temperature)
                 .filter(library_plate=library_well.plate)
                 .order_by('-date')
                 .values('date').distinct())

        for date in dates:
            mutant_rnai = (Experiment.objects.filter(
                           Q(is_junk=False),
                           Q(worm_strain=worm),
                           Q(temperature=temperature),
                           Q(date=date['date']),
                           Q(library_plate=library_well.plate)))

            n2_rnai = (Experiment.objects.filter(
                       Q(is_junk=False),
                       Q(worm_strain=n2),
                       Q(date=date['date']),
                       Q(library_plate=library_well.plate)))

            # For primary, L4440 is an entire separate plate
            if library_well.plate.screen_stage == 1:
                mutant_l4440 = (Experiment.objects.filter(
                                Q(is_junk=False),
                                Q(worm_strain=worm),
                                Q(temperature=temperature),
                                Q(date=date['date']),
                                Q(library_plate=l4440_plate)))

                n2_l4440 = (Experiment.objects.filter(
                            Q(is_junk=False),
                            Q(worm_strain=n2),
                            Q(date=date['date']),
                            Q(library_plate=l4440_plate)))

            # For secondary, L4440 wells are in the same plates as the RNAi.
            else:
                mutant_l4440 = mutant_rnai
                n2_l4440 = n2_rnai

            data.append((library_well, date['date'], {
                'mutant_rnai': mutant_rnai,
                'n2_rnai': n2_rnai,
                'mutant_l4440': mutant_l4440,
                'n2_l4440': n2_l4440,
            }))

    context = {
        'worm': worm,
        'clone': clone,
        'temperature': temperature,
        'data': data,
    }

    return render(request, 'double_knockdown.html', context)


def rnai_knockdown(request, clone, temperature):
    """Render the page displaying control worms (N2) with an RNAi knockdown."""
    clone = get_object_or_404(Clone, pk=clone)
    n2 = get_object_or_404(WormStrain, pk='N2')
    library_wells = (LibraryWell.objects
                     .filter(intended_clone=clone,
                             plate__screen_stage__gt=0)
                     .order_by('-plate__screen_stage'))

    # Each element of 'data' is in format (as needed by the template):
    #   (library_well, (experiments_ordered_by_id))
    data = []
    for library_well in library_wells:
        experiments = (Experiment.objects
                       .filter(is_junk=False, worm_strain=n2,
                               temperature=temperature,
                               library_plate=library_well.plate)
                       .order_by('-date', 'id'))
        if experiments:
            data.append((library_well, experiments))

    context = {
        'clone': clone,
        'temperature': temperature,
        'data': data,
    }

    return render(request, 'rnai_knockdown.html', context)


def mutant_knockdown(request, worm, temperature):
    """Render the page displaying control bacteria (L4440) with a mutant
    knockdown."""
    worm = get_object_or_404(WormStrain, pk=worm)
    plates = LibraryPlate.objects.filter(screen_stage__gt=0)

    # Each element of 'data' is in format (as needed by the template):
    #   (experiment, l4440_wells)
    data = {}
    for plate in plates:
        l4440_wells = plate.get_l4440_wells()
        if l4440_wells:
            experiments = (Experiment.objects
                           .filter(is_junk=False, worm_strain=worm,
                                   temperature=temperature,
                                   library_plate=plate)
                           .order_by('date', 'id'))

            for experiment in experiments:
                experiment.l4440_wells = l4440_wells
                if experiment.date not in data:
                    data[experiment.date] = []
                data[experiment.date].append(experiment)

    ordered_data = []
    for date in sorted(data):
        for experiment in data[date]:
            ordered_data.append(experiment)

    context = {
        'worm': worm,
        'temperature': temperature,
        'data': ordered_data,
    }

    return render(request, 'mutant_knockdown.html', context)


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

                    return redirect(rnai_knockdown, clone, temperature)

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
