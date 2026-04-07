# Developer Guide

Documentation for contributors and developers extending MMVII.

## Contents

| Topic | Description |
|-------|-------------|
| [Adding Commands](programming-guide.md) | How to register a new MMVII command, parameter declaration, naming conventions |
| [Serialization](serialization.md) | How objects describe, save, and load themselves across all formats |
| [Non-Linear Optimisation](nonlinear-optim.md) | Gauss-Newton solver, Schur complement, `cResolSysNonLinear` interface |
| [Symbolic Derivation](symbolic-derivation.md) | Automatic differentiation via DAGs and C++ code generation |
| [Image Classes](image-classes.md) | Image data structures, numerical types, filters |
| [Mapping Framework](mapping.md) | Abstract smooth mappings: projection, distortion, geodetic transforms |
| [Interpolators](interpolators.md) | Kernel-based image interpolation theory and classes |
| [Graph Library](graph.md) | Templated graph: vertices, edges, shortest path, MST, connected components |
| [Python API](python-api.md) | pybind11 bindings and how to expose new classes |

## Where to start

- To **add a new command**: read [Adding Commands](programming-guide.md)
- To **add a new cost function** to the optimiser: read [Symbolic Derivation](symbolic-derivation.md) then [Non-Linear Optimisation](nonlinear-optim.md)
- To **expose a C++ class to Python**: read [Python API](python-api.md)
- To **persist data to file**: read [Serialization](serialization.md)
