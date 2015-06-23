import unittest
import os  
import tempfile
from mpp.podcast import Podcast

class TestWhataver(unittest.TestCase):
    def setUp(self):
        feed_file = '%s/tests/feed.xml' % os.popen("git rev-parse --show-toplevel").read().strip()
        self.robots_podcast = Podcast.from_file_feed(feed_file)

    def test_episode_from_file(self):
        self.assertEqual(len(self.robots_podcast.episodes), 185)
        self.assertEqual(self.robots_podcast.title, 'Robots - The Podcast for News and Views on Robotics')

    def test_save_and_restore(self):
        with tempfile.NamedTemporaryFile() as f: tmp = f.name
        self.robots_podcast.save_to_file(tmp)
        p = Podcast.from_file(tmp)
        os.unlink(tmp)
        self.assertEqual(self.robots_podcast.title, p.title)

    #def test_bad_syntax(self):
    #    with self.assertRaises(SomeException):
    #        # Do a thing which raises SomeException
