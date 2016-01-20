from django.contrib.auth.decorators import permission_required
from django.shortcuts import redirect, render

from experiments.helpers.create import save_new_experiment_plate_and_wells
from experiments.models import Experiment, ExperimentPlate
from experiments.forms import AddExperimentPlateForm
from library.models import LibraryPlate


@permission_required(['experiments.change_experiment',
                      'experiments.change_experimentplate'])
def change_experiment_plates(request, pks):
    """Render the page to update bulk experiment plates (and wells)."""
    pks = pks.split(',')

    plates = ExperimentPlate.objects.filter(pk__in=pks)

    context = {
        'experiment_plates': plates,
    }

    return render(request, 'change_experiment_plates.html', context)


@permission_required(['experiments.add_experiment',
                      'experiments.add_experimentplate'])
def add_experiment_plate(request):
    """Render the page to add a new experiment plate (and wells)."""
    if request.POST:
        form = AddExperimentPlateForm(request.POST)

        if form.is_valid():
            data = form.cleaned_data
            plate_id = data['plate_id']
            library_plate = LibraryPlate.objects.get(
                pk=data['library_plate'])
            save_new_experiment_plate_and_wells(
                plate_id,
                data['screen_stage'],
                data['date'],
                data['temperature'],
                data['worm_strain'],
                library_plate,
                data['is_junk'],
                data['plate_comment'],
                data['well_comment'])

            plate = ExperimentPlate.objects.get(id=plate_id)

            return redirect('experiment_plate_url', plate_id)

    else:
        form = AddExperimentPlateForm()

    context = {
        'form': form,
    }

    return render(request, 'add_experiment_plate.html', context)
