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
        self.assertEqual(e.media_path, None)

    def test_episode_comparison(self):
        e1 = Episode.from_dict({'title': 'Ep 1', 
                                'media_url': 'http://foo.com/ep1.mp3', 
                                'published': '2014-01-01'})
        e2 = Episode.from_dict({'title': 'Ep 1a', 
                                'media_url': 'http://foo.com/ep1.mp3', 
                                'published': '2014-01-01'})
        e3 = Episode.from_dict({'title': 'Ep 1b', 
                                'media_url': 'http://foo.com/ep1.mp3', 
                                'published': '2014-01-02'})
        e4 = Episode.from_dict({'title': 'Ep 4', 
                                'media_url': 'http://foo.com/ep4.mp3', 
                                'published': '2014-02-02'})
        e5 = Episode.from_dict({'title': 'Ep 4', 
                                'media_url': 'http://foo.com/ep5.mp3', 
                                'published': '2014-03-02'})
        self.assertTrue(e1 == e2)
        # We want comparisons to ignore published date as many feeds 
        # will re-public episodes, en-masse, and we don't want to re-download
        # a bunch of stuff we've already downloaded.
        self.assertTrue(e1 == e3)
        self.assertTrue(e1 != e4)
        self.assertTrue(e4 != e5)

