from django import forms
from django.core.validators import MinLengthValidator

from clones.forms import RNAiKnockdownField
from experiments.models import Experiment, ExperimentPlate
from utils.forms import BlankNullBooleanSelect
from worms.forms import (MutantKnockdownField, ScreenTypeChoiceField,
                         clean_mutant_query_and_screen_type)


class ExperimentFormBase(forms.Form):
    plate__id = forms.IntegerField(
        required=False, label='Exact id', help_text='e.g. 32412')

    plate__id__gte = forms.IntegerField(
        required=False, label='Min id', help_text='inclusive')

    plate__id__lte = forms.IntegerField(
        required=False, label='Max id', help_text='inclusive')

    plate__date = forms.DateField(
        required=False, label='Exact date', help_text='YYYY-MM-DD')

    plate__date__gte = forms.DateField(
        required=False, label='Min date', help_text='inclusive')

    plate__date__lte = forms.DateField(
        required=False, label='Max date', help_text='inclusive')

    plate__temperature = forms.DecimalField(
        required=False, label='Exact temp', help_text='number only')

    plate__temperature__gte = forms.DecimalField(
        required=False, label='Min temp', help_text='inclusive')

    plate__temperature__lte = forms.DecimalField(
        required=False, label='Max temp', help_text='inclusive')

    worm_strain = forms.CharField(
        required=False, label='Worm strain', help_text='e.g. TH48')

    worm_strain__gene = forms.CharField(
        required=False, label='Worm gene', help_text='e.g. mbk-2')

    worm_strain__allele = forms.CharField(
        required=False, label='Worm allele', help_text='e.g. dd5')

    plate__screen_stage = forms.ChoiceField(
        required=False, label='Screen stage',
        choices=[('', '')] + list(ExperimentPlate.SCREEN_STAGE_CHOICES))


class ExperimentFilterForm(ExperimentFormBase):
    """Form for filtering Experiment intstances."""
    is_junk = forms.NullBooleanField(
        required=False, widget=BlankNullBooleanSelect)

    library_stock = forms.CharField(
        required=False, help_text='e.g. II-3-B2_A01')

    library_stock__intended_clone = forms.CharField(
        required=False, help_text='e.g. sjj_AH10.4')

    def clean(self):
        cleaned_data = super(ExperimentFilterForm, self).clean()

        for k, v in cleaned_data.items():
            # Retain 'False' as a legitimate filter
            if v is False:
                continue

            # Ditch empty strings and None as filters
            if not v:
                del cleaned_data[k]

        experiments = (Experiment.objects.filter(**cleaned_data))
        cleaned_data['experiments'] = experiments
        return cleaned_data



class ExperimentPlateFilterForm(ExperimentFormBase):
    """Form for filtering ExperimentPlate instances."""
    is_junk = forms.NullBooleanField(
        required=False, label="Has junk",
        widget=BlankNullBooleanSelect)

    library_stock__plate = forms.CharField(
        required=False, label='Library plate', help_text='e.g. II-3-B2')

    def clean(self):
        cleaned_data = super(ExperimentPlateFilterForm, self).clean()

        for k, v in cleaned_data.items():
            # Retain 'False' as a legitimate filter
            if v is False:
                continue

            # Ditch empty strings and None as filters
            if not v:
                del cleaned_data[k]

        plate_pks = (Experiment.objects.filter(**cleaned_data)
                     .order_by('plate').values_list('plate', flat=True))

        cleaned_data['experiment_plates'] = (ExperimentPlate.objects
                                             .filter(pk__in=plate_pks))

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
    screen_type = ScreenTypeChoiceField()

    def clean(self):
        cleaned_data = super(MutantKnockdownForm, self).clean()
        cleaned_data = clean_mutant_query_and_screen_type(self, cleaned_data)
        return cleaned_data


class DoubleKnockdownForm(forms.Form):
    """Form for finding a double knockdown."""
    mutant_query = MutantKnockdownField()
    rnai_query = RNAiKnockdownField(
        label='RNAi query',
        validators=[MinLengthValidator(1, message='No clone matches')])
    screen_type = ScreenTypeChoiceField()

    def clean(self):
        cleaned_data = super(DoubleKnockdownForm, self).clean()
        cleaned_data = clean_mutant_query_and_screen_type(self, cleaned_data)
        return cleaned_data


class SecondaryScoresForm(forms.Form):
    """Form for getting all secondary scores for a worm/screen combo."""
    mutant_query = MutantKnockdownField()
    screen_type = ScreenTypeChoiceField()

    def clean(self):
        cleaned_data = super(SecondaryScoresForm, self).clean()
        cleaned_data = clean_mutant_query_and_screen_type(self, cleaned_data)
        return cleaned_data
