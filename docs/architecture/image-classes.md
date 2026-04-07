# Image Classes

MMVII is not an image processing library, but image manipulation is a non-negligible part
of the codebase (target detection, function tabulation, texture mapping, etc.).
This page describes the organisation of image classes.

!!! note "Terminology"
    MMVII uses *image* to mean what is now commonly called a *tensor*: an array of
    $S_1 \times S_2 \times \cdots \times S_d$ values. $d=2$ (2D images) is the most common case.

---

## Numerical types

All numerical types are defined in `MMVII_AllClassDeclare.h`:

| MMVII type | C++ equivalent | Size |
|------------|---------------|------|
| `tREAL4` | `float` | 4 bytes |
| `tREAL8` | `double` | 8 bytes |
| `tREAL16` | `long double` | 16 bytes |
| `tINT1` | `int8_t` | 1 byte |
| `tINT2` | `int16_t` | 2 bytes |
| `tINT4` | `int32_t` | 4 bytes |
| `tINT8` | `int64_t` | 8 bytes |
| `tU_INT1` | `uint8_t` | 1 byte |
| `tU_INT2` | `uint16_t` | 2 bytes |
| `tU_INT4` | `uint32_t` | 4 bytes |
| `tU_INT8` | `uint64_t` | 8 bytes |

Always use these typedefs rather than raw C++ types to ensure cross-platform consistency.

---

## Header files

### Generic images (any dimension)

| Header | Contents |
|--------|----------|
| `MMVII_Images.h` | Generic image classes (`cIm<Dim,Type>`), 1D and 3D variants |
| `MMVII_Image2D.h` | 2D-specific classes (most common case) |
| `MMVII_Ptxd.h` | Points, pixels (integer-coordinate points), bounding boxes — images inherit from boxes |
| `MMVII_Matrix.h` | Dense vectors and matrices — implemented as 1D/2D images |

### Filtering

| Header | Contents |
|--------|----------|
| `MMVII_Linear2DFiltering.h` | Gaussian filters, Gaussian pyramid (for SIFT-like multiscale) |
| `MMVII_NonLinear2DFiltering.h` | Non-linear filters |
| `MMVII_TplGradImFilter.h` | Fast gradient computation via tabulation (polar decomposition) |

### Feature extraction

| Header | Contents |
|--------|----------|
| `MMVII_ImageInfoExtract.h` | Fast local extremum extraction, connected components on binary images |
| `MMVII_ExtractLines.h` | Line extraction (Hough transform) |

### Specialised templates (header-only)

| Header | Contents |
|--------|----------|
| `MMVII_TplImage_PtsFromValue.h` | Extract a point with a given value — used for target sub-pixel detection |
| `MMVII_Tpl_Images.h` | Global operations independent of spatial layout: diff, sum, conversion, reduction |
| `MMVII_TplSymbImage.h` | Image differentiation for use in non-linear optimisation |

---

## Source files (`.cpp`)

| Folder | Contents |
|--------|----------|
| `ImagesBase/` | Image class definitions (`MMVII_Images.h`, `MMVII_Image2D.h`) |
| `ImagesFiltrLinear/` | Linear filtering implementation |
| `ImagesInfoExtract/` | Low-level object extraction (extrema, connected components) |

---

## Relationship to other subsystems

- **Points and boxes**: `MMVII_Ptxd.h` defines `cPtxd<Type, Dim>` (generic point) and `cPixBox<Dim>` (axis-aligned box). Images inherit from `cPixBox`, so any image can be used where a box is expected.
- **Matrices**: `cIm<1, T>` = vector, `cIm<2, T>` = matrix. `MMVII_Matrix.h` provides the dense linear algebra interface on top.
- **Optimisation**: `MMVII_TplSymbImage.h` enables images to participate in [non-linear optimisation](nonlinear-optim.md) — image pixel values become unknowns or observations.
- **Interpolators**: Image classes have methods accepting [interpolator](interpolators.md) objects for sub-pixel value computation.
