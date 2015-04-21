from library.helpers.constants import ROWS_96, COLS_96, ROWS_384, COLS_384


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
