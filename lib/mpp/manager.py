import glob
import os
import logging
from prettytable import PrettyTable
from multiprocessing import Pool
from mpp.podcast import Podcast
from mpp.util import confirm, update_and_save_podcast, log

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
        print('args is a %s' % type(args))
        # Make sure the optional arguments at least exist as members of args
        for a in ['url', 'path']:
            if a not in args:
                setattr(args,a,None)
        log.debug('list_podcasts(%s)' % args.filter)
        matched = [x for x in self.podcasts if x.matches_filter(args.filter)]
        t = PrettyTable()
        t.align = 'r'
        t.add_column('Title', [p.title for p in matched])
        t.align['Title'] = 'l'
        if args.url:
            t.add_column('URL', [p.url for p in matched])
            t.align['URL'] = 'l'
        elif args.path:
            t.add_column('Path', [p.path for p in matched])
            t.align['Path'] = 'l'
        else:
            #t.add_column('File', [p.url_hash() + '.json' for p in matched])
            t.add_column('File', [os.path.basename(p.path) for p in matched])
            t.add_column('#Ep', [len(p.episodes) for p in matched])
            t.add_column('#Skp', [len([1 for x in p.episodes if x.is_skipped()]) for p in matched])
            if args.verbose:
                t.add_column('#Drt', [len([1 for x in p.episodes if x.is_dirty()]) for p in matched])
                t.add_column('#Cln', [len([1 for x in p.episodes if x.is_cleaned()]) for p in matched])
            t.add_column('#New', [len([1 for x in p.episodes if x.is_new()]) for p in matched])
            t.add_column('#Rdy', [len([1 for x in p.episodes if x.is_ready()]) for p in matched])

        print(t)

    def catchup_podcast(self, args):
        log.debug('catchup_podcast(%s, %s)' % ( args.filter, args.leave ))
        for p in [x for x in self.podcasts if x.matches_filter(args.filter)]:
            p.catch_up(args.leave)
            log.info('caught up %s, leaving %s' % (p.title, args.leave))
        self.save_podcasts()

    def update_podcasts(self, args):
        log.debug('update_podcasts(%s)' % args.filter)
        to_update = [x for x in self.podcasts if x.matches_filter(args.filter)]
        with Pool(args.parallel) as p:
            p.map(update_and_save_podcast, to_update)

    def rename_podcast(self, filter, new_title):
        log.debug('rename_podcast(%s, %s)' % ( filter, new_title ))
        
