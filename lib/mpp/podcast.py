import feedparser
import json
import datetime
import time
from mpp.episode import Episode

class BadlyFormedFeed(Exception):
    pass

class Podcast():
    def __init__(self, url, title):
        self.url = url
        self.title = title
        self.episodes = []

    def __str__(self):
        s = 'Podcast:\n+ url=%s\n+ title=%s\n+ episodes=%d :' % (
                self.title, 
                self.url,
                len(self.episodes))
        for i in range(len(self.episodes)):
            s += '\n  - %3d: %s' % (i, self.episodes[i].title)
        return s

    def save_to_file(self, path):
        with open(path, 'w') as f:
            f.write(json.dumps(self.to_dict()))

    def to_dict(self):
        d = dict()
        d['title'] = self.title
        d['url'] = self.url
        d['episodes'] = []
        for e in self.episodes:
            d['episodes'].append(e.to_dict())
        return d
    
    @classmethod
    def from_dict(cls, d):
        p = cls(d['url'], d['title'])
        if d.get('episodes'):
            for e in d['episodes']:
                p.episodes.append(Episode.from_dict(e))
        return p

    @classmethod
    def from_parsed(cls, feed):
        if feed.bozo:
            raise(bozo_exception)
        p = cls(feed.feed.link, feed.feed.title)
        for e in feed.entries:
            p.episodes.append(Episode(e.title, e.link, e.published))
        return p

    @classmethod
    def from_url(cls, url):
        feed = feedparser.parse(url)
        return cls.from_parsed(feed)

    @classmethod
    def from_file_feed(cls, path):
        with open(path, 'r') as f:
            s = f.read()
        feed = feedparser.parse(s)
        return cls.from_parsed(feed)

    @classmethod
    def from_file(cls, path):
        with open(path, 'r') as f:
            d = json.loads(f.read())
        return cls.from_dict(d)

    @classmethod
    def from_file_feed(cls, path):
        with open(path, 'r') as f:
            s = f.read()
        feed = feedparser.parse(s)
        return cls.from_parsed(feed)

