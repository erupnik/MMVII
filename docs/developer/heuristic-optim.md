# Heuristic Optimisation

MMVII provides derivative-free optimisation classes for low-dimensional problems. This page
describes their interfaces and is targeted at developers who need to optimise functions that
are not differentiable, not expressible as a sum of linear residuals, or that live on a
non-Euclidean manifold (sphere, rotation group, …).

!!! note "Prerequisites"
    Familiarity with the basic concepts of local optimisation is assumed.
    For differentiable problems, prefer the [Non-Linear Optimisation](nonlinear-optim.md)
    (Gauss-Newton) solver which is faster and scales to higher dimensions.

---

## Introduction

The classes described here minimise (or maximise) a scalar function $F$ using a heuristic
discrete-search strategy rather than gradient descent.

**Disadvantages compared to least-squares:**

- Slower per evaluation.
- Does not extend to high dimensions (currently limited to $D \leq 5$ in MMVII).

**Advantages:**

- Simpler to use: only $F$ itself needs to be provided, no Jacobian required.
- More general: $F$ need not be differentiable, nor a sum of linear observations.
- Guaranteed convergence to a *local* minimum within the search region.

---

## Discrete optimisation — `cOptimByStep`

### Mathematical formulation

![Illustration of restricted values computed](images/LocMin.jpg){ width="400" }

The classes in `MMVII_HeuristikOpt` find a local extremum of
$F : \mathbb{R}^D \rightarrow \mathbb{R}$ by successive discrete search at decreasing scale.

Define the neighbourhood set $N_d$ as the set of points $P \in \mathbb{Z}^D$ such that
$|P|_\infty \leq 1$ and $|P|_1 \leq d$.  For $D=2$, $N_1$ and $N_2$ correspond to the
familiar 4- and 8-connected neighbourhoods.

At a given scale/step $\Delta$ the algorithm is:

1. Let $P$ be the current point; define $N_{d,\Delta}(P) = \{P + \Delta Q : Q \in N_d\}$.
2. Compute $\overline{P} = \arg\min_{Q \in N_{d,\Delta}(P)} F(Q)$.
3. If $P = \overline{P}$, stop at this scale; otherwise set $P \leftarrow \overline{P}$ and repeat.

An important efficiency detail: at the first iteration all neighbours are evaluated; at
subsequent iterations the algorithm skips points already evaluated in the previous step.
The figure above illustrates this for $D=2$: starting from $P_0$, the algorithm evaluates
9 points $V_0$, then 3 new points $V_1$ around $P_1$, then 5 new points $V_2$ around $P_2$.

Once a local extremum is found at scale $\Delta$, the next stage uses step
$\Delta \leftarrow \rho \cdot \Delta$, continuing until $\Delta < \varepsilon$.

### Maintainer notes

The efficiency relies on a static dictionary $M$ precomputed for each direction, giving the
list of directions not yet explored when arriving from that direction.  For example in $D=2$
using Freeman codes, $M[0] = \{7,0,1\}$, $M[1] = \{7,0,1,2,3\}$, …

- `AllocNeighbourhood<D>(d)` — computes $N_d$.
- `VLNeighOptim<D>(d)` — computes the mapping $M$.

### API

**Constructor `cOptimByStep`** — four parameters:

| Parameter | Description |
|-----------|-------------|
| `F` | Function to minimise/maximise; a `cDataMapping<tREAL8,D,1>` |
| `bool` | `true` to minimise, `false` to maximise |
| `T` | Distance threshold from initial point (guardrail, rarely needed) |
| `d` | Neighbourhood order in $N_d$; default $d = D$ |

**Method `Optim`** — four parameters:

| Parameter | Description |
|-----------|-------------|
| Initial point | Starting point in $\mathbb{R}^D$ |
| $\Delta_0$ | Initial step size |
| $\varepsilon$ | Stop when $\Delta < \varepsilon$ |
| $\rho$ | Step reduction ratio: $\Delta_{k+1} = \rho \cdot \Delta_k$ |

### Example: symmetry-centre refinement

![cOptimByStep used to refine the symmetry centre of a coded target](images/OptIm.jpg){ width="400" }

