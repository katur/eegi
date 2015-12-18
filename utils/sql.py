"""Utility module with SQL database querying helpers."""


def get_field_dictionary(cursor, table, fieldnames):
    """
    Get a dictionary capturing fields of a table.

    Assumes fieldnames[0] is the primary key of table.
    The dictionary returned is keyed on this primary key.

    The value of the dictionary returned is a nested dictionary.
    This nested dictionary is keyed on fieldnames [1:],
    the values being the corresponding values from the table.
    """
    fieldnames_as_string = ', '.join(fieldnames)
    query = 'SELECT {} FROM {}'.format(fieldnames_as_string, table)
    cursor.execute(query)
    rows = cursor.fetchall()
    d = {}
    for row in rows:
        pk = row[0]
        d[pk] = {}
        for k, v in zip(fieldnames[1:], row[1:]):
            d[pk][k] = v
    return d
