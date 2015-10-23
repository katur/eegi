from django import forms
from django.core.validators import MinLengthValidator

from clones.forms import RNAiKnockdownField
from experiments.models import Experiment
from worms.helpers.queries import get_worm_and_temperature


class BlankNullBooleanSelect(forms.NullBooleanSelect):
    def __init__(self, attrs=None):
        choices = ((u'1', u''),
                   (u'3', u'No'),
                   (u'2', u'Yes'))
        forms.Select.__init__(self, attrs, choices)


class ExperimentFilterForm(forms.Form):
    """Form for filtering Experiment instances."""
    id = forms.IntegerField(required=False,
                            label='Exact id',
                            help_text='e.g. 32412')

    id__gte = forms.IntegerField(required=False,
                                 label='Min id',
                                 help_text='inclusive')

    id__lte = forms.IntegerField(required=False,
                                 label='Max id',
                                 help_text='inclusive')

    worm_strain = forms.CharField(required=False,
                                  help_text='e.g. TH48')

    worm_strain__gene = forms.CharField(required=False,
                                        label='Worm gene',
                                        help_text='e.g. mbk-2')

    worm_strain__allele = forms.CharField(required=False,
                                          label='Worm allele',
                                          help_text='e.g. dd5')

    temperature = forms.DecimalField(required=False,
                                     label='Exact temp',
                                     help_text='number only')

    temperature__gte = forms.DecimalField(required=False,
                                          label='Min temp',
                                          help_text='inclusive')

    temperature__lte = forms.DecimalField(required=False,
                                          label='Max temp',
                                          help_text='inclusive')
    library_plate = forms.CharField(required=False,
                                    help_text='e.g. II-3-B2')

    date = forms.DateField(required=False,
                           label='Date',
                           help_text='YYYY-MM-DD')

    date__gte = forms.DateField(required=False,
                                label='Min date',
                                help_text='inclusive')

    date__lte = forms.DateField(required=False,
                                label='Max date',
                                help_text='inclusive')

    is_junk = forms.NullBooleanField(required=False,
                                     initial=False,
                                     widget=BlankNullBooleanSelect)

    screen_stage = forms.ChoiceField(
        choices=[('', '')] + list(Experiment.SCREEN_STAGE_CHOICES),
        required=False)


class MutantKnockdownField(forms.CharField):
    """Field to find a mutant worm.

    Since this is meant for finding knockdowns,
    N2 (the control worm with no mutation) is not allowed.

    Since this is meant as a field to define a knockdown page,
    if no value is entered, a ValidationError is raised.

    Otherwise, the value is simply returned. (It is not coerced
    to a WormStrain object, because the particular WormStrain
    cannot be figured out without also checking the ScreenType
    value.)

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
    """Field defining the screen as SUP or ENH."""
    def __init__(self, **kwargs):
        if 'widget' not in kwargs:
            kwargs['widget'] = forms.RadioSelect

        if 'choices' not in kwargs:
            kwargs['choices'] = [('SUP', 'suppressor'), ('ENH', 'enhancer')]
        super(ScreenChoiceField, self).__init__(**kwargs)


def _clean_mutant_query_and_screen(form, cleaned_data):
    """Helper method to coerce a mutant query term and a screen into
    a particular worm strain.

    """
    mutant_query = cleaned_data.get('mutant_query')
    screen = cleaned_data.get('screen')

    if mutant_query and screen:
        worm_and_temp = get_worm_and_temperature(mutant_query, screen)
        if worm_and_temp:
            cleaned_data['worm'] = worm_and_temp[0]
            cleaned_data['temperature'] = worm_and_temp[1]
        else:
            form.add_error('mutant_query', 'No mutant match')

    return cleaned_data


class RNAiKnockdownForm(forms.Form):
    """Form for finding wildtype worms tested with a single RNAi clone."""
    rnai_query = RNAiKnockdownField(
        label='RNAi query',
        validators=[MinLengthValidator(1, message='No clone matches')])
    temperature = forms.DecimalField(required=False,
                                     label='Temperature',
                                     help_text='optional')


class MutantKnockdownForm(forms.Form):
    """Form for finding a mutant worm with the control bacteria."""
    mutant_query = MutantKnockdownField()
    screen = ScreenChoiceField()

    def clean(self):
        cleaned_data = super(MutantKnockdownForm, self).clean()
        cleaned_data = _clean_mutant_query_and_screen(self, cleaned_data)
        return cleaned_data


class DoubleKnockdownForm(forms.Form):
    """Form for finding a double knockdown."""
    mutant_query = MutantKnockdownField()
    rnai_query = RNAiKnockdownField(
        label='RNAi query',
        validators=[MinLengthValidator(1, message='No clone matches')])
    screen = ScreenChoiceField()

    def clean(self):
        cleaned_data = super(DoubleKnockdownForm, self).clean()
        cleaned_data = _clean_mutant_query_and_screen(self, cleaned_data)
        return cleaned_data


class SecondaryScoresForm(forms.Form):
    """Form for getting all secondary scores for a worm/screen combo."""
    query = MutantKnockdownField()
    screen = ScreenChoiceField()
