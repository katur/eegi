import sys

from django.core.exceptions import ObjectDoesNotExist


def update_or_save_object(new_object, recorded_objects, fields_to_compare,
                          alternate_pk=False):
    """Update the database to represent new_object.

    If new_object is not present in the database, add it (and print
    warning to syserr).

    If new_object is already present in the database (according to
    alternate_pk if specified, pk otherwise), compare the provided
    fields_to_compare. If any of these fields do not match, update them
    (and print updates to syserr).

    Returns True if new_object was already present and matched
    on all provided fields. Returns False otherwise.
    """
    try:
        if alternate_pk:
            recorded_object = recorded_objects.get(**alternate_pk)
        else:
            recorded_object = recorded_objects.get(pk=new_object.pk)
        if fields_to_compare:
            return compare_fields(recorded_object, new_object,
                                  fields_to_compare, update=True)
        else:
            return True

    except ObjectDoesNotExist:
        new_object.save()
        sys.stderr.write('Added new record {} to the database\n'
                         .format(str(new_object)))
        return False


def compare_fields(old_object, new_object, fields, update=False):
    """Compare two objects on the provided fields.
    Any differences are printed to stderr.

    If 'update' is True, old_object is updated to match
    new_object on these fields.
    """
    differences = []
    for field in fields:
        if not compare_fields_for_equality(getattr(old_object, field),
                                           getattr(new_object, field)):
            differences.append('{} previously recorded as {}, '
                               'now {}'
                               .format(field,
                                       str(getattr(old_object, field)),
                                       str(getattr(new_object, field))))
            if update:
                setattr(old_object, field, getattr(new_object, field))
                old_object.save()

    if differences:
        sys.stderr.write('WARNING: Record {} had these changes: {}\n'
                         .format(str(new_object),
                                 str([d for d in differences])))
        if update:
            sys.stderr.write('\tThe database was updated to reflect '
                             'the changes\n\n')
        else:
            sys.stderr.write('\tThe database was NOT updated to reflect '
                             'the changes\n\n')
        return False
    else:
        return True


def compare_floats_for_equality(x, y, error_margin=0.001):
    """Compare two floats for equality, allowing them to differ by
    error_margin.
    """
    if x is None and y is None:
        return True
    elif x is None or y is None:
        return False
    elif abs(x - y) < error_margin:
        return True
    else:
        return False


def compare_fields_for_equality(x, y):
    """Compare two fields for equality, allowing wiggle room for floats/longs.
    """
    if isinstance(x, float) or isinstance(x, long):
        return compare_floats_for_equality(x, y)
    else:
        return x == y
