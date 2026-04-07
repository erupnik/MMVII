# Mapping Framework

## Purpose

A *mapping* in MMVII is any smooth function $F: \mathbb{R}^n \rightarrow \mathbb{R}^p$.
The mapping framework provides a unified interface for all such functions, covering:

- Camera projection $\pi: (x,y,z) \rightarrow (i,j)$ as $\mathbb{R}^3 \rightarrow \mathbb{R}^2$
- Extended projection with depth $\pi_d: (x,y,z) \leftrightarrow (i,j,d)$ as a bijection of $\mathbb{R}^3$
- Central perspective distortion as a bijection of $\mathbb{R}^2$
- Coordinate system transformations between geodetic frames as bijections of $\mathbb{R}^3$

---

## Services provided

Every mapping offers, at minimum, a method to evaluate $F(x)$.
Beyond that, the framework provides default implementations that derived classes
may override with more efficient alternatives:

| Service | Default implementation | Override when |
|---------|----------------------|---------------|
| Jacobian $\partial F / \partial x$ | Finite differences | Analytical derivative available |
| Inverse $F^{-1}(v)$ (square maps only) | Newton iteration | Closed-form inverse available |
| Approximate inverse mapping | Least-squares fit in a function basis | — |
| Interface for generated symbolic Jacobians | — | Using [code-generated derivatives](symbolic-derivation.md) |

---

## Base class — `cDataMapping<Type, DimIn, DimOut>`

Declared in `include/MMVII_Mappings.h`, defined in `src/Mappings/`.

Template parameters:

| Parameter | Meaning |
|-----------|---------|
| `Type` | Floating-point type (`tREAL4`, `tREAL8`, `tREAL16`); in practice always `tREAL8` |
| `DimIn` | Input space dimension |
| `DimOut` | Output space dimension |

### Core method — `Value` / `Values`

```cpp
// Single evaluation
virtual tVecOut Value(const tVecIn & aX) const;

// Batch evaluation (may exploit parallelism)
virtual tVecVecOut Values(const tVecVecIn & aVX) const;
```

The two methods have cross-default implementations (each calls the other), so a derived class
only needs to override one. If neither is overridden an infinite recursion is detected at runtime
in debug mode.

`Values` has two variants:
- User-provided output buffer
- Class-owned buffer (same buffer reused on each call — copy if you need to keep the result)

### Jacobian

```cpp
// Returns {value, Jacobian} as a pair
virtual std::pair<tVecOut, tMatJac> Jacobian(const tVecIn & aX) const;
```

Value and Jacobian are returned together because computing the Jacobian requires the value,
and the user almost always needs both simultaneously.

The default uses finite differences. Override with an analytical or
[symbolic derivative](symbolic-derivation.md) for efficiency.

### Inverse (square mappings, `DimIn == DimOut`)

```cpp
virtual tVecIn Inverse(const tVecOut & aV) const;
```

Default: Newton iteration using the Jacobian. Override with a closed-form inverse when available
(e.g. inverse distortion).

---

## Code location

| Path | Contents |
|------|----------|
| `include/MMVII_Mappings.h` | All mapping class declarations |
| `src/Mappings/` | Implementations (explicit instantiation for all standard `<Type, DimIn, DimOut>` combinations) |
