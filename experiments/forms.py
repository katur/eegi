from django import forms

from clones.helpers.queries import get_clones
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


class MutantQueryField(forms.CharField):
    def __init__(self):
        super(MutantQueryField, self).__init__(
            label='Mutant query',
            help_text='gene, allele, or worm strain name')


class RNAiQueryField(forms.CharField):
    def __init__(self):
        super(RNAiQueryField, self).__init__(
            label='RNAi query',
            help_text='gene target (WormBase id, cosmid id, or locus)'
                      ' or clone name')


class ScreenChoiceField(forms.ChoiceField):
    def __init__(self):
        super(ScreenChoiceField, self).__init__(
            choices=[('SUP', 'suppressor'), ('ENH', 'enhancer')],
            widget=forms.RadioSelect)


def _clean_mutant_query_and_screen(form, cleaned_data):
    mutant_query = cleaned_data.get('mutant_query')
    screen = cleaned_data.get('screen')

    if mutant_query == 'N2':
        form.add_error('mutant_query', 'Mutant query cannot be N2')

    elif mutant_query:
        worm_and_temp = get_worm_and_temperature(mutant_query, screen)
        if worm_and_temp:
            cleaned_data['worm'] = worm_and_temp[0]
            cleaned_data['temperature'] = worm_and_temp[1]
        else:
            form.add_error('mutant_query', 'No mutant match')

    return cleaned_data


def _clean_rnai_query(form, cleaned_data):
    rnai_query = cleaned_data.get('rnai_query')

    if rnai_query == 'L4440':
        form.add_error('rnai_query', 'RNAi query cannot be L4440')

    clones = get_clones(rnai_query)
    if clones:
        cleaned_data['clones'] = clones
    else:
        form.add_error('rnai_query', 'No RNAi match')


class DoubleKnockdownForm(forms.Form):
    """Form for finding a double knockdown."""
    mutant_query = MutantQueryField()
    rnai_query = RNAiQueryField()
    screen = ScreenChoiceField()

    def clean(self):
        cleaned_data = super(DoubleKnockdownForm, self).clean()
        cleaned_data = _clean_mutant_query_and_screen(self, cleaned_data)
        cleaned_data = _clean_rnai_query(self, cleaned_data)
        return cleaned_data


class MutantKnockdownForm(forms.Form):
    """Form for finding a mutant worm with the control bacteria."""
    mutant_query = MutantQueryField()
    screen = ScreenChoiceField()

    def clean(self):
        cleaned_data = super(MutantKnockdownForm, self).clean()
        cleaned_data = _clean_mutant_query_and_screen(self, cleaned_data)
        return cleaned_data


class RNAiKnockdownForm(forms.Form):
    """Form for finding wildtype worms tested with a single RNAi clone."""
    rnai_query = RNAiQueryField()
    temperature = forms.DecimalField(required=False,
                                     label='Temperature',
                                     help_text='optional')

    def clean(self):
        cleaned_data = super(RNAiKnockdownForm, self).clean()
        cleaned_data = _clean_rnai_query(self, cleaned_data)
        return cleaned_data


class SecondaryScoresForm(forms.Form):
    """Form for getting all secondary scores for a strain."""
    query = MutantQueryField()
    screen = ScreenChoiceField()
