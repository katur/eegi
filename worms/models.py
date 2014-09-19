from django.db import models


class WormStrain(models.Model):
    """
    A worm strain used in this experiment. Can be either a
    temperature-sensitive mutant, or a control strain.
    """
    # The name of this strain on Wormbase.org
    id = models.CharField(max_length=10, primary_key=True)

    # Gene and allele causing temperature-sensitivity in this strain
    gene = models.CharField(max_length=10, blank=True)
    allele = models.CharField(max_length=10, blank=True)
    genotype = models.CharField(max_length=20, blank=True)

    # Temperatures in Celsius used for screening
    permissive_temperature = models.DecimalField(
        max_digits=3, decimal_places=1, null=True, blank=True)
    restrictive_temperature = models.DecimalField(
        max_digits=3, decimal_places=1, null=True, blank=True)

    # Whether the strain is on Wormbase.org
    on_wormbase = models.BooleanField(default=False)

    class Meta:
        db_table = 'WormStrain'
        ordering = ['genotype']

    def get_wormbase_url(self):
        return 'http://www.wormbase.org/species/c_elegans/strain/' + self.id

    def get_lab_website_url(self):
        return 'http://gunsiano.webfactional.com/strain/' + self.id

    def __unicode__(self):
        return self.id

    def __cmp__(self, other):
        if self.genotype < other.genotype:
            return -1
        elif self.genotype > other.genotype:
            return 1
        else:
            return 0
