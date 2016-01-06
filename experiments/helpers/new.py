from experiments.models import Experiment, ExperimentPlate
from experiments.helpers.naming import generate_experiment_id
from library.models import LibraryPlate
from library.helpers.naming import generate_library_stock_name
from utils.comparison import get_closest_candidate
from utils.plates import get_well_list


def save_new_experiment(experiment_plate, well, worm, library_stock,
                        is_junk=False, comment='', dry_run=False):
    """
    Create a new experiment well instance.

    By default, the instance is saved to the database.
    Set dry_run=True to instead do a dry run.
    """
    if Experiment.objects.filter(plate=experiment_plate, well=well).count():
        raise ValueError('Experiment for plate {}, well {} already exists'
                         .format(experiment_plate, well))

    experiment_well = Experiment(
        id=generate_experiment_id(experiment_plate.id, well),
        plate=experiment_plate,
        well=well,
        worm_strain=worm,
        library_stock=library_stock,
        is_junk=is_junk,
        comment=comment)

    if not dry_run:
        experiment_well.save()


def save_new_experiment_plate_and_wells(
        experiment_plate_id, screen_stage, date, temperature,
        worm, library_plate, is_junk=False,
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

    experiment_plate = ExperimentPlate(
        id=experiment_plate_id,
        screen_stage=screen_stage,
        temperature=temperature,
        date=date,
        comment=plate_comment)

    if not dry_run:
        experiment_plate.save()

    stocks_by_well = library_plate.get_stocks_as_dictionary()

    for well in get_well_list():
        library_stock = stocks_by_well[well]

        save_new_experiment(experiment_plate, well, worm, library_stock,
                            is_junk=is_junk, comment=well_comment,
                            dry_run=dry_run)
