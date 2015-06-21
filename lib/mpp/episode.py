import types
import logging

log = logging.getLogger('mpp')

class Episode():
    def __init__(self, title, media_url, media_path=None, listened=False):
        # this works a little like a named tuple
        l = locals()
        for v in [x for x in l.keys() if x != 'self']:
            setattr(self, v, l[v])

    def __str__(self):
        return 'Episode(%s)' % ', '.join(['%s=%s' % (x, getattr(self, x)) for x in self.get_fields()])

    def get_fields(self):
        return [x for x in dir(self) if x[0] != '_' and type(getattr(self, x)) != types.MethodType]

    def to_dict(self):
        return {x: getattr(self, x) for x in elf.get_fields()}

    @classmethod
    def from_dict(cls, d):
        return cls( d['title'], 
                    d['media_url'],
                    d.get('media_path'),
                    False if not d.get('listened') else d['listened'])


