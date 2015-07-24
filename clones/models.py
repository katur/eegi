from django.db import models


class Clone(models.Model):
    """An RNAi clone used in the screen."""
    id = models.CharField(max_length=30, primary_key=True)
    """
    antiquated_pk = models.CharField(max_length=30, blank=True)
    library = models.CharField(max_length=30, blank=True)
    clone_type = models.CharField(max_length=30, blank=True)
    forward_primer = models.CharField(max_length=100, blank=True)
    reverse_primer = models.CharField(max_length=100, blank=True)
    """

    class Meta:
        db_table = 'RNAiClone'
        ordering = ['id']

    def __unicode__(self):
        return self.id

    def is_control(self):
        return self.id == 'L4440'


'''
class Gene(models.Model):
    id = models.CharField(max_length=30, primary_key=True)
    cosmid_id = models.CharField(max_length=30)


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
'''
