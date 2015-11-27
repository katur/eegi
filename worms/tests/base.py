from django.test import TestCase

from worms.models import WormStrain


class WormTestCase(TestCase):
    def setUp(self):
        # Control worm strain
        WormStrain.objects.create(id='N2')

        # Mutant strain with only permissive temp
        WormStrain.objects.create(
            id='EU1006', gene='dnc-1', allele='or404',
            genotype='dnc-1(or404) IV',
            permissive_temperature=22.5)

        # Mutant strain with only restrictive temp
        WormStrain.objects.create(
            id='EU552', gene='glp-1', allele='or178',
            genotype='glp-1(or178) III',
            restrictive_temperature=22.5)

        # Mutant strain with both permissive and restrictive temps
        WormStrain.objects.create(
            id='MJ69', gene='emb-8', allele='hc69',
            genotype='emb-8(hc69) III',
            permissive_temperature=17.5,
            restrictive_temperature=25.0)

    def get_worms(self):
        n2 = WormStrain.objects.get(id='N2')
        dnc1 = WormStrain.objects.get(id='EU1006')
        glp1 = WormStrain.objects.get(id='EU552')
        emb8 = WormStrain.objects.get(id='MJ69')
        return (n2, dnc1, glp1, emb8)
