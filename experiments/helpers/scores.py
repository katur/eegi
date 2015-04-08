from __future__ import division
from collections import OrderedDict

from django.db.models import Count

from experiments.models import ManualScore, Experiment
from library.helpers import get_organized_library_wells
from library.models import LibraryPlate
from worms.models import WormStrain


def get_average_score_weight(scores):
    '''
    Get the average weight of scores.

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


def get_organized_scores_all_worms(screen, screen_level,
                                   most_relevant_only=False):
    '''
    Fetch all scores for a particular screen ('ENH' or 'SUP')
    and screen_level (1 for primary, 2 for secondary),
    organized as:

        s[worm][library_well][experiment] = [scores]

    Or, if most_relevant_only is set to True:

        s[worm][library_well][experiment] = most_relevant_score

    '''
    w = get_organized_library_wells(screen_level=screen_level)

    worms = WormStrain.objects
    if screen == 'ENH':
        worms = worms.exclude(permissive_temperature__isnull=True)
    elif screen == 'SUP':
        worms = worms.exclude(restrictive_temperature__isnull=True)

    s = {}
    for worm in worms:
        s[worm] = get_organized_scores_specific_worm(
            worm, screen, screen_level, most_relevant_only, library_wells=w)

    return s


def get_organized_scores_specific_worm(worm, screen, screen_level,
                                       most_relevant_only=False,
                                       library_wells=None):
    '''
    Fetch all scores for a particular worm, screen ('ENH' or 'SUP'),
    and screen level (1 for primary, 2 for secondary),
    organized as:

        s[library_well][experiment] = [scores]

    Or, if most_relevant_only is set to True:

        s[library_well][experiment] = most_relevant_score

    '''
    scores = ManualScore.objects.filter(
        experiment__screen_level=screen_level,
        experiment__is_junk=False,
        experiment__worm_strain=worm)

    if screen == 'ENH':
        scores = scores.filter(
            experiment__temperature=worm.permissive_temperature)
    elif screen == 'SUP':
        scores = scores.filter(
            experiment__temperature=worm.restrictive_temperature)

    scores = (scores
              .select_related('score_code')
              .prefetch_related('experiment__library_plate')
              .order_by('experiment__id', 'well'))

    if not library_wells:
        library_wells = get_organized_library_wells(screen_level=screen_level)

    return organize_scores(scores, library_wells, most_relevant_only)


def organize_scores(scores, library_wells, most_relevant_only=False):
    '''
    Organize a list of scores, consulting organized library_wells w, into:

        s[library_well][experiment] = [scores]

    Or, if most_relevant_only is set to True:

        s[library_well][experiment] = most_relevant_score

    '''
    s = {}

    for score in scores:
        experiment = score.experiment
        plate = experiment.library_plate
        well = score.well
        library_well = library_wells[plate][well]

        if library_well not in s:
            s[library_well] = OrderedDict()

        if most_relevant_only:
            if (experiment not in s[library_well] or
                    s[library_well][experiment].get_relevance_per_replicate() <
                    score.get_relevance_per_replicate()):
                s[library_well][experiment] = score

        else:
            if experiment not in s[library_well]:
                s[library_well][experiment] = []
            s[library_well][experiment].append(score)

    return s


def get_secondary_candidates(screen, passes_criteria):
    '''
    Get the list of library wells to include in the secondary.

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
    # Get all primary scores for the particular screen
    s = get_organized_scores_all_worms(screen, 1)

    # TODO: deal with cases of only one replicated tested

    candidates_by_worm = {}
    candidates_by_clone = {}

    for worm, library_wells in s.iteritems():
        for library_well, experiments in library_wells.iteritems():
            for experiment, scores in experiments.iteritems():
                # Replace all scores for this experiment with the most
                # relevant score only.
                score = get_most_relevant_score_per_replicate(scores)
                s[worm][library_well][experiment] = score

            if passes_criteria(experiments.values()):
                if worm not in candidates_by_worm:
                    candidates_by_worm[worm] = []
                candidates_by_worm[worm].append(library_well)

                if library_well not in candidates_by_clone:
                    candidates_by_clone[library_well] = []
                candidates_by_clone[library_well].append(worm)

    return (candidates_by_worm, candidates_by_clone)


def get_positives_across_all_worms(screen, screen_level, passes_criteria):
    if screen != 'SUP' and screen != 'ENH':
        raise Exception('screen must be SUP or ENH')

    s = get_organized_scores_all_worms(screen, screen_level=screen_level,
                                       most_relevant_only=True)
    passing_library_wells = set()

    for worm, wells in s.iteritems():
        for well, expts in wells.iteritems():
            scores = expts.values()
            if passes_criteria(scores):
                passing_library_wells.add(well)

    return passing_library_wells


def get_positives_specific_worm(worm, screen, screen_level, passes_criteria):
    if screen != 'SUP' and screen != 'ENH':
        raise Exception('screen must be SUP or ENH')

    s = get_organized_scores_specific_worm(worm, screen,
                                           screen_level=screen_level,
                                           most_relevant_only=True)
    passing_library_wells = set()

    for well, expts in s.iteritems():
        scores = expts.values()
        if passes_criteria(scores):
            well.scores = scores
            well.avg = get_average_score_weight(scores)
            passing_library_wells.add(well)

    return passing_library_wells


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