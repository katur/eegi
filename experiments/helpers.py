from experiments.models import ManualScore


def get_condensed_primary_scores(worm, library_well, screen):
    '''
    Get a summary of scores for a particular worm / library well
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
    scores = get_primary_scores_by_screen(worm, library_well, screen)
    condensed = condense_scores(scores)
    return get_top_two_scores(condensed)


def get_primary_scores_by_screen(worm, library_well, screen):
    '''
    Get all primary scores for a particular worm, library well,
    and screen.
    '''
    if screen == 'SUP':
        temp = worm.restrictive_temperature
    elif screen == 'ENH':
        temp = worm.permissive_temperature
    else:
        raise ValueError('screen must be "SUP" or "ENH"')

    return get_primary_scores_by_temp(worm, library_well, temp)


def get_primary_scores_by_temp(worm, library_well, temp):
    '''
    Get all primary scores for a particular worm, library well,
    and temperature.
    '''
    plate = library_well.plate
    well = library_well.well
    scores = ManualScore.objects.filter(experiment__worm_strain=worm,
                                        experiment__temperature=temp,
                                        experiment__is_junk=False,
                                        experiment__screen_level=1,
                                        experiment__library_plate=plate,
                                        well=well)
    return scores


def condense_scores(scores):
    '''
    Create a summarization of scores in which only the most relevant score
    (strong, medium, weak, negative, other) per experiment/image is counted.

    Returns a list of one summarized score per image, where the summarized
    score means:
    4: strong
    3: medium
    2: weak
    -1: other
    -2: negative

    The list of summarized scores is sorted in descending order, i.e., in with
    strongest candidates first.
    '''
    # First group scores by experiment
    score_dictionary = {}
    for score in scores:
        if score.experiment not in score_dictionary:
            score_dictionary[score.experiment] = []
        score_dictionary[score.experiment].append(score.get_score_weight())

    # Next extract the most meaningful score
    condensed = []
    for experiment, experiment_scores in score_dictionary.iteritems():
        experiment_scores.sort(reverse=True)
        countable = experiment_scores[0]

        # After extracting the most meaningful (where 'negative' is more
        # meaningful than 'other'), reorder such that 'negative' is
        # lower weight than 'other'
        if countable == 0:
            countable = -2

        condensed.append(countable)

    return sorted(condensed, reverse=True)


def get_top_two_scores(condensed_scores):
    '''
    Get the top two scores from condensed scores,
    where each condensed score is for a unique experiment.
    Assumes that condensed_scores are sorted in descending order, i.e.,
    with strongest candidates first.
    Returns a list of two scores, with same meanings as in
    condense_scores().

    If there are not enough scores to get two, pads with:
    1: unscored
    '''
    if len(condensed_scores) == 0:
        condensed_scores.extend([1, 1])
    elif len(condensed_scores) == 1:
        condensed_scores.append(1)
    return condensed_scores[0:2]
