from __future__ import division
from collections import OrderedDict

from django.shortcuts import render, redirect, get_object_or_404

from experiments.forms import SecondaryScoresForm
from experiments.helpers.criteria import (
    passes_sup_positive_percentage_criteria,
    passes_sup_positive_count_criteria,
    passes_sup_stringent_criteria)
from experiments.helpers.scores import (get_average_score_weight,
                                        get_organized_scores_specific_worm)
from worms.models import WormStrain


def secondary_scores(request, worm, temperature):
    """Render the page displaying the secondary scores for a particular worm,
    sorted with positives on top.
    """
    worm = get_object_or_404(WormStrain, pk=worm)
    screen = worm.get_screen_category(temperature)

    # TODO: Try to speed this up with a single query between Experiment
    # (plate-level), ManualScore (well-level), and LibraryWell (well-level).
    s = get_organized_scores_specific_worm(worm, screen, screen_stage=2,
                                           most_relevant_only=True)

    num_passes_stringent = 0
    num_passes_percentage = 0
    num_passes_count = 0
    num_experiment_columns = 0

    for well, expts in s.iteritems():
        scores = expts.values()
        well.avg = get_average_score_weight(scores)

        well.passes_stringent = passes_sup_stringent_criteria(scores)
        well.passes_percentage = passes_sup_positive_percentage_criteria(
            scores)
        well.passes_count = passes_sup_positive_count_criteria(scores)

        if well.passes_stringent:
            num_passes_stringent += 1

        if well.passes_percentage:
            num_passes_percentage += 1

        if well.passes_count:
            num_passes_count += 1

        if len(expts) > num_experiment_columns:
            num_experiment_columns = len(expts)

    s = OrderedDict(sorted(s.iteritems(),
                           key=lambda x: (
                               x[0].passes_stringent,
                               x[0].passes_percentage,
                               x[0].passes_count,
                               x[0].avg),
                           reverse=True))

    context = {
        'worm': worm,
        'temp': temperature,
        'screen': screen,
        's': s,
        'num_wells': len(s),
        'num_passes_percentage': num_passes_percentage,
        'num_passes_count': num_passes_count,
        'num_passes_stringent': num_passes_stringent,
        'num_experiment_columns': num_experiment_columns,
    }

    return render(request, 'secondary_scores.html', context)


def secondary_scores_search(request):
    """Render the page to search for secondar scores for a mutant/screen combo.
    """
    if request.method == 'POST':
        form = SecondaryScoresForm(request.POST)

        if form.is_valid():
            data = form.cleaned_data
            worm = data['worm']
            temperature = data['temperature']
            return redirect(secondary_scores, worm, temperature)

    else:
        form = SecondaryScoresForm(initial={'screen': 'SUP'})

    context = {
        'form': form,
    }

    return render(request, 'secondary_scores_search.html', context)
