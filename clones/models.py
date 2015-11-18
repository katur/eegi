from django.core.urlresolvers import reverse
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

    def get_absolute_url(self):
        return reverse('clones.views.clone', args=[self.id])

    def is_control(self):
        return self.id == 'L4440'

    def get_targets(self):
        return self.clonetarget_set.all()


class Gene(models.Model):
    """A gene, potentially targeted by an RNAi clone used in the screen."""
    id = models.CharField(max_length=30, primary_key=True)
    cosmid_id = models.CharField(max_length=30)
    locus = models.CharField(max_length=30, blank=True)
    gene_type = models.CharField(max_length=30, blank=True)
    gene_class_description = models.TextField(blank=True)
    functional_description = models.TextField(blank=True)

    class Meta:
        db_table = 'Gene'

    def __unicode__(self):
        return self.id

    def get_display_string(self):
        if self.locus:
            return self.locus
        elif self.cosmid_id:
            return self.cosmid_id
        else:
            return id

    def get_url(self):
        return self.get_wormbase_url()

    def get_wormbase_url(self):
        return 'http://www.wormbase.org/species/c_elegans/gene/' + self.id


class CloneTarget(models.Model):
    """Class defining a clone-to-gene-target relationship.

    If there is a CloneTarget in the database, it means that the
    given clone targets the given gene.

    """
    clone = models.ForeignKey(Clone)
    gene = models.ForeignKey(Gene)
    transcript_isoform = models.CharField(max_length=30, blank=True)
    clone_amplicon_id = models.IntegerField()
    amplicon_evidence = models.CharField(max_length=4)
    amplicon_is_designed = models.BooleanField()
    amplicon_is_unique = models.BooleanField()
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

    def __unicode__(self):
        return unicode(self.clone) + ' targets ' + unicode(self.gene)
