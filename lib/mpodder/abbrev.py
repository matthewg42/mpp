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

