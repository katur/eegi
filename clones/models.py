from django.db import models


class Clone(models.Model):
    """An RNAi clone used in the screen."""
    id = models.CharField(max_length=30, primary_key=True)
    mapping_db_pk = models.IntegerField(blank=True, null=True)
    library = models.CharField(max_length=30, blank=True)
    clone_type = models.CharField(max_length=30, blank=True)
    forward_primer = models.CharField(max_length=100, blank=True)
    reverse_primer = models.CharField(max_length=100, blank=True)

    class Meta:
        db_table = 'Clone'
        ordering = ['id']

    def __unicode__(self):
        return self.id

    def is_control(self):
        return self.id == 'L4440'


class Gene(models.Model):
    id = models.CharField(max_length=30, primary_key=True)
    cosmid_id = models.CharField(max_length=30)
    locus = models.CharField(max_length=30, blank=True)
    gene_type = models.CharField(max_length=30, blank=True)
    functional_description = models.TextField(blank=True)

    class Meta:
        db_table = 'Gene'


class CloneTarget(models.Model):
    clone = models.ForeignKey(Clone)
    clone_amplicon_id = models.IntegerField()
    amplicon_evidence = models.CharField(max_length=4)
    amplicon_is_designed = models.BooleanField()
    amplicon_is_unique = models.BooleanField()
    gene = models.ForeignKey(Gene)
    transcript_isoform = models.CharField(max_length=30, blank=True)
    length_span = models.IntegerField()
    raw_score = models.IntegerField()
    unique_raw_score = models.IntegerField()
    relative_score = models.FloatField()
    specificity_index = models.FloatField()
    unique_chunk_index = models.FloatField()
    is_on_target = models.BooleanField()
    is_primary_target = models.BooleanField()

    class Meta:
        db_table = 'CloneTarget'
