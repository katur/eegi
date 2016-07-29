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
    #   0 means used prior to screen stages (e.g. Ahringer 384 plates)
    #   1 means Primary screen only
    #   2 means Secondary screen only
    #   None means no limitations (e.g. L4440 plate which is used in both
    #       Primary and Secondary screens)
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
        return self.librarystock_set.filter(intended_clone=Clone.get_l4440())

    def is_ahringer_96_plate(self):
        """Determine if this plate is an Ahringer 96-format plate."""
        return re.match('(I|II|III|IV|V|X)-[1-9][0-3]?-[AB][12]',
                        self.id)

    @classmethod
    def get_screening_plates(cls, screen_stage=None):
        """
        Get library plates intended for screening.

        This excludes the plates with screen_stage=0 (which means not
        used for screening). This includes our Ahringer 384-format plates,
        and the Vidal plates from which our rearrays were derived.

        Optionally supply an integer screen_stage. What is returned in
        this case is both the plates specifically for that screen_stage,
        and also the plates with screen_stage=None (which is meant to
        signify that the plate is meant for use across screen stages).
        """
        if screen_stage:
            return cls.objects.filter(models.Q(screen_stage=screen_stage) |
                                      models.Q(screen_stage=None))
        else:
            return cls.objects.exclude(screen_stage=0)


class LibraryStock(models.Model):
    """
    A stock of an RNAi clone.

    May or may not be in a LibraryPlate.

    TODO: Make sure code doesn't assume stocks are in plates; once confirmed,
    add null=True, blank=True, and models.SET_NULL.

    Includes the clone intended on being in this position (according to
    whoever designed the library), separate from a sequence-verified clone.
    """

    id = models.CharField(max_length=24, primary_key=True)
    plate = models.ForeignKey(LibraryPlate, models.CASCADE)
    well = models.CharField(max_length=3)
    parent_stock = models.ForeignKey('self', models.SET_NULL,
                                     null=True, blank=True)
    intended_clone = models.ForeignKey(Clone, models.SET_NULL,
                                       null=True, blank=True)
    sequence_verified_clone = models.ForeignKey(Clone, models.SET_NULL,
                                                default=None,
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

    def get_sequencing_results(self):
        return (self.librarysequencing_set.all()
                .prefetch_related('librarysequencingblatresult_set'))

    def get_sequencing_hits(self, top_hit_only=False):
        hits = []
        for s in self.get_sequencing_results():
            blats = s.get_blat_results(top_hit_only=top_hit_only)
            hits.extend([blat.clone_hit for blat in blats])

        return hits

    def has_sequencing_match(self, top_hit_only=False):
        hits = self.get_sequencing_hits(top_hit_only=top_hit_only)
        return self.intended_clone in hits


class LibrarySequencing(models.Model):
    """
    Genewiz sequencing result from a particular LibraryStock.

    The fields sample_plate and sample_well are useful because they
    are how we label our physical samples, and how we record which
    library stocks were put into which sequencing plates.
    sample_tube_number is a simple numeric translation of sample_well,
    used in some of the Genewiz output, so convenient to have in the
    database too.

    The primary key -- id -- is in format x_y, where (x, y) are
    (genewiz_tracking_number, genewiz_tube_label). Note that
    (sample_plate, sample_well) does not work because sometimes
    Genewiz re-sequencing the same sample.

    Also note that genewiz_tube_label and sample_tube_number differ in
    two cases:

        1) Re-sequencing the same sample. In this case,
           sample_tube_number is the same for both sequences, but
           Genewiz assigns a different genewiz_tube_label for each.

        2) There are some sample plates for which wells 1-94 were
           processed as a separate tracking number than wells 95-96.
           This has something to do with Genewiz running a couple
           controls, and with our using a different Genewiz form for
           submitting the order.

    TODO: This ForeignKeys should SET NULL on delete.

    Overall, genewiz_tracking_number and genewiz_tube_label provide
    the only and best primary key for a sequencing result.
    """

    id = models.CharField(primary_key=True, max_length=40)
    source_stock = models.ForeignKey(LibraryStock, models.SET_NULL,
                                     null=True, blank=True)
    sample_plate = models.CharField(max_length=10, blank=True)
    sample_well = models.CharField(max_length=3, blank=True)
    sample_tube_number = models.IntegerField(null=True, blank=True)

    genewiz_order_date = models.DateField(null=True, blank=True)
    genewiz_tracking_number = models.CharField(max_length=20, blank=True)
    genewiz_tube_label = models.CharField(max_length=20, blank=True)

    sequence = models.TextField(blank=True)
    ab1_filename = models.CharField(max_length=20, blank=True)

    quality_score = models.IntegerField(null=True, blank=True)
    crl = models.IntegerField(null=True, blank=True)
    qv20plus = models.IntegerField(null=True, blank=True)
    si_a = models.IntegerField(null=True, blank=True)
    si_t = models.IntegerField(null=True, blank=True)
    si_c = models.IntegerField(null=True, blank=True)
    si_g = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'LibrarySequencing'
        ordering = ['sample_plate', 'sample_well']
        unique_together = ('genewiz_tracking_number', 'genewiz_tube_label')

    def __unicode__(self):
        return ('Sequence of {}, seq plate {}, seq tube {}'
                .format(self.source_stock, self.sample_plate_name,
                        self.sample_tube_number))

    def is_decent_quality(self):
        return self.crl >= 400 and self.quality_score >= 30

    def get_blat_results(self, top_hit_only=False):
        if top_hit_only:
            return self.librarysequencingblatresult_set.filter(hit_rank=1)
        else:
            return self.librarysequencingblatresult_set.all()


class LibrarySequencingBlatResult(models.Model):
    """BLAT result from a particular LibrarySequencing result."""

    sequencing = models.ForeignKey(LibrarySequencing, models.CASCADE)
    clone_hit = models.ForeignKey(Clone, models.CASCADE)
    e_value = models.FloatField()
    bit_score = models.IntegerField()
    hit_rank = models.PositiveSmallIntegerField()

    class Meta:
        db_table = 'LibrarySequencingBlatResult'
        ordering = ['sequencing', 'hit_rank']

    def __unicode__(self):
        return ('BLAT result for sequencing result <{}>, hitting clone <{}>'
                .format(self.sequencing, self.clone_hit))
