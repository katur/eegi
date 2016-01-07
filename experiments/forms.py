from django import forms
from django.core.validators import MinLengthValidator

from clones.forms import RNAiKnockdownField
from experiments.models import Experiment, ExperimentPlate
from utils.forms import BlankNullBooleanSelect, RangeField
from worms.forms import (MutantKnockdownField, ScreenTypeChoiceField,
                         clean_mutant_query_and_screen_type)
from worms.models import WormStrain

EMPTY_CHOICE = ('', '---------')


def get_worm_gene_choices():
    return (
        [EMPTY_CHOICE] + [(x, x) for x in (
            WormStrain.objects.all().order_by('gene')
            .values_list('gene', flat=True).distinct())])


def get_temperature_choices():
    return (
        [EMPTY_CHOICE] + [(x, x) for x in (
            ExperimentPlate.objects.all().order_by('temperature')
            .values_list('temperature', flat=True).distinct())])


class WormModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.get_display_string()


class ExperimentFormBase(forms.Form):
    plate__id = forms.IntegerField(
        required=False, label='Exact plate ID', help_text='e.g. 32412')

    plate__id__range = RangeField(
        forms.IntegerField, required=False, label='Plate ID range')

    plate__date = forms.DateField(
        required=False, label='Exact date', help_text='YYYY-MM-DD')

    plate__date__range = RangeField(
        forms.DateField, required=False, label='Date range')

    plate__temperature = forms.ChoiceField(
        choices=get_temperature_choices(),
        required=False, label='Exact temp')

    plate__temperature__range = RangeField(
        forms.DecimalField, widget_kwargs={'attrs': {'step': '0.1'}},
        required=False, label='Temp range')

    worm_strain = WormModelChoiceField(
        queryset=WormStrain.objects.all(),
        required=False, label='Worm strain')

    worm_strain__gene = forms.ChoiceField(
        choices=get_worm_gene_choices(),
        required=False, label='Worm gene')

    plate__screen_stage = forms.ChoiceField(
        choices=[EMPTY_CHOICE] + list(ExperimentPlate.SCREEN_STAGE_CHOICES),
        required=False, label='Screen stage')

    library_stock__plate = forms.CharField(
        required=False, label='Library plate', help_text='e.g. II-3-B2')


class ExperimentFilterForm(ExperimentFormBase):
    """Form for filtering Experiment instances."""

    library_stock = forms.CharField(
        required=False, help_text='e.g. I-3-B2_A01',
        widget=forms.TextInput(attrs={'size': '15'}))

    library_stock__intended_clone = forms.CharField(
        required=False, label='Intended clone', help_text='e.g. sjj_AH10.4',
        widget=forms.TextInput(attrs={'size': '15'}))

    exclude_l4440 = forms.BooleanField(
        required=False, label='Exclude L4440')

    is_junk = forms.NullBooleanField(
        required=False, initial=None, widget=BlankNullBooleanSelect)

    def clean(self):
        cleaned_data = super(ExperimentFilterForm, self).clean()

        if 'exclude_l4440' in cleaned_data:
            exclude_l4440 = cleaned_data['exclude_l4440']
            del cleaned_data['exclude_l4440']
        else:
            exclude_l4440 = None

        for k, v in cleaned_data.items():
            # Retain 'False' as a legitimate filter
            if v is False:
                continue

            # Ditch empty strings and None as filters
            if not v:
                del cleaned_data[k]

        experiments = Experiment.objects.filter(**cleaned_data)

        if exclude_l4440:
            experiments = experiments.exclude(library_stock__intended_clone='L4440')

        cleaned_data['experiments'] = experiments
        return cleaned_data



class ExperimentPlateFilterForm(ExperimentFormBase):
    """Form for filtering ExperimentPlate instances."""

    is_junk = forms.NullBooleanField(
        required=False, initial=None, label="Has junk",
        widget=BlankNullBooleanSelect)

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
