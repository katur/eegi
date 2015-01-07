from django import forms
from django.forms import Select, NullBooleanSelect


class BlankNullBooleanSelect(NullBooleanSelect):
    def __init__(self, attrs=None):
        choices = ((u'1', u''),
                   (u'3', u'No'),
                   (u'2', u'Yes'))
        Select.__init__(self, attrs, choices)


class ExperimentFilterForm(forms.Form):
    """
    Form for filtering Experiment instances.
    """
    id__gte = forms.IntegerField(required=False,
                                 label='Min id',
                                 help_text='inclusive')
    id__lte = forms.IntegerField(required=False,
                                 label='Max id',
                                 help_text='inclusive')
    worm_strain = forms.CharField(required=False)
    worm_strain__gene = forms.CharField(required=False)
    worm_strain__allele = forms.CharField(required=False)
    library_plate = forms.CharField(required=False)
    temperature = forms.DecimalField(required=False,
                                     help_text='number only')
    date = forms.DateField(required=False,
                           label='Date',
                           help_text='YYYY-MM-DD')
    is_junk = forms.NullBooleanField(required=False,
                                     initial=False,
                                     widget=BlankNullBooleanSelect)


class DoubleKnockdownForm(forms.Form):
    """
    Form for finding a double knockdown.
    """
    query = forms.CharField(label='Mutant query',
                            help_text='gene, allele, or worm strain name')
    target = forms.CharField(label='RNAi Target',
                             help_text='gene, cosmid, clone, or position')
    screen = forms.ChoiceField(
        choices=[('SUP', 'suppressor'), ('ENH', 'enhancer')],
        widget=forms.RadioSelect)
