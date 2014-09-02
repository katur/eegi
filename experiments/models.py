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

    def __str__(self):
        return str(self.id)

    def __repr__(self):
        return self.__str__()


class ManualScoreCode(models.Model):
    id = models.IntegerField(primary_key=True)
    description = models.CharField(max_length=100, blank=True)
    short_description = models.CharField(max_length=50, blank=True)
    legacy_description = models.CharField(max_length=100, blank=True)

    class Meta:
        db_table = 'ManualScoreCode'
        ordering = ['id']


class ManualScore(models.Model):
    experiment = models.ForeignKey(Experiment)
    well = models.CharField(max_length=3)
    score_code = models.ForeignKey(ManualScoreCode)
    scorer = models.ForeignKey(User, null=True, blank=True)
    timestamp = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'ManualScore'
