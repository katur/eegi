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


def get_well_list(vertical=False, is_384=False):
    """Get a list of all wells.

    vertical param determines whether to list first by column or by row.

    is_384 param determines if the well list should be for 384-format plates,
    or 96-format plates.

    """
    if is_384:
        rows = ROWS_384
        cols = COLS_384
    else:
        rows = ROWS_96
        cols = COLS_96

    if vertical:
        return get_well_list_vertical(rows, cols)
    else:
        return get_well_list_horizontal(rows, cols)


def get_well_list_vertical(rows, columns):
    """Get a list of all wells derived from the provided rows and columns,
    listed in 'vertical' order:

        ['A01', 'B01', ..., 'H01', 'A02', 'B02', ..., 'H02', ...,
         'A12', 'B12', ..., 'H12']

    """
    wells = []
    for column in columns:
        for row in rows:
            wells.append(get_well_name(row, column))
    return wells


def get_well_list_horizontal(rows, columns):
    """Get a list of all wells derived from the provided rows and columns,
    listed in 'horizontal' order:

        ['A01', 'A02', ..., 'A12', 'B01', 'B02', ..., 'B12', ...,
         'H01', 'H02', ..., 'H12']

    """
    wells = []
    for row in rows:
        for column in columns:
            wells.append(get_well_name(row, column))
    return wells


def get_96_well_set():
    """Get a set of all standard 96-plate well names: 'A01', ..., 'H12'"""
    return get_well_set(ROWS_96, COLS_96)


def get_384_well_set():
    """Get a set of all standard 384-plate well names: 'A01', ..., 'P24'"""
    return get_well_set(ROWS_384, COLS_384)


def get_well_set(rows, columns):
    """Get a set of all well names made from combining the provided rows
    and columns.

    Expects each column to be an integer with no more than 2 digits.

    """
    wells = set()
    for row in rows:
        for column in columns:
            wells.add(get_well_name(row, column))
    return wells


def get_96_grid():
    """Get a 2D array representing a 96-well plate (8 rows, 12 columns).

    Each element in the 2D array is a dictionary with 'well' and 'tile' keys
    mapping to the well name and tile name.

    """
    plate = []
    for row_index in range(NUM_ROWS_96):
        plate.append([])
        for column_index in range(NUM_COLS_96):
            row_name = ROWS_96[row_index]
            column_name = column_index + 1
            well = get_well_name(row_name, column_name)
            position_info = {
                'well': well,
                'tile': well_to_tile(well),
            }
            plate[row_index].append(position_info)

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