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

    '''
    SELECT * FROM ManualScore
    LEFT JOIN Experiment
        ON ManualScore.experiment_id = Experiment.id
    LEFT JOIN LibraryWell
        ON LibraryWell.plate_id = Experiment.library_plate_id
        AND LibraryWell.well = ManualScore.well
    WHERE Experiment.screen_level=2
        AND Experiment.is_junk=0
        AND Experiment.temperature=22.5
        AND Experiment.worm_strain_id="AR1"
    ORDER BY Experiment.id, ManualScore.well;
    '''

    '''
    SELECT Experiment.worm_strain_id, library_plate_id, ManualScore.well,
        intended_clone_id, AVG(score_code_id)
    FROM ManualScore
    LEFT JOIN Experiment
        ON ManualScore.experiment_id = Experiment.id
    LEFT JOIN LibraryWell
        ON LibraryWell.plate_id = Experiment.library_plate_id
        AND LibraryWell.well = ManualScore.well
    WHERE Experiment.screen_level=2
        AND Experiment.is_junk=0
        AND Experiment.temperature=22.5
        AND Experiment.worm_strain_id="EU554"
    GROUP BY library_plate_id, ManualScore.well;
    '''
    scores = (ManualScore.objects.filter(
              Q(experiment__worm_strain=worm),
              Q(experiment__screen_level=2),
              Q(experiment__is_junk=False),
              Q(experiment__temperature=temperature))
              .prefetch_related('experiment')
              .prefetch_related('experiment__library_plate')
              .order_by('experiment__id', 'well'))

    print 'before'
    d = {}

    for score in scores:
        experiment = score.experiment
        library_well = get_object_or_404(LibraryWell, well=score.well,
                                         plate=experiment.library_plate)

        if library_well not in d:
            d[library_well] = OrderedDict()

        # Adjust weights to be the 0-3 scale that we're used to
        weight = max(0, score.get_score_weight() - 1)

        if (experiment not in d[library_well] or
                d[library_well][experiment] < weight):
            d[library_well][experiment] = weight

    print 'after'

    max_expts = 0
    for well, expts in d.iteritems():
        well.avg = sum(x for x in expts.values()) / float(len(expts))
        if len(expts) > max_expts:
            max_expts = len(expts)

    # Sort by highest average
    d = OrderedDict(sorted(d.iteritems(), key=lambda x: x[0].avg,
                           reverse=True))

    context = {
        'worm': worm,
        'temp': temperature,
        'max_expts': max_expts,
        'd': d,
    }

    return render(request, 'secondary_scores.html', context)
