import logging
from mpp.abbrev import Abbrev

log = logging.getLogger('mpp')

class UnknownCommand(Exception):
    pass

class CommandSyntax(Exception):
    pass

class CmdParser():
    def __init__(self):
        self._cmds = dict()

    def __str__(self):
        return 'CmdParser (%d commands: %s)' % (len(self._cmds), ', '.join(sorted(self._cmds)))

    def register(self, name, func, help):
        if name in self._cmds:
            log.warn('command "%s" already registered - replacing' % name)
        self._cmds[name] = {'exec': func, 'name': name, 'help': help}
        self._abbrev = Abbrev(*list(self._cmds.keys()))
    
    def execute(self, *args):
        """ Accepts s list of arguments, the first of which is a command name
            and subsequent args are parameters to the command.
            Raises UnknownCommand if the command is not registered with 
            CmdParser
        """
        # look up abbreviated command name
        c = self._abbrev[args[0]]
        if c is None or c not in self._cmds:
            raise(UnknownCommand(c))
        try:
            return self._cmds[c]['exec'](*args[1:])
        except TypeError as e:
            raise(CommandSyntax(e))

