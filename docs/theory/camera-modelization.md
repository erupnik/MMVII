# Modelization of Central Perspective Cameras

This page describes the mathematical model used in MMVII for central perspective cameras.
Almost all images encountered in practice — smartphone, reflex, aerial cameras — are acquired
by central perspective cameras. The exceptions are most satellite imagery and a few aerial sensors
(e.g. Leica ADS40).

The model is built up progressively: starting from the simplest physical model, then adding
lens distortion layer by layer, each term justified by physical reasoning.

---

## Camera Obscura: the basic model

The simplest possible camera is the **camera obscura**: a box with a pinhole. Light from a
scene point $P^c = (x^c, y^c, z^c)$ (in the camera's local frame) travels in a straight line
through the hole and hits the image plane at pixel $q = (i, j)$.

![Camera obscura: schema and a real object](images/CameraObscura.jpg)

Setting up coordinates with origin at the hole, axes $\vec{i}, \vec{j}$ in the image plane,
and $\vec{k}$ orthogonal to it, and calling $P^p$ the **principal point** and $F$ the **focal length**:

$$
i = P^p_x + F \frac{x^c}{z^c} \;\;;\;\; j = P^p_y + F \frac{y^c}{z^c}
$$

![Notation for the camera coordinate relation](images/Camera3D.jpg)

!!! note "Sign convention"
    MMVII places the image plane *in front of* the hole (the mathematically equivalent but
    non-physical convention). This flips a sign compared to the physical camera obscura but
    is universally adopted in photogrammetry and computer vision.

![Camera model: physically-based (left) vs. convention used in MMVII (right)](images/InvCamera.jpg)

**MMVII convention for image axes:** $i$ runs left-to-right, $j$ top-to-bottom (native image
format coordinates). This makes the camera frame *direct* ($\vec{k} = \vec{i} \wedge \vec{j}$),
with $\vec{k}$ pointing in the **viewing direction** of the camera.

![Camera frame and ground frame relationship](images/RepairCam.jpg)

### Compact notation

Define the canonical projection $\pi_0$ and the intrinsic mapping $\mathcal{I}_0$:

$$
\pi_0 \begin{pmatrix} x^c \\ y^c \\ z^c \end{pmatrix} = \begin{pmatrix} x^c/z^c \\ y^c/z^c \end{pmatrix}
\qquad
\mathcal{I}_0 \begin{pmatrix} u \\ v \end{pmatrix} = P^p + F \begin{pmatrix} u \\ v \end{pmatrix}
$$

Then the full projection from **world coordinates** $P$, given camera centre $C$ and rotation $R$:

$$
\boxed{q = \mathcal{I}_0\!\left(\pi_0\!\left({}^t\!R\,(P - C)\right)\right)}
$$

This equation is the foundation of the whole model. What changes in later sections is $\mathcal{I}_0$,
and eventually $\pi_0$, to account for real lenses.

---

## The central perspective hypothesis

Real cameras have complex lens systems, not a pinhole. MMVII (like all standard photogrammetric
software) adopts one key hypothesis that is maintained throughout:

> **All light rays producing a given image point $q$ pass through a single virtual point $C$.**

![All outgoing light bundles converge to a single centre $C$](images/CamPersp.jpg)

This is justified by the physical diaphragm which constrains light convergence. The only known
practical exceptions are macro-photogrammetry and underwater photogrammetry.

Under this hypothesis, lenses add a **2D image deformation** $D$ (the distortion) on top of
the ideal projection:

$$
\mathcal{I} = \mathcal{I}_0 \circ D \qquad ; \qquad D \approx \mathrm{Id}
$$

$$
\boxed{q = \mathcal{I}\!\left(\pi_0\!\left({}^t\!R\,(P - C)\right)\right)}
$$

$D$ operates on dimensionless coordinates (i.e. $x/z$ ratios) for numerical stability.

---

## Radial distortion

### Physical origin

A camera lens system has **cylindrical symmetry** around its optical axis $\mathcal{A}$:

- Each individual lens has radial symmetry around its own axis
- All lenses are mechanically aligned on their common optical axis
- The sensor plane is orthogonal to that axis

<div style="display:flex; gap:1rem; align-items:flex-end; margin:1rem 0">
  <figure style="margin:0; flex:2">
    <img src="images/Lenses.jpg" style="width:100%">
    <figcaption>Cross-section of a single lens</figcaption>
  </figure>
  <figure style="margin:0; flex:1">
    <img src="images/LensesCyl.jpg" style="width:100%">
    <figcaption>Modern camera lens assembly</figcaption>
  </figure>
</div>

This global cylindrical symmetry has a direct consequence: the distortion $D$ also has
**radial symmetry**. The proof follows from Snell-Descartes refraction laws applied to each
diopter in sequence — the azimuthal angle $\theta$ of any ray is preserved through each
refraction, so the image of a point at polar angle $(\rho, \theta)$ from $P^p$ can only
be displaced radially, to $(\rho', \theta)$.

![Notation for diopter crossing in the proof of radial symmetry](images/Radial-PhiOmegaZ.jpg)

### Radial distortion in the plane

In polar coordinates around the principal point, the distortion reduces to a scalar function
$D_r : \rho \mapsto \rho'$. In Cartesian coordinates:

![Notation for radial distortion in the image plane](images/RadialInThePlane.jpg)

### Polynomial model

Three properties of $D_r$ follow from the physics:

1. **Smooth** — the lens surfaces are $\mathcal{C}^\infty$, so $D_r$ is too
2. **Close to identity** — for standard optics (near Gaussian regime), $D_r \approx \mathrm{Id}$
3. **Odd** — $\rho$ and $\rho'$ are both odd functions of the incidence angle $\phi$

By Stone-Weierstrass, any smooth function on a closed bounded set can be approximated
arbitrarily closely by polynomials. Combined with the odd-function constraint:

$$
D_r(\rho) = \rho \,(1 + k_1 \rho^2 + k_2 \rho^4 + \cdots + k_n \rho^{2n})
$$

Note $k_0 = 1$ is fixed — the scale factor is already handled by the focal length $F$.

In Euclidean coordinates $(x, y)$ around the principal point:

$$
D\begin{pmatrix} x \\ y \end{pmatrix}
= \bigl(1 + k_1(x^2+y^2) + k_2(x^2+y^2)^2 + \cdots\bigr) \begin{pmatrix} x \\ y \end{pmatrix}
$$

### Convention notes

| Convention | MMVII | OpenCV / many CV tools |
|---|---|---|
| Order | $\mathcal{I}_0 \circ D$ (distort in normalised coords) | $D \circ \mathcal{I}_0$ (distort in pixel coords) |
| Coefficient names | $k_1, k_2, \ldots$ | $k_1, k_2, \ldots$ or $R_3, R_5, R_7$ (photogrammetry tradition) |
| Coefficient magnitude | $10^{-1}$ to $10^{-3}$ | $10^{-8}$ to $10^{-27}$ (scaled by $F^{2n}$) |

Both conventions span the same function space — conversion is straightforward ($K_1 = k_1/F^2$, etc.).
MMVII prefers dimensionless coefficients for numerical stability.

### How many terms?

There is no universal rule. Tradition: aerial photogrammetry uses $n=3$; computer vision often $n=1$ or $2$.
MMVII allows arbitrary $n$. With modern automatic tie-point extraction (tens of thousands of points),
using $n=5$ or even $n=10$ carries little risk of over-parametrisation — and modern consumer-grade
optics with complex multi-lens assemblies may genuinely require higher-degree models.

<div style="display:grid; grid-template-columns:1fr 1fr; gap:0.5rem; margin:1rem 0">
  <figure style="margin:0">
    <img src="images/Courbe-Pts.jpg" style="width:100%">
    <figcaption>Observations to fit</figcaption>
  </figure>
  <figure style="margin:0">
    <img src="images/CourbeGoodParam.jpg" style="width:100%">
    <figcaption>Good parametrization</figcaption>
  </figure>
  <figure style="margin:0">
    <img src="images/Courbe-UndeParam.jpg" style="width:100%">
    <figcaption>Under-parametrization</figcaption>
  </figure>
  <figure style="margin:0">
    <img src="images/CourbeOverParam.jpg" style="width:100%">
    <figcaption>Over-parametrization</figcaption>
  </figure>
</div>

**Extrapolation warning:** Whatever model is chosen, accuracy degrades sharply outside the
region covered by measurements. If no tie points exist in the image corners, distortion
estimates there are unreliable.

![Extrapolation artefacts outside the measurement region](images/CourbeExrapol.jpg)

---

## Decentring distortion

### Physical origin

Radial distortion alone would be sufficient if all lens axes were perfectly aligned. In practice
they are not. The **decentring (tangential) distortion** models the effect of slight misalignment
between lens groups.

### Derivation

Each lens group $k$ can be modelled as a radial distortion $D^k$ centred at $C^k$. The
global distortion is the composition $D = D^1 \circ D^2 \circ \cdots \circ D^n$.

Since all $D^k \approx \mathrm{Id}$ and all centres $C^k$ are close, a first-order Taylor
expansion gives:

$$
D^1 \circ D^2 \circ \cdots \circ D^n \approx \mathrm{Id} + \delta^1 + \delta^2 + \cdots + \delta^n
$$

Expanding each $\delta^k$ around a common reference centre $C_1$ and collecting terms,
the composition reduces to a **single radial distortion** plus a **decentring correction**
parametrised by just two scalars $\alpha, \beta$:

$$
D(p) \approx p + D_r(R_1)\,\vec{u}_1
+ \begin{pmatrix} \alpha(3x^2 + y^2) + 2\beta xy \\ 2\alpha xy + \beta(x^2 + 3y^2) \end{pmatrix}
$$

where $(x, y) = \vec{u}_1 = p - C_1$ and $R_1 = x^2 + y^2$.

![Relation between the $\mathrm{Dec}_x$ and $T_y$ decentring functions](images/DecxTy.jpg)

This result holds regardless of the number of misaligned lens groups — any combination reduces
to a single $(\alpha, \beta)$ pair at first order.

---

## Calibration ambiguity: poses and rotations

### The problem

The intrinsic mapping $\mathcal{I}$ and the camera rotation $R$ are not independently observable.
For any rotation $R'$:

$$
\mathcal{I}\,\pi_0\,{}^t\!R = (\mathcal{I} \circ H_{R'})\,\pi_0\,{}^t\!(R\,{}^t\!R')
$$

where $H_{R'}$ is the 2D homography induced by $R'$. This means:

> A camera with calibration $\mathcal{I}$ and pose $(R, C)$ has **exactly the same projection**
> as a camera with calibration $\mathcal{I} \circ H_{R'}$ and pose $(R\,{}^t\!R', C)$.

### Consequence for model design

If the chosen calibration model $\mathcal{S}^i$ is such that $\mathcal{I} \circ H_{R'} \in \mathcal{S}^i$
for some non-trivial $R'$, the optimisation problem has infinitely many solutions (or is badly conditioned
if $\mathcal{S}^h$ is merely tangent to $\mathcal{S}^i$ at the identity).

The safe condition is that the tangent spaces of $\mathcal{S}^h$ (the set of small rotations) and
$\mathcal{S}^i$ (the calibration model) be **orthogonal** at the identity, under the $L^2$ scalar product
on the sensor domain.

![Possible geometric relations between $\mathcal{S}^h$ and $\mathcal{S}^i$](images/TangentSpace.jpg)

This analysis guides MMVII's choice of which higher-order terms to include or exclude in its
calibration models, to avoid introducing redundant parameters that mix with the pose.

---

## Summary: the MMVII camera model

| Component | Symbol | Parameters |
|-----------|--------|------------|
| Camera centre | $C$ | 3 (world position) |
| Rotation | $R$ | 3 (SO(3)) |
| Principal point | $P^p$ | 2 |
| Focal length | $F$ | 1 |
| Radial distortion | $k_1, \ldots, k_n$ | $n$ (user-selected) |
| Decentring distortion | $\alpha, \beta$ | 2 |

Full projection pipeline:

$$
q = \underbrace{\mathcal{I}_0 \circ D}_{\mathcal{I}}\!\left(\underbrace{\pi_0}_{\text{central proj}}\!\left(\underbrace{{}^t\!R\,(P - C)}_{\text{world} \to \text{camera}}\right)\right)
$$

For fish-eye lenses, $\pi_0$ is replaced by a different projection (equidistant, equisolid, etc.) —
see the Fish-Eye Camera Models page.
