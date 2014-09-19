from django.db import models


class Clone(models.Model):
    """
    An RNAi clone.
    """
    # The name of this strain on Wormbase.org
    id = models.CharField(max_length=30, primary_key=True)

    class Meta:
        db_table = 'RNAiClone'
        ordering = ['id']

    def __unicode__(self):
        return self.id
