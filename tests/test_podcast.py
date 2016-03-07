import unittest
import os  
import tempfile
import copy
from mpp.podcast import Podcast

class TestWhataver(unittest.TestCase):
    def setUp(self):
        self.feed_dict = {
            'title': 'My Lovely Horse',
            'url': 'http://localhost/lovelyhorse.xml',
            'episodes': [   {   'listened': False,
                                'media_path': None,
                                'media_url': 'http://localhost/ep1.mp3',
                                'published': 'Thu, 22 May 2008 07:00:00 GMT',
                                'title': 'Hooves'
                            },
                            {   'listened': False,
                                'media_path': None,
                                'media_url': 'http://localhost/ep2.mp3',
                                'published': 'Fri, 6 Jun 2008 07:00:00 GMT',
                                'title': 'Teeth'
                            },
                            {   'listened': False,
                                'media_path': None,
                                'media_url': 'http://localhost/ep3.mp3',
                                'published': 'Fri, 20 Jun 2008 07:00:00 GMT',
                                'title': 'Mane'
                            },
                        ]
        }

    def test_episode_from_file(self):
        feed_file = '%s/tests/feed.xml' % os.popen("git rev-parse --show-toplevel").read().strip()
        robots_podcast = Podcast.from_file_feed(feed_file)
        self.assertEqual(len(robots_podcast.episodes), 185)
        self.assertEqual(robots_podcast.title, 'Robots - The Podcast for News and Views on Robotics')

    def test_feed_from_dict(self):
        horse_podcast = Podcast.from_dict(self.feed_dict)
        self.assertEqual(len(horse_podcast.episodes), 3)
        self.assertEqual(horse_podcast.title, 'My Lovely Horse')

    def test_save_and_restore(self):
        horse_podcast = Podcast.from_dict(self.feed_dict)
        with tempfile.NamedTemporaryFile(suffix='.json') as f: tmp = f.name
        horse_podcast.save_to_file(tmp)
        restored_podcast = Podcast.from_file(tmp)
        os.unlink(tmp)
        self.assertEqual(horse_podcast.url, restored_podcast.url)
        self.assertEqual(len(horse_podcast.episodes), len(restored_podcast.episodes))

    def test_update_from_other_podcast(self):
        updated_feed_dict = copy.deepcopy(self.feed_dict)
        updated_feed_dict['episodes'].append({'listened': False, 
                                              'media_path': None, 
                                              'media_url': 'http://localhost/ep4.mp3', 
                                              'published': 'Fri, 27 Jun 2008 07:00:00 GMT', 
                                              'title': 'Tail'})
        podcast = Podcast.from_dict(self.feed_dict)
        other = Podcast.from_dict(updated_feed_dict)
        new_episode_count = podcast.update_from_podcast(other)
        self.assertEqual(len(podcast.episodes), 4)
        self.assertEqual(new_episode_count, 1)
        other.url = 'http://otherhost/feed.xml'
        with self.assertRaises(Exception):
            podcast.update_from_podcast(other)

