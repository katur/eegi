from django.db import models


class WormStrain(models.Model):
    name = models.CharField(max_length=10, primary_key=True)
    gene = models.CharField(max_length=10, blank=True)
    allele = models.CharField(max_length=10, blank=True, unique=True)
    genotype = models.CharField(max_length=20, blank=True, unique=True)
    permissive_temperature = models.DecimalField(
        max_digits=3, decimal_places=1, null=True, blank=True)
    restrictive_temperature = models.DecimalField(
        max_digits=3, decimal_places=1, null=True, blank=True)
    on_wormbase = models.BooleanField(default=False)

    class Meta:
        ordering = ['genotype']

    def get_wormbase_url(self):
        return 'http://www.wormbase.org/species/c_elegans/strain/' + self.name

    def get_restrictive_string(self):
        return temperature_to_string(self.restrictive_temperature)

    def get_permissive_string(self):
        return temperature_to_string(self.permissive_temperature)

    def __hash__(self):
        return 31 * hash(self.gene) * hash(self.allele)

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.__str__()


def temperature_to_string(temperature):
    if temperature:
        return str(temperature) + 'C'
    else:
        return None
