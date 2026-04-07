# Graph Library

MMVII includes a lightweight, templated, header-only graph library.

---

## Overview

The three core objects are **vertices**, **edges**, and **graphs**.
All three are templated by attribute types, allowing the user to attach arbitrary data:

| Template parameter | Attached to | Name |
|-------------------|-------------|------|
| `AttrV` | Vertices | Vertex attribute |
| `AttrEOr` | Oriented edge (directional) | Oriented edge attribute |
| `AttrESym` | Symmetric edge (undirected) | Symmetric edge attribute |

Each edge has **two** oriented attributes (one per direction) plus one symmetric attribute.
This distinction allows, for example, storing a directed cost (e.g. flow) separately from
an undirected property (e.g. weight).

---

## Creating a graph

```cpp
#include "MMVII_Tpl_GraphStruct.h"

// Declare the graph type
using tMyGraph = cGraphDuality<MyVertexAttr, MyOrientedEdgeAttr, MySymEdgeAttr>;

// Step 1: create the graph
tMyGraph aGraph;

// Step 2: add vertices
auto v1 = aGraph.NewSom(MyVertexAttr{...});
auto v2 = aGraph.NewSom(MyVertexAttr{...});

// Step 3: add an edge between v1 and v2
aGraph.AddEdge(v1, v2,
    MyOrientedEdgeAttr{...},   // attribute for v1→v2
    MyOrientedEdgeAttr{...},   // attribute for v2→v1
    MySymEdgeAttr{...}         // shared symmetric attribute
);
```

---

## Algorithms

Declared in `include/MMVII_Tpl_GraphAlgo_SPCC.h`:

| Algorithm | Function | Description |
|-----------|----------|-------------|
| Shortest path | `ShortestPath(...)` | Dijkstra-style |
| Minimum spanning tree | `MinSpanTree(...)` | Kruskal/Prim |
| Connected components | `ConnectedComponents(...)` | Union-find |

---

## Code location

| Path | Contents |
|------|----------|
| `include/MMVII_Tpl_GraphStruct.h` | Graph, vertex, edge data structures |
| `include/MMVII_Tpl_GraphAlgo_SPCC.h` | Shortest path, MST, connected components |
| `src/Graphs/BenchGraph.cpp` | Extensive tests with detailed comments — **use as tutorial** |

!!! tip
    `BenchGraph.cpp` is densely commented and covers all major use cases.
    It is the recommended starting point before writing graph-based code in MMVII.
