def get_tile(well):
    assert len(well) == 3
    row = well[0]

    assert row in 'ABCDEFGH'
    if row in 'ACEG':
        count_backwards = False
    else:
        count_backwards = True

    lowest_tile_number_in_row = (ord(row) - 65) * 12 + 1
    position_in_row = int(well[1:3]) - 1

    if count_backwards:
        tile_number = lowest_tile_number_in_row + (11 - position_in_row)
    else:
        tile_number = lowest_tile_number_in_row + position_in_row

    return 'Tile0000{0}.bmp'.format(
        str(tile_number).zfill(2))
