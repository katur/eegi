from django.test import TestCase

from utils.plates import (
    get_well_list, get_well_set, get_well_grid, get_symmetric_well,
    get_384_parent_well)


class GetWellListTestCase(TestCase):
    def setUp(self):
        self.horizontal_96 = get_well_list(is_384=False, vertical=False)
        self.vertical_96 = get_well_list(is_384=False, vertical=True)
        self.horizontal_384 = get_well_list(is_384=True, vertical=False)
        self.vertical_384 = get_well_list(is_384=True, vertical=True)

    def test_length(self):
        self.assertEqual(len(self.horizontal_96), 96)
        self.assertEqual(len(self.vertical_96), 96)
        self.assertEqual(len(self.horizontal_384), 384)
        self.assertEqual(len(self.vertical_384), 384)

    def test_first_wells_horizontal(self):
        horizontal_firsts = ['A01', 'A02', 'A03']
        self.assertEqual(self.horizontal_96[0:3], horizontal_firsts)
        self.assertEqual(self.horizontal_384[0:3], horizontal_firsts)

    def test_first_wells_vertical(self):
        vertical_firsts = ['A01', 'B01', 'C01']
        self.assertEqual(self.vertical_96[0:3], vertical_firsts)
        self.assertEqual(self.vertical_384[0:3], vertical_firsts)

    def test_last_wells_horizontal_96(self):
        self.assertEqual(self.horizontal_96[-3:], ['H10', 'H11', 'H12'])

    def test_last_wells_vertical_96(self):
        self.assertEqual(self.vertical_96[-3:], ['F12', 'G12', 'H12'])

    def test_last_wells_horizontal_384(self):
        self.assertEqual(self.horizontal_384[-3:], ['P22', 'P23', 'P24'])

    def test_last_wells_vertical_384(self):
        self.assertEqual(self.vertical_384[-3:], ['N24', 'O24', 'P24'])


class GetWellSetTestCase(TestCase):
    def setUp(self):
        self.set_96 = get_well_set(is_384=False)
        self.set_384 = get_well_set(is_384=True)

    def test_size(self):
        self.assertEqual(len(self.set_96), 96)
        self.assertEqual(len(self.set_384), 384)

    def test_upper_left(self):
        for i in ['A01', 'A02', 'B02']:
            self.assertIn(i, self.set_96)
            self.assertIn(i, self.set_384)

    def test_lower_right_96(self):
        for i in ['G12', 'H11', 'H12']:
            self.assertIn(i, self.set_96)

    def test_lower_right_384(self):
        lasts = ['O24', 'P23', 'P24']
        for i in lasts:
            self.assertIn(i, self.set_384)

    def test_out_of_bounds_96(self):
        for i in ['A00', 'A13', 'I01']:
            self.assertNotIn(i, self.set_96)

    def test_out_of_bounds_384(self):
        for i in ['A00', 'A25', 'Q01']:
            self.assertNotIn(i, self.set_384)


class GetWellGridTestCase(TestCase):
    def setUp(self):
        self.grid_96 = get_well_grid(is_384=False)
        self.grid_384 = get_well_grid(is_384=True)

    def test_dimensions_96(self):
        num_rows = len(self.grid_96)
        num_cols = len(self.grid_96[0])
        self.assertEqual(num_rows, 8)
        self.assertEqual(num_cols, 12)

    def test_dimensions_384(self):
        num_rows = len(self.grid_384)
        num_cols = len(self.grid_384[0])
        self.assertEqual(num_rows, 16)
        self.assertEqual(num_cols, 24)

    def test_corners(self):
        self.assertEqual(self.grid_96[0][0], 'A01')
        self.assertEqual(self.grid_384[0][0], 'A01')
        self.assertEqual(self.grid_96[7][11], 'H12')
        self.assertEqual(self.grid_384[15][23], 'P24')


class GetSymmetricWellTestCase(TestCase):
    def setUp(self):
        self.symmetric_96 = (
            ('A01', 'H12'),
            ('A12', 'H01'),
            ('G01', 'B12'),
            ('F06', 'C07'),
            ('D09', 'E07'),
        )

        self.symmetric_384 = (
            ('A01', 'P24'),
            ('A24', 'P01'),
            ('O01', 'B24'),
            ('J12', 'G13'),
            ('H20', 'I05'),
        )

        def test_pairs_96(self):
            for a, b in self.symmetric_96:
                self.assertEqual(get_symmetric_well(a), b)
                self.assertEqual(get_symmetric_well(b), a)

        def test_pairs_384(self):
            for a, b in self.symmetric_384:
                self.assertEqual(get_symmetric_well(a), b)
                self.assertEqual(get_symmetric_well(b), a)


class Get384ParentWellTestCase(TestCase):
    def test_upper_left_corner(self):
        self.assertEqual(get_384_parent_well('A1', 'A01'), 'A01')
        self.assertEqual(get_384_parent_well('A2', 'A01'), 'A02')
        self.assertEqual(get_384_parent_well('B1', 'A01'), 'B01')
        self.assertEqual(get_384_parent_well('B2', 'A01'), 'B02')

    def test_upper_right_corner(self):
        self.assertEqual(get_384_parent_well('A1', 'A12'), 'A23')
        self.assertEqual(get_384_parent_well('A2', 'A12'), 'A24')
        self.assertEqual(get_384_parent_well('B1', 'A12'), 'B23')
        self.assertEqual(get_384_parent_well('B2', 'A12'), 'B24')

    def test_lower_left_corner(self):
        self.assertEqual(get_384_parent_well('A1', 'H01'), 'O01')
        self.assertEqual(get_384_parent_well('A2', 'H01'), 'O02')
        self.assertEqual(get_384_parent_well('B1', 'H01'), 'P01')
        self.assertEqual(get_384_parent_well('B2', 'H01'), 'P02')

    def test_lower_right_corner(self):
        self.assertEqual(get_384_parent_well('A1', 'H12'), 'O23')
        self.assertEqual(get_384_parent_well('A2', 'H12'), 'O24')
        self.assertEqual(get_384_parent_well('B1', 'H12'), 'P23')
        self.assertEqual(get_384_parent_well('B2', 'H12'), 'P24')
