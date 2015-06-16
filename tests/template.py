import unittest
from mpp.whatever import whatever

class TestWhataver(unittest.TestCase):
    def setUp(self):
        self.fixture = ...

    def tearDown(self):
        del self.fixture

    def test_something(self):
        self.assertEqual(thing, thing)

    def test_bad_syntax(self):
        with self.assertRaises(SomeException):
            # Do a thing which raises SomeException
