from worms.helpers.queries import (
    get_n2, get_worms_for_screen_type,
    get_worm_and_temperature_from_search_term)
from worms.tests.base import WormTestCase


class WormHelpersTestCase(WormTestCase):
    def test_get_n2(self):
        n2 = get_n2()
        self.assertEquals(n2.id, 'N2')
        self.assertIsNone(n2.permissive_temperature)
        self.assertIsNone(n2.restrictive_temperature)

    def test_get_worm_and_temperature_from_search_term(self):
        n2, dnc1, glp1, emb8 = self.get_worms()

        # Shorten function name for convenience
        query = get_worm_and_temperature_from_search_term

        self.assertEquals(query('MJ69', 'ENH'), (emb8, 17.5))
        self.assertEquals(query('glp-1', 'SUP'), (glp1, 22.5))
        self.assertEquals(query('or404', 'ENH'), (dnc1, 22.5))

        self.assertIsNone(query('N2', 'ENH'))
        self.assertIsNone(query('N2', 'SUP'))
        self.assertIsNone(query('dnc1', 'SUP'))
        self.assertIsNone(query('EU552', 'ENH'))
        self.assertIsNone(query('nonsense', 'ENH'))


    def test_get_worms_for_screen_type(self):
        n2, dnc1, glp1, emb8 = self.get_worms()

        enhs = get_worms_for_screen_type('ENH')
        sups = get_worms_for_screen_type('SUP')

        for worms in (enhs, sups):
            self.assertNotIn(n2, worms)
            self.assertIn(emb8, worms)

        self.assertIn(dnc1, enhs)
        self.assertNotIn(dnc1, sups)

        self.assertNotIn(glp1, enhs)
        self.assertIn(glp1, sups)
