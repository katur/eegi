from decimal import Decimal

from django.db import models


class WormStrain(models.Model):
    """A worm strain used in this experiment.

    Can be either a temperature-sensitive mutant strain, or a control
    strain. Control strains are signified by allele=None.

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
        ordering = ['id']

    def __cmp__(self, other):
        if hasattr(other, 'genotype'):
            return cmp(self.genotype, other.genotype)
        else:
            return cmp(self.genotype, str(other))

    def __unicode__(self):
        return self.id

    def is_control(self):
        if not self.allele:
            return True
        else:
            return False

    def get_lab_website_url(self):
        return 'http://gunsiano.webfactional.com/strain/' + self.id

    def get_wormbase_url(self):
        return 'http://www.wormbase.org/species/c_elegans/strain/' + self.id

    def get_url(self, request):
        if request.user.is_authenticated():
            return self.get_lab_website_url()
        else:
            return self.get_wormbase_url()

    def get_short_genotype(self):
        return self.genotype.split()[0]

    def get_screen_category(self, temperature):
        """Determine if temperature is a screen temperature for this strain.

        Returns 'ENH' if temperature is this strain's permissive
        screening temperature.

        Returns 'SUP' if temperature is this strain's restrictive
        screening temperature.

        Returns None if temperature is not an official screening
        temperature for this strain.

        """
        temperature = Decimal(temperature)
        if self.permissive_temperature == temperature:
            return 'ENH'
        elif self.restrictive_temperature == temperature:
            return 'SUP'
        else:
            return None
