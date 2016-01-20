from django.contrib.auth.decorators import permission_required
from django.shortcuts import redirect, render

from experiments.helpers.create import save_new_experiment_plate_and_wells
from experiments.models import Experiment, ExperimentPlate
from experiments.forms import NewExperimentPlateAndWellsForm
from library.models import LibraryPlate


@permission_required(['experiments.change_experiment',
                      'experiments.change_experimentplate]'])
def update_experiment_plates_and_wells(request):
    """Render the page to update bulk experiment plates (and wells)."""
    experiment_plates = None
    if request.GET:
        plate_filter_form = ExperimentPlateFilterForm(request.GET)
        if plate_filter_form.is_valid():
            experiment_plates = (plate_filter_form
                                 .cleaned_data['experiment_plates'])


@permission_required(['experiments.add_experiment',
                      'experiments.add_experimentplate'])
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
