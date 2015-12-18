"""
Utility module with helpers to compare objects.

Includes functions to compare floats for equality allowing some wiggle room,
to get a candidate closest to a goal, etc.
"""


def compare_floats_for_equality(x, y, error_margin=0.001):
    """
    Compare two floats for equality.

    The two floats may differ by error_margin while still being considered
    equal.
    """
    if x is None and y is None:
        return True
    elif x is None or y is None:
        return False
    else:
        return abs(x - y) < error_margin


def compare_values_for_equality(x, y):
    """
    Compare two values for equality.

    Allows wiggle room for floats/longs.
    """
    if isinstance(x, float) or isinstance(x, long):
        return compare_floats_for_equality(x, y)
    else:
        return x == y


def get_closest_candidate(goal, candidates):
    """
    Get the value in candidates that numerically closest to goal.

    Each element of candidates, as well as goal, must be convertible
    to a floating point number.
    """
    best_candidate = None
    best_difference = None

    for candidate in candidates:
        difference = abs(float(goal) - float(candidate))

        if best_candidate is None or difference < best_difference:
            best_candidate = candidate
            best_difference = difference

    return best_candidate
