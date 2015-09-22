from __future__ import division
import string

from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q

from eegi.settings import IMG_PATH, THUMBNAIL_PATH, DEVSTAR_PATH
from library.models import LibraryPlate
from utils.well_tile_conversion import well_to_tile
from worms.models import WormStrain


STRONG = 'Strong'
MEDIUM = 'Medium'
WEAK = 'Weak'
OTHER = 'Other'
NEGATIVE = 'Negative'
UNSCORED = 'Unscored'

SCORE_WEIGHTS = {
    STRONG: 3,
    MEDIUM: 2,
    WEAK: 1,
    NEGATIVE: 0,
    OTHER: 0,
}

RELEVANCE_PER_REPLICATE = (OTHER, NEGATIVE, WEAK, MEDIUM, STRONG)
RELEVANCE_ACROSS_REPLICATES = (NEGATIVE, OTHER, UNSCORED, WEAK, MEDIUM, STRONG)


class Experiment(models.Model):
    """A plate-level experiment.

    I.e., flat-bottom plate in which worms and RNAi clones were combined
    and put at a specific temperature.

    """
    SCREEN_STAGE_CHOICES = (
        (1, 'Primary'),
        (2, 'Secondary'),
    )

    id = models.PositiveIntegerField(primary_key=True)
    worm_strain = models.ForeignKey(WormStrain)
    library_plate = models.ForeignKey(LibraryPlate)
    library_plate_copy_number = models.PositiveSmallIntegerField(null=True,
                                                                 blank=True)
    screen_stage = models.PositiveSmallIntegerField(db_index=True)
    temperature = models.DecimalField(max_digits=3, decimal_places=1,
                                      db_index=True)
    date = models.DateField(db_index=True)
    is_junk = models.BooleanField(default=False, db_index=True)
    comment = models.TextField(blank=True)

    class Meta:
        db_table = 'Experiment'
        ordering = ['id']

    def __unicode__(self):
        return str(self.id)

    def get_image_url(self, well):
        """Get the url of an experiment image.

        Accepts an Experiment object, and well as a string.

        """
        tile = well_to_tile(well)
        url = '/'.join((IMG_PATH, str(self.id), tile))
        return url

    def get_thumbnail_url(self, well):
        """Get the url of an experiment thumbnail image.

        Accepts an Experiment object, and well as a string.

        """
        tile = well_to_tile(well)
        url = '/'.join((THUMBNAIL_PATH, str(self.id), tile))
        url = string.replace(url, 'bmp', 'jpg')
        return url

    def get_devstar_image_url(self, well):
        """Get the url of a DevStaR output image.

        Accepts an Experiment object, and well as a string.

        """
        tile = well_to_tile(well)
        url = '/'.join((DEVSTAR_PATH, str(self.id), tile))
        url = string.replace(url, '.bmp', 'res.png')
        return url

    def get_scores(self, well=None):
        """Get all scores for this experiment.

        Defaults to all scores for the entire plate, or specify
        well to get the scores for a particular well.

        """
        if well:
            scores = (ManualScore.objects
                      .filter(Q(experiment=self), Q(well=well))
                      .order_by('scorer', 'timestamp', 'score_code'))
        else:
            scores = ManualScore.objects.filter(experiment=self)

        return scores

    def is_scored(self, well=None):
        """Determine whether an experiment has scores.

        Defaults to checking if any well was scored, or specify well
        to get whether a particular well was scored.

        """
        if self.get_scores(well=well):
            return True
        else:
            return False


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
        return (not self.is_strong() and not self.is_medium()
                and not self.is_weak() and not self.is_negative())


class ManualScore(models.Model):
    """A score that was assigned to a particular image by a human."""
    experiment = models.ForeignKey(Experiment)
    well = models.CharField(max_length=3)
    score_code = models.ForeignKey(ManualScoreCode)
    scorer = models.ForeignKey(User)
    timestamp = models.DateTimeField()

    class Meta:
        db_table = 'ManualScore'

    def __unicode__(self):
        return ('{}@{} scored {} by {}'
                .format(self.experiment_id, self.well,
                        self.score_code, self.scorer))

    def get_short_description(self):
        return '{} ({})'.format(self.score_code, self.scorer.get_short_name())

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
        if self.is_strong():
            return STRONG
        elif self.is_medium():
            return MEDIUM
        elif self.is_weak():
            return WEAK
        elif self.is_negative():
            return NEGATIVE
        elif self.is_other():
            return OTHER

    def get_weight(self):
        """Returns a relevance weight for this score.

        Note that relevance and strength do not always coincide
        (a 'negative' score is more relevant than an 'other' score, since
        'negative' means that it does not indicate a genetic interaction,
        whereas 'other' may be any auxiliary score, such as an experiment
        problem or a phenotype unrelated to sup/enh).

        """
        return SCORE_WEIGHTS[self.get_category()]

    def get_relevance_per_replicate(self):
        return RELEVANCE_PER_REPLICATE.index(self.get_category())

    def get_relevance_across_replicates(self):
        return RELEVANCE_ACROSS_REPLICATES.index(self.get_category())


class DevstarScore(models.Model):
    """Information about an image determined by the DevStaR computer vision
    program.

    """
    experiment = models.ForeignKey(Experiment)
    well = models.CharField(max_length=3)

    # TODO: consider adding db_index=True to some of these
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

    def __unicode__(self):
        return ('{}@{} DevStaR score'
                .format(self.experiment_id, self.well))

    def clean(self):
        # Set the fields calculated from the DevStaR fields (resets if already
        # set).

        # Floor division for egg count
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
