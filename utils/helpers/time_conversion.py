import datetime

from django.utils import timezone


def get_timestamp(year, month, day, time, ymd):
    """
    Return a datetime.datetime object from an integer year,
    a 3-letter-string month (e.g. 'Jan'), an integer day,
    and a string time in format '00:00:00'.

    If a ymd is passed in, it is simply confirmed to match the date derived
    from the year/month/day/time.

    If the year/month/day/time or ymd are not in the expected format,
    or if both exist and are in the expected format yet they do not match
    each other, returns None.

    This function assumes that the arguments refer to the timezone
    listed in settings.py, and converts to an 'aware' timestamp capable
    of more universal treatment.
    """
    try:
        string = '{}-{}-{}::{}'.format(year, month, day, time)
        timestamp = timezone.make_aware(
            datetime.datetime.strptime(string, '%Y-%b-%d::%H:%M:%S'),
            timezone.get_default_timezone())
    except Exception:
        return None

    if ymd:
        try:
            hour, minute, second = time.split(':')
            timestamp_from_ymd = timezone.make_aware(
                datetime.datetime(ymd.year, ymd.month, ymd.day,
                                  int(hour), int(minute), int(second)),
                timezone.get_default_timezone())

            if timestamp != timestamp_from_ymd:
                return None

        except Exception:
            return None

    return timestamp
