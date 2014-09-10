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
    scorer = models.ForeignKey(User, null=True, blank=True)
    timestamp = models.DateTimeField(null=True, blank=True)

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

    larvae_per_adult = models.FloatField(
        null=True, blank=True, default=None,
        help_text='count_larva / count_adult')
    embryo_per_adult = models.FloatField(
        null=True, blank=True, default=None,
        help_text='count_embryo / count_adult')
    survival = models.FloatField(
        null=True, blank=True, default=None,
        help_text='count_larvae / (count_larvae + count_embryo)')
    lethality = models.IntegerField(
        null=True, blank=True, default=None,
        help_text='count_embryo / (count_larvae + count_embryo)')

    is_bacteria_present = models.NullBooleanField(default=None)

    gi_score_larvae_per_adult = models.FloatField(
        null=True, blank=True, default=None, help_text='')
    gi_score_survival = models.FloatField(
        null=True, blank=True, default=None, help_text='')

    class Meta:
        db_table = 'DevstarScore'

    def __unicode__(self):
        return ('{}:{} DevStaR score'
                .format(str(self.experiment), self.well))
