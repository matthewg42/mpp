import unittest
from mpp.abbrev import Abbrev

class TestAbbrev(unittest.TestCase):
    def setUp(self):
        self.abb = Abbrev('ban', 'bananas', 'cruft')

    def test_non_matching(self):
        self.assertEqual(self.abb['a'], None)
        self.assertEqual(self.abb['crufty'], None)

    def test_not_unique(self):
        self.assertEqual(self.abb['b'], 'ban')

    def test_prefix(self):
        self.assertEqual(self.abb['bana'], 'bananas')
        self.assertEqual(self.abb['cru'], 'cruft')

    def test_full_match(self):
        self.assertEqual(self.abb['cruft'], 'cruft')
        self.assertEqual(self.abb['ban'], 'ban')
        self.assertEqual(self.abb['bananas'], 'bananas')

