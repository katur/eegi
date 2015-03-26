from __future__ import division
from collections import OrderedDict

from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404

from experiments.models import ManualScore
from experiments.forms import SecondaryScoresForm
from library.models import LibraryWell
from worms.models import WormStrain


def secondary_scores_search(request):
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
    worm = get_object_or_404(WormStrain, pk=worm)
    screen = worm.get_screen_category(temperature)

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

    library_wells = (LibraryWell.objects.filter(
                     Q(plate__in=scores.values('experiment__library_plate')
                       .distinct())))

    # Store LibraryWells in a dictionary for fast correlation to scores.
    # w[library_plate_name][well_name] = LibraryWell object
    #
    # TODO: I do this because I have not figured out how to easily translate
    # raw SQL output including a JOIN into multiple Django objects, in order
    # to execute a single query between Experiment (plate-level),
    # ManualScore (well-level), and LibraryWell (well-level).
    # Should figure out a way to do this faster.
    w = {}
    for library_well in library_wells:
        plate = library_well.plate_id
        well = library_well.well
        if plate not in w:
            w[plate] = {}
        w[plate][well] = library_well

    # Organize the scores into s[library_well][experiment] = score
    s = {}
    for score in scores:
        experiment = score.experiment
        library_well = w[experiment.library_plate_id][score.well]

        if library_well not in s:
            s[library_well] = OrderedDict()

        weight = score.get_score_weight()

        if (experiment not in s[library_well] or
                s[library_well][experiment].get_score_weight() < weight):
            s[library_well][experiment] = score

    def passes_criteria(scores):
        total = len(scores)
        present = 0
        maybe = 0
        for score in scores:
            if score.is_strong() or score.is_medium():
                present += 1
            elif score.is_weak():
                maybe += 1

        if ((present / total) >= .375 or
                ((present + maybe) / total) >= .5):
            return True

        return False

    num_passes = 0
    num_experiment_columns = 0
    for well, expts in s.iteritems():
        scores = expts.values()

        # TODO: below will be better once fix weights to reflect the 0-3 scale
        # well.avg = sum(x.get_score_weight() for x in scores) / float(len(expts))

        total_weight = 0
        for score in scores:
            weight = score.get_score_weight()
            if weight >= 2:
                weight -= 1
            if weight < 0:
                weight = 0
            total_weight += weight
        well.avg = total_weight / float(len(expts))

        well.passes_criteria = passes_criteria(scores)
        if well.passes_criteria:
            num_passes += 1
        if len(expts) > num_experiment_columns:
            num_experiment_columns = len(expts)

    # Sort by highest average
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
