#! /usr/bin/python

import re

from functools import partial

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
        """

        tokens = []
        for lineNum, line in enumerate(value.splitlines()):
            if len(line) > 0:
                tokens.extend(map(partial(self._ret_from_match, lineNum), self._re.finditer(line)))

        return tokens

    def _ret_from_match(self, line, match):
        return (
                self._tokens[match.lastindex-1][0],
                (line, match.start()),
                match.end(),
                match.group(match.lastindex)
                )

def graph_test():
    gTok = Tokenizer((
        ("id", "[_a-zA-Z0-9]+"),
        ("space", " +"),
        ("bslash", "\\\\"),
        ("fslash", "/"),
        ("pipe", "|")))
    
    testStr0 = """
This is a test \\//|/
sdfasdf | \\ / |              |
"""

    print(testStr0)
    print("-->\n")
    [print(t) for t in gTok.tokenize(testStr0)]
    print()

def self_test():
    graph_test()
    
if __name__ == "__main__":
    self_test()
