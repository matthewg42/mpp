import glob
import os
import logging
from prettytable import PrettyTable
from mpp.podcast import Podcast
from mpp.util import confirm

log = logging

class PodcastManager():
    def __init__(self, config):
        self.config = config
        self.podcasts = []
        self.load_podcasts()

    def exec(self, args):
        getattr(self, args.cmd)(args)
        
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

    def add_podcast(self, args):
        # check if we already have it
        p = Podcast(args.url)
        path = self.get_podcast_path(p)
        if os.path.exists(path):
            raise(Exception('already exists: %s : %s' % (args.url, path)))
        p = Podcast.from_url(args.url)
        if args.title:
            p.title = args.title
        self.podcasts.append(p)
        p.save_to_file(path)
        return p

    def remove_podcast(self, args):
        remove_count = 0
        to_remove = [x for x in self.podcasts if x.matches_filter(args.filter)]
        if len(to_remove) > 0:
            if args.verbose:
                self.list_podcasts(args)
            if args.assume_yes or confirm('Remove %d podcasts? [y,N]> ' % len(to_remove)):
                for p in to_remove:
                    p.delete()
                    remove_count += 1
        if args.verbose:
            print('Removed %d podcasts' % remove_count)

    def list_podcasts(self, args):
        log.debug('list_podcasts(%s)' % args.filter)
        t = PrettyTable()
        t.field_names = ['Title', 'File', '#Ep', '#New', '#Rdy', '#Done']
        for p in [x for x in self.podcasts if x.matches_filter(args.filter)]:
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
        
