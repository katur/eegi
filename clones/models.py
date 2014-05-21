from django.db import models


class ClonePlate(models.Model):
    """
    A plate of RNAi feeding clones.

    This table is not in the GenomeWideGI database.
    Rows for 384-well plates were added manually.
    Rows for 96-well plates from the primary screen were added by querying
    GenomeWideGI's RNAiPlate table for distinct RNAiPlateID values.
    Rows for 96-well plates from the secondary screen were added by querying
    GenomeWideGI's CherryPickRNAiPlate table for distinct RNAiPlateID values.
    """
    name = models.CharField(max_length=20, primary_key=True)
    screen_stage = models.PositiveSmallIntegerField(null=True, blank=True)
    number_of_wells = models.PositiveSmallIntegerField()
