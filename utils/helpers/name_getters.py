def get_ahringer_384_plate_name(chromosome, plate_number):
    return '{}-{}'.format(chromosome, plate_number)


def get_vidal_clone_name(orfeome_plate_name, orfeome_well):
    return '{}@{}'.format(orfeome_plate_name, orfeome_well)


def get_library_well_name(plate_name, well):
    return '{}_{}'.format(plate_name, well)
