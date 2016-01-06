"""
Functions to enforce certain experiment naming conventions.
"""


def generate_experiment_id(plate_id, well):
    """Generate an experiment well id from its plate id and well."""
    return '{}_{}'.format(plate_id, well)
