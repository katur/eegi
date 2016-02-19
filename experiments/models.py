from __future__ import division

from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db import models

from experiments.helpers.naming import generate_experiment_id
from experiments.helpers.scores import get_most_relevant_score_per_experiment
from library.models import LibraryPlate, LibraryStock
from utils.plates import get_well_list
from utils.well_tile_conversion import well_to_tile
from worms.models import WormStrain


class ExperimentPlate(models.Model):
    """A plate-level experiment."""

    SCREEN_STAGE_CHOICES = (
        (1, 'Primary'),
        (2, 'Secondary'),
    )

    id = models.PositiveIntegerField(primary_key=True)
    screen_stage = models.PositiveSmallIntegerField(db_index=True)
    temperature = models.DecimalField(max_digits=3, decimal_places=1,
                                      db_index=True)
    date = models.DateField(db_index=True)
    comment = models.TextField(blank=True)

    class Meta:
        db_table = 'ExperimentPlate'
        ordering = ['id']

    def __unicode__(self):
        return str(self.id)

    def get_absolute_url(self):
        return reverse('experiment_plate_url', args=[self.id])

    @classmethod
    def get_tested_temperatures(cls):
        """
        Get all temperatures for which there are experiments.
        """
        return (cls.objects.all()
                .order_by('temperature')
                .values_list('temperature', flat=True)
                .distinct())

    @classmethod
    def create_plate_and_wells(
            cls, experiment_plate_id, screen_stage, date, temperature,
            worm_strain, library_plate, is_junk=False, plate_comment='',
            dry_run=False):
        """
        Create a new experiment plate plus its 96 wells.

        Assumes that the new experiment plate:
            1) contains the same worm strain in all wells
            2) is derived from one library plate
            3) has the same is_junk value in all wells

        Returns a 2-tuple of the new plate and wells.

        By default, saves the new plate and wells to the database.
        Set dry_run=True to instead do a dry run.
        """
        if cls.objects.filter(id=experiment_plate_id).exists():
            raise ValueError('ExperimentPlate {} already exists'
                             .format(experiment_plate_id))

        experiment_plate = cls(
            id=experiment_plate_id,
            screen_stage=screen_stage,
            date=date,
            temperature=temperature,
            comment=plate_comment)

        experiment_wells = experiment_plate.create_wells(
            worm_strain, library_plate, is_junk=is_junk)

        if not dry_run:
            experiment_plate.save()
            Experiment.objects.bulk_create(experiment_wells)

        return (experiment_plate, experiment_wells)

    def create_wells(self, worm_strain, library_plate, is_junk=False):
        """
        Returns the experiment wells that go with this experiment plate.

        Raises an exception if there are already experiment wells
        for this experiment plate in the database.

        Initializes each new well's worm, library stock, and junk
        according to the parameters passed in.
        """
        if Experiment.objects.filter(plate=self).exists():
            raise Exception('Experiments already exists for plate {}'
                            .format(self))

        stocks_by_well = library_plate.get_stocks_as_dictionary()
        new_experiment_wells = []

        for well in get_well_list():
            library_stock = stocks_by_well[well]

            new_experiment_wells.append(Experiment(
                id=generate_experiment_id(self.id, well),
                plate=self, well=well,
                worm_strain=worm_strain,
                library_stock=library_stock,
                is_junk=is_junk))

        return new_experiment_wells

    def get_experiment_wells(self):
        """
        Get the experiment wells for this plate, ordered by well.

        Selects the related library stocks and intended clones.
        """
        experiments = (self.experiment_set
                       .select_related('library_stock',
                                       'library_stock__intended_clone')
                       .order_by('well'))

        return experiments

    def get_worm_strains(self):
        """
        Get all worm strains present in this plate.

        While we typically only put one worm strain in each plate,
        the database accommodates different worm strains
        in different wells.
        """
        worm_pks = (self.experiment_set.order_by('worm_strain')
                    .values('worm_strain').distinct())

        return WormStrain.objects.filter(pk__in=worm_pks)

    def get_library_plates(self):
        """
        Get all library plates present in this experiment plate.

        While we typically only put one library plate into each
        experiment plate, the database accommodates different
        assortments of library stocks.
        """
        library_plate_pks = (self.experiment_set
                             .order_by('library_stock__plate')
                             .values('library_stock__plate')
                             .distinct())

        return LibraryPlate.objects.filter(pk__in=library_plate_pks)

    def has_junk(self):
        """
        Determine if any of the wells in this experiment plate are junk.
        """
        junk = self.experiment_set.values_list('is_junk', flat=True)
        return True in junk

    def set_worm_strain(self, worm_strain):
        """Set the worm strain for all wells in this plate."""
        for experiment in self.experiment_set.all():
            experiment.worm_strain = worm_strain
            experiment.save()

    def set_library_plate(self, library_plate):
        """
        Set the library stock for all wells in this plate.

        Assumes the standard mapping from library_plate positions
        to experiment_plate positions.
        """
        stocks_by_well = library_plate.get_stocks_as_dictionary()
        for experiment in self.experiment_set.all():
            well = experiment.well
            experiment.library_stock = stocks_by_well[well]
            experiment.save()

    def set_junk(self, is_junk):
        """Set the junk field for all wells in this plate."""
        for experiment in self.experiment_set.all():
            experiment.is_junk = is_junk
            experiment.save()


