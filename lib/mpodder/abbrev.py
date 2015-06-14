class Abbrev():
    """ Given a list of strings, creates an abbreviation dict
        which, when indexed with a prefix of any of the original
        arguments, returns the shortest argument which has that 
        prefix.

        Note: this is somewhat different to other abbreviation
        classes which will not return non-unique completions, 
        where as this class returns the shortest match

        >>> a = abbrev.Abbrev('ban', 'bananas')
        >>> a['b']
        'ban'
        >>> a['ba']
        'ban'
        >>> a['ban']
        'ban'
        >>> a['bana']
        'bananas'
        >>> a['a']
        None

    """
    def __init__(self, *args):
        self._dict = dict()
        for word in reversed(sorted(args)):
            self._dict[word] = word
            for i in reversed(range(1, len(word))):
                self._dict[word[:i]] = word

    def __getitem__(self, i):
        return self._dict.get(i)

if __name__ == '__main__':
    import unittest
    class TestAbbrev(unittest.TestCase):
        def setUp(self):
            self.abb = Abbrev('ban', 'bananas', 'cruft')

        def test_non_matching(self):
            self.assertEqual(self.abb['a'], None)
            self.assertEqual(self.abb['crufty'], None)

        def test_not_unique(self):
            self.assertEqual(self.abb['b'], 'ban')

        def test_prefix(self):
            self.assertEqual(self.abb['bana'], 'bananas')
            self.assertEqual(self.abb['cru'], 'cruft')

        def test_full_match(self):
            self.assertEqual(self.abb['cruft'], 'cruft')
            self.assertEqual(self.abb['ban'], 'ban')
            self.assertEqual(self.abb['bananas'], 'bananas')

    unittest.main()

