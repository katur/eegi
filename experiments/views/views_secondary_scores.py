from __future__ import division
from collections import OrderedDict

from django.contrib.auth import get_user_model
from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404

from experiments.forms import SecondaryScoresForm

from experiments.helpers.criteria import (
    passes_sup_secondary_percent,
    passes_sup_secondary_count,
    passes_sup_secondary_stringent)

from experiments.helpers.scores import get_average_score_weight

from worms.models import WormStrain

NOAH_ID = 14
MALCOLM_ID = 22
KATHERINE_ID = 1
SHERLY_ID = 4
GISELLE_ID = 3

IDS = [NOAH_ID, MALCOLM_ID, SHERLY_ID]


def secondary_scores(request, worm, temperature, username=None):
    """
    Render the page to display secondary scores for a mutant/screen.

    Results show strongest positives on top.
    """
    worm = get_object_or_404(WormStrain, pk=worm)
    try:
        screen_type = worm.get_screen_type(temperature)
    except Exception:
        raise Http404

    if username:
        user = get_object_or_404(get_user_model(), username=username)
        data = worm.get_organized_scores(screen_type, screen_stage=2,
                                         most_relevant_only=True,
                                         scorer=user)
    else:
        data = worm.get_organized_scores(screen_type, screen_stage=2,
                                         most_relevant_only=True,
                                         scorer_id__in=IDS)

    num_passes_stringent = 0
    num_passes_percent = 0
    num_passes_count = 0
    num_experiment_columns = 0

    for stock, expts in data.iteritems():
        scores = expts.values()
        stock.avg = get_average_score_weight(scores)

        stock.passes_stringent = passes_sup_secondary_stringent(scores)
        stock.passes_percent = passes_sup_secondary_percent(
            scores)
        stock.passes_count = passes_sup_secondary_count(scores)

        if stock.passes_stringent:
            num_passes_stringent += 1

        if stock.passes_percent:
            num_passes_percent += 1

        if stock.passes_count:
            num_passes_count += 1

        if len(expts) > num_experiment_columns:
            num_experiment_columns = len(expts)

    data = OrderedDict(sorted(
        data.iteritems(),
        key=lambda x: (x[0].passes_stringent,
                       x[0].passes_percent,
                       x[0].passes_count,
                       x[0].avg),
        reverse=True))

    context = {
        'worm': worm,
        'screen_type': screen_type,
        'temperature': temperature,
        'data': data,
        'num_passes_percent': num_passes_percent,
        'num_passes_count': num_passes_count,
        'num_passes_stringent': num_passes_stringent,
        'num_experiment_columns': num_experiment_columns,
    }

    return render(request, 'secondary_scores.html', context)


def find_secondary_scores(request):
    """Render the page to find secondary scores for a mutant/screen."""
    if request.method == 'POST':
        form = SecondaryScoresForm(request.POST)

        if form.is_valid():
            data = form.cleaned_data
            worm = data['worm']
            temperature = data['temperature']
            return redirect(secondary_scores, worm.pk, temperature)

    else:
        form = SecondaryScoresForm(initial={'screen_type': 'SUP'})

    context = {
        'form': form,
    }

    return render(request, 'find_secondary_scores.html', context)
