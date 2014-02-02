#! /usr/bin/python

import re
from collections import namedtuple

from functools import partial

Position = namedtuple('Position', ['row', 'col'])
Token = namedtuple('Token', ['type', 'position', 'len', 'value'])

class TokenizationError(Exception):
    def __init__(self, errors):
        """ Creates a TokenizationError from the specified list of errors.

            The errors should each be a tuple (P, value), where position
            is the Position where the unmatched characters begin,
            and value is the value of the unmatched characters.
        """
        self._errors = tuple(errors)

    def __str__(self):
        return "\n".join(
                'Invalid token "{}" found at row {}, col {}.'.format(
                    e[1], e[0].row, e[0].col) for e in self._errors)

    def get_errors(self):
        return self._errors

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
            Returns a list of Tokens (type, position, len, value) where

            type is the token type specified in tokens[i][0]
            position is a Position with the row and column of the token
            len is the length of the token
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
        return Token(
                self._tokens[match.lastindex-1][0],
                Position(line, match.start()),
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
                yield (Position(lineNum, start), line[start:match.start()])
            start = match.end()
        
        if start < len(line):
            yield (Position(lineNum, start), line[start:])

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
        except TokenizationError as e:
            print(e)
        print()

def self_test():
    graph_test()
    
if __name__ == "__main__":
    self_test()
