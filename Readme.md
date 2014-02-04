# Graph Compiler

Convert ASCII representations of graphs into usable data structures in Python or C.

## Examples

### ASCII Tree --> Vertices and an Adjacency Matrix

```
     R
    /|\
   A B C
  /  | |
 D   E F
 |      \
 G       H


-->

Vertices = 
Vertex(id='R', rank=0)
Vertex(id='A', rank=2)
Vertex(id='B', rank=2)
Vertex(id='C', rank=2)
Vertex(id='D', rank=4)
Vertex(id='E', rank=4)
Vertex(id='F', rank=4)
Vertex(id='G', rank=6)
Vertex(id='H', rank=6)

Adj = 
[0]
[1, 0]
[1, 0, 0]
[1, 0, 0, 0]
[0, 1, 0, 0, 0]
[0, 0, 1, 0, 0, 0]
[0, 0, 0, 1, 0, 0, 0]
[0, 0, 0, 0, 1, 0, 0, 0]
[0, 0, 0, 0, 0, 0, 1, 0, 0]

```

### Error Checking

```
     R
    /|\  
   A B C
  /  | |   |
 D   E F


-->

Stray edge segment '|' in graph at row 3, col 11.
```

### Meaningful Vertex Names

```
     R
    /|\  
   A B C
  /  | | 
 <    \ \
  \    E F  
   \    /
    \  /
Long_Name
 

-->

Vertices = 
Vertex(id='R', rank=0)
Vertex(id='A', rank=2)
Vertex(id='B', rank=2)
Vertex(id='C', rank=2)
Vertex(id='E', rank=5)
Vertex(id='F', rank=5)
Vertex(id='Long_Name', rank=8)

Adj = 
[0]
[1, 0]
[1, 0, 0]
[1, 0, 0, 0]
[0, 0, 1, 0, 0]
[0, 0, 0, 1, 0, 0]
[0, 1, 0, 0, 0, 1, 0]
```
### Loops and Multigraphs


```




       ^
      / \
     <   >
      \ /
       B

-->

Vertices = 
Vertex(id='B', rank=5)

Adj = 
[2]




       A
      / \  
     <   >
      \ / 
       B


-->

Vertices = 
Vertex(id='A', rank=1)
Vertex(id='B', rank=5)

Adj = 
[0]
[2, 0]
```

## Stay tuned for more
