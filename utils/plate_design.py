"""Utility module to help with designing new plates."""

from constants import NUM_WELLS_96
from plate_layout import get_well_list, is_symmetric, get_random_wells


def assign_to_plates(l, vertical=False,
                     empties_per_plate=0,
                     empties_limit=None,
                     already_used_empties=set()):
    """Assign the items of l to 96-format plates.

    Fill order determined by optional 'vertical' parameter.

    Optionally assign empties_per_plate random, empty wells per plate
    (defaults to 0). If there are empty wells to be assigned, enforces
    that no two plates will have the same pattern (and that no plate
    will have a pattern already existing in optional parameter
    already_used_empties).

    """
    def add_new_plate(plates, empties_per_plate, already_used_empties):
        """Add a new plate to plates, generating new empty wells."""
        plates.append([])
        empties = []
        if empties_per_plate:
            while True:
                empties = tuple(sorted(get_random_wells(empties_per_plate)))
                if (not is_symmetric(empties) and
                        empties not in already_used_empties):
                    already_used_empties.add(empties)
                    break
        return empties

    well_list = get_well_list(vertical=vertical)
    plates = []
    empties = []
    empties_so_far = 0

    for item in l:
        if not plates or len(plates[-1]) >= NUM_WELLS_96:
            if empties_limit:
                while empties_so_far + empties_per_plate > empties_limit:
                    empties_per_plate -= 1
            empties = add_new_plate(plates, empties_per_plate,
                                    already_used_empties)
            empties_so_far += len(empties)

        current_well = well_list[len(plates[-1])]

        while current_well in empties:
            plates[-1].append(None)

            if len(plates[-1]) >= NUM_WELLS_96:
                if empties_limit:
                    while empties_so_far + empties_per_plate > empties_limit:
                        empties_per_plate -= 1
                empties = add_new_plate(plates, empties_per_plate,
                                        already_used_empties)
                empties_so_far += len(empties)

            current_well = well_list[len(plates[-1])]

        plates[-1].append(item)

    while len(plates[-1]) < NUM_WELLS_96:
        plates[-1].append(None)

    zipped = []
    for plate in plates:
        zipped.append(zip(well_list, plate))

    return zipped


def get_plate_assignment_rows(plates):
    """Transform nested dictionary 'plates' to rows for nicer tabular output

    Each rows lists the plate assigned to, the well assigned to,
    and the item.

    Parameter 'plates' must be in format as returned by assign_to_plates.

    """
    rows = []

    for plate_index, plate in enumerate(plates):
        for well, item in plate:
            rows.append((plate_index, well, item))

    return rows


def get_empties_from_list_of_lists(l):
    """List the positions in which a list of lists is 'None'.

    This is useful for cherry picking, to list the empty wills separately.

    """
    e = []
    for outer_i, nested_l in enumerate(l):
        empties = [i for i, item in enumerate(nested_l) if item is None]
        e.append((outer_i, empties))
    return e
