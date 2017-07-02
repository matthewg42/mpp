import glob
import os
import logging
import dateutil.parser
import sys
import json
from contextlib import contextmanager
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
        self.podcasts = []
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
        if args.filter is None:
            if not confirm('Remove all podcasts?'):
                return
        to_remove = [x for x in self.podcasts if x.matches_filter(args.filter)]
        if len(to_remove) > 0:
            if args.verbose:
                self.list_podcasts(args)
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
        t.add_column('Title', [p.title for p in matched], align='l')
        if args.url:
            t.add_column('URL', [p.url for p in matched], align='l')
        elif args.path:
            t.add_column('Path', [p.path for p in matched], align='l')
        else:
            if args.verbose:
                t.add_column('#Ep', [len(p.episodes) for p in matched], align='r')
                t.add_column('#Skp', [len([1 for x in p.episodes if x.has_status('skipped')]) for p in matched], align='r')
            t.add_column('#New', [len([1 for x in p.episodes if x.has_status('new')]) for p in matched], align='r')
            t.add_column('#Dld', [len([1 for x in p.episodes if x.has_status('downloaded')]) for p in matched], align='r')

        print(t)

    def catchup_podcast(self, args):
        log.debug('catchup_podcast(%s, %s)' % ( args.filter, args.leave ))
        for p in [x for x in self.podcasts if x.matches_filter(args.filter)]:
            skipped = p.catch_up(args.leave)
            log.info('caught up %s, skipped %d, leaving %s' % (p.title, skipped, args.leave))
            if skipped > 0:
                # Remove downloaded files for skipped episodes
                for e in [x for x in p.episodes if x.has_status('skipped')]:
                    if e.media_path and os.path.exists(e.media_path):
                        os.remove(e.media_path)
                p.save()

    def update_podcasts(self, args):
        log.debug('update_podcasts(filter=%s)' % args.filter)
        to_update = [(x, args) for x in self.podcasts if x.matches_filter(args.filter)]
        if args.verbose:
            print('Updating %d feeds...' % len(to_update))
        with Pool(args.parallel) as p:
            p.starmap(update_and_save_podcast, to_update)

    def download_podcasts(self, args):
        log.debug('download_podcasts(filter=%s)' % args.filter)
        new_episodes = []
        args.max = 1 # temp fix for update / thread problem (see problems section of README.md)
        for podcast in [x for x in self.podcasts if x.matches_filter(args.filter)]:
            new = [(podcast, x, args) for x in podcast.episodes if x.has_status('new')][:args.max]
            log.debug('download_podcasts() downloading %d from %s' % (len(new), podcast.title))
            new_episodes.extend(new)
        log.debug('download_podcasts() downloading total of %d new episodes with %d parallel' % (len(new_episodes), args.parallel))
        if args.verbose:
            if len(new_episodes) > 0:
                print('Downloading %d episode%s...' % (len(new_episodes), '' if len(new_episodes)==1 else 's'))
            else:
                print('No new episodes to download')
        with Pool(args.parallel) as p:
            try:
                p.starmap(download_podcast_episode, new_episodes)
            except Exception as e:
                log.exception('download_podcasts: error file downloading %s - %s: %s' % (str(new_episodes), type(e), e))

    def fetch_podcasts(self, args):
        self.update_podcasts(args)
        self.load_podcasts()
        self.download_podcasts(args)

    def list_episodes(self, args):
        stati = ['new', 'downloaded']
        if args.status: 
            stati = args.status
        log.debug('list_episodes(pfilter=%s, efilter=%s, first=%s, last=%s, since=%s, path=%s, stati=%s)' % (
                    args.pfilter,
                    args.efilter,
                    args.first,
                    args.last,
                    args.since,
                    args.path,
                    stati))
        if not args.path and not args.url:
            table = PrettyTable()
            table.field_names = ['Published', 'Podcast', 'Episode', 'Status']
            table.align = 'l'

        for podcast in [x for x in self.podcasts if x.matches_filter(args.pfilter)]:
            episodes = [e for e in podcast.episodes if stati_match(stati, e) and e.since(args.since) and e.matches_filter(args.efilter)]
            if args.first:
                episodes = episodes[:args.first]
            elif args.last:
                episodes = episodes[0-args.last:]

            for e in episodes:
                if args.path:
                    if e.media_path: 
                        print(e.media_path)
                elif args.url:
                    print(e.media_url)
                else:
                    if args.full or len(e.title) <= 50:
                        title = e.title
                    else:
                        title = e.title[:47] + '...'
                    table.add_row([ e._pub_date().strftime('%Y-%m-%d %T'),
                                    podcast.title, 
                                    title, 
                                    e.status() ])
                
        if not args.path and not args.url:
            print(table.get_string(sortby="Published"))

    def renew_episodes(self, args):
        stati = ['skipped', 'listened']
        if args.status: 
            stati = args.status
        log.debug('renew_episodes(filter=%s, first=%s, last=%s, since=%s, stati=%s)' % (
                    args.filter,
                    args.first,
                    args.last,
                    args.since,
                    stati))

        total = 0
        for podcast in [x for x in self.podcasts if x.matches_filter(args.filter)]:
            count_this_podcast = 0
            episodes = [e for e in podcast.episodes if stati_match(stati, e) and e.since(args.since)]
            if args.first:
                episodes = episodes[:args.first]
            elif args.last:
                episodes = episodes[0-args.last:]

            for e in episodes:
                if e.skipped:
                    e.skipped = False
                    total += 1
                    count_this_podcast += 1
                else:
                    log.log

                if e.media_path:
                    if not os.path.exists(e.media_path):
                        e.media_path = None

            if count_this_podcast > 0:
                podcast.save()

        if args.verbose:
            print('%d episodes renewed' % total)

    def export_podcasts(self, args):
        log.debug('export_podcasts(filter=%s, output_path=%s)' % (args.filter, args.path))
        with get_fh_or(sys.stdout, args.path, 'w') as f:
            data = [x.to_dict() for x in self.podcasts if x.matches_filter(args.filter)]
            f.write(json.dumps(data, indent=4, separators=(',', ': ')))

    def import_podcasts(self, args):
        log.debug('import_podcasts(filter=%s, input_path=%s)' % (args.filter, args.path))
        with get_fh_or(sys.stdin, args.path, 'r') as f:
            data = json.load(f)
            for podcast_dict in data:
                try:
                    p = Podcast.from_dict(podcast_dict)
                    log.debug('import_podcasts: examining: %s' % p.title)
                    path = self.get_podcast_path(p)
                    if os.path.exists(path):
                        raise(Exception('already exists: %s for %s' % (path, p.title)))
                    p.path = path
                    if p.matches_filter(args.filter):
                        log.debug('import_podcasts: Podcast matches filter, saving... %s' % p.title)
                        p.save()
                except Exception as e:
                    log.warning('import_podcasts: exception while importing podcast: %s' % e)
                
def stati_match(stati, e):
    for s in stati:
        if e.has_status(s):
            return True
    return False

@contextmanager
def get_fh_or(alt, path, mode):
    if path is None:
        yield alt
    else:
        yield open(path, mode)

