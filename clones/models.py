from django.db import models


class Clone(models.Model):
    """An RNAi clone used in the screen."""
    id = models.CharField(max_length=30, primary_key=True)

    class Meta:
        db_table = 'RNAiClone'
        ordering = ['id']

    def __unicode__(self):
        return self.id

    def is_control(self):
        return self.id == 'L4440'
