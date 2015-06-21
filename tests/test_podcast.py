import unittest
import os  
from mpp.podcast import Podcast

class TestWhataver(unittest.TestCase):
    def test_episode_from_file(self):
        feed_file = '%s/tests/feed.xml' % os.popen("git rev-parse --show-toplevel").read().strip()
        p = Podcast.from_file(feed_file)
        self.assertEqual(len(p.episodes), 185)
        self.assertEqual(p.title, 'Robots - The Podcast for News and Views on Robotics')

    #def test_bad_syntax(self):
    #    with self.assertRaises(SomeException):
    #        # Do a thing which raises SomeException
