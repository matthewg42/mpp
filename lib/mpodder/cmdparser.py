import logging
from mpodder.abbrev import Abbrev

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

if __name__ == '__main__':
    import unittest

    class TestCmdParser(unittest.TestCase):
        def setUp(self):
            self.p = CmdParser()
            self.p.register('double', lambda x: x*2, 'Doubles a number')
            self.p.register('triple', lambda x: x*3, 'Triples a number')
            self.p.register('decrement', lambda x: x-1, 'Takes 1 from a number')

        def tearDown(self):
            del(self.p)

        def test_registered_command(self):
            self.assertEqual(self.p.execute('double', 4), 8)

        def test_abbreviated_command(self):
            self.assertEqual(self.p.execute('do', 4), 8)
            self.assertEqual(self.p.execute('t', 4), 12)
            
        def test_register_command(self):
            b4 = len(self.p._cmds)
            self.p.register('increment', lambda x: x+1, 'Adds 1 to a number')
            self.assertEqual(b4+1, len(self.p._cmds))
            self.assertEqual(self.p.execute('increment', 4), 5)

        def test_missing_command(self):
            with self.assertRaises(UnknownCommand):
                self.p.execute('nonexisting', 4)

        def test_bad_syntax(self):
            with self.assertRaises(CommandSyntax):
                # we should have a single argument
                self.p.execute('double')
            with self.assertRaises(CommandSyntax):
                # we should have a single integer argument
                self.p.execute('triple', 2, 3)

    unittest.main()

