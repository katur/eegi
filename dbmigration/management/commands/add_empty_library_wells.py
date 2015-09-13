import sys

from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand

from dbmigration.helpers.name_getters import get_library_well_name
from dbmigration.helpers.object_getters import get_library_plate
from library.helpers.plate_layout import (get_96_well_set, get_384_position,
                                          is_ahringer_96_plate)
from library.models import LibraryWell
from utils.scripting import require_db_write_acknowledgement

HELP = '''
Add empty library wells (i.e., wells without intended clones) to the database.

These empty library wells are not added while syncing with the legacy database,
because the legacy database does not include empty wells.

It is useful to have empty wells represented in the database, if with no
intended clone. This is because these wells are still photographed,
and there are cases where despite there being no intended clone according
to the library creator, we do have bacteria that grows in the well,
whose identity can be resolved through sequencing.

'''


class Command(BaseCommand):
    help = HELP

    def handle(self, **options):
        require_db_write_acknowledgement()

        wells_96 = get_96_well_set()

        library_wells = (LibraryWell.objects.filter(plate__number_of_wells=96)
                         .exclude(plate__id__startswith='GHR-'))

        plate_wells = {}
        for well in library_wells:
            if well.plate not in plate_wells:
                plate_wells[well.plate] = set()

            plate_wells[well.plate].add(well.well)

        for plate in plate_wells:
            missing_wells = get_missing_wells(plate_wells[plate],
                                              wells_96)
            if is_ahringer_96_plate(plate.id):
                is_ahringer = True
            else:
                is_ahringer = False

            for missing_well in missing_wells:
                well = LibraryWell(
                    id=get_library_well_name(plate.id, missing_well),
                    plate=plate,
                    well=missing_well,
                    parent_library_well=None,
                    intended_clone=None,
                )

                if is_ahringer:
                    well.parent_library_well = get_384_parent_well(well)

                well.save()


def get_missing_wells(present, complete):
    return complete - present


def get_384_parent_well(well):
    """Get the 384 format well from which a particular 96 format well is
    derived, assuming standard Ahringer naming.
    """
    child_plate_parts = well.plate.id.split('-')
    parent_plate_name = child_plate_parts[0] + '-' + child_plate_parts[1]
    parent_plate = get_library_plate(parent_plate_name)

    child_position = well.well
    parent_position = get_384_position(child_plate_parts[2], child_position)

    parent_well_pk = get_library_well_name(parent_plate_name, parent_position)

    try:
        parent_well = LibraryWell.objects.get(pk=parent_well_pk)
        if parent_well.intended_clone:
            sys.stderr.write('384 well {} has a non-null intended clone, '
                             'while its 96-well derivative {} is empty\n'
                             .format(parent_well, well))

    except ObjectDoesNotExist:
        parent_well = LibraryWell(
            id=parent_well_pk,
            plate=parent_plate,
            well=parent_position,
            parent_library_well=None,
            intended_clone=None,
        )

        parent_well.save()

    return parent_well