class Experiment(models.Model):
    """A well-level experiment."""
    id = models.CharField(max_length=20, primary_key=True)
    plate = models.ForeignKey(ExperimentPlate)
    well = models.CharField(max_length=3)
    worm_strain = models.ForeignKey(WormStrain)
    library_stock = models.ForeignKey(LibraryStock)
    is_junk = models.BooleanField(default=False, db_index=True)
    comment = models.TextField(blank=True)

    class Meta:
        db_table = 'Experiment'
        ordering = ['plate', 'well']
        unique_together = ('plate', 'well')

    def __unicode__(self):
        return str(self.id)

    def get_absolute_url(self):
        return reverse('experiment_well_url', args=[self.id])

    def is_control(self):
        return self.has_control_worm() or self.has_control_clone()

    def has_control_worm(self):
        return self.worm_strain.is_control()

    def has_control_clone(self):
        return self.library_stock.intended_clone.is_control()

    def date(self):
        return self.plate.date

    def screen_stage(self):
        return self.plate.screen_stage

    def temperature(self):
        return self.plate.temperature

    def intended_clone(self):
        return self.library_stock.intended_clone

    # TODO: These three are repeated in Experiment and LibraryStock;
    # consider making a superclass or mixin
    def get_row(self):
        return self.well[0]

    def get_column(self):
        return int(self.well[1:])

    def get_tile(self):
        return well_to_tile(self.well)

    def get_image_url(self, mode=None):
        """
        Get the image url for this experiment.

        Optionally supply mode='thumbnail' or mode='devstar'.
        """
        tile = well_to_tile(self.well)
        if mode == 'thumbnail':
            url = '/'.join((settings.BASE_URL_THUMBNAIL,
                            str(self.plate_id), tile))
            url += '.jpg'
        elif mode == 'devstar':
            url = '/'.join((settings.BASE_URL_DEVSTAR,
                            str(self.plate_id), tile))
            url += 'res.png'
        else:
            url = '/'.join((settings.BASE_URL_IMG,
                            str(self.plate_id), tile))
            url += '.bmp'
        return url

    def get_devstar_count_path(self):
        tile = well_to_tile(self.well)
        f = '/'.join((settings.BASE_DIR_DEVSTAR_OUTPUT,
                      str(self.plate_id), tile))
        f += 'cnt.txt'
        return f

    def get_manual_scores(self):
        """Get all manual scores for this experiment well."""
        return self.manualscore_set.all()

    def get_devstar_scores(self):
        """Get all DevStaR scores for this experiment."""
        return self.devstarscore_set.all()

    def is_manually_scored(self):
        """Check if an experiment was manually scored."""
        if self.get_manual_scores():
            return True
        else:
            return False

    def is_devstar_scored(self):
        """Check if an experiment was scored by DevStaR."""
        if self.get_devstar_scores():
            return True
        else:
            return False

    def get_most_relevant_manual_score(self):
        """Get the most relevant manual score for this experiment."""
        scores = self.get_manual_scores()
        return get_most_relevant_score_per_experiment(scores)

    def toggle_junk(self):
        """
        Toggle the junk state of this experiment.

        I.e., if this experiment is not junk, change it to junk;
        if this experiment is junk, change it to not junk.
        """
        self.is_junk = not self.is_junk
        self.save()


