from __future__ import division

from django.db import models
from django.contrib.auth.models import User

from worms.models import WormStrain
from library.models import LibraryPlate


class Experiment(models.Model):
    """
    A plate-level experiment (i.e., a flat-bottom plate in which
    worms and RNAi clones were put at a specific temperature).

    This table is essentially 'RawData' in the GenomeWideGI database.
    """
    id = models.PositiveIntegerField(primary_key=True)
    worm_strain = models.ForeignKey(WormStrain)
    library_plate = models.ForeignKey(LibraryPlate)
    library_plate_copy_number = models.PositiveSmallIntegerField(null=True,
                                                                 blank=True)
    screen_level = models.PositiveSmallIntegerField()
    temperature = models.DecimalField(max_digits=3, decimal_places=1)
    date = models.DateField()
    is_junk = models.BooleanField(default=False)
    comment = models.TextField(blank=True)

    class Meta:
        db_table = 'Experiment'
        ordering = ['id']

    def __unicode__(self):
        return str(self.id)


class ManualScoreCode(models.Model):
    id = models.IntegerField(primary_key=True)
    description = models.CharField(max_length=100, blank=True)
    short_description = models.CharField(max_length=50, blank=True)
    legacy_description = models.CharField(max_length=100, blank=True)

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


class ManualScore(models.Model):
    experiment = models.ForeignKey(Experiment)
    well = models.CharField(max_length=3)
    score_code = models.ForeignKey(ManualScoreCode)
    scorer = models.ForeignKey(User)
    timestamp = models.DateTimeField()

    class Meta:
        db_table = 'ManualScore'

    def __unicode__(self):
        return ('{}:{} scored {} by {}'
                .format(str(self.experiment), self.well,
                        str(self.score_code), str(self.scorer)))


class DevstarScore(models.Model):
    experiment = models.ForeignKey(Experiment)
    well = models.CharField(max_length=3)

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
                                       help_text='area_embryo / 70')

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

    gi_score_larva_per_adult = models.FloatField(
        null=True, blank=True, default=None, help_text='')
    gi_score_survival = models.FloatField(
        null=True, blank=True, default=None, help_text='')

    class Meta:
        db_table = 'DevstarScore'

    def __unicode__(self):
        return ('{}:{} DevStaR score'
                .format(str(self.experiment), self.well))

    def clean(self):
        # Set the fields calculated from the DevStaR fields (resets if already
        # set).

        # Floor division for egg count
        if self.area_embryo is not None:
            self.count_embryo = self.area_embryo // 70

        if self.count_larva is not None and self.count_adult is not None:
            if self.count_adult == 0:
                self.larva_per_adult = 0
            else:
                self.larva_per_adult = self.count_larva / self.count_adult

        if self.count_embryo is not None and self.count_adult is not None:
            if self.count_adult == 0:
                self.embryo_per_adult = 0
            else:
                self.embryo_per_adult = self.count_embryo / self.count_adult

        if self.count_embryo is not None and self.count_larva is not None:
            brood_size = self.count_larva + self.count_embryo
            if brood_size == 0:
                self.surival = 0
                self.lethality = 0
            else:
                self.survival = self.count_larva / brood_size
                self.lethality = self.count_embryo / brood_size
