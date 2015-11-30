from experiments.models import Experiment
from utils.comparison import get_closest_candidate


def get_all_dates(experiment_filters):
    """Get a list of dates among the Experiments that match filters."""
    return (Experiment.objects.filter(**experiment_filters)
            .order_by('-plate__date')
            .values_list('plate__date', flat=True)
            .distinct())


def get_all_temperatures(experiment_filters):
    """Get a list of temperatures among Experiments that match filters."""
    return (Experiment.objects.filter(**experiment_filters)
            .order_by('plate__temperature')
            .values_list('plate__temperature', flat=True)
            .distinct())


def get_closest_temperature(goal, experiment_filters):
    """Get the temperature that is closest to goal among the Experiments
    that match filters."""
    options = get_all_temperatures(experiment_filters)
    return get_closest_candidate(goal, options)
