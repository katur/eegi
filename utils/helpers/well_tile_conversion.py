import re

rows = 'ABCDEFGH'
backwards_rows = 'BDFH'
NUMBER_OF_COLUMNS = 12


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
    row = rows[index / NUMBER_OF_COLUMNS]
    index_in_row = index % NUMBER_OF_COLUMNS

    if row in backwards_rows:
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
    if row in backwards_rows:
        index_in_row = NUMBER_OF_COLUMNS - 1 - position_from_left
    else:
        index_in_row = position_from_left

    overall_index = min_row_index + index_in_row
    return overall_index


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
