import re

from django.core.urlresolvers import reverse
from django.db import models

from clones.models import Clone
from utils.well_tile_conversion import well_to_tile


class LibraryPlate(models.Model):
    """
    A plate of RNAi feeding clones.

    Note that while we may have multiple frozen replicates of the same library
    plate, we only represent one copy in the database. This is because,
    historically, we did not keep track of which copy was used in which
    experiment.
    """

    id = models.CharField(max_length=20, primary_key=True)
    number_of_wells = models.PositiveSmallIntegerField()

    # screen_stage:
    #   1 means Primary screen only
    #   2 means Secondary screen only
    #   None means no limitations (e.g. L4440 plate which is used in both
    #       Primary and Secondary screens)
    #   0 means not used in screen stages (e.g. Ahringer 384 plates)
    screen_stage = models.PositiveSmallIntegerField(null=True, blank=True,
                                                    db_index=True)

    class Meta:
        db_table = 'LibraryPlate'
        ordering = ['screen_stage', 'id']

    def __hash__(self):
        return 31 * hash(self.id)

    def __unicode__(self):
        return self.id

    def get_absolute_url(self):
        return reverse('library_plate_url', args=[self.id])

    def get_stocks(self):
        return (self.librarystock_set.all()
                .select_related('intended_clone')
                .order_by('well'))

    def get_stocks_as_dictionary(self):
        stocks = self.librarystock_set.all()
        s = {}
        for stock in stocks:
            s[stock.well] = stock
        return s

    def get_l4440_stocks(self):
        return self.librarystock_set.filter(intended_clone='L4440')

    def is_ahringer_96_plate(self):
        """Determine if this plate is an Ahringer 96-format plate."""
        return re.match('(I|II|III|IV|V|X)-[1-9][0-3]?-[AB][12]',
                        self.id)


class LibraryStock(models.Model):
    """
    A stock of an RNAi clone.

    May or may not be in a LibraryPlate.

    Includes the clone intended on being in this position (according to
    whoever designed the library), separate from a sequence-verified clone.
    """

    id = models.CharField(max_length=24, primary_key=True)
    plate = models.ForeignKey(LibraryPlate)
    well = models.CharField(max_length=3)
    parent_stock = models.ForeignKey('self', null=True, blank=True)
    intended_clone = models.ForeignKey(Clone, null=True, blank=True)
    sequence_verified_clone = models.ForeignKey(Clone, default=None,
                                                null=True, blank=True,
                                                related_name='seq_clone')

    class Meta:
        db_table = 'LibraryStock'
        ordering = ['id']
        unique_together = ('plate', 'well')

    def __unicode__(self):
        return '{}'.format(self.id)

    def get_display_string(self):
        return '{} (intended clone: {})'.format(self.id,
                                                self.intended_clone)

    def is_control(self):
        return self.intended_clone.is_control()

    def get_row(self):
        return self.well[0]

    def get_column(self):
        return int(self.well[1:])

    def get_tile(self):
        return well_to_tile(self.well)


class LibrarySequencing(models.Model):
    """Genewiz sequencing result from a particular LibraryStock."""

    source_stock = models.ForeignKey(LibraryStock, null=True, blank=True)
    sample_plate_name = models.CharField(max_length=10, blank=True)
    sample_tube_number = models.IntegerField(null=True, blank=True)

    genewiz_tracking_number = models.CharField(max_length=20, null=True,
                                               blank=True)
    genewiz_tube_label = models.CharField(max_length=20, null=True, blank=True)

    sequence = models.TextField(blank=True)
    ab1_filename = models.CharField(max_length=20, null=True, blank=True)

    quality_score = models.IntegerField(null=True, blank=True)
    crl = models.IntegerField(null=True, blank=True)
    qv20plus = models.IntegerField(null=True, blank=True)
    si_a = models.IntegerField(null=True, blank=True)
    si_t = models.IntegerField(null=True, blank=True)
    si_c = models.IntegerField(null=True, blank=True)
    si_g = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'LibrarySequencing'
        ordering = ['sample_plate_name', 'sample_tube_number']
        unique_together = ('genewiz_tracking_number', 'genewiz_tube_label')

    def __unicode__(self):
        return ('Sequence of {}, seq plate {}, seq tube {}'
                .format(self.source_stock, self.sample_plate_name,
                        self.sample_tube_number))

    def is_decent_quality(self):
        return self.crl >= 400 and self.quality_score >= 30


class LibrarySequencingBlatResult(models.Model):
    """BLAT result from a particular LibrarySequencing result."""

    sequencing = models.ForeignKey(LibrarySequencing)
    clone_hit = models.ForeignKey(Clone)
    e_value = models.FloatField()
    bit_score = models.IntegerField()
    hit_rank = models.PositiveSmallIntegerField()

    class Meta:
        db_table = 'LibrarySequencingBlatResult'
        ordering = ['sequencing', 'hit_rank']

    def __unicode__(self):
        return ('BLAT result for sequencing result <{}>, hitting clone <{}>'
                .format(self.sequencing, self.clone_hit))
