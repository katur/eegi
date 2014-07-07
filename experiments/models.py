from django.db import models
from wormstrains.models import WormStrain
from clones.models import ClonePlate


class Experiment(models.Model):
    """
    A plate-level experiment (i.e., a flat-bottom plate in which
    worms and RNAi clones were put at a specific temperature).

    This table is essentially 'RawData' in the GenomeWideGI database.
    """
    id = models.PositiveIntegerField(primary_key=True)
    worm_strain = models.ForeignKey(WormStrain)
    clone_plate = models.ForeignKey(ClonePlate)
    temperature = models.DecimalField(max_digits=3, decimal_places=1)
    date = models.DateField()
    is_junk = models.BooleanField(default=False)
    comment = models.TextField(blank=True)

    class Meta:
        db_table = 'experiment'
        ordering = ['id']

    def __str__(self):
        return str(self.id)

    def __repr__(self):
        return self.__str__()
