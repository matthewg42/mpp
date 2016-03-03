import unittest
import logging
from mpp.fixedparser import feedparser
import os
#from mpp.feed import Feed
#from mpp.whatever import whatever

class TestParseFeed(unittest.TestCase):
    def setUp(self):
        feed_file = '%s/tests/feed.xml' % os.popen("git rev-parse --show-toplevel").read().strip()
        with open(feed_file, 'r') as f:
            self.xml_data = f.read()

    def test_load_feed(self):
        feed = feedparser.parse(self.xml_data)
        self.assertEqual(feed['feed']['title'], 'Robots - The Podcast for News and Views on Robotics')
        self.assertEqual(len(feed['entries']), 185)

    #def test_bad_syntax(self):
    #    with self.assertRaises(SomeException):
    #        # Do a thing which raises SomeException
