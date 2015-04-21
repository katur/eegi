import random

from library.helpers.constants import (ROWS_96, COLS_96, NUM_WELLS_96,
                                       ROWS_384, COLS_384, NUM_WELLS_384)
from library.helpers.plate_layout import get_well_list
from library.helpers.well_naming import get_well_name


def get_random_well(is_384=False):
    '''
    Get a 96-format random well.

    '''
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
    '''
    Get random, unique wells (number determined by count parameter).
    count must be between 0 and number of wells in a plate, inclusive.

    '''
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


def assign_to_plates(l, vertical=False, num_empties=0,
                     already_used_empties=[]):
    '''
    Assign the items of l to 96-format plates.

    Fill order determined by optional 'vertical' parameter.

    Optionally assign num_empties random, empty wells per plate
    (defaults to 0). If there are empty wells to be assigned, enforces
    that no two plates will have the same pattern (and that no plate
    will have a pattern already existing in optional parameter
    already_used_empties).

    '''

    well_list = get_well_list(vertical=vertical)

    plates = []
    empties = []

    for item in l:
        if not plates or len(plates[-1]) >= NUM_WELLS_96:
            plates.append([])

            if num_empties:
                while True:
                    empties = get_random_wells(num_empties)
                    # TODO: check for empties being symmetric with itself or
                    # to any in already_used_empties
                    if empties not in already_used_empties:
                        already_used_empties.append(empties)
                        break

        current_plate = plates[-1]
        current_well = well_list[len(current_plate)]

        while current_well in empties:
            current_plate.append(None)
            current_well = well_list[len(current_plate)]

        current_plate.append(item)

    zipped = []
    for plate in plates:
        zipped.append(zip(well_list, plate))

    return zipped


def get_plate_assignment_rows(plates, include_header=False):
    rows = []

    if include_header:
        rows.append(('item', 'plate', 'well'))

    for plate_index, plate in enumerate(plates):
        for well, item in plate:
            rows.append((item, plate_index, well))

    return rows


def get_empties_from_list_of_lists(l):
    '''
    List the positions in which a list of lists is 'None'.

    This is useful for cherry picking, to list the empty wills separately.

    '''
    e = []
    for outer_i, nested_l in enumerate(l):
        empties = [i for i, item in enumerate(nested_l) if item is None]
        e.append((outer_i, empties))
    return e
