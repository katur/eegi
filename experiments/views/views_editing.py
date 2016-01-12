from django.contrib.auth.decorators import permission_required
from django.shortcuts import redirect, render

from experiments.helpers.create import save_new_experiment_plate_and_wells
from experiments.models import Experiment, ExperimentPlate
from experiments.forms import NewExperimentPlateAndWellsForm
from library.models import LibraryPlate


@permission_required(['experiments.add_experiment',
                      'experiments.add_experimentplage'])
def new_experiment_plate_and_wells(request):
    """Render the page to add a new experiment plate (and wells)."""

    if request.POST:
        form = NewExperimentPlateAndWellsForm(request.POST)

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
        form = NewExperimentPlateAndWellsForm()

    context = {
        'form': form,
    }

    return render(request, 'new_experiment_plate.html', context)
