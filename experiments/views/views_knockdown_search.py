from django.shortcuts import render, redirect

from clones.helpers.queries import get_clones
from experiments.forms import (
    DoubleKnockdownForm, MutantKnockdownForm, RNAiKnockdownForm)
from experiments.views import (
    double_knockdown, mutant_knockdown, rnai_knockdown)
from worms.helpers.queries import get_worm_and_temperature


def get_clone_ids(query):
    """Get a comma-separated string listing the clones that match a query term.

    The clone could match the query term either in the clone's name, or
    in the wormbase id, cosmid id, or locus of any of its targets.

    """
    clones = get_clones(query)
    if not clones:
        return None
    return ','.join(clone.id for clone in clones)


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

                worm_and_temp = get_worm_and_temperature(mutant_query, screen)
                if not worm_and_temp:
                    raise Exception('No mutant match')
                worm, temperature = worm_and_temp

                clones = get_clone_ids(rnai_query)
                if not clones:
                    raise Exception('No RNAi match')

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
                if not clones:
                    raise Exception('No RNAi match')

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

                worm_and_temp = get_worm_and_temperature(mutant_query, screen)
                if not worm_and_temp:
                    raise Exception('No mutant match')
                worm, temperature = worm_and_temp

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
