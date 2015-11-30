from worms.tests.base import WormTestCase
from utils.http import http_response_ok


class WormModelsTestCase(WormTestCase):
    def test_str_and_unicode(self):
        n2, dnc1, glp1, emb8 = self.get_worms()
        self.assertEquals(unicode(n2), 'N2')
        self.assertEquals(unicode(dnc1), 'EU1006')
        self.assertEquals(unicode(glp1), 'EU552')
        self.assertEquals(unicode(emb8), 'MJ69')
        self.assertEquals(str(n2), 'N2')
        self.assertEquals(str(dnc1), 'EU1006')
        self.assertEquals(str(glp1), 'EU552')
        self.assertEquals(str(emb8), 'MJ69')

    def test_get_short_genotype(self):
        n2, dnc1, glp1, emb8 = self.get_worms()
        self.assertEquals(dnc1.get_short_genotype(), 'dnc-1(or404)')
        self.assertEquals(glp1.get_short_genotype(), 'glp-1(or178)')
        self.assertEquals(emb8.get_short_genotype(), 'emb-8(hc69)')

    def test_get_display_string(self):
        n2, dnc1, glp1, emb8 = self.get_worms()
        self.assertEquals(n2.get_display_string(), 'N2')
        self.assertEquals(dnc1.get_display_string(), 'EU1006: dnc-1(or404)')
        self.assertEquals(glp1.get_display_string(), 'EU552: glp-1(or178)')
        self.assertEquals(emb8.get_display_string(), 'MJ69: emb-8(hc69)')

    def test_get_wormbase_url(self):
        worms = self.get_worms()
        for worm in worms:
            self.assertTrue(http_response_ok(worm.get_wormbase_url()))

    def test_is_control(self):
        worms = self.get_worms()
        n2 = worms[0]
        mutants = worms[1:]

        self.assertTrue(n2.is_control())
        for mutant in mutants:
            self.assertFalse(mutant.is_control())

    def test_is_permissive_temperature(self):
        n2, dnc1, glp1, emb8 = self.get_worms()
        self.assertFalse(n2.is_permissive_temperature(22.5))

        self.assertFalse(glp1.is_permissive_temperature(22.5))

        self.assertTrue(dnc1.is_permissive_temperature(22.5))
        self.assertFalse(dnc1.is_permissive_temperature(20))

        self.assertTrue(emb8.is_permissive_temperature(17.5))
        self.assertFalse(emb8.is_permissive_temperature(22.5))

    def test_is_restrictive_temperature(self):
        n2, dnc1, glp1, emb8 = self.get_worms()
        self.assertFalse(n2.is_restrictive_temperature(22.5))

        self.assertFalse(dnc1.is_restrictive_temperature(22.5))

        self.assertTrue(glp1.is_restrictive_temperature(22.5))
        self.assertFalse(glp1.is_restrictive_temperature(25))

        self.assertTrue(emb8.is_restrictive_temperature(25))
        self.assertFalse(emb8.is_restrictive_temperature(15))

    def test_get_screen_type(self):
        n2, dnc1, glp1, emb8 = self.get_worms()

        self.assertIsNone(n2.get_screen_type(15))

        self.assertEquals(dnc1.get_screen_type(22.5), 'ENH')
        self.assertIsNone(dnc1.get_screen_type(25))

        self.assertEquals(glp1.get_screen_type(22.5), 'SUP')
        self.assertIsNone(glp1.get_screen_type(15))

        self.assertEquals(emb8.get_screen_type(17.5), 'ENH')
        self.assertEquals(emb8.get_screen_type(25), 'SUP')
        self.assertIsNone(emb8.get_screen_type(15))
        self.assertIsNone(emb8.get_screen_type(26))
