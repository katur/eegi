from django.shortcuts import get_object_or_404
from experiments.models import ManualScore
from worms.models import WormStrain
from library.models import LibraryWell


def get_condensed_primary_scores(worm, library_well, screen):
    '''
    Get a summarization of scores for a particular worm / library well
    combination.

    First, each image is binned as strong, medium, weak, negative, or
    other (where precedance follows the order given, i.e., being scored as
    strong outweighs also being scored as medium, or being scored as negative
    outweighs being scored as other).

    Second, the strongest two images are selected, where
    strong > medium > weak > unscored > other > negative.

    A list of length two is returned, where
    4: strong
    3: medium
    2: weak
    1: unscored
    -1: other
    -2: negative
    '''
    scores = get_all_primary_scores(worm, library_well, screen)
    return condense_primary_scores(scores)


def get_all_primary_scores(worm, library_well, screen):
    '''
    Get all primary scores for a particular worm, library well, and screen.
    '''
    if screen == 'SUP':
        temp = worm.restrictive_temperature
    elif screen == 'ENH':
        temp = worm.permissive_temperature
    else:
        raise ValueError('screen must be "SUP" or "ENH"')

    plate = library_well.plate
    well = library_well.well
    scores = ManualScore.objects.filter(experiment__worm_strain=worm,
                                        experiment__temperature=temp,
                                        experiment__is_junk=False,
                                        experiment__screen_level=1,
                                        experiment__library_plate=plate,
                                        well=well)
    return scores


def condense_primary_scores(scores):
    '''
    Create a summarization of scores in which only the most relevant score
    per image is counted (strong, medium, weak,
    '''

    # First group scores by experiment
    score_dictionary = {}
    for score in scores:
        if score.experiment not in score_dictionary:
            score_dictionary[score.experiment] = []
        score_dictionary[score.experiment].append(score.get_score_weight())

    condensed = []
    for experiment, experiment_scores in score_dictionary.iteritems():
        experiment_scores.sort(reverse=True)
        countable = experiment_scores[0]
        if countable == 0:
            countable = -2
        condensed.append(countable)

    if len(condensed) == 0:
        condensed.extend([1, 1])
    elif len(condensed) == 1:
        condensed.append(1)

    condensed.sort(reverse=True)
    return condensed[0:2]


test_worm = get_object_or_404(WormStrain, gene='mbk-2')
test_well = get_object_or_404(LibraryWell, plate__id='I-5-A2', well='E12')
