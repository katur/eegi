import random

from library.helpers.constants import (ROWS_96, COLS_96, NUM_WELLS_96,
                                       ROWS_384, COLS_384, NUM_WELLS_384)
from library.helpers.plate_layout import get_well_list, is_symmetric
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


def assign_to_plates(l, vertical=False, empties_per_plate=0,
                     already_used_empties=set()):
    '''
    Assign the items of l to 96-format plates.

    Fill order determined by optional 'vertical' parameter.

    Optionally assign empties_per_plate random, empty wells per plate
    (defaults to 0). If there are empty wells to be assigned, enforces
    that no two plates will have the same pattern (and that no plate
    will have a pattern already existing in optional parameter
    already_used_empties).

    '''
    def add_new_plate(plates, empties_per_plate, already_used_empties):
        '''
        Add a new plate to plates, generating new empty wells.

        '''
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

    for item in l:
        if not plates or len(plates[-1]) >= NUM_WELLS_96:
            empties = add_new_plate(plates, empties_per_plate,
                                    already_used_empties)

        current_well = well_list[len(plates[-1])]

        while current_well in empties:
            plates[-1].append(None)

            if len(plates[-1]) >= NUM_WELLS_96:
                empties = add_new_plate(plates, empties_per_plate,
                                        already_used_empties)
            current_well = well_list[len(plates[-1])]

        plates[-1].append(item)

    while len(plates[-1]) < 96:
        plates[-1].append(None)

    zipped = []
    for plate in plates:
        zipped.append(zip(well_list, plate))

    return zipped


def get_plate_assignment_rows(plates):
    '''
    Get rows corresponding to a plate assignment. Each rows lists the item,
    the plate assigned to, and the well assigned to.

    'plates' param must be in format as returned by assign_to_plates

    '''
    rows = []

    for plate_index, plate in enumerate(plates):
        for well, item in plate:
            rows.append((plate_index, well, item))

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
