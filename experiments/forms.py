from django import forms
from django.core.validators import MinLengthValidator

from clones.forms import RNAiKnockdownField
from experiments.models import (Experiment, ExperimentPlate, ManualScore,
                                ManualScoreCode)
from library.forms import LibraryPlateField
from utils.forms import EMPTY_CHOICE, BlankNullBooleanSelect, RangeField
from worms.forms import (MutantKnockdownField, ScreenTypeChoiceField,
                         WormChoiceField, clean_mutant_query_and_screen_type)


###########
# Helpers #
###########

def remove_empties_and_none(d):
    """Remove key-value pairs from dictionary if the value is '' or None."""
    for k, v in d.items():
        # Retain 'False' as a legitimate filter
        if v is False:
            continue

        # Ditch empty strings and None as filters
        if not v:
            del d[k]


######################
# Custom Form Fields #
######################

class ScreenStageChoiceField(forms.ChoiceField):
    """Field for choosing Primary, Secondary, etc."""

    def __init__(self, **kwargs):
        if 'choices' not in kwargs:
            choices = ([EMPTY_CHOICE] +
                       list(ExperimentPlate.SCREEN_STAGE_CHOICES))

            kwargs['choices'] = choices

        super(ScreenStageChoiceField, self).__init__(**kwargs)


class TemperatureChoiceField(forms.ChoiceField):
    """Field for selecting a tested temperature."""

    def __init__(self, **kwargs):
        if 'choices' not in kwargs:
            temperatures = ExperimentPlate.get_tested_temperatures()
            choices = [EMPTY_CHOICE] + [(x, x) for x in temperatures]
            kwargs['choices'] = choices

        super(TemperatureChoiceField, self).__init__(**kwargs)


class ScoringFormChoiceField(forms.ChoiceField):
    """Field for selecting which scoring form (buttons) should display."""

    def __init__(self, **kwargs):
        if 'choices' not in kwargs:
            kwargs['choices'] = [
                ('SUP', 'Suppressor w/m/s'),
            ]

        super(ScoringFormChoiceField, self).__init__(**kwargs)


class SuppressorScoreField(forms.ModelChoiceField):
    """Field for choosing a level of suppression."""

    def __init__(self, **kwargs):
        if 'queryset' not in kwargs:
            kwargs['queryset'] = ManualScoreCode.get_codes('SUP')

        if 'widget' not in kwargs:
            kwargs['widget'] = forms.RadioSelect

        super(SuppressorScoreField, self).__init__(**kwargs)


class AuxiliaryScoreField(forms.ModelMultipleChoiceField):
    """Field for selecting auxiliary scores."""

    def __init__(self, **kwargs):
        if 'queryset' not in kwargs:
            kwargs['queryset'] = ManualScoreCode.get_codes('AUXILIARY')

        if 'widget' not in kwargs:
            kwargs['widget'] = forms.CheckboxSelectMultiple

        super(AuxiliaryScoreField, self).__init__(**kwargs)


#####################
# Custom validators #
#####################

def validate_new_experiment_plate_id(x):
    """Validate that x is a valid ID for a new experiment plate."""
    if x <= 0:
        raise forms.ValidationError('ExperimentPlate ID must be positive')

    if ExperimentPlate.objects.filter(pk=x).count():
        raise forms.ValidationError('ExperimentPlate ID {} already exists'
                                    .format(x))


###################################
# Forms for filtering experiments #
###################################

class _FilterExperimentsBaseForm(forms.Form):
    """Base for FilterExperimentWellsForm, FilterExperimentPlatesForm, etc."""

    plate__pk = forms.IntegerField(
        required=False, label='Plate ID', help_text='e.g. 32412')

    plate__date = forms.DateField(
        required=False, label='Date', help_text='YYYY-MM-DD')

    '''
    TODO: When the below field was a TemperatureChoiceField, it caused
    issues when calling ./manage.py subcommands on an empty database.

    (In case you're wonding, why was I calling ./manage.py on an empty
     database? It was to populate an empty database from scratch, by
     running `./manage.py migrate`).

    The error (which I saw both when trying to run `./manage.py migrate`
    and `./manage.py runserver`:

        django.db.utils.ProgrammingError: (1146, "Table
            'eegi.experimentplate' doesn't exist")

    This only causes an issue with Django >=1.9.0. Django 1.8.9 was
    fine.

    Will need to look into this. For now just use a DecimalField instead.
    '''
    plate__temperature = forms.DecimalField(
        required=False, label='Temperature')

    plate__screen_stage = ScreenStageChoiceField(
        required=False, label='Screen stage')

    worm_strain = WormChoiceField(required=False)


