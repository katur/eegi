from django.db import models

from clones.models import Clone


class LibraryPlate(models.Model):
    """
    A library plate of RNAi feeding clones. This plate is meant to represent
    the theoretical plate, not an individual frozen stock of the plate.
    """
    id = models.CharField(max_length=20, primary_key=True)
    screen_stage = models.PositiveSmallIntegerField(null=True, blank=True)
    number_of_wells = models.PositiveSmallIntegerField()

    class Meta:
        db_table = 'LibraryPlate'
        ordering = ['id']

    def __unicode__(self):
        return self.id

    def __hash__(self):
        return 31 * hash(self.id)

    def __cmp__(self, other):
        # First order by screen stage
        if self.screen_stage != other.screen_stage:
            return cmp(self.screen_stage, other.screen_stage)

        # Then by id
        else:
            self_parts = self.id.split('-')
            other_parts = other.id.split('-')

            # 1st token numeric comparison
            if self_parts[0].isdigit() and other_parts[0].isdigit():
                return cmp(int(self_parts[0]), int(other_parts[0]))

            # 2nd token numeric comparison (if 1st token match)
            elif (self_parts[0] == other_parts[0]
                  and len(self_parts) > 1 and len(other_parts) > 1
                  and self_parts[1].isdigit() and other_parts[1].isdigit()):
                return cmp(int(self_parts[1]), int(other_parts[1]))

            # All other situations, simply order alphabetically
            else:
                return cmp(self.id, other.id)


class LibraryWell(models.Model):
    """
    A well in a library plate, including the intended clone.
    """
    id = models.CharField(max_length=24, primary_key=True)
    plate = models.ForeignKey(LibraryPlate)
    well = models.CharField(max_length=3)
    intended_clone = models.ForeignKey(Clone, null=True, blank=True)
    parent_library_well = models.ForeignKey('self', null=True, blank=True)

    class Meta:
        db_table = 'LibraryWell'
        ordering = ['id']

    def __unicode__(self):
        return '{} (intended clone: {})'.format(self.id,
                                                str(self.intended_clone))


class LibrarySequencing(models.Model):
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
                .format(self.source_library_well, self.seq_plate_name,
                        self.seq_tube_number))
