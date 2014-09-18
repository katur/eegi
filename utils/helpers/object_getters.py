from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist

from worms.models import WormStrain
from clones.models import Clone
from library.models import LibraryPlate, LibraryWell
from experiments.models import Experiment, ManualScoreCode


def get_worm_strain(mutant, mutantAllele):
    """
    Get a worm strain from new database,
    from its mutant gene and mutant allele.

    Exists with an error if the worm strain is not present.
    """
    try:
        if mutant == 'N2':
            gene = None
            allele = None
            worm_strain = WormStrain.objects.get(id='N2')
        else:
            gene = mutant
            allele = mutantAllele
            if allele == 'zc310':
                allele = 'zu310'
            worm_strain = WormStrain.objects.get(gene=gene, allele=allele)
        return worm_strain

    except ObjectDoesNotExist:
        raise ObjectDoesNotExist(get_missing_object_message(
            'WormStrain', gene=mutant, allele=mutantAllele))


def get_library_plate(library_plate_name):
    """
    Get a library plate from the new database, from its plate name.

    Exits with an error if the plate is not present.
    """
    try:
        return LibraryPlate.objects.get(id=library_plate_name)

    except ObjectDoesNotExist:
        raise ObjectDoesNotExist(get_missing_object_message(
            'LibraryPlate', id=library_plate_name))


def get_experiment(experiment_id):
    try:
        return Experiment.objects.get(id=experiment_id)
    except ObjectDoesNotExist:
        raise ObjectDoesNotExist(get_missing_object_message(
            'Experiment', id=experiment_id))


def get_score_code(score_code_id):
    try:
        return ManualScoreCode.objects.get(id=score_code_id)
    except ObjectDoesNotExist:
        raise ObjectDoesNotExist(get_missing_object_message(
            'ManualScoreCode', id=score_code_id))


def get_user(username):
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
    try:
        return Clone.objects.get(id=clone_name)
    except ObjectDoesNotExist:
        raise ObjectDoesNotExist(get_missing_object_message(
            'Clone', id=clone_name))


def get_library_well(library_well_name):
    try:
        return LibraryWell.objects.get(id=library_well_name)
    except ObjectDoesNotExist:
        raise ObjectDoesNotExist(get_missing_object_message(
            'LibraryWell', id=library_well_name))


def get_missing_object_message(klass, **kwargs):
    return ('ERROR: {} with {} not found in the new database\n'
            .format(klass, str(kwargs)))
