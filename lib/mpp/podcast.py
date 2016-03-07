import json
import datetime
import time
import hashlib
import os
import logging
from mpp.fixedparser import feedparser
from mpp.episode import Episode
from mpp.util import log

class BadlyFormedFeed(Exception):
    pass

class Podcast():
    def __init__(self, url, title=None):
        self.url = url
        self.title = title
        self.path = None
        self.episodes = []
        log.log(logging.DEBUG-1, 'Podcast.__init__(url=%s, ...)' % self.url)

    def __str__(self):
        s = 'Podcast:\n+ url=%s\n+ title=%s\n+ episodes=%d :' % (
                self.title, 
                self.url,
                len(self.episodes))
        for i in range(len(self.episodes)):
            s += '\n  - %3d: %s [%s]' % (i, self.episodes[i].title, self.episodes[i]._status())
        return s

    def save(self):
        if not self.path:
            raise Exception('cannot save - no path defined for this Podcast')
        self.save_to_file(self.path)

    def save_to_file(self, path):
        log.log(logging.DEBUG-1, 'Podcast.save_to_file(%s/%s, %s)' % (self.title, self.url, path))
        with open(path, 'w') as f:
            f.write(json.dumps(self.to_dict()))

    def delete(self):
        # TODO: remove episodes first
        log.log(logging.DEBUG-1, 'Podcast.delete(%s/%s, %s)' % (self.title, self.url, self.path))
        if self.path is not None:
            os.unlink(self.path)

    def to_dict(self):
        log.log(logging.DEBUG-1, 'Podcast.to_dict()')
        d = dict()
        d['title'] = self.title
        d['url'] = self.url
        d['episodes'] = []
        for e in self.episodes:
            d['episodes'].append(e.to_dict())
        return d

    def url_hash(self):
        log.log(logging.DEBUG-1, 'Podcast.url_hash()')
        m = hashlib.md5()
        m.update(self.url.lower().encode('utf-8'))
        return m.hexdigest()

    def matches_filter(self, filter):
        if filter is None:
            return True
        return filter.lower() in self.title.lower()

    def catch_up(self, leave=0):
        log.log(logging.DEBUG-1, 'Podcast.catch_up()')
        for i in range(len(self.episodes)-leave):
            self.episodes[i].listened = True

    def update(self):
        """ Downloads feed data from self.url, and adds new episodes if they 
            are in the feed data
        """
        log.log(logging.DEBUG-1, 'Podcast.update()')
        p = Podcast.from_url(self.url)
        return self.update_from_podcast(p)

    def update_from_podcast(self, p):
        """ Takes another feed and updates this feed from it.
            returns the number of new episodes found
        """
        log.log(logging.DEBUG-1, 'Podcast.update_from_podcast(%s)' % p.url)
        if p.url != self.url:
            raise Exception('cannot update from a different podcast')
        new_count = 0
        for episode in p.episodes:
            if episode not in self.episodes:
                log.log(logging.DEBUG-1, 'adding new episode: %s' % episode)
                self.episodes.append(episode)
                new_count += 1
        return new_count
        
    @classmethod
    def from_dict(cls, d):
        log.log(logging.DEBUG-1, 'Podcast.from_dict()')
        p = cls(d['url'], d['title'])
        if d.get('episodes'):
            for e in d['episodes']:
                p.episodes.append(Episode.from_dict(e))
            p.episodes.sort()
        return p

    @classmethod
    def from_parsed(cls, feed, url=None):
        log.log(logging.DEBUG-1, 'Podcast.from_parsed()')
        if feed.bozo:
            if type(feed.bozo_exception) != feedparser.CharacterEncodingOverride:
                raise(feed.bozo_exception)
        if url is None:
            try:
                url = [x.href for x in feed.feed.links if x.rel == 'self'][0]
            except:
                url = feed.feed.link
        p = cls(url, feed.feed.title)
        for e in feed.entries:
            if 'feedburner_origenclosurelink' in e:
                link = e.feedburner_origenclosurelink
            elif 'media_content' in e:
                link = e['media_content'][0]['url']
            else:
                link = e.link
            p.episodes.append(Episode(e.title, link, e.published))
        p.episodes.sort()
        return p

    @classmethod
    def from_url(cls, url):
        log.log(logging.DEBUG-1, 'Podcast.from_url()')
        feed = feedparser.parse(url)
        return cls.from_parsed(feed,url)

    @classmethod
    def from_file_feed(cls, path):
        log.log(logging.DEBUG-1, 'Podcast.from_file_feed()')
        with open(path, 'r') as f:
            s = f.read()
        feed = feedparser.parse(s)
        return cls.from_parsed(feed)

    @classmethod
    def from_file(cls, path):
        log.log(logging.DEBUG-1, 'Podcast.from_file()')
        with open(path, 'r') as f:
            d = json.loads(f.read())
        p = cls.from_dict(d)
        p.path = path
        return p

