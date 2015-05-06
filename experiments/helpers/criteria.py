from __future__ import division


def passes_sup_stringent_criteria(scores):
    total = len(scores)
    yes = 0
    for score in scores:
        if score.is_strong() or score.is_medium():
            yes += 1

    if (yes / total) >= .375:
        return True

    return False


def passes_sup_positive_percentage_criteria(scores):
    '''
    Determine if a set of countable secondary scores (i.e., one most relevant
    score per secondary replicate) passes the criteria to make it a
    positive.

    '''
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


def passes_enh_secondary_criteria(scores, singles=[]):
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

    if num_weaks == 1 and scores[0].experiment in singles:
        is_positive = True

    return is_positive
