from django.shortcuts import render, redirect

from experiments.forms import (
    DoubleKnockdownForm, MutantKnockdownForm, RNAiKnockdownForm)
from experiments.views import (
    double_knockdown, mutant_knockdown, rnai_knockdown)


def double_knockdown_search(request):
    """Render the page to search for a double knockdown."""
    if request.method == 'POST':
        form = DoubleKnockdownForm(request.POST)

        if form.is_valid():
            data = form.cleaned_data
            worm = data['worm']
            temperature = data['temperature']
            clones = ','.join(clone.id for clone in data['rnai_query'])
            return redirect(double_knockdown, worm, clones, temperature)

    else:
        form = DoubleKnockdownForm(initial={'screen': 'SUP'})

    context = {
        'form': form,
    }

    return render(request, 'double_knockdown_search.html', context)


def single_knockdown_search(request):
    """Render the page to search for a single knockdown."""
    empty_rnai_form = RNAiKnockdownForm(prefix='rnai')
    empty_mutant_form = MutantKnockdownForm(prefix='mutant',
                                            initial={'screen': 'SUP'})

    if request.method == 'POST' and 'rnai' in request.POST:
        rnai_form = RNAiKnockdownForm(request.POST, prefix='rnai')

        if rnai_form.is_valid():
            data = rnai_form.cleaned_data
            temperature = data['temperature']
            clones = ','.join(clone.id for clone in data['rnai_query'])

            if temperature:
                return redirect(rnai_knockdown, clones, temperature)
            else:
                return redirect(rnai_knockdown, clones)

        mutant_form = empty_mutant_form

    elif request.method == 'POST' and 'mutant' in request.POST:
        mutant_form = MutantKnockdownForm(request.POST, prefix='mutant')

        if mutant_form.is_valid():
            data = mutant_form.cleaned_data
            worm = data['worm']
            temperature = data['temperature']
            return redirect(mutant_knockdown, worm, temperature)

        rnai_form = empty_rnai_form

    else:
        mutant_form = empty_mutant_form
        rnai_form = empty_rnai_form

    context = {
        'rnai_form': rnai_form,
        'mutant_form': mutant_form,
    }

    return render(request, 'single_knockdown_search.html', context)
