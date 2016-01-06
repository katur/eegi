from experiments.models import Experiment, ExperimentPlate
from library.models import LibraryStock
from utils.comparison import get_closest_candidate
from utils.name_getters import get_experiment_name, get_library_stock_name
from utils.plates import get_well_list


def save_experiment_plate_and_wells(
        experiment_plate_id, screen_stage, date, temperature,
        worm, library_plate_id, is_junk=0,
        plate_comment='', well_comment='',
        dry_run=False):
    """
    Save a new experiment plate and its 96 wells.

    Assumes that the experiment plate:
        1) contains the same worm strain in all wells
        2) is derived from one library plate
        3) has the same is_junk value in all wells
    """
    if ExperimentPlate.objects.filter(id=experiment_plate_id).count():
        raise ValueError('ExperimentPlate {} already exists'
                         .format(experiment_plate_id))

    if Experiment.objects.filter(
            plate_id=experiment_plate_id).count():
        raise ValueError('Experiment well for plate {} already exists'
                         .format(experiment_plate_id))

    experiment_plate = ExperimentPlate(
        id=experiment_plate_id,
        screen_stage=screen_stage,
        temperature=temperature,
        date=date,
        comment=plate_comment)

    if not dry_run:
        experiment_plate.save()

    for well in get_well_list():
        experiment_id = get_experiment_name(experiment_plate_id, well)

        library_stock_name = get_library_stock_name(library_plate_id, well)

        library_stock = LibraryStock.objects.get(id=library_stock_name)

        experiment_well = Experiment(
            id=experiment_id,
            plate=experiment_plate,
            well=well,
            worm_strain=worm,
            library_stock=library_stock,
            is_junk=is_junk,
            comment=well_comment)

        if not dry_run:
            experiment_well.save()
