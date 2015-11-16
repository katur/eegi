from library.models import LibraryWell


def get_organized_library_wells(screen_stage=None):
    """Fetch all library wells from the database, organized as:

        l[plate][well] = library_well

    Optionally provide a screen_stage, to limit to the Primary or Secondary
    screen.
    """
    wells = LibraryWell.objects.select_related('plate')
    if screen_stage:
        wells = wells.filter(plate__screen_stage=screen_stage)
    else:
        wells = wells.all()

    return organize_library_wells(wells)


def organize_library_wells(library_wells):
    """Organize library_wells into the format:

        l[plate][well] = library_well
    """
    l = {}
    for library_well in library_wells:
        plate = library_well.plate
        well = library_well.well
        if plate not in l:
            l[plate] = {}
        l[plate][well] = library_well

    return l
