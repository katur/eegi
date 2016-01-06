"""
Functions to enfore certain clone naming conventions.
"""


def generate_vidal_clone_name(orfeome_plate, orfeome_well):
    return '{}@{}'.format(orfeome_plate, orfeome_well)
