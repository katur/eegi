"""Utility module to help work with plates (library and experiment plates).

This module includes functions to:

    - Retrieve all the wells that exist in a 96-format or 384-format
      plate, in various formats (e.g. as a list sorted by column first
      or row first, as a Python set for more speedy access,
      as a 96-well 2D array).

    - Translating between 96-format and 384-format positions. This
      is useful for figuring out what position 96-format wells
      derived from, if the 96-format plate derives from a 384-format
      plate.

    - Calculate which well is symmetric to a given well. This is useful
      for designing plates without symmetric patterns, and for fixing
      issues with plates that were accidentally flipped 180 degrees.

"""

from constants import (ROWS_96, COLS_96, NUM_ROWS_96, NUM_COLS_96,
                       ROWS_384, COLS_384)
from well_tile_conversion import well_to_tile
from well_naming import get_well_name, is_proper_well_name


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
    if is_384:
        rows = ROWS_384
        cols = COLS_384
    else:
        rows = ROWS_96
        cols = COLS_96

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

    is_384 param determines if the well list should be for 384-format plates,
    or 96-format plates. Defaults to 96-format plates (i.e., 8 rows and 12
    columns).

    Each element in the 2D array is a dictionary with 'well' and 'tile' keys
    mapping to the well name and tile name.

    """
    if is_384:
        rows = ROWS_384
        cols = COLS_384
    else:
        rows = ROWS_96
        cols = COLS_96

    plate = []
    for row in rows:
        this_row = []
        for column in cols:
            well = get_well_name(row, column)

            position_info = {
                'well': well,
                'tile': well_to_tile(well),
            }

            this_row.append(position_info)
        plate.append(this_row)

    return plate


def get_384_position(child_quadrant, child_position):
    """Get the 384-format position corresponding to a 96-format child position.

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


def get_symmetric_well(well):
    """Get the well that is symmetric to the provided well.

    Well A is symmetric to well B if the two would swap positions if the
    plate were flipped 180 degrees.

    """
    if not is_proper_well_name(well):
        raise ValueError('{} is an improper well name'.format(well))

    row_idx = (NUM_ROWS_96 - 1) - ROWS_96.index(well[0])
    row = ROWS_96[row_idx]
    col = (NUM_COLS_96 + 1) - int(well[1:])
    return get_well_name(row, col)


def is_symmetric(wells):
    """Determine if a list of wells create a symmetrical pattern.

    Symmetry requires that for each well present in wells, its symmetric well
    is also present.

    """
    for well in wells:
        s = get_symmetric_well(well)
        if s not in wells:
            return False

    return True


if __name__ == '__main__':
    print 'A1 H12 to 384: ' + get_384_position('A1', 'H12')
    print 'B1 H12 to 384: ' + get_384_position('B1', 'H12')
    print 'A2 H12 to 384: ' + get_384_position('A2', 'H12')
    print 'B2 H12 to 384: ' + get_384_position('B2', 'H12')
