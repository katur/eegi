from experiments.models import ManualScore
from library.helpers import get_organized_library_wells
from worms.models import WormStrain


def passes_enh_primary_criteria(countable_scores):
    '''
    Determine if a set of countable primary scores (i.e., one most relevant
    score per primary replicate) passes the criteria to make it into
    the Enhancer secondary screen.

    '''
    is_positive = False
    num_weaks = 0
    for score in countable_scores:
        if score.is_strong() or score.is_medium():
            is_positive = True
            break
        if score.is_weak():
            num_weaks += 1

    if num_weaks >= 2:
        is_positive = True

    return is_positive


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


def organize_scores(scores, w):
    '''
    Organize a list of scores, consulting organized library_wells w, into:

        s[library_well][experiment] = [scores]
    '''
    s = {}

    for score in scores:
        experiment = score.experiment
        plate = experiment.library_plate
        well = score.well
        library_well = w[plate][well]

        if library_well not in s:
            s[library_well] = {}

        if experiment not in s[library_well]:
            s[library_well][experiment] = []

        s[library_well][experiment].append(score)

    return s


def get_organized_primary_scores(screen, screen_level=None):
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
        s[worm] = organize_scores(scores, w)

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


def get_clones_for_enh_secondary():
    '''
    Get the list of clones to include in the Enhancer secondary screen.

    '''
    return get_clones_for_secondary('ENH', passes_enh_primary_criteria)
