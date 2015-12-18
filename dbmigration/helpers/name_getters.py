"""
This module contains functions enforcing certain naming conventions.

These helpers are meant for use while syncing to the legacy database.
"""


def get_ahringer_384_plate_name(chromosome, plate_number):
    return '{}-{}'.format(chromosome, plate_number)


def get_library_plate_name(legacy_plate_name):
    if not legacy_plate_name:
        return legacy_plate_name

    # par-1 allele is misspelled in the legacy database. Fix this.
    plate_name = legacy_plate_name.replace('zc310', 'zu310')

    # Some plate names (e.g. secondary plates) include underscores
    # in the legacy database. This is now confusing, since plate
    # wells will now be named plate_well. So change underscores to
    # dashes.
    plate_name = plate_name.replace('_', '-')

    # Vidal rearray plates were named simply 1-21 in the
    # legacy database. Change this to be more clear.
    if plate_name.isdigit():
        plate_name = 'vidal-{}'.format(legacy_plate_name)

    return plate_name


def get_library_stock_name(legacy_plate_name, well):
    plate_name = get_library_plate_name(legacy_plate_name)
    return '{}_{}'.format(plate_name, well)


def get_experiment_name(experiment_plate_id, well):
    return '{}_{}'.format(experiment_plate_id, well)


def get_vidal_clone_name(orfeome_plate_name, orfeome_well):
    return '{}@{}'.format(orfeome_plate_name, orfeome_well)
