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
    Get all primary, manual scores for a particular worm, library well, and
    screen.
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
            countable == -2

        condensed.append(countable)

    if len(condensed) == 0:
        condensed.extend([1, 1])
    elif len(condensed) == 1:
        condensed.append(1)

    condensed.sort(reverse=True)

    return condensed[0:2]


"""
Preliminary work towards migrating antiquated SUP scores. not finished at all.


PRIMARY_POSITIVE_CRITERIA = {
    '''
    PRIMARY_POSITIVE_CRITERIA[gene][screen], where screen is 'SUP' or 'ENH'.
    '''
    'dhc-1': {
        'SUP': lambda score, scorers, dates: (
            's' in score or 'm' in score or score == 'ww' or score == 'wo')},
    'div-1': {
        'SUP': lambda score, scorers, dates: (
            's' in score or score == 'mm' or score == 'mw' or score == 'mo' or
            score == 'ww')},
    'emb-27': {
        'SUP': lambda score, scorers, dates: (
            's' in score or 'm' in score or score == 'ww' or score == 'wo')},
    'emb-30': {
        'SUP': lambda score, scorers, dates: (
            's' in score or score == 'mm' or score == 'mw' or score == 'mo' or
            score == 'mn' or score == 'ww' or score == 'wo')},
    'emb-8': {
        'SUP': lambda score, scorers, dates: (
            's' in score or score == 'mm' or score == 'mw' or score == 'mo' or
   G         score == 'ww')},
    'glp-1': {
        'SUP': lambda score, scorers, dates: (
            score == 'ss' or score == 'sm' or score == 'sw' or score == 'so' or
            score == 'sn' or score == 'mm' or score == 'mw' or score == 'mo' or
            score == 'mn' or score == 'ww' or (
                '20100421' not in dates and (score == 'su' or score == 'mu')
            ))},
    'hcp-6': {
        'SUP': lambda score, scorers, dates: (
            's' in score or 'm' in score or score == 'ww' or score == 'wo')},
    'lin-5': {
        'SUP': lambda score, scorers, dates: (
            's' in score or 'm' in score or score == 'ww' or score == 'wo')},
    'mat-1': {
        'SUP': lambda score, scorers, dates: (
            's' in score or score == 'mm' or score == 'mw' or score == 'mo' or
            score == 'ww')},
    'mbk-2': {
        'SUP': lambda score, scorers, dates: (
            score == 'ss' or score == 'sm' or score == 'sw' or score == 'so' or
            score == 'mm' or score == 'mw' or score == 'mo' or
            score == 'ww' or (
                '20100707' not in dates and (
                    score == 'su' or score == 'sn' or score == 'mu' or
                    score == 'mn')))},
    'mel-26': {
        'SUP': lambda score, scorers, dates: (
            's' in score or score == 'mm' or score == 'mw' or score == 'mo' or
            score == 'ww' or score == 'wo')},
    'par-1': {
        'SUP': lambda score, scorers, dates: (
            's' in score or 'm' in score or score == 'ww' or score == 'wo' or (
                score == 'wu' and ('20110309' in dates or '20110330' in dates)
            ))},
    'par-2': {
        'SUP': lambda score, scorers, dates: (
            's' in score or score == 'mm' or score == 'mw' or score == 'mo' or
            score == 'ww' or score == 'wo')},
    'par-4': {
        'SUP': lambda score, scorers, dates: (
            's' in score or 'm' in score or score == 'ww' or score == 'wo')},
    'pod-2': {
        'SUP': lambda score, scorers, dates: (
            's' in score or 'm' in score or score == 'ww' or score == 'wo')},
    'rme-8': {
        'SUP': lambda score, scorers, dates: (
            score == 'ss' or score == 'sm' or score == 'sw' or score == 'so' or
            score == 'sn' or score == 'mm' or score == 'mw' or score == 'mo' or
            score == 'ww')},
    'spd-5': {
        'SUP': lambda score, scorers, dates: (
            's' in score or 'm' in score or score == 'ww')},
    'spn-4': {
        'SUP': lambda score, scorers, dates: (
            's' in score or 'm' in score or score == 'ww' or score == 'wo')},
    'tba-1': {
        'SUP': lambda score, scorers, dates: (
            score == 'ss' or score == 'sm' or score == 'sw' or score == 'so' or
            score == 'sn' or score == 'mm' or score == 'mw' or score == 'mo' or
            score == 'mn' or (score == 'ww' and 'noah' in scorers))},
    'zen-4': {
        'SUP': lambda score, scorers, dates: (
            score == 'ss' or score == 'sm' or score == 'sw' or score == 'sn' or
            score == 'mm' or score == 'mw' or score == 'mo' or (
                (score == 'so' or score == 'su') and '20100921' not in dates)
            )},
    'zyg-1': {
        'SUP': lambda score, scorers, dates: (
            's' in score or 'm' in score or score == 'ww' or score == 'wo')},
    'zyg-8': {
        'SUP': lambda score, scorers, dates: (
            's' in score or 'm' in score or score == 'ww' or score == 'wo')},
    'zyg-9': {
        'SUP': lambda score, scorers, dates: (
            's' in score or 'm' in score or score == 'ww' or score == 'wo')},
}


def get_primary_score_criteria(self, screen):
    return PRIMARY_POSITIVE_CRITERIA[self.gene][screen]
"""


test_worm = get_object_or_404(WormStrain, gene='mbk-2')
test_well = get_object_or_404(LibraryWell, plate__id='I-5-A2', well='E12')
