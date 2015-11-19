from __future__ import division
from collections import OrderedDict

from django.db.models import Count

from experiments.models import ManualScore, ExperimentPlate
from library.helpers.queries import get_organized_library_stocks
from worms.models import WormStrain


def get_average_score_weight(scores):
    """Get the average weight of scores."""
    num_countable = 0
    total_weight = 0
    for score in scores:
        if not score.is_other():
            num_countable += 1
            total_weight += score.get_weight()
    if num_countable:
        return total_weight / num_countable
    else:
        return 0


def get_most_relevant_score_per_replicate(scores):
    """Get the most relevant score for a single experiment replicate.

    scores should contain all the scores for a single experiment
    replicate.

    """
    scores.sort(
        key=lambda x: x.get_relevance_per_replicate(),
        reverse=True)
    return scores[0]


def sort_scores_by_relevance_across_replicates(scores):
    """Sort scores across experiment replicates by relevance.

    scores should contain the one most relevant score per
    experiment replicate.

    """
    return sorted(scores,
                  key=lambda x: x.get_relevance_across_replicates(),
                  reverse=True)


def get_organized_scores_all_worms(screen_for, screen_stage,
                                   most_relevant_only=False):
    """Get all scores for all worms in a screen, in an organized way.

    A screen is defined by both screen_for ('ENH' or 'SUP')
    and screen_stage (1 for primary, 2 for secondary).

    The data returned is organized as:

        s[worm][library_stock][experiment] = [scores]

    Or, if called with most_relevant_only=True:

        s[worm][library_stock][experiment] = most_relevant_score

    """
    w = get_organized_library_stocks(screen_stage=screen_stage)

    worms = WormStrain.objects
    if screen_for == 'ENH':
        worms = worms.exclude(permissive_temperature__isnull=True)
    elif screen_for == 'SUP':
        worms = worms.exclude(restrictive_temperature__isnull=True)

    s = {}
    for worm in worms:
        s[worm] = get_organized_scores_specific_worm(
            worm, screen_for, screen_stage, most_relevant_only,
            library_stocks=w)

    return s


def get_organized_scores_specific_worm(worm, screen_for, screen_stage,
                                       most_relevant_only=False,
                                       library_stocks=None):
    """Get all scores for one worm in a screen, in an organized way.

    A screen is defined by both screen_for ('ENH' or 'SUP')
    and screen_stage (1 for primary, 2 for secondary).

    The data returned is organized as:

        s[library_stock][experiment] = [scores]

    Or, if most_relevant_only is set to True:

        s[library_stock][experiment] = most_relevant_score

    """
    scores = ManualScore.objects.filter(
        experiment__screen_stage=screen_stage,
        experiment__is_junk=False,
        experiment__worm_strain=worm)

    if screen_for == 'ENH':
        scores = scores.filter(
            experiment__temperature=worm.permissive_temperature)

    elif screen_for == 'SUP':
        scores = scores.filter(
            experiment__temperature=worm.restrictive_temperature)

    scores = (scores
              .select_related('score_code')
              .prefetch_related('experiment__library_plate')
              .order_by('experiment__id', 'well'))

    if not library_stocks:
        library_stocks = get_organized_library_stocks(
            screen_stage=screen_stage)

    return _organize_scores(scores, library_stocks, most_relevant_only)


def _organize_scores(scores, library_stocks, most_relevant_only=False):
    """Organize scores according to library_stocks.

    The data returned is in format:

        s[library_stock][experiment] = [scores]

    Or, if most_relevant_only is set to True:

        s[library_stock][experiment] = most_relevant_score

    """
    s = {}

    for score in scores:
        experiment = score.experiment
        plate = experiment.library_plate
        well = score.well
        library_stock = library_stocks[plate][well]

        if library_stock not in s:
            s[library_stock] = OrderedDict()

        if most_relevant_only:
            if (experiment not in s[library_stock] or
                    s[library_stock][experiment].get_relevance_per_replicate()
                    < score.get_relevance_per_replicate()):
                s[library_stock][experiment] = score

        else:
            if experiment not in s[library_stock]:
                s[library_stock][experiment] = []
            s[library_stock][experiment].append(score)

    return s


def get_positives_across_all_worms(screen, screen_stage, passes_criteria):
    if screen != 'SUP' and screen != 'ENH':
        raise Exception('screen must be SUP or ENH')

    s = get_organized_scores_all_worms(screen, screen_stage=screen_stage,
                                       most_relevant_only=True)
    passing_library_stocks = set()

    for worm, wells in s.iteritems():
        for well, expts in wells.iteritems():
            scores = expts.values()
            if passes_criteria(scores):
                passing_library_stocks.add(well)

    return passing_library_stocks


def get_positives_specific_worm(worm, screen, screen_stage, passes_criteria):
    if screen != 'SUP' and screen != 'ENH':
        raise Exception('screen must be SUP or ENH')

    s = get_organized_scores_specific_worm(worm, screen,
                                           screen_stage=screen_stage,
                                           most_relevant_only=True)
    passing_library_stocks = set()

    for well, expts in s.iteritems():
        scores = expts.values()
        if passes_criteria(scores):
            well.scores = scores
            well.avg = get_average_score_weight(scores)
            passing_library_stocks.add(well)

    return passing_library_stocks


def get_secondary_candidates(screen, passes_criteria):
    """Get the list of library stocks to include in the secondary.

    TODO: this has not yet been implemented for SUP screen. The
    secondary candidate selection for the SUP screen predated this
    codebase.

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

    """
    # Get all primary scores for the particular screen
    s = get_organized_scores_all_worms(screen, 1)

    candidates_by_worm = {}
    candidates_by_clone = {}

    singles = get_primary_single_replicate_experiments(screen)

    for worm, library_stocks in s.iteritems():
        for library_stock, experiments in library_stocks.iteritems():
            for experiment, scores in experiments.iteritems():
                # Replace all scores for this experiment with the most
                # relevant score only.
                score = get_most_relevant_score_per_replicate(scores)
                s[worm][library_stock][experiment] = score

            if passes_criteria(experiments.values(), singles):
                if worm not in candidates_by_worm:
                    candidates_by_worm[worm] = []
                candidates_by_worm[worm].append(library_stock)

                if library_stock not in candidates_by_clone:
                    candidates_by_clone[library_stock] = []
                candidates_by_clone[library_stock].append(worm)

    return (candidates_by_worm, candidates_by_clone)


def get_primary_single_replicate_experiments(screen):
    """Get primary experiments that have only a single replicate."""
    if screen == 'SUP':
        worms = WormStrain.objects.filter(
            restrictive_temperature__isnull=False)
    else:
        worms = WormStrain.objects.filter(
            permissive_temperature__isnull=False)

    singles = set()

    for worm in worms:
        if screen == 'SUP':
            experiments = (ExperimentPlate.objects
                           .filter(is_junk=False, screen_stage=1,
                                   worm_strain=worm,
                                   temperature=worm.restrictive_temperature)
                           .order_by('library_plate'))
        else:
            experiments = (ExperimentPlate.objects
                           .filter(is_junk=False, screen_stage=1,
                                   worm_strain=worm,
                                   temperature=worm.permissive_temperature)
                           .order_by('library_plate'))

        annotated = experiments.values('library_plate').annotate(Count('id'))

        single_plates = [x['library_plate'] for x in annotated
                         if x['id__count'] == 1]

        for plate in single_plates:
            singles.add(experiments.get(library_plate=plate))

    return singles