class FilterExperimentPlatesForm(_FilterExperimentsBaseForm):
    """Form for filtering ExperimentPlate instances."""

    plate__pk__range = RangeField(
        forms.IntegerField, required=False, label='Plate ID range')

    plate__date__range = RangeField(
        forms.DateField, required=False, label='Date range')

    plate__temperature__range = RangeField(
        forms.DecimalField, required=False, label='Temperature range')

    library_stock__plate = LibraryPlateField(
        required=False, label='Library plate', help_text='e.g. II-3-B2')

    is_junk = forms.NullBooleanField(
        required=False, initial=None, label='Has junk',
        widget=BlankNullBooleanSelect)

    field_order = [
        'plate__pk', 'plate__pk__range',
        'plate__date',  'plate__date__range',
        'plate__temperature', 'plate__temperature__range',
        'worm_strain', 'plate__screen_stage',
        'library_stock__plate', 'is_junk',
    ]

    def clean(self):
        cleaned_data = super(FilterExperimentPlatesForm, self).clean()

        remove_empties_and_none(cleaned_data)
        plate_pks = (Experiment.objects.filter(**cleaned_data)
                     .order_by('plate').values_list('plate', flat=True))
        cleaned_data['experiment_plates'] = (ExperimentPlate.objects
                                             .filter(pk__in=plate_pks))

        return cleaned_data


class FilterExperimentWellsForm(_FilterExperimentsBaseForm):
    """Form for filtering Experiment instances."""

    pk = forms.CharField(required=False, help_text='e.g. 32412_A01',
                         label='ID')

    well = forms.CharField(required=False, help_text='e.g. A01')

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

    field_order = [
        'pk', 'plate__pk', 'well',
        'plate__date', 'plate__temperature',
        'worm_strain', 'plate__screen_stage',
        'library_stock', 'library_stock__intended_clone',
        'exclude_l4440', 'is_junk',
    ]

    def clean(self):
        cleaned_data = super(FilterExperimentWellsForm, self).clean()

        exclude_l4440 = cleaned_data.pop('exclude_l4440')

        remove_empties_and_none(cleaned_data)
        experiments = Experiment.objects.filter(**cleaned_data)

        if exclude_l4440:
            experiments = experiments.exclude(
                library_stock__intended_clone='L4440')

        cleaned_data['experiments'] = experiments
        return cleaned_data


#################################
# Forms for scoring experiments #
#################################

