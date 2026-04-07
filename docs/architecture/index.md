# Architecture Overview

!!! note "Work in progress"
    This section is being written. Detailed documentation is available in `Doc/Programmer/`
    and `Doc/Methods/` in the source tree, and as a
    [PDF](https://github.com/micmac-V2/MMVII/releases/download/MMVII_Documentation/Doc2007_a4.pdf).

## Codebase structure

```
MMVII/
├── src/              # C++ source code
│   ├── BundleAdjustment/
│   ├── PoseEstim/
│   ├── DenseMatch/
│   ├── Radiometry/
│   ├── PointCloud/
│   └── ...
├── MMVII-TestDir/    # Test data and scripts
├── Doc/              # Documentation sources (LaTeX, Markdown)
├── apib11/           # Python API bindings
└── Doxyfile          # Doxygen configuration
```

## Key design principles

- **Serialization-driven** — commands and parameters are defined via a serialization framework that also auto-generates help text and parameter validation
- **Symbolic differentiation** — analytical Jacobians via an internal symbolic differentiation engine
- **Manifold optimization** — optimization on Lie groups (SO3, SE3) for camera pose parametrization
- **Modular commands** — each photogrammetric step is an independent command, composable into pipelines

## Subsystems

| Subsystem | Description |
|-----------|-------------|
| [Programming Guide](programming-guide.md) | Coding conventions, internal APIs, how to add commands |
