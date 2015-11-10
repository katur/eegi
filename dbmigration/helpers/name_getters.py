def get_ahringer_384_plate_name(chromosome, plate_number):
    return '{}-{}'.format(chromosome, plate_number)


def get_library_plate_name(legacy_plate_name):
    # par-1 allele is misspelled in the legacy database. Fix this.
    legacy_plate_name = legacy_plate_name.replace('zc310', 'zu310')

    # Some plate names (e.g. secondary plates) include underscores
    # in the legacy database. This is now confusing, since plate
    # wells will now be named plate_well. So change underscores to
    # dashes.
    legacy_plate_name = legacy_plate_name.replace('_', '-')

    # Vidal rearray plates were named simply 1-21 in the
    # legacy database. Change this to be more clear.
    if legacy_plate_name.isdigit():
        legacy_plate_name = 'vidal-{}'.format(legacy_plate_name)

    return legacy_plate_name


def get_library_well_name(plate_name, well):
    return '{}_{}'.format(plate_name, well)


def get_vidal_clone_name(orfeome_plate_name, orfeome_well):
    return '{}@{}'.format(orfeome_plate_name, orfeome_well)
