#! /usr/bin/python

import operator

from collections import namedtuple
from collections import defaultdict
from functools import partial
from itertools import chain

from tokenizer import Tokenizer
from tokenizer import TokenizationError

def compose(f, g):
    def composition(*args, **kwargs):
        return f(g(*args, **kwargs))
    return composition

# Rank is the row in the original depiction
Vertex = namedtuple('Vertex', ['id', 'rank'])

class GraphCompilerError(Exception):
    pass

class StrayEdgeError(GraphCompilerError):
    def __init__(self, token):
        self._token = token

    def __str__(self):
        tok = self._token
        return "Stray edge segment '{}' in graph at row {}, col {}.".format(
                tok.value, tok.position.row, tok.position.col)

class OverconnectedEdgeError(GraphCompilerError):
    def __init__(self, token):
        self._token = token

    def __str__(self):
        tok = self._token
        return "Overconnected edge segment '{}' in graph at row {}, col {}.".format(
                tok.value, tok.position.row, tok.position.col)

class Tokens:
    ID = 0
    SPACE = 1
    BSLASH = 2
    FSLASH = 3
    PIPE = 4
    LANGLE = 5
    RANGLE = 6
    TANGLE = 7

#class DefaultList(list):
    #def __init__(self, fillFactory=None, outOfBoundsFactory=None, fillOnGet=False):
        #self._fillFactory = fillFactory
        #self._oobFactory = outOfBoundsFactory
        #self._fillOnGet = fillOnGet

    #def __setitem__(self, key, value):
        #return super().__setitem__(key, value)

    #def __getitem__(self, key, value):
        #try:
            #return super().__getitem__(key, value)
        #except IndexError:
            #pass

class AutoGrid():
    """ Automatically resizing grid.
    """
    def __init__(self, nowrap=True):
        self._nowrap = nowrap
        self._rows = []

    def insert_item(self, position, length, value):
        rowdiff = position.row - len(self._rows) + 1
        if rowdiff > 0:
            self._rows.extend([] for i in range(rowdiff))

        row = self._rows[position.row]

        coldiff = position.col - len(row)
        if coldiff > 0:
            row.extend([None]*coldiff)

        row[position.col:position.col+length] = [value]*length

    def get(self, row, col):
        try:
            # The grid does not wrap around
            if (row < 0 or col < 0) and self._nowrap:
                return None
            else:
                return self._rows[row][col]
        except IndexError:
            return None

    def get_neighbors(self, row, col, length):
        assert(length > 0)
        
        return set(filter(operator.truth,
                chain((self.get(row-1, col+i) for i in range(-1, length+1)),
                      (self.get(row+1, col+i) for i in range(-1, length+1)),
                      (self.get(row, col-1), self.get(row, col+length+1)))))

    def __str__(self):
        return "Grid(\n" + "\n".join(str(row) for row in self._rows) + "\n)"

class GridItem():
    def __init__(self, token):
        self._token = token

        self._connections = 0

    def get_attached(self, grid):
        raise NotImplementedError()

    def is_attached_to(self, grid):
        raise NotImplementedError()

    @classmethod
    def are_attached(cls, left, right):
        attached = left.is_attached_to(right) and right.is_attached_to(left)
        return attached


class EdgeSegmentItem(GridItem):
    def __init__(self, info, token):
        super().__init__(token)

        assert(info)
        self._info = info
        self._visiting = False
        self._visited = False
        self._attached = defaultdict(int) # int() -> 0

    def get_attached(self, grid):
        # No attached set, but visited means that there's we're cycling
        # In that case just return the empty set
        if self._visiting:
            return dict()

        if not self._visited:
            self._visiting = True
            tok = self._token

            neighbors = grid.get_neighbors(tok.position.row, tok.position.col, tok.length)

            for neighbor in filter(partial(GridItem.are_attached, self), neighbors):
                self._connections += 1
                for k,v in neighbor.get_attached(grid).items():
                    self._attached[k] += v

            self._visiting = False
            self._visited = True
            
            # TODO: Check that self._attached is not empty

        return self._attached

    def is_attached_to(self, other):
        myPos = self._token.position
        otherPos = other._token.position
        rowDiff = otherPos.row - myPos.row
        colDiff = myPos.col - otherPos.col

        return any(rowDiff == port[0] and 0 <= colDiff + port[1] < other._token.length
                for port in self._info._ports)

    def assert_processed(self):
        if self._connections < self._info.mincon:
            raise StrayEdgeError(self._token)
        elif self._info.maxcon < self._connections:
            raise OverconnectedEdgeError(self._token)

