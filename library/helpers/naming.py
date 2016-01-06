"""
Functions to enforce certain library naming conventions.
"""


def generate_ahringer_384_plate_name(chromosome, plate_number):
    return '{}-{}'.format(chromosome, plate_number)


def generate_library_plate_name(plate_name):
    if not plate_name:
        return plate_name

    # par-1 allele is misspelled in the legacy database. Fix this.
    plate_name = plate_name.replace('zc310', 'zu310')

    # Some plate names (e.g. secondary plates) include underscores
    # in the legacy database. This is now confusing, since plate
    # wells will now be named plate_well. So change underscores to
    # dashes.
    plate_name = plate_name.replace('_', '-')

    # Vidal rearray plates were named simply 1-21 in the
    # legacy database. Change this to be more clear.
    if plate_name.isdigit():
        plate_name = 'vidal-{}'.format(plate_name)

    return plate_name


def generate_library_stock_name(plate_name, well):
    plate_name = generate_library_plate_name(plate_name)
    return '{}_{}'.format(plate_name, well)
