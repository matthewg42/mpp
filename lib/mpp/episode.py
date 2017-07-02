import types
import logging
import dateutil.parser
import os
import re
from mpp.util import log

class Episode():
    def __init__(self, title, media_url, published, media_path=None, skipped=False):
        # this works a little like a named tuple
        l = locals()
        for v in [x for x in l.keys() if x != 'self']:
            setattr(self, v, l[v])

    def __str__(self):
        return 'Episode(%s)' % ', '.join(['%s=%s' % (x, getattr(self, x)) for x in self.get_fields()])

    def __lt__(self, other):
        pd = self._pub_date().replace(tzinfo=None)
        od = other._pub_date().replace(tzinfo=None)
        return pd < od

    def get_fields(self):
        return [x for x in dir(self) if x[0] != '_' and type(getattr(self, x)) != types.MethodType]

    def to_dict(self):
        return {x: getattr(self, x) for x in self.get_fields()}

    def _pub_date(self):
        """ Returns a datetime object from the published value (which is a
            string)
        """
        if self.published:
            return dateutil.parser.parse(self.published)
        return None

    def status(self):
        if self.skipped:
            return 'skipped'
        else:
            if self.media_path is None:
                return 'new'
            elif os.path.exists(self.media_path):
                return 'downloaded'
            else:
                return 'listened'

    def has_status(self, s):
        if s not in ['new', 'skipped', 'downloaded', 'listened', 'any']:
            log.warning('unknown status: %s' % s)
        status = self.status()
        return(s == status or s == 'any')

    def matches_filter(self, filter):
        if filter is None or filter == '*':
            return True
        return filter.lower() in self.title.lower()

    def since(self, datestring):
        if datestring is None:
            return True
        return self._pub_date() >= dateutil.parser.parse(datestring)

    def __eq__(self, ep):
        """ Somewhat fuzzy equality operator. There are some cases where we
            want to think of two episodes as being the same even though they 
            may have some different memebers.  This is because web site
            operators may do things like update URLs when re-arranging their 
            sites.  In these cases we don't want to suddenly think there are 
            a bunch of new podcasts.
        """
        if self.media_url == ep.media_url:
            return True
        elif self.title == ep.title and self._pub_date() == ep._pub_date():
            return True
        else:
            return False

    def url_basename(self):
        if self.media_url:
            u = re.sub(r'\?.*$', '', self.media_url)
            u = u.replace('\\', '.')
            return u.split('/')[-1:][0]
        else:
            return None

    @classmethod
    def from_dict(cls, d):
        return cls( d['title'], 
                    d['media_url'],
                    d['published'],
                    d.get('media_path'),
                    d.get('skipped') )


