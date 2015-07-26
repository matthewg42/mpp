import glob
import os
import logging
from prettytable import PrettyTable
from mpp.podcast import Podcast
from mpp.cmdparser import CmdParser

log = logging

class PodcastManager():
    def __init__(self, config):
        self.config = config
        self.podcasts = []
        self.load_podcasts()
        self.cmds = CmdParser()
        self.cmds.register('add', self.add_podcast, 
            'usage: add url [title]\nAdd a new podcast')
        self.cmds.register('rm', self.remove_podcast, 
            'usage: rm vilter\nRemove one or more podcasts')
        self.cmds.register('ls', self.list_podcasts, 
            'usage: ls [filter]\nShow a list of podcasts')
        self.cmds.register('catchup', self.catchup_podcast, 
            'usage: catchup filter [leave]\nCatch up specific episodes')
        self.cmds.register('rename', self.rename_podcast, 
            'usage: rename filter "new name"\nSet the title of the podcast')
        
    def load_podcasts(self):
        log.debug('looking for feeds in: %s' % self.config['feed_dir'])
        for path in glob.glob('%s/*.json' % self.config['feed_dir']):
            podcast = Podcast.from_file(path)
            self.podcasts.append(podcast)
        return len(self.podcasts)

    def save_podcasts(self):
        for p in self.podcasts:
            p.save_to_file(self.config['feed_dir'] + '/%s.json' % p.url_hash())

    def get_podcast_path(self, p):
        return self.config['feed_dir'] + '/%s.json' % p.url_hash()

    def add_podcast(self, url, title=None):
        # check if we already have it
        p = Podcast(url)
        path = self.get_podcast_path(p)
        if os.path.exists(path):
            raise(Exception('already exists: %s : %s' % (url, path)))
        p = Podcast.from_url(url)
        if title is not None:
            p.title = title
        self.podcasts.append(p)
        p.save_to_file(path)
        return p

    def remove_podcast(self, filter=None):
        for p in [x for x in self.podcasts if x.matches_filter(filter)]:
            p.delete_file()

    def list_podcasts(self, filter=None):
        log.debug('list_podcasts(%s)' % filter)
        t = PrettyTable()
        t.field_names = ['Title', 'File', '#Ep', '#New', '#Rdy', '#Done']
        for p in [x for x in self.podcasts if x.matches_filter(filter)]:
            t.add_row([ p.title,
                p.url_hash() + '.json',
                len(p.episodes), 
                len([1 for x in p.episodes if x._status() == 'new']),
                len([1 for x in p.episodes if x._status() == 'ready']),
                len([1 for x in p.episodes if x._status() == 'cleaned'])
              ])
        t.align = 'r'
        t.align['Title'] = 'l'
        t.align['File'] = 'l'
        print(t)

    def catchup_podcast(self, filter=None, leave=0):
        log.debug('catchup_podcast(%s, %s)' % ( filter, leave ))
        for p in [x for x in self.podcasts if x.matches_filter(filter)]:
            p.catch_up(leave)
            log.info('caught up %s, leaving %s' % (p.title, leave))
        self.save_podcasts()

    def rename_podcast(self, filter, new_title):
        log.debug('rename_podcast(%s, %s)' % ( filter, new_title ))
        
