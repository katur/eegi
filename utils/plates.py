"""Utility module to help work with plates (e.g. library plates and
experiment platse).

This module includes functions to:

    - Retrieve all wells in a 96-well or 384-well plate, in various formats
      (as a list sorted by column first; as a list sorted by row first;
       as a set; as a 2D array; etc)

    - Translate between 96-format and 384-format positions.

    - Get random wells. Useful for adding random empty wells to a new library
      plate, or for scoring random wells in a plate.

    - Calculate which well is symmetric to a given well. Useful for
      designing plates with asymmetric empty well patterns, and for
      fixing plates accidentally flipped 180 degrees.

"""

import random

from constants import get_rows_and_cols, ROWS_96, ROWS_384
from wells import get_well_name, is_proper_well_name


def get_well_list(is_384=False, vertical=False):
    """Get a list of all wells.

    is_384 param determines if the well list should be for 384-format plates,
    or 96-format plates. Defaults to 96-format plates.

    vertical param determines whether to list first by column or by row:
        - with vertical=False (the default), the order is:
            ['A01', 'A02', ..., 'A12', 'B01', 'B02', ..., 'B12', ...,
             'H01', 'H02', ..., 'H12']

        - with vertical=True, the order is:
            ['A01', 'B01', ..., 'H01', 'A02', 'B02', ..., 'H02', ...,
             'A12', 'B12', ..., 'H12']

    """
    rows, cols = get_rows_and_cols(is_384)

    if vertical:
        return _get_well_list_vertical(rows, cols)
    else:
        return _get_well_list_horizontal(rows, cols)


def _get_well_list_vertical(rows, columns):
    """Helper to get wells in 'vertical' order."""
    wells = []
    for column in columns:
        for row in rows:
            wells.append(get_well_name(row, column))
    return wells


def _get_well_list_horizontal(rows, columns):
    """Helper to get wells in 'horizontal' order."""
    wells = []
    for row in rows:
        for column in columns:
            wells.append(get_well_name(row, column))
    return wells


def get_well_set(is_384=False):
    """Get a set of all wells.

    is_384 param determines if the well list should be for 384-format plates,
    or 96-format plates. Defaults to 96-format plates.

    """
    return set(get_well_list(is_384=is_384))


def get_well_grid(is_384=False):
    """Get a 2D array representing the wells in one plate.

    is_384 param determines if the well list should be for 384-format
    plates, or 96-format plates. Defaults to 96-format.

    """
    rows, cols = get_rows_and_cols(is_384)

    plate = []
    for row in rows:
        this_row = []
        for column in cols:
            well = get_well_name(row, column)
            this_row.append(well)

        plate.append(this_row)

    return plate


def get_symmetric_well(well, is_384=False):
    """Get the well that is symmetric to the provided well.

    Well A is symmetric to well B if the two would swap positions if the
    plate were flipped 180 degrees.

    """
    if not is_proper_well_name(well):
        raise ValueError('{} is an improper well name'.format(well))

    rows, cols = get_rows_and_cols(is_384)

    row_idx = (len(rows) - 1) - rows.index(well[0])
    row = rows[row_idx]
    col = (len(cols) + 1) - int(well[1:])
    return get_well_name(row, col)


def is_symmetric(wells, is_384=False):
    """Determine if a list of wells create a symmetrical pattern.

    Symmetry requires that for each well present in wells, its
    symmetric well is also present.

    """
    for well in wells:
        s = get_symmetric_well(well, is_384=is_384)
        if s not in wells:
            return False

    return True


def get_random_well(is_384=False):
    """Get a random well."""
    rows, cols = get_rows_and_cols(is_384)
    row = random.choice(rows)
    col = random.choice(cols)
    return get_well_name(row, col)


def get_random_wells(count, is_384=False):
    """Get unique, random wells (number determined by count parameter).

    count must be between 0 and number of wells in a plate, inclusive.

    """
    if is_384:
        upper = 384
    else:
        upper = 96
    if count < 0 or count > upper:
        raise ValueError('count must be between 0 and {}, inclusive'
                         .format(upper))

    wells = set()
    for i in range(count):
        found = False
        while not found:
            well = get_random_well(is_384)
            if well not in wells:
                found = True
                wells.add(well)
    return wells


def assign_to_plates(l, vertical=False, is_384=False,
                     empties_per_plate=0, empties_limit=None,
                     already_used_empties=set()):
    """Assign the items of l to plates.

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

    if is_384:
        num_wells = 384
    else:
        num_wells = 96

    well_list = get_well_list(vertical=vertical)
    plates = []
    empties = []
    empties_so_far = 0

    for item in l:
        if not plates or len(plates[-1]) >= num_wells:
            if empties_limit:
                while empties_so_far + empties_per_plate > empties_limit:
                    empties_per_plate -= 1
            empties = add_new_plate(plates, empties_per_plate,
                                    already_used_empties)
            empties_so_far += len(empties)

        current_well = well_list[len(plates[-1])]

        while current_well in empties:
            plates[-1].append(None)

            if len(plates[-1]) >= num_wells:
                if empties_limit:
                    while empties_so_far + empties_per_plate > empties_limit:
                        empties_per_plate -= 1
                empties = add_new_plate(plates, empties_per_plate,
                                        already_used_empties)
                empties_so_far += len(empties)

            current_well = well_list[len(plates[-1])]

        plates[-1].append(item)

    while len(plates[-1]) < num_wells:
        plates[-1].append(None)

    zipped = []
    for plate in plates:
        zipped.append(zip(well_list, plate))

    return zipped


def get_plate_assignment_rows(plates):
    """Transform nested dictionary 'plates' to rows for tabular output.

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

    This is useful for cherrypicking, to list empty wells separately.

    """
    e = []
    for outer_i, nested_l in enumerate(l):
        empties = [i for i, item in enumerate(nested_l) if item is None]
        e.append((outer_i, empties))
    return e


def get_384_parent_well(child_quadrant, child_position):
    """Get the 384-format position corresponding to a 96-format child
    position.

    Uses the child's quadrant (A1, A2, B1, or B2) and the child's position
    to calculate this.

    """
    if child_quadrant[0] == 'A':
        odd_row = True
    else:
        odd_row = False

    if child_quadrant[1] == '1':
        odd_column = True
    else:
        odd_column = False

    child_row = child_position[0]
    child_row_index = ROWS_96.index(child_row)
    parent_row_index = child_row_index * 2
    if not odd_row:
        parent_row_index += 1
    parent_row = ROWS_384[parent_row_index]

    child_column = int(child_position[1:])
    parent_column = child_column * 2
    if odd_column:
        parent_column -= 1

    return get_well_name(parent_row, parent_column)
