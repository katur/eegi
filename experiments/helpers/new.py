from experiments.models import ExperimentPlate


# TODO: consider making this an ExperimentPlate class method
def save_new_experiment_plate_and_wells(
        experiment_plate_id, screen_stage, date, temperature,
        worm_strain, library_plate, is_junk=False,
        plate_comment='', dry_run=False):
    """
    Save a new experiment plate and its 96 wells.

    Assumes that the experiment plate:
        1) contains the same worm strain in all wells
        2) is derived from one library plate
        3) has the same is_junk value in all wells

    By default, the plate and wells are saved to the database.
    Set dry_run=True to instead do a dry run.
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

    experiment.create_experiment_wells(worm_strain, library_plate,
                                      is_junk=is_junk, dry_run=dry_run)
