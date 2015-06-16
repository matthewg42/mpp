import unittest
import mpp.cmdparser

class TestCmdParser(unittest.TestCase):
    def setUp(self):
        self.p = mpp.cmdparser.CmdParser()
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
        with self.assertRaises(mpp.cmdparser.UnknownCommand):
            self.p.execute('nonexisting', 4)

    def test_bad_syntax(self):
        with self.assertRaises(mpp.cmdparser.CommandSyntax):
            # we should have a single argument
            self.p.execute('double')
        with self.assertRaises(mpp.cmdparser.CommandSyntax):
            # we should have a single integer argument
            self.p.execute('triple', 2, 3)


