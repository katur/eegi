import random
import re

ROWS_96 = 'ABCDEFGH'
NUM_ROWS_96 = len(ROWS_96)
NUM_COLS_96 = 12
NUM_WELLS_96 = 96
COLS_96 = [i for i in range(1, NUM_COLS_96 + 1)]
BACKWARDS_ROWS_96 = 'BDFH'

ROWS_384 = 'ABCDEFGHIJKLMNOP'
NUM_ROWS_384 = len(ROWS_384)
NUM_COLS_384 = 24
NUM_WELLS_384 = 384
COLS_384 = [i for i in range(1, NUM_COLS_384 + 1)]


def get_well_name(row, column):
    '''
    Get well name (e.g. 'A05') from a row (e.g. 'A') and a column (e.g. 4).

    row_name should be a capital letter.

    column_name should be an integer.

    '''
    return '{}{}'.format(row, str(column).zfill(2))


def get_three_character_well(well):
    '''
    Return a well in 3-character format (e.g. 'A05'), whether the input is
    in 3-character format or 2-character format (e.g. 'A5').

    '''
    row = well[0]
    column = int(well[1:])
    return get_well_name(row, column)


def is_proper_well_name(well, is_384=False):
    '''
    Determine if a 96-format well is properly named.

    '''
    if len(well) != 3:
        return False

    row = well[0]

    try:
        col = int(well[1:])
    except ValueError:
        return False

    if is_384:
        rows = ROWS_384
        cols = COLS_384
    else:
        rows = ROWS_96
        cols = COLS_96

    if row not in rows or col not in cols:
        return False

    return True


def well_to_tile(well):
    '''
    Convert a well (e.g. 'B05') to a tile (e.g. 'Tile000020.bmp').

    '''
    index = well_to_index(well)
    return index_to_tile(index)


def tile_to_well(tile):
    '''
    Convert a tile (e.g. 'Tile000020.bmp') to a well (e.g. 'B05').

    '''
    index = tile_to_index(tile)
    return index_to_well(index)


def well_to_index(well):
    '''
    Convert a well (e.g. 'B05') to a 0-indexed 'snake' position in the plate
    (e.g. 19).

    '''
    if not re.match('[A-H]\d\d?', well):
        raise ValueError('Improper well string')
    row = well[0]
    column = int(well[1:])
    position_from_left = column - 1
    assert position_from_left >= 0 and position_from_left < NUM_COLS_96

    min_row_index = (ord(row) - 65) * NUM_COLS_96
    if row in BACKWARDS_ROWS_96:
        index_in_row = NUM_COLS_96 - 1 - position_from_left
    else:
        index_in_row = position_from_left

    overall_index = min_row_index + index_in_row
    return overall_index


def index_to_well(index):
    '''
    Convert a 0-indexed 'snake' position in the plate (e.g. 19)
    to a well (e.g. 'B05')

    '''
    row = ROWS_96[index / NUM_COLS_96]
    index_in_row = index % NUM_COLS_96

    if row in BACKWARDS_ROWS_96:
        position_from_left = NUM_COLS_96 - 1 - index_in_row
    else:
        position_from_left = index_in_row

    column = position_from_left + 1
    return get_well_name(row, column)


def tile_to_index(tile):
    '''
    Convert a tile (e.g. 'Tile000020.bmp') to a 0-indexed 'snake' position
    in the plate (e.g. 19)

    '''
    if not re.match('Tile0000\d\d.bmp', tile):
        raise ValueError('Improper tile string')
    index = int(tile[8:10]) - 1
    return index


def index_to_tile(index):
    '''
    Convert a 0-indexed 'snake' position in the plate (e.g. 19)
    to a tile (e.g. 'Tile000020.bmp').

    '''
    return 'Tile0000{}.bmp'.format(str(index + 1).zfill(2))


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


def assign_to_plates(l, vertical=False,
                     num_empties=0, already_used_empties=[]):
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
        if not plates or len(plates[-1]) >= 96:
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

    return plates


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


def get_well_list(vertical=False, is_384=False):
    '''
    Get a list of wells.

    vertical param determines whether to list first by column or by row.

    is_384 param determines if the well list should be for 384-format plates,
    or 96-format plates.

    '''
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
    '''
    Get a list of all wells derived from the provided rows and columns,
    listed in 'vertical' order:

        ['A01', 'B01', ..., 'H01',
         'A02', 'B02', ..., 'H02',
         ...,
         'A12', 'B12', ..., 'H12']

    '''
    wells = []
    for row in rows:
        for column in columns:
            wells.append(get_well_name(row, column))
    return wells


def get_well_list_horizontal(rows, columns):
    '''
    Get a list of all wells derived from the provided rows and columns,
    listed in 'horizontal' order:

        ['A01', 'A02', ..., 'A12',
         'B01', 'B02', ..., 'B12',
         ...,
         'H01', 'H02', ..., 'H12']

    '''
    wells = []
    for column in columns:
        for row in rows:
            wells.append(get_well_name(row, column))
    return wells


def get_96_well_set():
    '''
    Get a set of all standard 96-plate well names: 'A01', ..., 'H12'

    '''
    return get_well_set(ROWS_96, COLS_96)


def get_384_well_set():
    '''
    Get a set of all standard 384-plate well names: 'A01', ..., 'P24'

    '''
    return get_well_set(ROWS_384, COLS_384)


def get_well_set(rows, columns):
    '''
    Get a set of all well names made from combining the provided rows
    and columns. Expects integer columns, no more than 2 digits.

    '''
    wells = set()
    for row in rows:
        for column in columns:
            wells.add(get_well_name(row, column))
    return wells


def get_96_grid():
    '''
    Get a 2D array representing a 96-well plate (8 rows, 12 columns),
    where each element is a dictionary containing 'well' name and 'tile' name.

    '''
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
    '''
    Get the 384-format position corresponding to a 96-format 'child' position,
    using the child's quadrant (A1, A2, B1, or B2) and the child's position.

    '''
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


def is_ahringer_96_plate(plate_name):
    '''
    Determine if a plate name matches the correct format for an Ahringer
    plate (in 96-format).

    '''
    return re.match('(I|II|III|IV|V|X)-[1-9][0-3]?-[AB][12]', plate_name)


if __name__ == '__main__':
    tests = (
        ('A01', 'Tile000001.bmp'),
        ('A12', 'Tile000012.bmp'),
        ('B12', 'Tile000013.bmp'),
        ('B01', 'Tile000024.bmp'),
        ('C02', 'Tile000026.bmp'),
        ('H12', 'Tile000085.bmp'),
        ('H01', 'Tile000096.bmp'),
    )

    for test in tests:
        if well_to_tile(test[0]) != test[1]:
            print 'fail:' + well_to_tile(test[0])
        if tile_to_well(test[1]) != test[0]:
            print 'FAIL: ' + tile_to_well(test[1])

    print 'A1 H12 to 384: ' + get_384_position('A1', 'H12')
    print 'B1 H12 to 384: ' + get_384_position('B1', 'H12')
    print 'A2 H12 to 384: ' + get_384_position('A2', 'H12')
    print 'B2 H12 to 384: ' + get_384_position('B2', 'H12')
