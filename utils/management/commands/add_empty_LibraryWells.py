import sys

from utils.helpers.well_tile_conversion import (get_96_well_set,
                                                get_384_position,
                                                is_ahringer_96_plate)
from utils.helpers.name_getters import get_library_well_name
from utils.helpers.object_getters import get_library_plate

from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand

from library.models import LibraryWell


class Command(BaseCommand):
    help = ('Add empty wells to LibraryWell')

    def handle(self, *args, **options):
        proceed = False
        while not proceed:
            sys.stdout.write('This script modifies the database. '
                             'Proceed? (yes/no): ')
            response = raw_input()
            if response == 'no':
                sys.stdout.write('Okay. Goodbye!\n')
                sys.exit(0)
            elif response != 'yes':
                sys.stdout.write('Please try again, '
                                 'responding "yes" or "no"\n')
                continue
            else:
                proceed = True

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
                    well.parent = get_384_parent_well(well)

                well.save()


def get_missing_wells(present, complete):
    return complete - present


def get_384_parent_well(well):
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
