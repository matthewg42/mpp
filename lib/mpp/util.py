import logging
import requests
import mpp.config 
import os
import re
import sys

log = logging.getLogger('mpp')

def confirm(prompt='Confirm?', def_yes=False):
    if def_yes:
        prompt += ' [Y/n] > '
    else:
        prompt += ' [y/N] > '
    
    while True:
        resp = input(prompt)
        if not resp:
            return def_yes
        if resp not in ['y', 'Y', 'n', 'N']:
            print('please enter y or n.')
            continue
        if resp.lower() == 'y':
            return True
        if resp.lower() == 'n':
            return False

def update_and_save_podcast(p, args):
    log.debug('update_and_save_podcast(%s) starting' % p.title)
    try:
        new = p.update()
        log.debug('update_and_save_podcast(%s) %d new episodes' % (p.title, new))
        if args.verbose:
            print('%d new episode%s for %s' % (new, '' if new == 1 else 's', p.title))
        if new > 0:
            log.debug('update_and_save_podcast(%s) saving' % p.title)
            p.save()
    except Exception as e:
        log.warning('Failed to update %s: %s/%s' % (p.title, type(e), e))
    
def download_podcast_episode(podcast=None, episode=None, args=None):
    """ download an episode and save the podcast item
        podcast_episode is a tuple (podcast, episode)
        return True if the episode was downloaded successfully, else False
    """
    try:
        path = '%s/%s/%s' % ( mpp.config.config['audio_directory'], 
                                 podcast.url_hash(), 
                                 episode.url_basename() )
        log.debug('download_episode((%s / %s)) starting -> %s' % (podcast.title, episode.title, path))
    except Exception as e:
        log.exception('download_podcast_episode: %s : %s' % (type(e), e))
        return False
    # make parent directory
    try:
        if os.path.exists(path):
            log.warning('download_podcast_episode: already exists: "%s", SKIPPING' % path)
            return False
        if not os.path.exists(os.path.dirname(path)):
            recursively_make_dir(os.path.dirname(path))
    except Exception as e:
        log.exception('download_podcast_episode: %s : %s' % (type(e), e))
        return False
        
    try:
        r = requests.head(episode.media_url, allow_redirects=True)
        size = int(r.headers['Content-Length'])
        r = requests.get(episode.media_url, stream=True)
        so_far = 0
        next_notify_percent = 5 
        with open(path, 'wb') as f:
            print('Downloading %s / %s : %d bytes' % (podcast.title, episode.title, size))
            for chunk in r.iter_content(chunk_size=1024*64): 
                if chunk: # filter out keep-alive new chunks
                    f.write(chunk)
                    so_far += len(chunk)
                    percent = so_far * 100 / size
                    if percent >= next_notify_percent and args.verbose:
                        print('%.1f%% %s / %s' % (percent, podcast.title, episode.title))
                        next_notify_percent += 5
            print('Complete %s / %s' % (podcast.title, episode.title))
        episode.media_path = path
        podcast.save()
        return True
    except Exception as e:
        log.exception('download_podcast_episode: %s : %s' % (type(e), e))
        return False

def recursively_make_dir(path):
    p = os.path.dirname(path)
    if not os.path.exists(p):
        recursively_make_dir(p)
    if not os.path.exists(path):
        os.mkdir(path)

def sanitize_title_for_path(title):
    title = re.sub('\++', '_', title.lower())
    title = re.sub('\s+', '_', title)
    title = re.sub('%20', '_', title)
    title = re.sub('_+', '_', title)
    title = re.sub('[\\(\\)\\[\\]\\{\\}\\\\]', '-', title)
    title = re.sub('\\&', 'and', title)
    title = re.sub('[\\\'\\`:\\?",!$\*]', '', title)
    title = re.sub('_-_', '-', title)
    title = re.sub('^[\\-_]+', '-', title)
    return title[:60]

