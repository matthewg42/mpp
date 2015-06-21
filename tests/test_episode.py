import unittest
import os  
from mpp.episode import Episode

class TestWhataver(unittest.TestCase):
    def test_episode_from_dict(self):
        d = {'title': 'Episode Test', 
             'media_url': 'http://foo.com/ep1.mp3'}
        e = Episode.from_dict(d)
        self.assertEqual(e.title, 'Episode Test')
        self.assertEqual(e.media_url, 'http://foo.com/ep1.mp3')
        self.assertEqual(e.listened, False)
        self.assertEqual(e.media_path, None)

