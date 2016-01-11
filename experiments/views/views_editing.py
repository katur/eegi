import os

from django.contrib.auth.decorators import permission_required
from django.shortcuts import redirect, get_object_or_404

from experiments.models import Experiment


@permission_required('experiments.change_experiment')
def experiment_toggle_junk(request, pk):
    """Toggle the junk state of the experiment with primary key pk."""
    experiment = get_object_or_404(Experiment, pk=pk)
    experiment.is_junk = not experiment.is_junk
    experiment.save()
    return redirect('experiment_url', experiment.pk)
