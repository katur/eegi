from django.test import TestCase

from utils.well_tile_conversion import well_to_tile, tile_to_well


class WellTileConversionTestCase(TestCase):
    def setUp(self):
        self.well_tile_tuples = (
            ('A01', 'Tile000001'),
            ('A12', 'Tile000012'),
            ('B12', 'Tile000013'),
            ('B01', 'Tile000024'),
            ('C02', 'Tile000026'),
            ('H12', 'Tile000085'),
            ('H01', 'Tile000096'),
        )

    def test_well_to_tile(self):
        for well, tile in self.well_tile_tuples:
            self.assertEqual(well_to_tile(well), tile)

    def test_tile_to_well(self):
        for well, tile in self.well_tile_tuples:
            self.assertEqual(tile_to_well(tile), well)

    def test_improper_well_format(self):
        self.assertRaises(ValueError, well_to_tile, '06')
        self.assertRaises(ValueError, well_to_tile, 'a01')
        self.assertRaises(ValueError, well_to_tile, 'ab')

    def test_improper_tile_format(self):
        self.assertRaises(ValueError, tile_to_well, 'tile000076')
        self.assertRaises(ValueError, tile_to_well, 'Tile00076')
        self.assertRaises(ValueError, tile_to_well, 'TILE000076')

    def test_well_out_of_range(self):
        self.assertRaises(ValueError, well_to_tile, 'B13')
        self.assertRaises(ValueError, well_to_tile, 'C00')
        self.assertRaises(ValueError, well_to_tile, 'I01')

    def test_tile_out_of_range(self):
        self.assertRaises(ValueError, tile_to_well, 'Tile000000')
        self.assertRaises(ValueError, tile_to_well, 'Tile000097')