class VertexItem(GridItem):
    def __init__(self, token):
        super().__init__(token)

        self._attached = {self.get_key():1}
        self._adjacent = None

    def get_attached(self, grid):
        return self._attached

    def is_attached_to(self, other):
        myPos = self._token.position
        otherPos = other._token.position
        rowDiff = otherPos.row - myPos.row
        colDiff = otherPos.col - myPos.col

        return -1 <= rowDiff <= 1 and -1 <= colDiff <= self._token.length

    def get_adjacent(self, grid):
        if self._adjacent is None:
            self._adjacent = defaultdict(int)
            tok = self._token
            neighbors = grid.get_neighbors(tok.position.row, tok.position.col, tok.length)

            for neighbor in filter(partial(GridItem.are_attached, self), neighbors):
                # NOTE: Adjacent ids are not attached
                if neighbor._token.type != Tokens.ID:
                    for key, value in neighbor.get_attached(grid).items():
                        # A vertex is only adjacent to itself if there is a loop
                        if key != self.get_key() or value > 1:
                            self._adjacent[key] += value

        return self._adjacent

    def get_vertex(self):
        return Vertex(self._token.value, self._token.position.row)

    def get_key(self):
        return self._token

class EdgeSegmentFactory:
    def __init__(self, mincon, maxcon, ports):
        assert(mincon <= len(ports) <= maxcon)

        self._mincon = mincon
        self._maxcon = maxcon
        self._ports = ports

    @property
    def mincon(self):
        return self._mincon

    @property
    def maxcon(self):
        return self._maxcon

    @property
    def grid(self):
        return self._grid

    def __call__(self, token):
        return EdgeSegmentItem(self, token)

class GraphCompiler:
    tokenizer = Tokenizer((
        (Tokens.ID, "[_a-zA-Z0-9]+"),
        (Tokens.SPACE, " +"),
        (Tokens.BSLASH, "\\\\"),
        (Tokens.FSLASH, "/"),
        (Tokens.LANGLE, "<"),
        (Tokens.RANGLE, ">"),
        (Tokens.TANGLE, "\\^"),
        (Tokens.PIPE, "\\|")))

    edgeFactories = {
            Tokens.ID: VertexItem,
            Tokens.SPACE: lambda *args: None,
            Tokens.BSLASH: EdgeSegmentFactory(2,2, set(((-1,-1), (1,1)))),
            Tokens.FSLASH: EdgeSegmentFactory(2,2, set(((-1,1), (1,-1)))),
            Tokens.LANGLE: EdgeSegmentFactory(2,2, set(((-1,1), (1,1)))),
            Tokens.RANGLE: EdgeSegmentFactory(2,2, set(((-1,-1), (1,-1)))),
            Tokens.TANGLE: EdgeSegmentFactory(2,2, set(((1,-1), (1,1)))),
            Tokens.PIPE: EdgeSegmentFactory(2,6,
                    set(((-1,-1), (-1,0), (-1,1), (1,-1), (1,0), (1,1))))
            }

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
        # 2. For each vertex:
        #    a. Process each adjacent edge segment (recursively).
        #    b. Mark the vertex as visited.
        # 3. If there unprocessed edge segments, throw an exception.

        # TODO: Do something about non-unique vertices

        grid, vertices, edgeSegments = self._get_grid(tokens)
        adj = [[0]*i for i in range(1, len(vertices)+1)]

        adjacencies = {}
        vertNums = {}
        for vNum, v in enumerate(vertices):
            vertNums[v.get_key()] = vNum
            adjacencies[v.get_key()] = v.get_adjacent(grid)

        for vert0, connections in adjacencies.items():
            for vert1, elem in connections.items():
                adjC, adjR = sorted((vertNums[vert0], vertNums[vert1]))
                adj[adjR][adjC] = elem

        # Check that all the edge segments were processed
        for segment in edgeSegments:
            segment.assert_processed()

        return (map(VertexItem.get_vertex, vertices), adj)

    def _get_grid(self, tokens):
        grid = AutoGrid()
        vertices = []
        edgeSegments = []

        # TODO: If this is slow, reverse tokens before inserting
        for t in tokens:
            gridItem = self.edgeFactories[t.type](t)

            if t.type == Tokens.ID:
                vertices.append(gridItem)
            elif t.type != Tokens.SPACE:
                edgeSegments.append(gridItem)

            grid.insert_item(t.position, t.length, gridItem)

        return grid, vertices, edgeSegments


def self_test():
    import os

    comp = GraphCompiler()

    tests = [
        "simpletree",
        "strayedge",
        "longname",
        "1cycle",
        "2cycle",
        "edgelooperror"
    ]

    for testPath in tests:
        teststr = open(os.path.join("tests", testPath + ".graph"), "r").read()
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



if __name__ == "__main__":
    self_test()
