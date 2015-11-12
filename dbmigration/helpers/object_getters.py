"""This module contains methods for retrieving objects that already
exist in the new database, based on legacy values.

These helpers are meant for use while syncing to the legacy database.

"""
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist

from clones.models import Clone
from experiments.models import (ExperimentWell, ExperimentPlate,
                                ManualScoreCode)
from library.models import LibraryPlate, LibraryWell
from worms.models import WormStrain
from dbmigration.helpers.name_getters import (get_library_plate_name,
                                              get_library_well_name)


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
    legacy_plate_name = get_library_plate_name(legacy_plate_name)

    try:
        return LibraryPlate.objects.get(id=legacy_plate_name)

    except ObjectDoesNotExist:
        raise ObjectDoesNotExist(get_missing_object_message(
            'LibraryPlate', id=legacy_plate_name))


def get_library_well(legacy_plate_name, well):
    """Get a library well from its legacy plate name and well."""
    library_well_name = get_library_well_name(legacy_plate_name, well)

    try:
        return LibraryWell.objects.get(id=library_well_name)

    except ObjectDoesNotExist:
        raise ObjectDoesNotExist(get_missing_object_message(
            'LibraryWell', id=library_well_name))


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


def get_experiment_plate(exp_id):
    """Get an experiment plate from its id."""
    try:
        return ExperimentPlate.objects.get(id=exp_id)

    except ObjectDoesNotExist:
        raise ObjectDoesNotExist(get_missing_object_message(
            'ExperimentPlate', id=exp_id))


def get_experiment_well(exp_id, well):
    try:
        return ExperimentWell.objects.get(
            experiment_plate_id=exp_id, well=well)

    except ObjectDoesNotExist:
        raise ObjectDoesNotExist(get_missing_object_message(
            'ExperimentWell', experiment_plate_id=exp_id, well=well))


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