MMVII uses `cOptimByStep<2>` to refine the position of symmetry centres in coded-target
detection.  Given an initial centre $C$ and approximate segment directions:

1. Select points $P_k$ near both segments (high sensitivity to symmetry criterion, low count).
2. For a candidate centre $C$, the symmetric of $P_k$ is $2C - P_k$.  Perfect symmetry requires
   $I(P_k) = I(2C - P_k)$ for all $k$.
3. Minimise:

$$
\mathrm{Sym}(C) = \sum_k \bigl|I(P_k) - I(2C - P_k)\bigr|
$$

using `cOptimByStep<2>` until $\Delta < \varepsilon$.

---

## Sampling spheres and projective spheres

### Overview

![Sampling the hypercube, sphere, and projective sphere for D=1](images/SamplSpher.jpg){ width="400" }

Before applying local optimisation on a bounded manifold $\mathcal{M}$
(e.g. $\mathbb{S}^N$, $\mathbb{RP}^N$, or their products), a good starting point must be found.
Because $\mathcal{M}$ is compact, a sufficiently dense sampling can get arbitrarily close to
the global minimum.  The classes below provide this sampling.

### Sampling the hypercube — `cSampleHyperCube`

Denote by $\mathrm{Cub}^N$ the hypercube $\{P \in \mathbb{R}^{N+1} : |P|_\infty = 1\}$.
The map $\pi_{\infty/2} : P \mapsto P/|P|_2$ is a continuous bijection from
$\mathrm{Cub}^N$ to $\mathbb{S}^N$, so sampling $\mathbb{S}^N$ reduces to sampling
$\mathrm{Cub}^N$, which has $2(N+1)$ faces each homeomorphic to $[-1,1]^N$.

For the *projective* hypercube (points identified with their antipodes), only the first
$N+1$ faces are sampled.

`cSampleHyperCube` is an internal class (returns `std::vector`, not `cPtxd`) used by
the sphere-sampling classes.

| Method | Description |
|--------|-------------|
| `cSampleHyperCube(int aDim, int aNbStep, bool isProj)` | Constructor; `aNbStep` = $f$ points per face dimension → $2 \cdot D \cdot f^{D-1}$ total samples |
| `int NbSamples() const` | Total number of sampled points |
| `void KthPt(std::vector<tREAL8>& aPts, int aK) const` | Coordinates of the $k$-th sample |
| `bool IsProj() const` | Whether the projective variant is used |

Enumerate all samples with a simple integer loop over `NbSamples()`, accessing each with `KthPt`.

### Sampling the sphere — `cSampleSphere3D`

Currently only $\mathbb{S}^2$ is implemented (generic $\mathbb{S}^N$ can be built from
`cSampleHyperCube` following the same pattern).

| Method | Description |
|--------|-------------|
| `cSampleSphere3D(int aNbStep, bool isProj)` | Constructor |
| `int NbSamples() const` | Number of samples |
| `cPt3dr KthPt(int aK) const` | $k$-th sample point on $\mathbb{S}^2$ |
| `bool IsProj() const` | Projective variant |
| `tREAL8 SqDist(const cPt3dr&, const cPt3dr&) const` | Squared distance; in the projective case returns $\min(|P_1-P_2|^2, |P_1+P_2|^2)$ |

### Sampling rotations — `cSampleQuat`

Rotations are sampled via quaternions using the homeomorphism $\mathbb{RP}^3 \cong SO(3)$,
sampling $\mathrm{Cub}^3$ with `cSampleHyperCube`.

| Method | Description |
|--------|-------------|
| `cSampleQuat(int aNbElem, bool ForRot)` | Constructor |
| `static cSampleQuat FromNbRot(int aNbRot, bool ForRot)` | Construct from desired number of rotations rather than step count |
| `size_t NbRot() const` | Number of sampled rotations |
| `cPt4dr KthQuat(int aK) const` | $k$-th quaternion |
| `tRotR KthRot(int aK) const` | $k$-th rotation (quaternion converted via `Quat2MatrRot`) |

---

## Global optimisation on manifolds

### Motivation

