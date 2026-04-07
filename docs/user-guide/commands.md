# Command Reference

!!! note "Work in progress"
    This page is being populated. The full command reference is currently available in the
    [PDF documentation](https://github.com/micmac-V2/MMVII/releases/download/MMVII_Documentation/Doc2007_a4.pdf)
    and in `Doc/CommandReferences/` in the source tree.

## General syntax

```
MMVII <CommandName> [arguments...]
```

To list all available commands:
```bash
MMVII --help
```

To get help for a specific command:
```bash
MMVII <CommandName> --help
```

## Command categories

| Category | Description |
|----------|-------------|
| **Orientation** | Image pose estimation, relative and absolute orientation |
| **Bundle Adjustment** | Global photogrammetric block adjustment |
| **Dense Matching** | Multi-view stereo, depth map computation |
| **Point Cloud** | Filtering, decimation, format conversion |
| **Radiometry** | Radiometric calibration and correction |
| **Mesh** | 2D/3D mesh generation and processing |
| **Topometry** | Topo-photogrammetric processing |
| **Utility** | Format conversion, benchmarks, diagnostics |

## Running benchmarks

```bash
MMVII Bench 1    # basic correctness test
MMVII Bench 2    # extended tests
```
