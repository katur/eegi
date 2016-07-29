from django import forms

from worms.models import WormStrain


class WormChoiceField(forms.ModelChoiceField):
    """
    Field to choose a worm strain.
    """

    def __init__(self, **kwargs):
        if 'queryset' not in kwargs:
            kwargs['queryset'] = WormStrain.objects.all()

        super(WormChoiceField, self).__init__(**kwargs)


class WormMultipleChoiceField(forms.ModelMultipleChoiceField):
    """
    Field to choose multiple worm strains.
    """

    def __init__(self, **kwargs):
        if 'queryset' not in kwargs:
            kwargs['queryset'] = WormStrain.objects.all()

        super(WormMultipleChoiceField, self).__init__(**kwargs)


class MutantKnockdownField(forms.CharField):
    """
    Field to find a mutant worm strain.

    Finds the worm strain based on worm strain name, gene,
    or allele. Since some genes have different worm strains
    for the suppressor and enhancer screens, this field
    only makes sense to use in concert with a
    ScreenTypeChoiceField.

    Since this is meant for finding knockdowns,
    N2 (the control worm with no mutation) is not allowed.

    Since this is meant as a field to define a knockdown page,
    if no value is entered, a ValidationError is raised.

    Otherwise, the value is simply returned. It is not coerced
    to a WormStrain object, since that requires also looking
    at the ScreenTypeChoiceField. The clean_mutant_query_and_screen_type
    function is meant for help transforming both fields
    into a particular worm strain and temperature.
    """

    def __init__(self, **kwargs):
        if 'help_text' not in kwargs:
            kwargs['help_text'] = 'gene, allele, or worm strain name'

        super(MutantKnockdownField, self).__init__(**kwargs)

    def to_python(self, value):
        if value == 'N2':
            raise forms.ValidationError('Mutant query cannot be N2')
        return value


def clean_mutant_query_and_screen_type(form, cleaned_data):
    """
    Helper to derive worm strain and temperature from cleaned_data.

    If cleaned_data['mutant_query'] and cleaned_data['screen_type']
    are defined, cleaned_data['worm'] and cleaned_data['temperature']
    will be populated.

    Returns the modified cleaned_data.
    """
    mutant_query = cleaned_data.get('mutant_query')
    screen_type = cleaned_data.get('screen_type')

    if mutant_query and screen_type:
        worm_and_temp = WormStrain.get_worm_and_temperature_from_search_term(
            mutant_query, screen_type)
        if worm_and_temp:
            cleaned_data['worm'] = worm_and_temp[0]
            cleaned_data['temperature'] = worm_and_temp[1]
        else:
            form.add_error('mutant_query', 'No mutant match')

    return cleaned_data
