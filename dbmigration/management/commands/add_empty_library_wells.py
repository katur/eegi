from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand

from dbmigration.helpers.object_getters import get_library_plate
from library.models import LibraryStock
from library.helpers.naming import generate_library_stock_name
from utils.plates import get_well_set, get_384_parent_well
from utils.scripting import require_db_write_acknowledgement


class Command(BaseCommand):
    """
    Command to add empty (no intended clone) library wells to the database.

    This is not one of the legacy database syncing steps, because
    empty library wells were not represented in the legacy database.

    It is useful to have empty wells represented in the database.
    This is because these wells are still photographed, and there
    are cases where despite there being no intended clone according
    to the library manufacturer, we do have bacteria that grows in the
    well, whose identity can be resolved through sequencing.
    """

    help = 'Add empty (i.e. no intended clone) library wells to the database.'

    def handle(self, **options):
        require_db_write_acknowledgement()

        all_wells = get_well_set()

        # Get all wells, to determine which wells are missing.
        #
        # Skip 384-well plates, since the empty wells from these Ahringer
        # parent plates can be created in concert with their 96-well children.
        #
        # Also skip 'GHR-' style plates. Since we don't actually have these
        # plates in the lab, we only care about the small fraction of the
        # wells from these plates that were used to generated our Vidal
        # rearrays.
        library_stocks = (LibraryStock.objects
                          .filter(plate__number_of_wells=96)
                          .exclude(plate__id__startswith='GHR-'))

        plate_wells = {}

        for library_stock in library_stocks:
            if library_stock.plate not in plate_wells:
                plate_wells[library_stock.plate] = set()

            plate_wells[library_stock.plate].add(library_stock.well)

        for library_plate in plate_wells:
            missing_wells = all_wells - plate_wells[library_plate]

            for missing_well in missing_wells:
                library_stock = LibraryStock(
                    id=generate_library_stock_name(library_plate.id,
                                                   missing_well),
                    plate=library_plate, well=missing_well,
                    parent_stock=None, intended_clone=None,
                )

                if library_plate.is_ahringer_96_plate():
                    parent_stock = _get_ahringer_384_parent(library_stock)

                    if parent_stock.intended_clone:
                        self.stderr.write(
                            '384 well {} has a non-null intended clone, '
                            'but its 96-well derivative {} is empty\n'
                            .format(parent_stock, library_stock))

                    library_stock.parent_stock = parent_stock

                library_stock.save()


def _get_ahringer_384_parent(child_stock):
    """
    Get the 384-format LibraryStock corresponding to a 96-format child stock.

    Assumes standard Ahringer naming conventions.

    If the parent doesn't exist, creates it, assuming same parent
    as the child.
    """
    child_plate_parts = child_stock.plate.id.split('-')
    parent_plate_name = child_plate_parts[0] + '-' + child_plate_parts[1]
    parent_plate = get_library_plate(parent_plate_name)

    child_well = child_stock.well
    parent_well = get_384_parent_well(child_plate_parts[2], child_well)

    parent_pk = generate_library_stock_name(parent_plate_name, parent_well)

    try:
        parent_stock = LibraryStock.objects.get(pk=parent_pk)

    except ObjectDoesNotExist:
        parent_stock = LibraryStock(
            id=parent_pk,
            plate=parent_plate,
            well=parent_well,
            parent_stock=None,
            intended_clone=child_stock.intended_clone,
        )

        parent_stock.save()

    return parent_stock
