from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist

from clones.models import Clone
from experiments.models import ExperimentPlate, ManualScoreCode
from library.models import LibraryPlate, LibraryWell
from worms.models import WormStrain
from dbmigration.helpers.name_getters import get_library_plate_name


def get_missing_object_message(klass, **kwargs):
    return ('ERROR: {} with {} not found in the new database\n'
            .format(klass, str(kwargs)))


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


def get_library_plate(legacy_plate_name):
    """Get a library plate from its plate name."""
    legacy_plate_name = get_library_plate_name(legacy_plate_name)

    try:
        return LibraryPlate.objects.get(id=legacy_plate_name)

    except ObjectDoesNotExist:
        raise ObjectDoesNotExist(get_missing_object_message(
            'LibraryPlate', id=legacy_plate_name))


def get_experiment_plate(experiment_plate_id):
    """Get an experiment plate from its id."""
    try:
        return ExperimentPlate.objects.get(id=experiment_plate_id)

    except ObjectDoesNotExist:
        raise ObjectDoesNotExist(get_missing_object_message(
            'ExperimentPlate', id=experiment_plate_id))


def get_score_code(score_code_id):
    """Get a score code from its id."""
    try:
        return ManualScoreCode.objects.get(id=score_code_id)

    except ObjectDoesNotExist:
        raise ObjectDoesNotExist(get_missing_object_message(
            'ManualScoreCode', id=score_code_id))


def get_user(username):
    """Get a user from its username."""
    if username == 'Julie':
        username = 'julie'

    if username == 'patricia':
        username = 'giselle'

    try:
        return User.objects.get(username=username)

    except ObjectDoesNotExist:
        raise ObjectDoesNotExist(get_missing_object_message(
            'User', username=username))


def get_clone(clone_name):
    """Get a clone from its clone name."""
    try:
        return Clone.objects.get(id=clone_name)

    except ObjectDoesNotExist:
        raise ObjectDoesNotExist(get_missing_object_message(
            'Clone', id=clone_name))


def get_library_well(library_well_name):
    """Get a library well from its name."""
    try:
        return LibraryWell.objects.get(id=library_well_name)

    except ObjectDoesNotExist:
        raise ObjectDoesNotExist(get_missing_object_message(
            'LibraryWell', id=library_well_name))
