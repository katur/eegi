from django.db.models import Q

from library.models import LibraryPlate


def get_screening_plates(screen_stage=None):
    """
    Get library plates intended for screening.

    This excludes the plates with screen_stage=0 (which means not
    used for screening). This includes our Ahringer 384-format plates,
    and the Vidal plates from which our rearrays were derived.

    Optionally supply an integer screen_stage. What is returned in
    this case is both the plates specifically for that screen_stage,
    and also the plates with screen_stage=None (which is meant to
    signify that the plate is meant for use across screen stages).
    """
    if screen_stage:
        return LibraryPlate.objects.filter(
            Q(screen_stage=screen_stage) | Q(screen_stage=None))
    else:
        return LibraryPlate.objects.exclude(screen_stage=0)
