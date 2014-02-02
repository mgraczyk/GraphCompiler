#! /usr/bin/python

from collections import namedtuple


from tokenizer import Tokenizer
from tokenizer import TokenizationError

# Rank is the row in the original depiction
Vertex = namedtuple('Vertex', ['id', 'ordinal', 'rank'])

class GraphCompilerError(Exception):
    pass

class StrayEdgeError(GraphCompilerError):
    def __init__(self, message, token):
        self._token = token

    def __str__(self):
        tok = self._token
        return "Stray edge segment '{}' in graph at row {}, col {}.".format(
                tok.value, tok.position.row, tok.position.col)

class Tokens:
    ID = 0
    SPACE = 1
    BSLASH = 2
    FSLASH = 3
    PIPE = 4


class GraphCompiler:
    tokenizer = Tokenizer((
        (Tokens.ID, "[_a-zA-Z0-9]+"),
        (Tokens.SPACE, " +"),
        (Tokens.BSLASH, "\\\\"),
        (Tokens.FSLASH, "/"),
        (Tokens.PIPE, "\|")))

    def __init__(self):
        pass


    def compile(self, graph):
        """ Compiles an ASCII representation of a graph into a list of 
            vertices and an adjacency matrix.

            Returns (vertices, A), where A is the adjacency matrix.
        """

        return self._compile(self.tokenizer.tokenize(graph))

    def _compile(self, tokens):
        # We compile the graph by visiting all vertices
        # and edge segments with the following algorithm:
        #
        # 1. Build a grid of Points.
        #    Located at each point is either a vertex or edge segment.
        #    Put all the vertices in an "unvisited" list.
        # 2. While there are still unvisited vertices:
        #    a. Select an unvisited vertex.
        #    b. Process each adjacent edge segment (recursively).
        #    c. Mark the vertex as visited.
        # 3. If there unremaining edge segments, throw an exception.
        
        vertices = tuple(self._get_vertices(tokens))
        adj = [[0]*i for i in range(1, len(vertices))]


        return (vertices, adj)


    def _get_vertices(self, tokens):
        return (Vertex(v.value, num, v.position.row)
                for num, v in enumerate(t for t in tokens if t.type == Tokens.ID))


def self_test():
    import os

    comp = GraphCompiler()

    tests = [
        "simpletree",
        "strayedge"
    ]

    for testPath in tests:
        teststr = open(os.path.join("tests", testPath + ".graph"), "r").read()
        print(teststr)
        print("-->\n")

        try:
            (verts, adj) = comp.compile(teststr)
            [print(v) for v in verts]
            [print(r) for r in adj]
        except TokenizationError as e:
            print(e)
        print()



if __name__ == "__main__":
    self_test()
