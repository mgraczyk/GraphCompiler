#! /usr/bin/python

import re

from functools import partial

class TokenizationError(Exception):
    def __init__(self, errors):
        """ Creates a TokenizationError from the specified list of errors.

            The errors should each be a tuple (pos, value), where position
            is the row and column where the unmatched characters begin,
            and value is the value of the unmatched characters.
        """
        self._errors = errors

    def __str__(self):
        return "\n".join(
                'Invalid token "{}" found at row {}, col {}.'.format(
                    e[1], e[0][0], e[0][1]) for e in self._errors)

class Tokenizer:
    def __init__(self, tokens):
        """ Creates a tokenizer that uses the specified list of tokens.
            tokens should be an iterable of tuples t where
            t[0] = The token type (can be anything to identify the token)
            t[1] = The regex that matches the token

            Where there are tokenization conflicts, tokens are matched
            in the same order as they appear in the tokens list.
        """
        self._tokens = tokens
        allPattern = '|'.join("(" + t[1] + ")" for t in tokens)
        self._re = re.compile(allPattern)


    def tokenize(self, value):
        """ Tokenizes the value.
            Returns a list of tuples (type, pos, len, value) where

            pos is a tuple with the row and column of the token
            len is the length of the token
            type is the token type specified in tokens[i][0]
            value is the literal value of the token

            If non-tokens are discovered, a TokenizationError is raised.
        """

        tokens = []
        errors = []
        for lineNum, line in enumerate(value.splitlines()):
            if line:
                matches = tuple(self._re.finditer(line))

                errors.extend(self._find_unmatched(line, lineNum, matches))
                tokens.extend(map(partial(self._ret_from_match, lineNum), matches))

        if errors:
            raise TokenizationError(errors)

        return tokens

    def _ret_from_match(self, line, match):
        return (
                self._tokens[match.lastindex-1][0],
                (line, match.start()),
                match.end(),
                match.group(match.lastindex)
                )

    def _find_unmatched(self, line, lineNum, matches):
        """ For every substring of line that is not matched by one of matches,
            a tuple (pos, substring) is yielded.
        """
        start = 0
        for match in matches:
            if start < match.start():
                yield ((lineNum, start), line[start:match.start()])
            start = match.end()
        
        if start < len(line):
            yield ((lineNum, start), line[start:])

def graph_test():
    import os

    gTok = Tokenizer((
        ("id", "[_a-zA-Z0-9]+"),
        ("space", " +"),
        ("bslash", "\\\\"),
        ("fslash", "/"),
        ("pipe", "\|")))

    tests = [
        "simpletree",
        "simpleerrors",
        "errors"
    ]

    for testPath in tests:
        teststr = open(os.path.join("tests", testPath + ".graph"), "r").read()
        print(teststr)
        print("-->\n")

        try:
            [print(t) for t in gTok.tokenize(teststr)]
        except TokenizationError as t:
            print(t)
        print()

def self_test():
    graph_test()
    
if __name__ == "__main__":
    self_test()
