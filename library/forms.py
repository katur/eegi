from django import forms
from django.core.exceptions import ObjectDoesNotExist

from library.models import LibraryPlate


def validate_library_plate_name_exists(library_plate_name):
    try:
        LibraryPlate.objects.get(pk=library_plate_name)
    except ObjectDoesNotExist:
        raise forms.ValidationError('No LibraryPlate exists with name {}'
                                    .format(library_plate_name))
