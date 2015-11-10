"""This module contains helpers for the sync_legacy_database command,
e.g. functions to sync sets of rows and to sync individual objects.

"""
from django.core.exceptions import ObjectDoesNotExist
from utils.comparison import compare_values_for_equality


def sync_rows(command, cursor, legacy_query, sync_row_function, **kwargs):
    """Sync the rows from a query to the legacy database to the current
    database, according to sync_row_function(legacy_row, **kwargs).

    """
    cursor.execute(legacy_query)
    legacy_rows = cursor.fetchall()
    all_match = True

    for legacy_row in legacy_rows:
        matches = sync_row_function(legacy_row, **kwargs)
        all_match &= matches

    if all_match:
        command.stdout.write(
            'All objects from legacy query:\n\n\t{}\n\n'
            'were already represented in new database.\n\n'
            .format(legacy_query))

    else:
        command.stdout.write(
            'Some objects from legacy query:\n\n\t{}\n\n'
            'were just added or updated in new database'
            '(individual changes and warnings printed to stderr.)\n\n'
            .format(legacy_query))


def update_or_save_object(command, new_object, recorded_objects,
                          fields_to_compare, alternate_pk=False):
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
            return compare_fields(command, recorded_object, new_object,
                                  fields_to_compare, update=True)
        else:
            return True

    except ObjectDoesNotExist:
        new_object.save()
        command.stderr.write('Added new record {} to the database\n'
                             .format(str(new_object)))
        return False


def compare_fields(command, old_object, new_object, fields, update=False):
    """Compare two objects on the provided fields.

    Any differences are printed to stderr.

    If 'update' is True, old_object is updated to match
    new_object on these fields.

    """
    differences = []
    for field in fields:
        if not compare_values_for_equality(getattr(old_object, field),
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
        command.stderr.write(
            'WARNING: Record {} had these changes: {}\n'
            .format(str(new_object), str([d for d in differences])))

        if update:
            command.stderr.write(
                '\tThe database was updated to reflect the changes\n\n')
        else:
            command.stderr.write(
                '\tThe database was NOT updated to reflect the changes\n\n')
        return False

    else:
        return True
