# mpp

mpp or "mpodder python", is a re-implementation of the perl-based mpodder program using Python 3 and a more modern approch to configuration and data storage.  The intention is to create broadly the same end-user experience in terms of program usage, but with a more robust program which is easier to maintain and performs better than the original mpodder.

Non-exhaustive list of goals:

1.  Use Python's multi-processing module to parallelize downloads of RSS feeds.
2.  Use JSON format to store configuration.
3.  Faster handling of large feeds.


## Design

Each Podcast saves itself into a .json file from which is can be loaded too.  This file keeps trck of the basic attributes of the podcast:

1.   Title
2.   URL
3.   Episode status:
     1.  Listened
