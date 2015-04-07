from __future__ import division


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


def passes_sup_high_confidence_criteria(scores):
    total = len(scores)
    present = 0
    for score in scores:
        if score.is_strong() or score.is_medium():
            present += 1

    if (present / total) >= .375:
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
