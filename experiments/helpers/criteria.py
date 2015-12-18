from __future__ import division


def shows_any_suppression(scores):
    """Check if scores contains at least a single suppression score."""
    for score in scores:
        if score.is_strong() or score.is_medium() or score.is_weak():
            return True

    return False


def passes_sup_secondary_stringent(scores):
    """
    Check if scores passes stringent criteria for a positive suppressor.

    scores should include the single most relevant score per replicate,
    and include all replicates for a particular worm / library_stock combo
    in the suppressor secondary.
    """
    total = len(scores)
    yes = 0
    for score in scores:
        if score.is_strong() or score.is_medium():
            yes += 1

    return (yes / total) >= .375


def passes_sup_secondary_percent(scores):
    """
    Check if scores passes percent-based criteria for a positive suppressor.

    scores should include the single most relevant score per replicate,
    and include all replicates for a particular worm / library_stock combo
    in the suppressor secondary.
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
        return passes_sup_secondary_count(scores)

    yes = yes / total
    maybe = maybe / total

    return (yes >= .375 or
            (yes >= .125 and yes + maybe >= .5) or
            yes + maybe >= .625)


def passes_sup_secondary_count(scores):
    """
    Check if scores passes count-based criteria for a positive suppressor.

    scores should include the single most relevant score per replicate,
    and include all replicates for a particular worm / library_stock combo
    in the suppressor secondary.
    """
    yes = 0
    maybe = 0
    for score in scores:
        if score.is_strong() or score.is_medium():
            yes += 1
        elif score.is_weak():
            maybe += 1

    return (yes >= 3 or
            (yes >= 1 and yes + maybe >= 4) or
            yes + maybe >= 5)


def passes_enh_primary(scores, singles=[]):
    """
    Check if scores qualifies for the enhancer secondary screen.

    scores should include the single most relevant score per replicate,
    and include all replicates for a particular worm / library_stock combo
    in the enhancer primary.

    singles is an optional list of library_stocks that only had a single
    copy tested for this worm. This is different from having a single
    copy scored. When two copies were tested but only one copy
    scored, it is presumed that the unscored copy is a negative, since
    DevStaR did not select it for scoring. However, in the rare case
    that we only tested one copy, we do not presume anything about the
    other copy.
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

    if num_weaks == 1 and scores[0].experiment.library_stock in singles:
        is_positive = True

    return is_positive
