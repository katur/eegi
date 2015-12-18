from __future__ import division
from collections import OrderedDict

from worms.helpers.queries import get_worms_for_screen_type


def get_most_relevant_score_per_experiment(scores):
    """
    Get the most relevant score for a single experiment replicate.

    scores should contain all the scores for a single experiment
    replicate.
    """
    scores.sort(
        key=lambda x: x.get_relevance_per_replicate(), reverse=True)
    return scores[0]


def get_average_score_weight(scores):
    """
    Get the average weight of scores.

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
    """
    Organize scores into a structured dictionary.

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


def get_positives_any_worm(screen_type, screen_stage, criteria, **kwargs):
    """
    Get the set of library stocks that are positive for ANY worm.

    A screen is defined by both screen_type ('ENH' or 'SUP')
    and screen_stage (1 for primary, 2 for secondary).
    """
    worms = get_worms_for_screen_type(screen_type)

    all_positives = set()
    for worm in worms:
        positives = worm.get_positives(screen_type, screen_stage, criteria,
                                       **kwargs)
        all_positives = all_positives.union(positives)

    return all_positives
