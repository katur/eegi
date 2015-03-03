from collections import OrderedDict
from itertools import chain

from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404

from clones.models import Clone
from experiments.models import Experiment, ManualScore
from experiments.forms import (ExperimentFilterForm, DoubleKnockdownForm,
                               SecondaryScoresForm)
from library.models import LibraryWell, LibraryPlate
from worms.models import WormStrain


def experiments(request, context=None):
    """
    Render the page to navigate all experiments. Provides navigation
    by either a specific experiment id, or various filters.
    """
    exact_id_errors = []

    if 'exact_id' in request.GET:
        try:
            id = int(request.GET['exact_id'])
            if (id > 0):
                return redirect(experiment_plate, id)
            else:
                exact_id_errors.append('Experiment id must be positive')

        except ValueError:
            exact_id_errors.append('Experiment id must be a positive integer')

    total_results = None
    display_experiments = None
    link_to_vertical = None

    if len(request.GET):
        form = ExperimentFilterForm(request.GET)
        if form.is_valid():
            filters = form.cleaned_data
            for k, v in filters.items():
                # Retain 'False' as a legitimate filter
                if v is False:
                    continue

                # Ditch empty strings and None as filters
                if not v:
                    del filters[k]

            if filters:
                experiments = (
                    Experiment.objects.filter(**filters)
                    .values('id', 'worm_strain', 'worm_strain__genotype',
                            'library_plate', 'temperature', 'date',
                            'is_junk', 'comment'))
                total_results = len(experiments)

                if total_results > 0 and total_results < 25:
                    ids = experiments.values_list('id')
                    ids = (str(i[0]) for i in ids)
                    id_string = ','.join(ids)
                    link_to_vertical = reverse('experiment_plate_vertical_url',
                                               args=[id_string])

                paginator = Paginator(experiments, 100)
                page = request.GET.get('page')
                try:
                    display_experiments = paginator.page(page)
                except PageNotAnInteger:
                    display_experiments = paginator.page(1)
                except EmptyPage:
                    display_experiments = paginator.page(paginator.num_pages)

    else:
        form = ExperimentFilterForm()

    context = {
        'exact_id_errors': exact_id_errors,
        'form': form,
        'total_results': total_results,
        'display_experiments': display_experiments,
        'link_to_vertical': link_to_vertical,
    }

    return render(request, 'experiments.html', context)


def experiment_plate(request, id):
    """
    Render the page to see information about a specific experiment.
    """
    experiment = get_object_or_404(Experiment, pk=id)
    experiment.worm_strain.url = experiment.worm_strain.get_url(request)

    wells = LibraryWell.objects.filter(
        plate=experiment.library_plate).order_by('well')

    for well in wells:
        well.row = well.get_row()

    context = {
        'experiment': experiment,
        'wells': wells,
    }

    return render(request, 'experiment_plate.html', context)


def experiment_plate_vertical(request, ids):
    """
    Render the page to see information about a specific experiment.
    """
    ids = ids.split(',')
    experiments = []
    for id in ids:
        experiment = get_object_or_404(Experiment, pk=id)
        experiment.wells = LibraryWell.objects.filter(
            plate=experiment.library_plate).order_by('well')
        experiments.append(experiment)

    context = {
        'experiments': experiments,
    }

    return render(request, 'experiment_plate_vertical.html', context)


def experiment_well(request, id, well):
    experiment = get_object_or_404(Experiment, pk=id)
    experiment.worm_strain.url = experiment.worm_strain.get_url(request)

    well = LibraryWell.objects.filter(
        plate=experiment.library_plate).filter(well=well)[0]
    experiment.score_summary = experiment.get_score_summary(well)

    context = {
        'experiment': experiment,
        'well': well,
    }

    return render(request, 'experiment_well.html', context)


def double_knockdown_search(request):
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


def double_knockdown(request, worm, clone, temperature):
    worm = get_object_or_404(WormStrain, pk=worm)
    clone = get_object_or_404(Clone, pk=clone)
    n2 = get_object_or_404(WormStrain, pk='N2')
    l4440_plate = get_object_or_404(LibraryPlate, pk='L4440')

    # plates_with_l4440 = LibraryPlate.objects.filter(
    #    librarywell__intended_clone=l4440_clone)

    library_wells = (LibraryWell.objects
                     .filter(intended_clone=clone,
                             plate__screen_stage__gt=0)
                     .order_by('-plate__screen_stage'))

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

            for e in list(chain(mutant_rnai, n2_rnai, mutant_l4440, n2_l4440)):
                e.score_summary = e.get_score_summary(library_well)

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

    scores = (ManualScore.objects.filter(
              Q(experiment__worm_strain=worm),
              Q(experiment__screen_level=2),
              Q(experiment__is_junk=False),
              Q(experiment__temperature=temperature)).
              order_by('experiment__worm_strain', 'experiment__id', 'well'))

    d = {}
    for score in scores:
        experiment = score.experiment
        library_well = get_object_or_404(LibraryWell, well=score.well,
                                         plate=experiment.library_plate)

        if library_well not in d:
            d[library_well] = OrderedDict()

        # Adjust weights to be the 0-3 scale that we're used to
        weight = score.get_score_weight() - 1
        if weight < 0:
            weight = 0

        if (experiment not in d[library_well] or
                d[library_well][experiment] < weight):
            d[library_well][experiment] = weight

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
