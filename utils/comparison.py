"""Utility module with float comparison helpers."""


def compare_floats_for_equality(x, y, error_margin=0.001):
    """Compare two floats for equality.

    The two floats are allowed to differ by error_margin.

    """
    if x is None and y is None:
        return True
    elif x is None or y is None:
        return False
    else:
        return abs(x - y) < error_margin


def compare_values_for_equality(x, y):
    """Compare two values for equality.

    Allows wiggle room for floats/longs.

    """
    if isinstance(x, float) or isinstance(x, long):
        return compare_floats_for_equality(x, y)
    else:
        return x == y
