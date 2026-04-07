# Topometry: Clinometer Calibration

This tutorial describes how to integrate **clinometer measurements** into a photogrammetric
bundle adjustment to calibrate the boresight matrices between a camera and its attached clinometers.

---

## Prerequisites

- A calibrated camera (internal parameters known)
- A set of images
- Clinometer measurements acquired simultaneously with the images
- GCP (ground control points) with known 3D coordinates and their 2D measurements in images

The relative orientation between camera and clinometers is assumed constant across all acquisitions.
The goal is to estimate the **boresight matrices** $B_1, B_2$ (rotation from camera frame to each
clinometer frame).

---

## Mathematical model

### Notation

| Symbol | Meaning |
|--------|---------|
| $R_C$ | Rotation of the camera in the absolute (world) frame |
| $B_k$ | Boresight matrix: rotation from camera frame to clinometer $k$ frame |
| $B_{k0}$ | Initial approximation of $B_k$ |
| $\theta_k$ | Measurement of clinometer $k$ |
| $\vec{v}_{loc}$ | Vertical direction in the local (world) frame |

For each clinometer, $(\vec{i}, \vec{j}, \vec{k})$ is the clinometer coordinate frame,
and $\theta$ is the angle between $\vec{i}$ and the vertical in the $(\vec{i}, \vec{j})$ plane.

### Equation 1 — Single clinometer constraint

The vertical in the clinometer frame is:
$$
\vec{v}_{clino} = B_1 R_C \vec{v}_{loc}
$$

Let $\Phi$ denote projection onto the $(\vec{i}, \vec{j})$ plane:
$$
\Phi \begin{pmatrix} v_i \\ v_j \\ v_k \end{pmatrix} = \begin{pmatrix} v_i \\ v_j \end{pmatrix}
$$

The clinometer measurement equation:
$$
\frac{\Phi(\vec{v}_{clino})}{\|\Phi(\vec{v}_{clino})\|} = \begin{pmatrix} \cos\theta_1 \\ \sin\theta_1 \end{pmatrix}
$$

### Equation 2 — Inter-clinometer stability constraint

The relative orientation between two clinometers is assumed constant over time.
This regularisation prevents divergence of the least-squares system:

$$
B_2 B_1^\intercal = B_{20} B_{10}^\intercal
$$

!!! note
    This equation is not physically exact but serves as a soft constraint to stabilise the optimisation.

---

## Pipeline

### Step 1 — Format the clinometer measurements file

One line per image, format: `image_name  clino_name  measurement  sigma  ...`

```
image1 clino1 +0.064786 0.00001 clino2 +0.014629 0.00002
image2 clino1 +0.064786 0.00001 clino2 +0.014629 0.00002
image3 clino1 +0.064786 0.00001 clino2 +0.014629 0.00002
```

### Step 2 — Import clinometer measurements

```bash
MMVII ImportMeasuresClino ClinoValue.txt "ImNASNASNASNAS" clinoMeasures [043_,.tif]
```

Parameters:

| Parameter | Meaning |
|-----------|---------|
| `ClinoValue.txt` | Input file with clinometer measurements |
| `"ImNASNASNASNAS"` | Column structure: `Im`=image name, `N`=clinometer name, `A`=measurement, `S`=sigma |
| `clinoMeasures` | Output directory (`MMVII-PhgrProj/MeasureClino/clinoMeasures`) |
| `[043_,.tif]` | Prefix/suffix added to image names to match MMVII naming convention |

### Step 3 — Initialise boresight matrices

```bash
MMVII ClinoInit clinoMeasures [1,0] BA_Br INIT_CLINO Rel12="i-kj"
```

Parameters:

| Parameter | Meaning |
|-----------|---------|
| `clinoMeasures` | Directory with imported measurements |
| `[1,0]` | Indices of clinometers to use |
| `BA_Br` | Input camera orientation |
| `INIT_CLINO` | Output directory for initial boresight approximations |
| `Rel12="i-kj"` | Approximate relative orientation: $\vec{i}_2=\vec{i}_1$, $\vec{j}_2=-\vec{k}_1$, $\vec{k}_2=\vec{j}_1$ |

Output: boresight matrices per clinometer + relative inter-clinometer orientation in `INIT_CLINO/`.

### Step 4 — Bundle adjustment with clinometer constraints

```bash
MMVII OriBundleAdj AllImClino.xml BA_Br BA_Clino \
      GCP2D=[[Clino_Filtered,0.1]] \
      GCP3D=[[Clino_Filtered,1]] \
      PPFzCal=.* \
      ClinoDirIn=INIT_CLINO \
      ClinoDirOut=CALIB_CLINO \
      InMeasureClino=clinoMeasures
```

Parameters:

| Parameter | Meaning |
|-----------|---------|
| `AllImClino.xml` | List of images |
| `BA_Br` | Input camera orientation |
| `BA_Clino` | Output camera orientation after adjustment |
| `GCP2D=[[Clino_Filtered,0.1]]` | 2D GCP measurements with weight 0.1 |
| `GCP3D=[[Clino_Filtered,1]]` | 3D GCP coordinates with weight 1 |
| `PPFzCal=.*` | Freeze internal camera calibration |
| `ClinoDirIn=INIT_CLINO` | Initial boresight matrices from `ClinoInit` |
| `ClinoDirOut=CALIB_CLINO` | Output calibrated boresight matrices |
| `InMeasureClino=clinoMeasures` | Directory with imported clinometer measurements |

---

## Output

The calibrated boresight matrices are written to `CALIB_CLINO/`, in the same format as `INIT_CLINO`.
They can be used directly for subsequent acquisitions with the same camera-clinometer setup.
