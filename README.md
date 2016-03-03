# mpp

mpp or "mpodder python", is a re-implementation of the perl-based mpodder program using Python 3 and a more modern approch to configuration and data storage.  The intention is to create broadly the same end-user experience in terms of program usage, but with a more robust program which is easier to maintain and performs better than the original mpodder.

Non-exhaustive list of goals:

1.  Use Python's multi-processing module to parallelize downloads of RSS feeds.
2.  Use JSON format to store configuration.
3.  Faster handling of large feeds.

## Dependencies

- Python 3 (come on people, let's not be staring new projects with Python 2!)
- Python modules (pip3 package names):
    - veryprettytable
    - python-dateutil

Optional development dependencies:

- python-nose (for running tests)

## Design

Podcast objects can be created from a URL or loaded from a file. They contain limited information about a podcast: 

- the feed URL
- podcast title
- a list of episodes

Each Episode object stores:

- the episode download url
- episode title
- published date
- media path (where the downloaded media file is stored locally)
- listened flag

When a Podcast object is created from a URL, the URL is downloaded, and the title set. Episode objects are created with listened=False.

Each episode has a value *media_path* which describes the state of the podcast:

-  *None* - the episode is ready for download
-  *empty string* - the episode has been skipped
-  *some path* - the episode has been downloaded. If a file exists with the path, the podast is downloaded and ready for listening.  If a file does not exist, the podcast has status 'listened'

After downloading episodes are stored in holding area.  It is expected that a separate program moves the files out of this area either to play them, or when they have been played.

## Commands

### list 

#### Synopsis

    list [filter]

#### Description

Print a list of podcasts which are known to mpp. If a filter is specified the resulting list of filtered to include only podcasts whose title matches the filter.

#### Aliases

ls

### add

#### Synopsis

    add <url>

#### Description

Adds a podcast from a feed URL.  All episodes are set to ready to download.

### show 

#### Synopsis

    show [filter]

#### Description

Dump all available information about one of more podcasts.  This includes the URL.

#### Aliases

info

### remove

#### Synopsis

    remove <filter>

#### Description

Remove podcasts whose title matches filter. This will also remove any downloaded episodes of the podcast, and all information regarding which episodes have been listened to.

#### Aliases

rm

### catchup

#### Synopsis

    catchup [--leave n] <filter>

#### Description

Sets all episodes to state "listened" for podcasts matching filter.  If the --leave option is specified, *n* episodes will be left with ready status.

### rename

#### Synopsis

    rename <filter>

#### Description

Rename a podcast matching filter. If more than one podcast matches filter, an error is raised and mpp quits.

#### Aliases

mv

## Known Problems

### Changing URL
The original URL supplied when adding the podcast may not be the same as the one the feed replies with, causing the hash to change between the original addition and subsequent saves. 

Solution: instead of basing the filename on a hash of the URL, each podcast should be allocated a unique.
Challenge: detecting duplicates on addition
