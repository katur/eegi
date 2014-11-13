from django import forms


class ExperimentFilterForm(forms.Form):
    """
    Form for filtering Experiment instances.
    """
    id__gte = forms.IntegerField(required=False, label='Min id (inclusive)')
    id__lte = forms.IntegerField(required=False, label='Max id (inclusive)')
    worm_strain = forms.CharField(required=False)
    worm_strain__gene = forms.CharField(required=False)
    worm_strain__allele = forms.CharField(required=False)
    library_plate = forms.CharField(required=False)
    temperature = forms.DecimalField(required=False,
                                     label='Temperature (number only)')
    date = forms.DateField(required=False,
                           label="Date (YYYY-MM-DD)")
    is_junk = forms.NullBooleanField(required=False)


class DoubleKnockdownForm(forms.Form):
    """
    Form for finding a double knockdown.
    """
    query = forms.CharField()
    target = forms.CharField()
    screen = forms.ChoiceField(choices=[('SUP', 'SUP'), ('ENH', 'ENH')],
                               widget=forms.RadioSelect)
