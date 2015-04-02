from experiments.models import ManualScore
from library.models import LibraryWell
from worms.models import WormStrain


def get_most_relevant_score_per_replicate(scores):
    '''
    From multiple scores for a single replicate, get the most relevant.

    '''
    scores.sort(
        key=lambda x: x.get_relevance_per_replicate(),
        reverse=True)
    return scores[0]


def sort_by_relevance_across_replicates(scores):
    '''
    From scores across replicates (a single, most relevant score per
    replicate), sort by the most relevant.

    '''
    return sorted(scores,
                  key=lambda x: x.get_relevance_across_replicates(),
                  reverse=True)


def get_enhancer_secondary_list():
    '''
    Get the list of clones to include in the Enhancer Secondary screen.

    '''
    def enhancer_criteria(countable_scores):
        is_positive = False
        num_weaks = 0
        for score in countable_scores:
            if score.is_strong() or score.is_medium():
                is_positive = True
                break
            if score.is_weak():
                num_weaks += 1

        return is_positive or num_weaks >= 2
    return get_secondary_list('ENH', enhancer_criteria)


def get_secondary_list(screen, criteria):
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

            if criteria(experiments.values()):
                if worm not in secondary_list_by_worm:
                    secondary_list_by_worm[worm] = []
                secondary_list_by_worm[worm].append(library_well)

                if library_well not in secondary_list_by_clone:
                    secondary_list_by_clone[library_well] = []
                secondary_list_by_clone[library_well].append(worm)

    return (secondary_list_by_worm, secondary_list_by_clone)


def get_organized_library_wells(screen_level=None):
    '''
    Get library wells organized as:

        l[library_plate][well] = library_well

    Optionally provide a screen_level, to limit to the Primary or Secondary
    screen.

    '''
    library_wells = LibraryWell.objects.select_related('plate')
    if screen_level:
        library_wells = library_wells.filter(plate__screen_stage=screen_level)
    else:
        library_wells = library_wells.all()

    l = {}
    for library_well in library_wells:
        plate = library_well.plate
        well = library_well.well
        if plate not in l:
            l[plate] = {}
        l[plate][well] = library_well

    return l


def get_organized_primary_scores(screen, screen_level=None):
    '''
    Get primary scores for a particular screen ('ENH' or 'SUP'), organized as:

        s[worm][library_well][experiment] = [scores]

    '''
    l = get_organized_library_wells(screen_level=1)

    worms = WormStrain.objects
    if screen == 'ENH':
        worms = worms.exclude(permissive_temperature__isnull=True)
    elif screen == 'SUP':
        worms = worms.exclude(restrictive_temperature__isnull=True)

    s = {}
    for worm in worms:
        print worm
        s[worm] = {}
        scores = (ManualScore.objects.filter(
                  experiment__worm_strain=worm,
                  experiment__temperature=worm.permissive_temperature,
                  experiment__is_junk=False,
                  experiment__screen_level=1)
                  .prefetch_related('score_code', 'experiment',
                                    'experiment__library_plate'))
        for score in scores:
            experiment = score.experiment
            plate = experiment.library_plate
            well = score.well
            library_well = l[plate][well]

            if library_well not in s[worm]:
                s[worm][library_well] = {}

            if experiment not in s[worm][library_well]:
                s[worm][library_well][experiment] = []

            s[worm][library_well][experiment].append(score)

    return s
