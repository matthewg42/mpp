import glob
import os
import logging
from prettytable import PrettyTable
from multiprocessing import Pool
from mpp.podcast import Podcast
from mpp.util import log, confirm, update_and_save_podcast, download_podcast_episode

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

    def rename_podcast(self, args):
        to_rename = [x for x in self.podcasts if x.matches_filter(args.filter)]
        if len(to_rename) != 1:
            log.error('the filter for renaming a podcast should match exactly one podcast (but matches %d)' % len(to_rename))
            exit(1)
        to_rename = to_rename[0]
        log.debug('Renaming %s -> %s' % (to_rename.title, ' '.join(args.title)))
        to_rename.title = ' '.join(args.title)
        to_rename.save()

    def show_podcast(self, args):
        log.debug('show_podcast(%s)' % args.filter)
        [print(x) for x in self.podcasts if x.matches_filter(args.filter)]

    def list_podcasts(self, args):
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
        log.debug('update_podcasts(filter=%s)' % args.filter)
        to_update = [x for x in self.podcasts if x.matches_filter(args.filter)]
        with Pool(args.parallel) as p:
            p.map(update_and_save_podcast, to_update)

    def download_podcasts(self, args):
        log.debug('download_podcasts(filter=%s)' % args.filter)
        new_episodes = []
        for podcast in [x for x in self.podcasts if x.matches_filter(args.filter)]:
            new = [(podcast, x) for x in podcast.episodes if x.is_new()][:args.max]
            log.debug('download_podcasts() downloading %d from %s' % (len(new), podcast.title))
            new_episodes.extend(new)
        log.debug('download_podcasts() downloading total of %d new episodes with %d parallel' % (len(new_episodes), args.parallel))
        with Pool(args.parallel) as p:
            p.map(download_podcast_episode, new_episodes)

    def list_episodes(self, args):
        stati = ['new', 'ready']
        if args.status: 
            stati = args.status
        log.debug('list_episodes(filter=%s, first=%s, last=%s, path=%s, stati=%s)' % (
                    args.filter,
                    args.first,
                    args.last,
                    args.path,
                    stati))
        if not args.path:
            table = PrettyTable()
            table.field_names = ["Podcast", "Episode", "Published", "Status"]

        for podcast in [x for x in self.podcasts if x.matches_filter(args.filter)]:
            episodes = [e for e in podcast.episodes if e._status() in stati]
            if args.first:
                episodes = episodes[:args.first]
            elif args.last:
                episodes = episodes[0-args.last:]

            for e in episodes:
                if args.path:
                    if e.media_path: 
                        print(e.media_path)
                else:
                    table.add_row([podcast.title, e.title, e.published, e._status()])
                
        if not args.path:
            print(table)
