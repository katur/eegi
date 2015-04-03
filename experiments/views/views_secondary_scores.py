from __future__ import division
from collections import OrderedDict

from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404

from experiments.forms import SecondaryScoresForm
from experiments.helpers.scores import (passes_sup_positive_criteria,
                                        get_average_weight)
from experiments.models import ManualScore
from library.helpers import get_organized_library_wells
from worms.models import WormStrain


def secondary_scores_search(request):
    '''
    Render page to search for secondary scores for a particular mutant.

    '''
    error = ''
    if request.method == 'POST':
        form = SecondaryScoresForm(request.POST)
        if form.is_valid():
            try:
                data = form.cleaned_data
                query = data['query']
                screen = data['screen']

                if screen != 'ENH' and screen != 'SUP':
                    raise Exception('screen must be ENH or SUP')

                if query == 'N2':
                    raise Exception('query must be a mutant, not N2')

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

                return redirect(secondary_scores, worm, temperature)

            except Exception as e:
                error = e.message

    else:
        form = SecondaryScoresForm(initial={'screen': 'SUP'})

    context = {
        'form': form,
        'error': error,
    }

    return render(request, 'secondary_scores_search.html', context)


def secondary_scores(request, worm, temperature):
    '''
    Render page displaying the secondary scores for a particular worm,
    sorted with positives on top.

    '''
    worm = get_object_or_404(WormStrain, pk=worm)
    screen = worm.get_screen_category(temperature)

    # Store LibraryWells in a fast lookup dictionary.
    #
    # TODO: I do this because I have not figured out how to easily translate
    # raw SQL output including a JOIN into multiple Django objects, in order
    # to execute a single query between Experiment (plate-level),
    # ManualScore (well-level), and LibraryWell (well-level).
    # Should figure out a way to do this faster.
    w = get_organized_library_wells(2)

    # Fetch the non-junk secondary scores for this worm and temperature,
    # prefetching corresponding ScoreCode and LibraryPlate for faster lookup
    # later on.
    scores = (ManualScore.objects.filter(
              Q(experiment__worm_strain=worm),
              Q(experiment__screen_level=2),
              Q(experiment__is_junk=False),
              Q(experiment__temperature=temperature))
              .select_related('score_code')
              .prefetch_related('experiment__library_plate')
              .order_by('-experiment__id', 'well'))

    # Organize the scores into s[library_well][experiment] = score
    s = {}
    for score in scores:
        experiment = score.experiment
        library_well = w[experiment.library_plate][score.well]

        if library_well not in s:
            s[library_well] = OrderedDict()

        if (experiment not in s[library_well] or
                s[library_well][experiment].get_relevance_per_replicate() <
                score.get_relevance_per_replicate()):
            s[library_well][experiment] = score

    num_passes = 0
    num_experiment_columns = 0
    for well, expts in s.iteritems():
        scores = expts.values()
        well.avg = get_average_weight(scores)

        well.passes_criteria = passes_sup_positive_criteria(scores)
        if well.passes_criteria:
            num_passes += 1
        if len(expts) > num_experiment_columns:
            num_experiment_columns = len(expts)

    s = OrderedDict(sorted(s.iteritems(),
                           key=lambda x: (x[0].passes_criteria, x[0].avg),
                           reverse=True))

    context = {
        'worm': worm,
        'temp': temperature,
        'screen': screen,
        's': s,
        'num_wells': len(s),
        'num_passes': num_passes,
        'num_experiment_columns': num_experiment_columns,
    }

    return render(request, 'secondary_scores.html', context)
