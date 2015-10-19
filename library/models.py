import re

from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Q

from clones.models import Clone
from utils.well_tile_conversion import well_to_tile


class LibraryPlate(models.Model):
    """A plate of RNAi feeding clones.

    Note that while we may have multiple frozen replicates of the same library
    plate, we only represent one copy in the database. This is because,
    historically, we did not keep track of which copy was used in which
    experiment.

    """
    id = models.CharField(max_length=20, primary_key=True)
    screen_stage = models.PositiveSmallIntegerField(null=True, blank=True,
                                                    db_index=True)
    number_of_wells = models.PositiveSmallIntegerField()

    class Meta:
        db_table = 'LibraryPlate'
        ordering = ['id']

    def __cmp__(self, other):
        # First order by screen stage
        if self.screen_stage != other.screen_stage:
            return cmp(self.screen_stage, other.screen_stage)

        # Then by id
        if self.id.isdecimal() and other.id.isdecimal():
            return cmp(int(self.id), int(other.id))

        elif self.is_ahringer_96_plate() and other.is_ahringer_96_plate():
            self_parts = self.id.split('-')
            other_parts = other.id.split('-')

            if (self_parts[0] != other_parts[0]):
                return cmp(self_parts[0], other_parts[0])
            elif (self_parts[1] != other_parts[1]):
                return cmp(int(self_parts[1]), int(other_parts[1]))
            else:  # chromosome and number match
                return cmp(self_parts[2], other_parts[2])

        # All other situations, simply order alphabetically
        else:
            return cmp(self.id, other.id)

    def __hash__(self):
        return 31 * hash(self.id)

    def __unicode__(self):
        return self.id

    def get_absolute_url(self):
        return reverse('library.views.library_plate', args=[self.id])

    def get_all_wells(self):
        return LibraryWell.objects.filter(plate=self)

    def get_l4440_wells(self):
        return LibraryWell.objects.filter(Q(plate=self),
                                          Q(intended_clone='L4440'))

    def is_ahringer_96_plate(self):
        """Determine if a plate name is in the correct format for an
        Ahringer 96-format plate.

        """
        return re.match('(I|II|III|IV|V|X)-[1-9][0-3]?-[AB][12]',
                        self.id)


class LibraryWell(models.Model):
    """A well in a LibraryPlate.

    Includes the clone intended on being in this position (according to
    whoever designed the library), separate from a sequence-verified clone.

    """
    id = models.CharField(max_length=24, primary_key=True)
    plate = models.ForeignKey(LibraryPlate, related_name='wells')
    well = models.CharField(max_length=3, db_index=True)
    intended_clone = models.ForeignKey(Clone, null=True, blank=True)
    sequence_verified_clone = models.ForeignKey(Clone, default=None,
                                                null=True, blank=True,
                                                related_name='seq_clone')
    parent_library_well = models.ForeignKey('self', null=True, blank=True)

    class Meta:
        db_table = 'LibraryWell'
        ordering = ['id']

    def __cmp__(self, other):
        if self.plate == other.plate:
            return cmp(self.well, other.well)
        else:
            return cmp(self.plate, other.plate)

    def __unicode__(self):
        return '{} (intended clone: {})'.format(self.id,
                                                self.intended_clone)

    def get_row(self):
        return self.well[0]

    def get_column(self):
        return int(self.well[1:])

    def get_tile(self):
        return well_to_tile(self.well)

    def is_control(self):
        return self.intended_clone.is_control()


class LibrarySequencing(models.Model):
    """A Genewiz sequencing result from a particular LibraryWell."""
    source_library_well = models.ForeignKey(LibraryWell, null=True, blank=True)
    library_plate_copy_number = models.PositiveSmallIntegerField(null=True,
                                                                 blank=True)
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
                .format(self.source_library_well, self.sample_plate_name,
                        self.sample_tube_number))

    def is_decent_quality(self):
        return self.crl >= 400 and self.quality_score >= 30


class LibrarySequencingBlatResult(models.Model):
    """A BLAT result from a particular LibrarySequencing result."""
    library_sequencing = models.ForeignKey(LibrarySequencing)
    clone_hit = models.ForeignKey(Clone)
    e_value = models.FloatField()
    bit_score = models.IntegerField()
    hit_rank = models.PositiveSmallIntegerField()

    class Meta:
        db_table = 'LibrarySequencingBlatResult'
        ordering = ['library_sequencing', 'hit_rank']

    def __unicode__(self):
        return ('BLAT result for sequencing result <{}>, hitting clone <{}>'
                .format(self.library_sequencing, self.clone_hit))
