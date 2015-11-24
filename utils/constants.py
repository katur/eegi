"""Utility module with constants needed across apps."""

ROWS_96 = 'ABCDEFGH'
COLS_96 = [i for i in range(1, 12 + 1)]

ROWS_384 = 'ABCDEFGHIJKLMNOP'
COLS_384 = [i for i in range(1, 24 + 1)]


def get_rows_and_cols(is_384=False):
    if is_384:
        return (ROWS_384, COLS_384)
    else:
        return (ROWS_96, COLS_96)