A common use case is computing the initial calibration of clinometers.  A single clinometer
calibration is a unit vector ($\mathbb{S}^2$); two orthogonal clinometers form a rotation
($\mathbb{RP}^3$); combining with an unknown vertical adds another factor.  This leads to
four cases:

| Configuration | Search space |
|---------------|-------------|
| 1 clinometer, vertical known | $\mathbb{S}^2$ |
| 2 orthogonal clinometers, vertical known | $\mathbb{RP}^3$ |
| 1 clinometer, vertical unknown | $\mathbb{S}^2 \times \mathbb{RP}^2$ |
| 2 orthogonal clinometers, vertical unknown | $\mathbb{RP}^3 \times \mathbb{RP}^2$ |

### Methodology

Optimising $F$ on manifold $\mathcal{M}$ combines the two strategies above:

1. **Global sampling** (Section [Sampling spheres](#sampling-spheres-and-projective-spheres)):
   extract candidate local extrema $E_1, E_2, \ldots$ from the discrete sampling of $\mathcal{M}$.
2. **Local refinement** (Section [cOptimByStep](#discrete-optimisation--coptimbystep)):
   refine each $E_k$ using discrete neighbourhood search in the tangent space
   $T_{\mathcal{M}}(E_k)$, a local diffeomorphism to $\mathbb{R}^N$.

**Multiple extrema**: when the initial sampling is too coarse, the greedy maximum may miss
the global optimum.  The algorithm therefore:

- Starts from the global maximum $E_1$.
- After finding each $E_k$, marks all samples within distance $\delta$ as reached
  (using the manifold metric $D_\mathcal{M}$).
- Repeats until the desired number of extrema is found.

### Manifold descriptor requirements

To use the template machinery, a class describing a manifold must provide:

| Requirement | Description |
|-------------|-------------|
| `typedef … tObj` | Type of points on the manifold |
| `static constexpr int DimTgtSp` | Dimension of the tangent space |
| `typedef … tDescrTgtSp` | Type holding the tangent-space diffeomorphism at a point |
| `int NbObjDisc() const` | Number of sampled points |
| `tObj KthObjDisc(size_t aK) const` | $k$-th sample |
| `tREAL8 SqDist(const tObj&, const tObj&) const` | Squared manifold distance (projective-aware) |
| `tREAL8 Density()` | Approximate sample density |
| `tDescrTgtSp* CreateTgtSpace(const tObj&) const` | Build tangent-space descriptor at a point |
| `void DeleteObjFromTgtSp(tDescrTgtSp*) const` | Free tangent-space descriptor |
| `tObj GetObjFromTgSpace(const tDescrTgtSp&, const tPtTgt&)` | Apply the tangent-space diffeomorphism |

The class `cSph3_OptimDisc` (sphere $\mathbb{S}^2$) and `cRot_OptimDisc` (rotations) are
the two built-in implementations.

### Cartesian product of manifolds — `cCartProduct_OptimDisc`

If `T1` and `T2` are manifold descriptors for $\mathcal{M}_1$ and $\mathcal{M}_2$,
`cCartProduct_OptimDisc<T1,T2>` is a valid descriptor for $\mathcal{M}_1 \times \mathcal{M}_2$.
The construction composes, so products of three or more manifolds can be built iteratively.

A convenience alias for pose space (translation + rotation):

```cpp
typedef cCartProduct_OptimDisc<cSph3_OptimDisc, cRot_OptimDisc> tPoseCart_OptimDisc;

// Factory:
inline tPoseCart_OptimDisc Pose_OptimDisc(int aNbTr, bool isSPhProj, int aNbRot);
// isSPhProj=true  → clinometer calibration (projective sphere)
// isSPhProj=false → pose estimation (ordinary sphere)
```

### User API — `cTplOptDisc_OnManifold`

Once a manifold descriptor is built, use `cTplOptDisc_OnManifold` to run the optimisation:

| Method | Description |
|--------|-------------|
| Constructor | Takes the manifold descriptor and the objective as a `cOptDiscScorer<tObj>` |
| `void ComputeSol(tREAL8 aDistNeigh, tREAL8 anEpsilon, int aNbTest)` | Run; `aDistNeigh` and `aNbTest` control multiple-extrema search |
| `GetSol()` | Access extrema after `ComputeSol` |
