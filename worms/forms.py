from django import forms

from worms.helpers.queries import get_worm_and_temperature_from_search_term


class MutantKnockdownField(forms.CharField):
    """Field to find a mutant worm strain.

    Finds the worm strain based on worm strain name, gene,
    or allele. Since some genes have different worm strains
    for the suppressor and enhancer screens, this field
    only makes sense to use in concert with a ScreenChoiceField.

    Since this is meant for finding knockdowns,
    N2 (the control worm with no mutation) is not allowed.

    Since this is meant as a field to define a knockdown page,
    if no value is entered, a ValidationError is raised.

    Otherwise, the value is simply returned. It is not coerced
    to a WormStrain object, since that requires also looking
    at the ScreenChoiceField. The clean_mutant_query_and_screen
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


class ScreenChoiceField(forms.ChoiceField):
    """Field defining a screen as SUP or ENH."""
    def __init__(self, **kwargs):
        if 'widget' not in kwargs:
            kwargs['widget'] = forms.RadioSelect

        if 'choices' not in kwargs:
            kwargs['choices'] = [('SUP', 'suppressor'), ('ENH', 'enhancer')]
        super(ScreenChoiceField, self).__init__(**kwargs)


def clean_mutant_query_and_screen(form, cleaned_data):
    """Helper method to transform a mutant query and a screen
    choice into a worm strain and temperature.

    """
    mutant_query = cleaned_data.get('mutant_query')
    screen = cleaned_data.get('screen')

    if mutant_query and screen:
        worm_and_temp = get_worm_and_temperature_from_search_term(
            mutant_query, screen)
        if worm_and_temp:
            cleaned_data['worm'] = worm_and_temp[0]
            cleaned_data['temperature'] = worm_and_temp[1]
        else:
            form.add_error('mutant_query', 'No mutant match')

    return cleaned_data
