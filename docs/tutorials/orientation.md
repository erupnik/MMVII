# Orientation & Relative Poses

This tutorial covers the full image orientation pipeline: from projection formulas
to global pose estimation of a multi-image block.
The recommended progression for learning is to implement each step in Python
using the MMVII Python bindings (`apib11`).

---

## 1. Image projection formulas

### 1.1 Forward projection (world → image)

**Inputs:**

- An image with known pose and calibration (principal point $P^p$ + focal $F$, no distortion)
- A set of 3D points (e.g. 4 coded targets)
- 2D positions of a subset of those points for numerical validation

**Goal:** implement the projection function $q = \mathcal{I}_0(\pi_0({}^t\!R\,(P - C)))$

**Validation:** visualise projected points overlaid on the image; check numerically against known 2D positions.

---

### 1.2 Back-projection (image → ray)

**Inputs:**

- Multiple images with known pose and calibration
- 2D image coordinates of tie points

**Goal:** implement the inverse projection — given a 2D point, pose and calibration, compute the 3D ray direction (bundle).

**Validation:**

- Visualise multiple bundles in 3D
- Check the ray direction vector numerically against a reference
- Intersect bundles from two images and re-project onto a third image for 2D residual check

---

### 1.3 Bundle intersection (optional)

**Goal:** implement least-squares intersection of $N$ 3D lines.

The key identity: for a unit direction $\vec{u}$,

$$
\vec{v}^T\vec{v} + \vec{w}^T\vec{w} = I - \vec{u}^T\vec{u}
$$

allows the normal equations to be assembled directly without explicit orthonormal complement computation.

**Validation:** check recovered 3D position; test that the iterative method diverges for points outside the convex hull of the observations.

---

## 2. Pose estimation — 11/12 parameters

The 11-parameter (DLT) method is primarily didactic: it is rarely used in practice (space resection is preferred once calibration is known) but it can be implemented from scratch by students and gives insight into the structure of the photogrammetric equations.

**Inputs:**

- Images of coded targets
- 2D target positions (some missing, intentionally)
- 3D target coordinates
- MMVII binding to read and merge 2D/3D measurements

**Step 1 — Estimate the 12 parameters by least squares**

The projection equation is linear in the 12 entries of ${}^t\!R$ stacked with $\mathcal{I}_0$:

$$
\lambda \begin{pmatrix} i \\ j \\ 1 \end{pmatrix} = M \begin{pmatrix} X \\ Y \\ Z \\ 1 \end{pmatrix}
$$

With $\geq 6$ 2D/3D correspondences, $M$ is over-determined and solved by least squares.

Camera centre $C$ is then extracted from the null space of $M$.

**Step 2 — Extract physical parameters via RQ decomposition**

The $3 \times 3$ top-left submatrix of $M$ decomposes as $R \cdot K$ (RQ decomposition), recovering:

- Rotation $R$ (external calibration)
- $K$ = intrinsic matrix ($F$, $P^p$)

MMVII provides a binding for the RQ decomposition, or `numpy.linalg` can be used.

**Validation:** compare recovered camera centre and focal length against ground truth; visualise poses; test reprojection on control points not used in estimation.

!!! warning "Degenerate case"
    When all 3D points are coplanar, the 11P method is degenerate (focal length is unreliable). Always include at least 3 non-coplanar points.

---

## 3. Image formulas with distortion

### 3.1 Forward projection with distortion

**Goal:** implement the full image formula with the Fraser / 3-1-1 distortion model:
3 radial coefficients ($k_1, k_2, k_3$), 1 affine term, 2 decentring coefficients ($\alpha, \beta$).

$$
q = \mathcal{I}_0 \circ D \circ \pi_0 \circ {}^t\!R\,(P - C)
$$

**Inputs:** poses and calibration in separate files (MMVII bindings); 2D/3D correspondences; pre-computed distorted/undistorted point pairs for validation.

**Validation:** check distorted 2D positions against reference pairs; visualise projected points.

---

### 3.2 Distortion inversion

Two approaches:

| Method | Principle | When to use |
|--------|-----------|-------------|
| Iterative | $(Id + \delta)^{-1} \approx Id - \delta$, iterate | Simple to implement; sufficient for standard lenses |
| Least squares | Fit inverse polynomial to sampled pairs | More robust; handles larger distortions |

**Validation:**

- Verify $D(D^{-1}(x)) = x$ and $D^{-1}(D(x)) = x$ on test points
- Verify that the iterative method diverges for points far outside the calibrated image area

---

## 4. Relative pose estimation

### 4.1 Essential matrix

**Inputs:**

- Homologous points between two images (inliers only, on a 3D scene)
- Known camera calibration
- MMVII binding to extract relative pose from the essential matrix (or `numpy.linalg.svd`)

**Algorithm:**

1. Normalise image points with $K^{-1}$
2. Assemble and solve the $8 \times 9$ linear system for $E$ (SVD)
3. Enforce rank-2 constraint on $E$
4. Extract $(R, t)$ from $E$ (4 candidate solutions, disambiguated by cheirality)

**Validation:** ground truth on known image pair; residual check on remaining pairs.

---

### 4.2 Bundle adjustment on tie points

**Inputs:**

- 2 images with known calibration and approximate relative pose from 4.1
- A small set of precise tie points (~10, e.g. coded targets degraded to tie points)

**Algorithm:**

1. Compute initial 3D positions by bundle intersection (section 1.3)
2. Formulate the cost function with 5 DOF for one pose (fixing the other to remove gauge freedom)
3. Optimise with Python's `scipy.optimize`

**Validation:** final reprojection residuals; comparison against ground truth.

---

## 5. Space resection

Space resection is the most common method for adding a new image to an already-oriented block.
Given $\geq 3$ 2D/3D correspondences and known calibration, it recovers the pose by solving a
degree-4 polynomial system (P3P).

MMVII provides this as a binding; the pedagogical work is in composing the pipeline around it.

**Algorithm:**

1. Use section 3.2 to compute ray directions from 2D observations
2. Call MMVII P3P solver to recover depth triplets
3. Recover camera-frame 3D coordinates from depths and ray directions
4. Estimate rotation sending the camera-frame triangle to the world-frame triangle
5. Refine with all remaining 2D/3D pairs

### 5.1 Robust estimation with RANSAC

**Inputs:**

- Calibrated camera
- 2D/3D correspondences with ~50% outliers

**Algorithm:** RANSAC loop over triplets — for small datasets, enumerate all triplets; for large ones, sample randomly. Score by reprojection residual.

---

## 6. Global pose estimation

**Goal:** build a complete multi-image block incrementally.

**Inputs:**

- Camera calibration (from section 2 or 3.1)
- Image ordering (initial pair, then sequence with overlap graph)
- Multiple tie points with MMVII API for efficient querying

**Algorithm:**

1. Estimate relative pose of the first pair (section 4.1)
2. For each new image:
   a. Find tie points shared with already-oriented images
   b. Triangulate their 3D positions in the current reference frame
   c. Estimate the new pose with robust space resection (section 5.1)

**Validation:** visualise the reconstructed block (sparse point cloud + camera frusta).

!!! note "Drift"
    Incremental reconstruction accumulates errors. Bundle adjustment (section 4.2, extended to $N$ images) is needed to compensate — even with BA, some residual drift remains in long sequences.
