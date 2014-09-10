import re

ROWS = 'ABCDEFGH'
BACKWARDS_ROWS = 'BDFH'
NUMBER_OF_COLUMNS = 12
NUMBER_OF_ROWS = len(ROWS)


def well_to_tile(well):
    index = well_to_index(well)
    return index_to_tile(index)


def tile_to_well(tile):
    index = tile_to_index(tile)
    return index_to_well(index)


def index_to_tile(index):
    return 'Tile0000{}.bmp'.format(str(index + 1).zfill(2))


def tile_to_index(tile):
    if not re.match('Tile0000\d\d.bmp', tile):
        raise ValueError('Improper tile string')
    index = int(tile[8:10]) - 1
    return index


def index_to_well(index):
    row = ROWS[index / NUMBER_OF_COLUMNS]
    index_in_row = index % NUMBER_OF_COLUMNS

    if row in BACKWARDS_ROWS:
        position_from_left = NUMBER_OF_COLUMNS - 1 - index_in_row
    else:
        position_from_left = index_in_row

    column = position_from_left + 1
    return '{}{}'.format(row, str(column).zfill(2))


def well_to_index(well):
    if not re.match('[A-H]\d\d', well):
        raise ValueError('Improper well string')
    row = well[0]
    column = int(well[1:3])
    position_from_left = column - 1
    assert position_from_left >= 0 and position_from_left < NUMBER_OF_COLUMNS

    min_row_index = (ord(row) - 65) * NUMBER_OF_COLUMNS
    if row in BACKWARDS_ROWS:
        index_in_row = NUMBER_OF_COLUMNS - 1 - position_from_left
    else:
        index_in_row = position_from_left

    overall_index = min_row_index + index_in_row
    return overall_index


def row_and_column_indices_to_well(row_index, column_index):
    row_string = ROWS[row_index]
    column_string = str(column_index + 1).zfill(2)
    return row_string + column_string


def get_96_well_plate_template():
    plate = []
    for row in range(NUMBER_OF_ROWS):
        plate.append([])
        for column in range(NUMBER_OF_COLUMNS):
            well = row_and_column_indices_to_well(row, column)
            position_info = {
                'well': well,
                'tile': well_to_tile(well),
                'index': well_to_index(well),
            }
            plate[row].append(position_info)

    return plate


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
