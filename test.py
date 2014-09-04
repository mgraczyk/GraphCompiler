#!/usr/bin/env python3

import os
from os import listdir
from os.path import isfile, join

from itertools import islice

from compiler import GraphCompiler
from compiler import GraphCompilerError
from tokenizer import TokenizationError

def get_tests():
    testsDir = "tests"
    for testName in listdir(testsDir):
        testPath = os.path.join(testsDir, testName)
        if os.path.isfile(testPath) and testName.endswith(".graph"):
            yield testPath

def print_truncate(items, maxPrint):
    it = iter(items)
    for item in islice(it, maxPrint):
        print(item)

    remaining = sum(1 for _ in it)
    if remaining:
        print("... truncated {} items ...".format(remaining))

################################################################################
# Compiler
################################################################################

def compiler_test():
    maxPrint = 40

    comp = GraphCompiler()

    for testPath in get_tests():
        teststr = open(testPath, "r").read()

        print_truncate(teststr.split("\n"), maxPrint)
        print("-->\n")

        try:
            (verts, adj) = comp.compile(teststr)
            print("Vertices = ")
            print_truncate(verts, maxPrint)
            print()
            print("Adj = ")
            print_truncate(adj, maxPrint)
            print()
        except (TokenizationError, GraphCompilerError) as e:
            print(e)
        print()
    return 0

################################################################################
# Tokenizer
################################################################################

def graph_test():
    maxPrint = 40
    gTok = GraphCompiler.tokenizer

    for testPath in get_tests():
        teststr = open(testPath, "r").read()

        print_truncate(teststr.split("\n"), maxPrint)
        print("-->\n")

        try:
            tokens = gTok.tokenize(teststr)
            print_truncate(tokens, maxPrint)
        except TokenizationError as e:
            print(e)
        print()
    return 0

def tokenizer_test():
    return graph_test()

if __name__ == "__main__":
    exit(all((
            tokenizer_test(),
            compiler_test(),
            )))
