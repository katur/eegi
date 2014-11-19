from django.db import models


class WormStrain(models.Model):
    """
    A worm strain used in this experiment. Can be either a
    temperature-sensitive mutant, or a control strain.
    """
    # The name of this strain (e.g. KK300)
    id = models.CharField(max_length=10, primary_key=True)

    # Gene and allele causing temperature-sensitivity in this strain
    gene = models.CharField(max_length=10, blank=True)
    allele = models.CharField(max_length=10, blank=True)
    genotype = models.CharField(max_length=20, blank=True)

    # Temperatures, in Celsius, used for screening
    permissive_temperature = models.DecimalField(
        max_digits=3, decimal_places=1, null=True, blank=True)
    restrictive_temperature = models.DecimalField(
        max_digits=3, decimal_places=1, null=True, blank=True)

    class Meta:
        db_table = 'WormStrain'
        ordering = ['genotype']

    def __cmp__(self, other):
        return cmp(self.genotype, other.genotype)

    def __unicode__(self):
        return self.id

    def get_lab_website_url(self):
        return 'http://gunsiano.webfactional.com/strain/' + self.id

    def get_wormbase_url(self):
        return 'http://www.wormbase.org/species/c_elegans/strain/' + self.id

    def get_url(self, request):
        if request.user.is_authenticated():
            return self.get_lab_website_url()
        else:
            return self.get_wormbase_url()

    def is_control(self):
        if not self.allele:
            return True
        else:
            return False