class ManualScoreCode(models.Model):
    """A class of score that could be assigned to an image by a human."""

    id = models.IntegerField(primary_key=True)
    description = models.CharField(max_length=100, blank=True)
    short_description = models.CharField(max_length=50, blank=True)
    legacy_description = models.CharField(max_length=100, blank=True)

    STRONG_CODES = (3, 14, 18)
    MEDIUM_CODES = (2, 13, 17)
    WEAK_CODES = (1, 12, 16)
    NEGATIVE_CODES = (0,)

    class Meta:
        db_table = 'ManualScoreCode'
        ordering = ['id']

    def __unicode__(self):
        if self.short_description:
            return self.short_description
        elif self.description:
            return self.description
        elif self.legacy_description:
            return self.legacy_description
        else:
            return str(self.id)

    def is_strong(self):
        return self.id in ManualScoreCode.STRONG_CODES

    def is_medium(self):
        return self.id in ManualScoreCode.MEDIUM_CODES

    def is_weak(self):
        return self.id in ManualScoreCode.WEAK_CODES

    def is_negative(self):
        return self.id in ManualScoreCode.NEGATIVE_CODES

    def is_other(self):
        return (not self.is_strong() and not self.is_medium() and
                not self.is_weak() and not self.is_negative())


class ManualScore(models.Model):
    """A score that was assigned to a particular image by a human."""

    experiment = models.ForeignKey(Experiment)
    score_code = models.ForeignKey(ManualScoreCode)
    scorer = models.ForeignKey(User)
    timestamp = models.DateTimeField()

    STRONG = 'Strong'
    MEDIUM = 'Medium'
    WEAK = 'Weak'
    OTHER = 'Other'
    NEGATIVE = 'Negative'
    UNSCORED = 'Unscored'

    WEIGHTS = {
        STRONG: 3,
        MEDIUM: 2,
        WEAK: 1,
        NEGATIVE: 0,
        OTHER: 0,
    }

    # Both start with least relevant, end with most relevant
    RELEVANCE_PER_REPLICATE = (OTHER, NEGATIVE, WEAK, MEDIUM, STRONG)
    RELEVANCE_ACROSS_REPLICATES = (NEGATIVE, OTHER, UNSCORED, WEAK, MEDIUM,
                                   STRONG)

    class Meta:
        db_table = 'ManualScore'
        ordering = ['experiment', 'scorer', 'timestamp', 'score_code']

    def __unicode__(self):
        return ('{} scored {} by {}'
                .format(self.experiment_id, self.score_code, self.scorer))

    def get_short_description(self):
        return '{} ({})'.format(self.score_code,
                                self.scorer.get_short_name())

    def is_strong(self):
        return self.score_code.is_strong()

    def is_medium(self):
        return self.score_code.is_medium()

    def is_weak(self):
        return self.score_code.is_weak()

    def is_negative(self):
        return self.score_code.is_negative()

    def is_other(self):
        return self.score_code.is_other()

    def get_category(self):
        """Get this score's more general score category."""
        if self.is_strong():
            return ManualScore.STRONG
        elif self.is_medium():
            return ManualScore.MEDIUM
        elif self.is_weak():
            return ManualScore.WEAK
        elif self.is_negative():
            return ManualScore.NEGATIVE
        elif self.is_other():
            return ManualScore.OTHER

    def get_weight(self):
        """
        Get the relevance weight for this score.

        Note that relevance and strength do not always coincide
        (a 'negative' score is more relevant than an 'other' score, since
        'negative' means that it does not indicate a genetic interaction,
        whereas 'other' may be any auxiliary score, such as an experiment
        problem or a phenotype unrelated to sup/enh).
        """
        return ManualScore.WEIGHTS[self.get_category()]

    def get_relevance_per_replicate(self):
        """
        Get this score's relevance within an experiment replicate.

        This ranking can be used to boil down the multiple scores for
        an experiment to a single most important score.
        """
        return ManualScore.RELEVANCE_PER_REPLICATE.index(
            self.get_category())

    def get_relevance_across_replicates(self):
        """
        Get this score's relevance across experiment replicates.

        This ranking can be used to decide the most important
        replicates. For example, we generally had two primary replicates,
        but in some cases we had more. If a positive definition is
        required to look at two scores, this ranking can help
        determine the two most relevant replicates.
        """
        return ManualScore.RELEVANCE_ACROSS_REPLICATES.index(
            self.get_category())


