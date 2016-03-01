from django import forms
from django.core.exceptions import ObjectDoesNotExist

from library.models import LibraryPlate


class LibraryPlateField(forms.CharField):
    """Field for entering a library plate and getting the object."""

    def to_python(self, value):
        if not value:
            return value

        try:
            return LibraryPlate.objects.get(pk=value)
        except ObjectDoesNotExist:
            raise forms.ValidationError('No LibraryPlate exists with '
                                        'name {}'.format(value))
