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

### Episode Status

    LISTENED    MEDIA_PATH is None  MEDIA_PATH_EXISTS   STATUS

    False       True                -                   new
    True        True                -                   skipped
    False       False               False               dirty (after download)
    False       False               True                ready
    True        False               False               cleaned
    True        False               True                dirty

Expected status changes over time:

new -> skipped
new -> ready -> dirty -> cleaned
new -> ready -> dirty -> skipped

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

    rename <filter> <title> [title ...]

#### Description

Rename a podcast matching filter. If more than one podcast matches filter, an error is raised and mpp quits. If multiple title arguments are specified, they are joined with the space character.

#### Aliases

mv

### download

#### Synopsis

    download [--parallel=p] [--max=m] filter

#### Description

Download up to m new episodes for each podcast which matches filter, using at most p parallel download processes.

#### Aliases

dl

### fetch

#### Synopsis

    fetch [--max=m] filter

#### Description

Updates (checks for new epidodes), and then downloads up to m new episodes for each podcast which matches filter, using at most p parallel download processes.

#### Aliases

get, f

### episodes

#### Synopsis

    episodes [--first=f] [--last=l] [--path] [--status=s] filter 

#### Description

Lists the episodes for podcasts matching filter.  By default only new and ready episodes are displayed, and the output consistes of: podcast title, episode title, episode status.

The --first option may be used to show only the first f results (sorted in feed order). The --last option shows only the las l results. If --status is specified, only episodes having status s are displayed (possible statuses are: new, ready, skipped, cleanedm and all, which selects episodes with any status.  If the --path option is used, only new podcasts with the media downloaded are displayed, and the output is just the path to the downloaded files.

#### Aliases

ep, lse

### renew

#### Synopsis

    renew [--since=YYYYMMDD] [--last=l] [--first=f] [--status=s] filter 

#### Description

For podcasts that match filter, change the status from 'skipped' or 'cleaned' to 'new'.

If --status is specified, only affect episodes which have status s.  If --last is specified, only affect the last l episodes.  If --first is specified, only affect the first f episodes.  If --sine is specified, only affect episodes published since the date defined by YYYYMMDD (inclusive).

## Known Problems

### Changing URL
The original URL supplied when adding the podcast may not be the same as the one the feed replies with, causing the hash to change between the original addition and subsequent saves. 

Solution: instead of basing the filename on a hash of the URL, each podcast should be allocated a unique.
Challenge: detecting duplicates on addition

