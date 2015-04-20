import re

ROWS = 'ABCDEFGH'
BACKWARDS_ROWS = 'BDFH'
NUMBER_OF_ROWS = len(ROWS)
NUMBER_OF_COLUMNS = 12

ROWS_384 = 'ABCDEFGHIJKLMNOP'
NUMBER_OF_ROWS_384 = len(ROWS_384)
NUMBER_OF_COLUMNS_384 = 24


def get_well_name(row_name, column_name):
    """
    Get well name (e.g. 'A05') from a row (e.g. 'A') and a column (e.g. 4).

    row_name should be a capital letter.

    column_name should be an integer.
    """
    return '{}{}'.format(row_name, str(column_name).zfill(2))


def get_three_character_well(well):
    """
    Return a well in 3-character format (e.g. 'A05'), whether the input is
    in 3-character format or 2-character format (e.g. 'A5').
    """
    row_name = well[0]
    column_name = int(well[1:])
    return get_well_name(row_name, column_name)


def well_to_tile(well):
    """
    Convert a well (e.g. 'B05') to a tile (e.g. 'Tile000020.bmp').
    """
    index = well_to_index(well)
    return index_to_tile(index)


def well_to_index(well):
    """
    Convert a well (e.g. 'B05') to a 0-indexed 'snake' position in the plate
    (e.g. 19).
    """
    if not re.match('[A-H]\d\d?', well):
        raise ValueError('Improper well string')
    row = well[0]
    column = int(well[1:])
    position_from_left = column - 1
    assert position_from_left >= 0 and position_from_left < NUMBER_OF_COLUMNS

    min_row_index = (ord(row) - 65) * NUMBER_OF_COLUMNS
    if row in BACKWARDS_ROWS:
        index_in_row = NUMBER_OF_COLUMNS - 1 - position_from_left
    else:
        index_in_row = position_from_left

    overall_index = min_row_index + index_in_row
    return overall_index


def index_to_tile(index):
    """
    Convert a 0-indexed 'snake' position in the plate (e.g. 19)
    to a tile (e.g. 'Tile000020.bmp').
    """
    return 'Tile0000{}.bmp'.format(str(index + 1).zfill(2))


def tile_to_well(tile):
    """
    Convert a tile (e.g. 'Tile000020.bmp') to a well (e.g. 'B05').
    """
    index = tile_to_index(tile)
    return index_to_well(index)


def tile_to_index(tile):
    """
    Convert a tile (e.g. 'Tile000020.bmp') to a 0-indexed 'snake' position
    in the plate (e.g. 19)
    """
    if not re.match('Tile0000\d\d.bmp', tile):
        raise ValueError('Improper tile string')
    index = int(tile[8:10]) - 1
    return index


def index_to_well(index):
    """
    Convert a 0-indexed 'snake' position in the plate (e.g. 19)
    to a well (e.g. 'B05')
    """
    row = ROWS[index / NUMBER_OF_COLUMNS]
    index_in_row = index % NUMBER_OF_COLUMNS

    if row in BACKWARDS_ROWS:
        position_from_left = NUMBER_OF_COLUMNS - 1 - index_in_row
    else:
        position_from_left = index_in_row

    column = position_from_left + 1
    return get_well_name(row, column)


def get_96_grid():
    """
    Get a 2D array representing a 96-well plate (8 rows, 12 columns),
    where each element is a dictionary containing 'well' name and 'tile' name.
    """
    plate = []
    for row_index in range(NUMBER_OF_ROWS):
        plate.append([])
        for column_index in range(NUMBER_OF_COLUMNS):
            row_name = ROWS[row_index]
            column_name = column_index + 1
            well = get_well_name(row_name, column_name)
            position_info = {
                'well': well,
                'tile': well_to_tile(well),
            }
            plate[row_index].append(position_info)

    return plate


def get_96_well_set():
    """
    Get set of all standard 96-plate well names: 'A01', ..., 'H12'
    """
    return get_well_set(ROWS, range(1, NUMBER_OF_COLUMNS + 1))


def get_384_well_set():
    """
    Get set of all standard 384-plate well names: 'A01', ..., 'P24'
    """
    return get_well_set(ROWS_384, range(1, NUMBER_OF_COLUMNS_384 + 1))


def get_well_set(rows, columns):
    """
    Get a list of all well names made from combining the provided rows
    and columns. Expects integer columns, no more than 2 digits.
    """
    wells = set()
    for row in rows:
        for column in columns:
            wells.add(get_well_name(row, column))
    return wells


def get_384_position(child_quadrant, child_position):
    if child_quadrant[0] == 'A':
        odd_row = True
    else:
        odd_row = False

    if child_quadrant[1] == '1':
        odd_column = True
    else:
        odd_column = False

    child_row = child_position[0]
    child_row_index = ROWS.index(child_row)
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
