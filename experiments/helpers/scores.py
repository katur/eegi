from __future__ import division
from collections import OrderedDict

from django.db.models import Count

from experiments.models import Experiment
from worms.helpers.queries import get_worms_for_screen_type


def get_most_relevant_score_per_experiment(scores):
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

    Returns a list where most relevant is first.

    scores should contain the single most relevant score per
    experiment replicate.

    """
    return sorted(scores,
                  key=lambda x: x.get_relevance_across_replicates(),
                  reverse=True)


def get_average_score_weight(scores):
    """Get the average weight of scores.

    scores should contain the single most relevant score per
    experiment replicate.

    """
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


def organize_manual_scores(scores, most_relevant_only=False):
    """Organize scores into a structured dictionary.

    The data returned is organized as:
        s[library_stock][experiment] = [scores]

    Or, if most_relevant_only is set to True:
        s[library_stock][experiment] = most_relevant_score

    """
    data = {}

    for score in scores:
        experiment = score.experiment
        lstock = experiment.library_stock

        if lstock not in data:
            data[lstock] = OrderedDict()

        if experiment not in data[lstock]:
            data[lstock][experiment] = []

        data[lstock][experiment].append(score)

    if most_relevant_only:
        for lstock, experiments in data.iteritems():
            for experiment, scores in experiments.iteritems():
                score = get_most_relevant_score_per_experiment(scores)
                data[lstock][experiment] = score

    return data


def get_organized_scores_all_worms(screen_for, screen_stage,
                                   most_relevant_only=False):
    """Get all scores for all worms for a particular screen.

    A screen is defined by both screen_for ('ENH' or 'SUP')
    and screen_stage (1 for primary, 2 for secondary).

    The data returned is organized as:
        s[worm][library_stock][experiment] = [scores]

    Or, if called with most_relevant_only=True:
        s[worm][library_stock][experiment] = most_relevant_score

    """
    worms = get_worms_for_screen_type(screen_for)

    s = {}
    for worm in worms:
        s[worm] = worm.get_organized_scores(
            screen_for, screen_stage, most_relevant_only)

    return s


def get_positives_any_worm(screen_for, screen_stage, criteria):
    """Get the set of library stocks that are positive for ANY
    worm in a particular screen.

    A screen is defined by both screen_for ('ENH' or 'SUP')
    and screen_stage (1 for primary, 2 for secondary).

    """
    worms = get_worms_for_screen_type(screen_for)

    all_positives = set()
    for worm in worms:
        positives = worm.get_positives(screen_for, screen_stage, criteria)
        all_positives.union(positives)

    return all_positives


def get_secondary_candidates(screen_for, criteria):
    """Get the positives for the secondary cherry-pick list.

    TODO:
        - this function should be modified to use the
          worm.get_positives() method to get the secondary
          candidates. The reason it is does not is twofold:

          1) It does futher organizational steps to help with making
             universal plates
          2) The "criteria" for primary involves a special case of
             single replicates

    Returns:
        A 2-tuple of:
            1) a dictionary of the clones organized by worm
            2) a dictionary of the clones organized by clone

        These two dictionaries can then be used to organize clones into
        plates, including any universal plates.

    Args:
        screen_for: Either 'ENH' or 'SUP'.

        criteria: A function that determines the criteria for a library
            stock to make it into the secondary. This function takes a
            list of scores, where each score should be the most relevant
            score for a particular replicate. It should return True if
            the list of countable scores passes the criteria, or
            False otherwise.

    """
    worms = get_worms_for_screen_type(screen_for)

    # To handle special case for stocks that have only a single replicate
    singles = _get_primary_single_replicate_experiments(screen_for)

    candidates_by_worm = {}
    candidates_by_clone = {}

    for worm in worms:
        s = worm.get_organized_scores(screen_for, 1,
                                      most_relevant_only=True)

        for library_stock, experiments in s.iteritems():
            if criteria(experiments.values(), singles):
                if worm not in candidates_by_worm:
                    candidates_by_worm[worm] = []
                candidates_by_worm[worm].append(library_stock)

                if library_stock not in candidates_by_clone:
                    candidates_by_clone[library_stock] = []
                candidates_by_clone[library_stock].append(worm)

    return (candidates_by_worm, candidates_by_clone)


def _get_primary_single_replicate_experiments(screen):
    """Get primary experiments that have only a single replicate."""

    """

    TODO : This is not really refactored yet.

    Accounting for singles still expects to work on a plate-level,
    not well-level.


    """
    worms = get_worms_for_screen_type(screen)

    singles = set()

    for worm in worms:
        if screen == 'SUP':
            experiments = (
                Experiment.objects
                .filter(is_junk=False,
                        plate__screen_stage=1,
                        worm_strain=worm,
                        plate__temperature=worm.restrictive_temperature)
                .order_by('library_stock'))

        else:
            experiments = (
                Experiment.objects
                .filter(is_junk=False,
                        plate__screen_stage=1,
                        worm_strain=worm,
                        plate__temperature=worm.permissive_temperature)
                .order_by('library_stock'))

        annotated = experiments.values('library_stock').annotate(Count('id'))

        single_stocks = [x['library_stock'] for x in annotated
                         if x['id__count'] == 1]

        for stock in single_stocks:
            singles.add(experiments.get(library_stock=stock))

    return singles
