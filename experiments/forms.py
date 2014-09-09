from django import forms


class ExperimentFilterForm(forms.Form):
    """
    Form for filtering Experiment instances.
    """
    id__gte = forms.IntegerField(required=False, label="Min id")
    id__lte = forms.IntegerField(required=False, label="Max id")
    worm_strain = forms.CharField(required=False)
    worm_strain__gene = forms.CharField(required=False)
    worm_strain__allele = forms.CharField(required=False)
    library_plate = forms.CharField(required=False)
    temperature = forms.DecimalField(required=False)
    date = forms.DateField(required=False)
    is_junk = forms.NullBooleanField(required=False, initial=False)
