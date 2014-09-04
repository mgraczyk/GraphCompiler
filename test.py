#!/usr/bin/env python3

import os
from os import listdir
from os.path import isfile, join

from compiler import GraphCompiler
from compiler import GraphCompilerError
from tokenizer import TokenizationError

def get_tests():
    testsDir = "tests"
    for testName in listdir(testsDir):
        testPath = os.path.join(testsDir, testName)
        if os.path.isfile(testPath) and testName.endswith(".graph"):
            yield testPath

################################################################################
# Compiler
################################################################################

def compiler_test():
    comp = GraphCompiler()

    for testPath in get_tests():
        teststr = open(testPath, "r").read()
        print(teststr)
        print("-->\n")

        try:
            (verts, adj) = comp.compile(teststr)
            print("Vertices = ")
            [print(v) for v in verts]
            print()
            print("Adj = ")
            [print(r) for r in adj]
            print('\n')
        except (TokenizationError, GraphCompilerError) as e:
            print(e)
        print()
    return 0

################################################################################
# Tokenizer
################################################################################

def graph_test():
    gTok = GraphCompiler.tokenizer

    for testPath in get_tests():
        teststr = open(testPath, "r").read()
        print(teststr)
        print("-->\n")

        try:
            [print(t) for t in gTok.tokenize(teststr)]
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
