from __future__ import division
from collections import OrderedDict

from django.db.models import Count

from experiments.models import ManualScore, Experiment
from library.helpers import get_organized_library_wells
from library.models import LibraryPlate
from worms.models import WormStrain


def get_average_weight(scores):
    '''
    Get the average weight of scores

    '''
    total_weight = 0
    for score in scores:
        weight = score.get_weight()
        total_weight += weight
    return total_weight / len(scores)


def get_most_relevant_score_per_replicate(scores):
    '''
    From multiple scores for a single replicate, get the most relevant.

    '''
    scores.sort(
        key=lambda x: x.get_relevance_per_replicate(),
        reverse=True)
    return scores[0]


def sort_scores_by_relevance_across_replicates(scores):
    '''
    From scores across replicates (a single, most relevant score per
    replicate), sort by the most relevant.

    '''
    return sorted(scores,
                  key=lambda x: x.get_relevance_across_replicates(),
                  reverse=True)


def passes_sup_positive_criteria(scores):
    '''
    Determine if a set of countable secondary scores (i.e., one most relevant
    score per secondary replicate) passes the criteria to make it a
    positive.

    '''
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


def passes_enh_secondary_criteria(scores):
    '''
    Determine if a set of countable primary scores (i.e., one most relevant
    score per primary replicate) passes the criteria to make it into
    the Enhancer secondary screen.

    '''
    is_positive = False
    num_weaks = 0
    for score in scores:
        if score.is_strong() or score.is_medium():
            is_positive = True
            break
        if score.is_weak():
            num_weaks += 1

    if num_weaks >= 2:
        is_positive = True

    return is_positive


def organize_scores(scores, library_wells, most_relevant=False):
    '''
    Organize a list of scores, consulting organized library_wells w, into:

        s[library_well][experiment] = [scores]
    '''
    s = {}

    for score in scores:
        experiment = score.experiment
        plate = experiment.library_plate
        well = score.well
        library_well = library_wells[plate][well]

        if library_well not in s:
            s[library_well] = OrderedDict()

        if most_relevant:
            if (experiment not in s[library_well] or
                    s[library_well][experiment].get_relevance_per_replicate() <
                    score.get_relevance_per_replicate()):
                s[library_well][experiment] = score

        else:
            if experiment not in s[library_well]:
                s[library_well][experiment] = []
            s[library_well][experiment].append(score)

    return s


def get_organized_primary_scores(screen, screen_level=None,
                                 most_relevant=False):
    '''
    Get primary scores for a particular screen ('ENH' or 'SUP'), organized as:

        s[worm][library_well][experiment] = [scores]

    '''
    w = get_organized_library_wells(screen_level=1)

    worms = WormStrain.objects
    if screen == 'ENH':
        worms = worms.exclude(permissive_temperature__isnull=True)
    elif screen == 'SUP':
        worms = worms.exclude(restrictive_temperature__isnull=True)

    s = {}
    for worm in worms:
        scores = (ManualScore.objects.filter(
                  experiment__worm_strain=worm,
                  experiment__temperature=worm.permissive_temperature,
                  experiment__is_junk=False,
                  experiment__screen_level=1)
                  .prefetch_related('score_code', 'experiment',
                                    'experiment__library_plate'))

        s[worm] = organize_scores(scores, w, most_relevant)

    return s


def get_clones_for_secondary(screen, passes_criteria):
    '''
    Get the list of clones to include in the secondary, for the provided
    screen.

    Returns:
        A 2-tuple of:
            1) a dictionary of the clones organized by worm
            2) a dictionary of the clones organized by clone
        These two dictionaries can then be used to organize the clones into
        plates, including any universal plates.

    Args:
        screen: Either 'ENH' or 'SUP'.

        criteria: A function that determines the criteria for a library well
            making it into the secondary. This function takes a list of
            scores, where each score should be the most relevant score
            for a particular replicate. It should return True if the list
            of countable scores passes the criteria, or False otherwise.

    '''
    s = get_organized_primary_scores(screen)

    # For the (few) cases where there is just one replicate,
    # duplicate all scores for that replicate.
    # single_replicates = get_primary_single_replicate_experiments()

    secondary_list_by_worm = {}
    secondary_list_by_clone = {}

    for worm, library_wells in s.iteritems():
        for library_well, experiments in library_wells.iteritems():
            for experiment, scores in experiments.iteritems():
                # Replace all scores for this experiment with the most
                # relevant score only.
                score = get_most_relevant_score_per_replicate(scores)
                s[worm][library_well][experiment] = score

            if passes_criteria(experiments.values()):
                if worm not in secondary_list_by_worm:
                    secondary_list_by_worm[worm] = []
                secondary_list_by_worm[worm].append(library_well)

                if library_well not in secondary_list_by_clone:
                    secondary_list_by_clone[library_well] = []
                secondary_list_by_clone[library_well].append(worm)

    return (secondary_list_by_worm, secondary_list_by_clone)


def get_primary_single_replicate_experiments():
    '''
    Get primary experiments that don't have a second replicate.
    '''
    experiments = Experiment.objects.filter(
        is_junk=False, screen_level=1)

    plate_replicate_counts = (experiments.values('library_plate')
                              .annotate(num_replicates=Count('id')))

    single_replicate_plates = [x['library_plate'] for x in
                               plate_replicate_counts if
                               x['num_replicates'] == 1]

    single_replicate_experiments = []
    for plate_string in single_replicate_plates:
        plate = LibraryPlate.objects.get(pk=plate_string)
        experiment = experiments.get(library_plate=plate)
        single_replicate_experiments.append(experiment)

    return single_replicate_experiments
