import re

rows = 'ABCDEFGH'
backwards_rows = 'BDFH'
NUMBER_OF_COLUMNS = 12


def get_tile(well):
    assert re.match('[A-H]\d\d', well)
    row = well[0]
    column = int(well[1:3])
    position_from_left = column - 1
    assert position_from_left >= 0 and position_from_left < NUMBER_OF_COLUMNS

    min_row_rank = (ord(row) - 65) * NUMBER_OF_COLUMNS
    if row in backwards_rows:
        rank_in_row = NUMBER_OF_COLUMNS - 1 - position_from_left
    else:
        rank_in_row = position_from_left

    overall_rank = min_row_rank + rank_in_row

    return 'Tile0000{0}.bmp'.format(
        str(overall_rank + 1).zfill(2))


def get_well(tile):
    assert re.match('Tile0000\d\d.bmp', tile)
    overall_rank = int(tile[8:10]) - 1
    row = rows[overall_rank / NUMBER_OF_COLUMNS]
    rank_in_row = overall_rank % NUMBER_OF_COLUMNS

    if row in backwards_rows:
        position_from_left = NUMBER_OF_COLUMNS - 1 - rank_in_row
    else:
        position_from_left = rank_in_row

    column = position_from_left + 1
    return '{}{}'.format(row, str(column).zfill(2))


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
        if get_tile(test[0]) != test[1]:
            print 'fail:' + get_tile(test[0])
        if get_well(test[1]) != test[0]:
            print 'FAIL: ' + get_well(test[1])
