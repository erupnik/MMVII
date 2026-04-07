# Interpolators

## Purpose

Given image values $v_k$ on an integer grid $\mathbb{Z}^n$, interpolation extends them to
a continuous function $F: \mathbb{R}^n \rightarrow \mathbb{R}$.

MMVII provides a library of kernel-based interpolators used throughout the codebase
for sub-pixel image access, image warping, and differentiation.

---

## Theoretical background

### Kernel representation

Under linearity and translation-invariance, any interpolation can be characterised by a
**kernel function** $K: \mathbb{R} \rightarrow \mathbb{R}$ such that:

$$
F(x) = \sum_{k} v_k \, K(x - k)
$$

Standard properties required of $K$:

| Property | Equation | Meaning |
|----------|----------|---------|
| Symmetry | $K(-x) = K(x)$ | No bias left/right |
| Partition of unity | $\sum_k K(x+k) = 1$ | Constant signal reproduced exactly |
| Interpolation | $K(0) = 1$, $K(k) = 0$ for $k \neq 0$ | Values preserved on grid |
| Compact support | $K(x) = 0$ for $|x| > r$ | Finite computation |

### 2D extension

2D interpolation is separable: the 2D kernel is the tensor product of two 1D kernels:
$$
K_{2D}(x, y) = K(x) \cdot K(y)
$$

### Interpolation vs approximation

- **Interpolation**: $F(k) = v_k$ exactly — the kernel satisfies the interpolation property above
- **Approximation**: $F(k) \approx v_k$ — useful for smoother reconstruction (e.g. B-splines)

---

## Available kernels

| Kernel | Support | Properties |
|--------|---------|------------|
| Nearest neighbour | $[-0.5, 0.5]$ | Discontinuous |
| Bilinear | $[-1, 1]$ | $C^0$, fast, used as default in many places |
| Bicubic (Keys) | $[-2, 2]$ | $C^1$, better quality, standard choice |
| Sinc (windowed) | $[-r, r]$ | Theoretically optimal; $r$ controls quality vs. cost |
| B-spline | $[-r, r]$ | Smooth approximation (not interpolation) |

---

## Using interpolators

### Header files

| Header | Contents |
|--------|----------|
| `MMVII_Interpolators.h` | Interpolator class declarations |
| `MMVII_Images.h`, `MMVII_Image2D.h` | Image methods that accept interpolator objects |
| `MMVII_TplSymbImage.h` | Image differentiation with interpolator support |

### Source files

| File | Contents |
|------|----------|
| `UtiMaths/Interpolators.cpp` | Interpolator class definitions |
| `ImagesBase/cIm2d_Interpolators.cpp` | 2D image interpolation methods |
| `Bench/BenchInterpolators.cpp` | Unit tests and correctness checks |
| `Bench/BenchTutoImageDef.cpp` | Image differentiation tests (bilinear + interpolators) |

### Example usage

```cpp
// Create a bicubic interpolator
cInterpolator1D * aInterp = new cCubicInterp(/*param*/);

// Interpolate image at sub-pixel position
double aVal = aImage.GetV(cPt2dr(3.7, 12.4), *aInterp);
```

---

## Interpolators in optimisation

When image values are used as observations in non-linear optimisation
(e.g. direct image alignment, photometric bundle adjustment), the interpolated
value must be differentiable with respect to the 2D position.

`MMVII_TplSymbImage.h` provides this: it supports the same kernel-based interpolation
but returns a `cFormula` (symbolic expression) instead of a `double`, enabling
the [symbolic derivation](symbolic-derivation.md) system to differentiate through
the interpolation.

!!! note
    Bilinear interpolation is differentiable almost everywhere ($C^0$ but piecewise-$C^1$).
    For smoother gradients, prefer bicubic or higher-order kernels when differentiating.
