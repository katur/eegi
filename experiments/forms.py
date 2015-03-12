from django import forms
from django.forms import Select, NullBooleanSelect


class BlankNullBooleanSelect(NullBooleanSelect):
    def __init__(self, attrs=None):
        choices = ((u'1', u'All'),
                   (u'3', u'No'),
                   (u'2', u'Yes'))
        Select.__init__(self, attrs, choices)


class ExperimentFilterForm(forms.Form):
    """
    Form for filtering Experiment instances.
    """
    id = forms.IntegerField(required=False,
                            label='Exact id')
    id__gte = forms.IntegerField(required=False,
                                 label='Min id',
                                 help_text='inclusive')
    id__lte = forms.IntegerField(required=False,
                                 label='Max id',
                                 help_text='inclusive')
    worm_strain = forms.CharField(required=False)
    worm_strain__gene = forms.CharField(required=False,
                                        label='Worm gene')
    worm_strain__allele = forms.CharField(required=False,
                                          label='Worm allele')
    library_plate = forms.CharField(required=False)
    temperature = forms.DecimalField(required=False,
                                     label='Exact temp',
                                     help_text='number only')
    temperature__gte = forms.DecimalField(required=False,
                                          label='Min temp',
                                          help_text='inclusive')
    temperature__lte = forms.DecimalField(required=False,
                                          label='Max temp',
                                          help_text='inclusive')
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


class SecondaryScoresForm(forms.Form):
    """
    Form for getting all secondary scores for a strain.
    """
    query = forms.CharField(label='Mutant query',
                            help_text='gene, allele, or worm strain name')
    screen = forms.ChoiceField(
        choices=[('SUP', 'suppressor'), ('ENH', 'enhancer')],
        widget=forms.RadioSelect)