class FilterExperimentWellsToScoreForm(_FilterExperimentsBaseForm):
    """Form for filtering experiment wells to score."""

    form = ScoringFormChoiceField(label='Which buttons?')
    unscored_by_user = forms.BooleanField(
        required=False, initial=True,
        label='Limit to unscored by currently logged in user?')
    exclude_l4440 = forms.BooleanField(
        required=False, initial=True, label='Exclude L4440')

    pk = forms.CharField(required=False, help_text='e.g. 32412_A01',
                         label='ID')
    is_junk = forms.NullBooleanField(
        required=False, initial=False, widget=BlankNullBooleanSelect)

    field_order = [
        'form', 'unscored_by_user', 'exclude_l4440',
        'pk', 'plate__pk', 'well',
        'plate__date', 'plate__temperature',
        'worm_strain', 'plate__screen_stage', 'is_junk'
    ]

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(FilterExperimentWellsToScoreForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super(FilterExperimentWellsToScoreForm, self).clean()

        form = cleaned_data.pop('form')
        unscored_by_user = cleaned_data.pop('unscored_by_user')
        exclude_l4440 = cleaned_data.pop('exclude_l4440')

        remove_empties_and_none(cleaned_data)
        experiments = Experiment.objects.filter(**cleaned_data)

        if exclude_l4440:
            experiments = experiments.exclude(
                library_stock__intended_clone='L4440')

        if unscored_by_user:
            score_ids = (
                ManualScore.objects
                .filter(experiment__in=experiments, scorer=self.user)
                .values_list('experiment_id', flat=True))
            experiments = experiments.exclude(id__in=score_ids)

        cleaned_data['form'] = form
        cleaned_data['unscored_by_user'] = unscored_by_user
        cleaned_data['experiments'] = experiments

        return cleaned_data


class SuppressorScoreForm(forms.Form):
    sup_score = SuppressorScoreField()
    auxiliary_scores = AuxiliaryScoreField(required=False)


def get_score_form(key):
    d = {
        'SUP': SuppressorScoreForm,
    }
    return d[key]


#################################
# Forms for editing experiments #
#################################

class AddExperimentPlateForm(forms.Form):
    """
    Form for adding a new experiment plate.

    Adding a new experiment plate also adds the corresponding
    experiment wells.

    This form makes certain assumptions about the experiment plate:
        - it comes from one library plate
        - it has same worm strain in every well
        - the whole plate is or is not junk
    """

    experiment_plate_id = forms.IntegerField(
        required=True,
        validators=[validate_new_experiment_plate_id])
    screen_stage = ScreenStageChoiceField(required=True)
    date = forms.DateField(required=True, help_text='YYYY-MM-DD')
    temperature = forms.DecimalField(required=True)
    worm_strain = WormChoiceField(required=True)
    library_plate = LibraryPlateField(required=True)
    is_junk = forms.BooleanField(initial=False, required=False)
    plate_comment = forms.CharField(required=False)


class ChangeExperimentPlatesForm(forms.Form):
    """
    Form for updating multiple experiment plates.

    Depending on what field(s) are being updated, the corresponding
    experiment wells might be updated as well.

    Keep in mind the following assumptions that will apply if
    updating one of the following fields:
        - each experiment plate comes from one library plate
        - each experiment plate has only one worm strain
        - each experiment plate is or is not junk
    """

    # Plate-level fields
    screen_stage = ScreenStageChoiceField(required=False)
    date = forms.DateField(required=False, help_text='YYYY-MM-DD')
    temperature = forms.DecimalField(required=False)
    comment = forms.CharField(required=False, label='Plate comment')

    # Well-level fields
    worm_strain = WormChoiceField(required=False)
    is_junk = forms.NullBooleanField(
        required=False, initial=None, widget=BlankNullBooleanSelect)

    # Other
    library_plate = LibraryPlateField(required=False)
    clear_plate_comment = forms.BooleanField(required=False)

    field_order = [
        'screen_stage', 'date', 'temperature', 'worm_strain',
        'library_plate', 'is_junk', 'plate_comment', 'well_comment']


def process_ChangeExperimentPlatesForm_data(experiment_plate, data):
    """
    Helper to apply the ChangeExperimentPlateForm changes to a specific
    plate.

    data should be the cleaned_data from a ChangeExperimentPlatesForm.
    """
    # First update straightforward plate fields
    for key in ('screen_stage', 'date', 'temperature', 'comment',):
        value = data.get(key)

        if value:
            setattr(experiment_plate, key, value)
            experiment_plate.save()

    # Next update plate methods
    if data.get('worm_strain'):
        experiment_plate.set_worm_strain(data.get('worm_strain'))

    if data.get('library_plate'):
        experiment_plate.set_library_plate(data.get('library_plate'))

    if data.get('is_junk') is not None:
        experiment_plate.set_junk(data.get('is_junk'))

    return


#############################
# Forms for Knockdown pages #
#############################

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


####################################
# Forms for Secondary Scores pages #
####################################

class SecondaryScoresForm(forms.Form):
    """Form for getting all secondary scores for a worm/screen combo."""

    mutant_query = MutantKnockdownField()
    screen_type = ScreenTypeChoiceField()

    def clean(self):
        cleaned_data = super(SecondaryScoresForm, self).clean()
        cleaned_data = clean_mutant_query_and_screen_type(self, cleaned_data)
        return cleaned_data
