from experiments.models import Experiment
from utils.comparison import get_closest_candidate


def get_all_temperatures(experiment_filters):
    """Get a list of all temperatures among the Experiment objects
    that match filters."""
    return (Experiment.objects.filter(**experiment_filters)
            .order_by('plate__temperature')
            .values_list('plate__temperature', flat=True)
            .distinct())


def get_closest_temperature(goal, experiment_filters):
    """Get the temperature that is closest to goal among the Experiment
    objects that match filters."""
    options = get_all_temperatures(experiment_filters)
    return get_closest_candidate(goal, options)
