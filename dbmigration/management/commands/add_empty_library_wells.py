"""Command to add empty (i.e. no intended clone) library wells to the database.

This is not one of the steps of syncing to the legacy database,
because empty library wells were not represented in the legacy database.

It is useful to have empty wells represented in the database.
This is because these wells are still photographed, and there
are cases where despite there being no intended clone according
to the library manufacturer, we do have bacteria that grows in the
well, whose identity can be resolved through sequencing.

"""

from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand

from dbmigration.helpers.name_getters import get_library_well_name
from dbmigration.helpers.object_getters import get_library_plate
from library.models import LibraryWell
from utils.plate_layout import get_96_well_set, get_384_position
from utils.scripting import require_db_write_acknowledgement

HELP = 'Add empty (i.e. no intended clone) library wells to the database.'


class Command(BaseCommand):
    help = HELP

    def handle(self, **options):
        require_db_write_acknowledgement()

        wells_96 = get_96_well_set()

        # Do not add empty wells for the 'GHR-' style plates, since we don't
        # have these plates in the lab (they are the original plates from
        # which our Vidal rearrays were generated).
        library_wells = (LibraryWell.objects.filter(plate__number_of_wells=96)
                         .exclude(plate__id__startswith='GHR-'))

        plate_wells = {}

        for library_well in library_wells:
            if library_well.library_plate not in plate_wells:
                plate_wells[library_well.library_plate] = set()

            plate_wells[library_well.library_plate].add(library_well.well)

        for library_plate in plate_wells:
            missing_wells = wells_96 - plate_wells[library_plate]

            for missing_well in missing_wells:
                library_well = LibraryWell(
                    id=get_library_well_name(library_plate.id, missing_well),
                    plate=library_plate,
                    well=missing_well,
                    parent_library_well=None,
                    intended_clone=None,
                )

                if library_plate.is_ahringer_96_plate():
                    parent_well = get_ahringer_384_parent_well(library_well)

                    if parent_well.intended_clone:
                        self.stderr.write(
                            '384 well {} has a non-null intended clone, '
                            'but its 96-well derivative {} is empty\n'
                            .format(parent_well, library_well))

                    library_well.parent_library_well = parent_well

                library_well.save()


def get_ahringer_384_parent_well(child_well):
    """Get the 384 format well from which a particular 96 format well is
    derived, assuming standard Ahringer naming.

    If the parent doesn't exist, creates it, assuming same parent
    as the child.

    """
    child_plate_parts = child_well.plate.id.split('-')
    parent_plate_name = child_plate_parts[0] + '-' + child_plate_parts[1]
    parent_plate = get_library_plate(parent_plate_name)

    child_position = child_well.well
    parent_position = get_384_position(child_plate_parts[2], child_position)

    parent_well_pk = get_library_well_name(parent_plate_name, parent_position)

    try:
        parent_well = LibraryWell.objects.get(pk=parent_well_pk)

    except ObjectDoesNotExist:
        parent_well = LibraryWell(
            id=parent_well_pk,
            plate=parent_plate,
            well=parent_position,
            parent_library_well=None,
            intended_clone=child_well.intended_clone,
        )

        parent_well.save()

    return parent_well