class DevstarScore(models.Model):
    """Information about an image determined by the DevStaR."""

    experiment = models.ForeignKey(Experiment)

    area_adult = models.IntegerField(null=True, blank=True,
                                     help_text='DevStaR program output')
    area_larva = models.IntegerField(null=True, blank=True,
                                     help_text='DevStaR program output')
    area_embryo = models.IntegerField(null=True, blank=True,
                                      help_text='DevStaR program output')
    count_adult = models.IntegerField(null=True, blank=True,
                                      help_text='DevStaR program output')
    count_larva = models.IntegerField(null=True, blank=True,
                                      help_text='DevStaR program output')
    count_embryo = models.IntegerField(null=True, blank=True,
                                       help_text='area_embryo // 70')

    larva_per_adult = models.FloatField(
        null=True, blank=True, default=None,
        help_text='count_larva / count_adult')
    embryo_per_adult = models.FloatField(
        null=True, blank=True, default=None,
        help_text='count_embryo / count_adult')

    survival = models.FloatField(
        null=True, blank=True, default=None,
        help_text='count_larva / (count_larva + count_embryo)')
    lethality = models.FloatField(
        null=True, blank=True, default=None,
        help_text='count_embryo / (count_larva + count_embryo)')

    is_bacteria_present = models.NullBooleanField(
        default=None, help_text='DevStaR program output')

    selected_for_scoring = models.NullBooleanField(default=None)

    gi_score_larva_per_adult = models.FloatField(null=True, blank=True,
                                                 default=None)
    gi_score_survival = models.FloatField(null=True, blank=True, default=None)

    class Meta:
        db_table = 'DevstarScore'
        ordering = ['experiment']

    def __unicode__(self):
        return ('{} DevStaR score'.format(self.experiment_id))

    def clean(self):
        """
        Clean up to run when saving a DevstarScore instance.

        This sets the fields that are derived from the DevStaR raw output.
        """
        # Use floor division for egg count
        if self.area_embryo is not None:
            self.count_embryo = self.area_embryo // 70

        if self.count_larva is not None and self.count_adult is not None:
            if self.count_adult == 0:
                self.larva_per_adult = None
            else:
                self.larva_per_adult = self.count_larva / self.count_adult

        if self.count_embryo is not None and self.count_adult is not None:
            if self.count_adult == 0:
                self.embryo_per_adult = None
            else:
                self.embryo_per_adult = self.count_embryo / self.count_adult

        if self.count_embryo is not None and self.count_larva is not None:
            brood_size = self.count_larva + self.count_embryo
            if brood_size == 0:
                self.surival = None
                self.lethality = None
            else:
                self.survival = self.count_larva / brood_size
                self.lethality = self.count_embryo / brood_size

    def matches_raw_fields(self, other):
        return (
            self.experiment == other.experiment and
            self.is_bacteria_present == other.is_bacteria_present and
            self.area_adult == other.area_adult and
            self.area_larva == other.area_larva and
            self.area_embryo == other.area_embryo and
            self.count_adult == other.count_adult and
            self.count_larva == other.count_larva)
