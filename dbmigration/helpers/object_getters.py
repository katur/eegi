"""
This module contains methods for retrieving objects based on legacy values.

These helpers are meant for use while syncing to the legacy database.
"""

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist

from clones.models import Clone
from experiments.models import Experiment, ExperimentPlate, ManualScoreCode
from library.models import LibraryStock, LibraryPlate
from library.helpers.naming import (generate_library_plate_name,
                                    generate_library_stock_name
from utils.wells import get_three_character_well
from worms.models import WormStrain


def get_missing_object_message(klass, **kwargs):
    return ('ERROR: {} with {} not found in the new database\n'
            .format(klass, str(kwargs)))


def get_clone(clone_name):
    """Get a clone from its clone name."""
    try:
        return Clone.objects.get(id=clone_name)

    except ObjectDoesNotExist:
        raise ObjectDoesNotExist(get_missing_object_message(
            'Clone', id=clone_name))


def get_library_plate(legacy_plate_name):
    """Get a library plate from a legacy library plate name."""
    legacy_plate_name = generate_library_plate_name(legacy_plate_name)

    try:
        return LibraryPlate.objects.get(id=legacy_plate_name)

    except ObjectDoesNotExist:
        raise ObjectDoesNotExist(get_missing_object_message(
            'LibraryPlate', id=legacy_plate_name))


def get_library_stock(legacy_plate_name, well):
    """Get a library well from its legacy plate name and well."""
    library_stock_name = generate_library_stock_name(legacy_plate_name, well)

    try:
        return LibraryStock.objects.get(id=library_stock_name)

    except ObjectDoesNotExist:
        raise ObjectDoesNotExist(get_missing_object_message(
            'LibraryStock', id=library_stock_name))


def get_worm_strain(mutant, mutantAllele):
    """Get a worm strain from its mutant gene and mutant allele."""
    try:
        if mutant == 'N2':
            worm_strain = WormStrain.objects.get(id='N2')

        else:
            if mutantAllele == 'zc310':
                mutantAllele = 'zu310'

            worm_strain = WormStrain.objects.get(gene=mutant,
                                                 allele=mutantAllele)

        return worm_strain

    except ObjectDoesNotExist:
        raise ObjectDoesNotExist(get_missing_object_message(
            'WormStrain', gene=mutant, allele=mutantAllele))


def get_experiment_plate(experiment_plate_id):
    """Get an experiment plate from its id."""
    try:
        return ExperimentPlate.objects.get(id=experiment_plate_id)

    except ObjectDoesNotExist:
        raise ObjectDoesNotExist(get_missing_object_message(
            'ExperimentPlate', id=experiment_plate_id))


def get_experiment(experiment_plate_id, well):
    try:
        return Experiment.objects.get(
            plate_id=experiment_plate_id,
            well=get_three_character_well(well))

    except ObjectDoesNotExist:
        raise ObjectDoesNotExist(get_missing_object_message(
            'Experiment', plate_id=experiment_plate_id, well=well))


def get_score_code(score_code_id):
    """Get a score code from its id."""
    try:
        return ManualScoreCode.objects.get(id=score_code_id)

    except ObjectDoesNotExist:
        raise ObjectDoesNotExist(get_missing_object_message(
            'ManualScoreCode', id=score_code_id))


def get_user(legacy_username):
    """Get a user from its username."""
    if legacy_username == 'Julie':
        legacy_username = 'julie'
    if legacy_username == 'patricia':
        legacy_username = 'giselle'

    try:
        return User.objects.get(username=legacy_username)
    except ObjectDoesNotExist:
        raise ObjectDoesNotExist(get_missing_object_message(
            'User', username=legacy_username))
