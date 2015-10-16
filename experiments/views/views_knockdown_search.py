from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.shortcuts import render, redirect

from clones.models import Clone, CloneTarget, Gene
from experiments.forms import (
    DoubleKnockdownForm, MutantKnockdownForm, RNAiKnockdownForm)
from experiments.views import (
    double_knockdown, mutant_knockdown, rnai_knockdown)
from worms.models import WormStrain


def get_worm_and_temperature(mutant_query, screen):
    if screen != 'ENH' and screen != 'SUP':
        raise Exception('screen must be ENH or SUP')

    if screen == 'ENH':
        worms = (WormStrain.objects
                 .filter(Q(gene=mutant_query) |
                         Q(allele=mutant_query) |
                         Q(id=mutant_query))
                 .exclude(permissive_temperature__isnull=True))
    else:
        worms = (WormStrain.objects
                 .filter(Q(gene=mutant_query) |
                         Q(allele=mutant_query) |
                         Q(id=mutant_query))
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

    return (worm, temperature)


def get_clone_ids(rnai_query):
    try:
        clone = Clone.objects.get(pk=rnai_query)
        clone_ids = [clone.id]

    except ObjectDoesNotExist:
        genes = (Gene.objects
                 .filter(Q(id=rnai_query) |
                         Q(cosmid_id=rnai_query) |
                         Q(locus=rnai_query)))

        if len(genes) == 0:
            raise Exception('No clone or gene matches target.')
        elif len(genes) > 1:
            raise Exception('Multiple genes match target.')
        else:
            gene = genes[0]

        clone_ids = (CloneTarget.objects.filter(gene=gene)
                     .values_list('clone_id', flat=True))

    return ','.join(clone_id for clone_id in clone_ids)


def double_knockdown_search(request):
    """Render the page to search for a double knockdown."""
    error = ''
    if request.method == 'POST':
        form = DoubleKnockdownForm(request.POST)
        if form.is_valid():
            try:
                data = form.cleaned_data
                mutant_query = data['mutant_query']
                rnai_query = data['rnai_query']
                screen = data['screen']

                if mutant_query == 'N2':
                    raise Exception('mutant query cannot be N2')

                if rnai_query == 'L4440':
                    raise Exception('rnai query cannot be L4440')

                worm, temperature = get_worm_and_temperature(mutant_query,
                                                             screen)
                clones = get_clone_ids(rnai_query)

                return redirect(double_knockdown, worm, clones, temperature)

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
    if request.method == 'POST' and 'rnai' in request.POST:
        mutant_form = MutantKnockdownForm(prefix='mutant',
                                          initial={'screen': 'SUP'})
        rnai_form = RNAiKnockdownForm(request.POST, prefix='rnai')
        if rnai_form.is_valid():
            try:
                data = rnai_form.cleaned_data
                rnai_query = data['rnai_query']
                temperature = data['temperature']

                clones = get_clone_ids(rnai_query)

                if temperature:
                    return redirect(rnai_knockdown, clones, temperature)
                else:
                    return redirect(rnai_knockdown, clones)

            except Exception as e:
                error = e.message

    elif request.method == 'POST' and 'mutant' in request.POST:
        rnai_form = RNAiKnockdownForm(prefix='rnai')
        mutant_form = MutantKnockdownForm(request.POST, prefix='mutant')
        if mutant_form.is_valid():
            try:
                data = mutant_form.cleaned_data
                mutant_query = data['mutant_query']
                screen = data['screen']

                worm, temperature = get_worm_and_temperature(mutant_query,
                                                             screen)

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
