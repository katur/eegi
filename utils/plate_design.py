"""Utility module to help with designing plates (e.g. library plates).

This module includes functions to:

    - Select random wells. This is useful when designing new frozen
      bacteria plates, when we want some empty wells to create
      a recognizable pattern whenever the bacteria is replicated.

    - Assign items to plate positions. This is useful e.g. for
      rearraying positives from the Primary screen into Secondary
      plates, and rearraying clones that need to be resequenced into
      PCR plates.

"""

import random

from constants import (ROWS_96, COLS_96, NUM_WELLS_96,
                       ROWS_384, COLS_384, NUM_WELLS_384)
from plate_layout import get_well_list, is_symmetric
from well_naming import get_well_name


def get_random_well(is_384=False):
    """Get a random 96-format well."""
    if is_384:
        rows = ROWS_384
        cols = COLS_384
    else:
        rows = ROWS_96
        cols = COLS_96

    row = random.choice(rows)
    col = random.choice(cols)
    return get_well_name(row, col)


def get_random_wells(count, is_384=False):
    """Get unique, random wells (number determined by count parameter).

    count must be between 0 and number of wells in a plate, inclusive.

    """
    if is_384:
        upper = NUM_WELLS_384
    else:
        upper = NUM_WELLS_96

    if count < 0 or count > upper:
        raise ValueError('count must be between 0 and {}, inclusive'
                         .format(upper))

    wells = set()
    for i in range(count):
        found = False
        while not found:
            well = get_random_well(is_384=is_384)
            if well not in wells:
                found = True
                wells.add(well)
    return wells


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

    while len(plates[-1]) < 96:
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
