from __future__ import division


def passes_sup_positive_percentage_criteria(scores):
    """Determine if a set of suppressor secondary scores passes the
    percentage-based criteria for a positive suppressor.

    The scores should be for the same worm + library well combination, and
    should include just the most relevant score per replicate.
    """
    total = 0
    yes = 0
    maybe = 0
    for score in scores:
        if not score.is_other():
            total += 1

        if score.is_strong() or score.is_medium():
            yes += 1
        elif score.is_weak():
            maybe += 1

    if not total:
        return False

    if total < 8:
        return passes_sup_positive_count_criteria(scores)

    yes = yes / total
    maybe = maybe / total

    if (
            yes >= .375 or
            (yes >= .125 and yes + maybe >= .5) or
            yes + maybe >= .625):
        return True

    return False


def passes_sup_positive_count_criteria(scores):
    """Determine if a set of suppressor secondary scores passes the
    count-based criteria for a positive suppressor.

    The scores should be for the same worm + library well combination, and
    should include just the most relevant score per replicate.
    """
    yes = 0
    maybe = 0
    for score in scores:
        if score.is_strong() or score.is_medium():
            yes += 1
        elif score.is_weak():
            maybe += 1

    if (
            yes >= 3 or
            (yes >= 1 and yes + maybe >= 4) or
            yes + maybe >= 5):
        return True

    return False


def passes_sup_stringent_criteria(scores):
    """Determine if a set of suppressor secondary scores passes the
    stringent criteria for a positive suppressor.

    The scores should be for the same worm + library well combination, and
    should include just the most relevant score per replicate.
    """
    total = len(scores)
    yes = 0
    for score in scores:
        if score.is_strong() or score.is_medium():
            yes += 1

    if (yes / total) >= .375:
        return True

    return False


def passes_enh_secondary_criteria(scores, singles=[]):
    """Determine if a set of enhancer primary scores passes the criteria
    to make it into the enhancer secondary screen.

    The scores should be for the same worm + library well combination, and
    should include just the most relevant score per replicate.
    """
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

    if num_weaks == 1 and scores[0].experiment in singles:
        is_positive = True

    return is_positive
