import unittest
import os  
import time
import datetime
from mpp.episode import Episode

class TestWhataver(unittest.TestCase):
    def test_episode_from_dict(self):
        d = {'title': 'Episode Test', 
             'media_url': 'http://foo.com/ep1.mp3',
             'published': '2014-01-01 12:00:00'}
        e = Episode.from_dict(d)
        self.assertEqual(e.title, 'Episode Test')
        self.assertEqual(e.media_url, 'http://foo.com/ep1.mp3')
        self.assertIsNotNone(e.published)
        self.assertEqual(e.listened, False)
        self.assertEqual(e.media_path, None)

    def test_episode_comparison(self):
        e1 = Episode.from_dict({'title': 'Ep 1', 
                                'media_url': 'http://foo.com/ep1.mp3', 
                                'published': '2014-01-01'})
        e2 = Episode.from_dict({'title': 'Ep 1', 
                                'media_url': 'http://foo.com/ep1.mp3', 
                                'published': '2014-01-01'})
        self.assertTrue(e1 == e2)

