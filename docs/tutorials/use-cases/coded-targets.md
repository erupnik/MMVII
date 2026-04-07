# Use Case: Coded Target Processing

This use case demonstrates the full pipeline for **camera calibration and pose estimation
using coded targets**, on a dataset (`Circ-Code-Target`) acquired with a 2-camera rigid block
on a calibration panel.

!!! info "Dataset"
    - Calibration panel with ~234 targets: ~25% coded (automatic first pass), rest uncoded (completed in a second pass)
    - ~3 targets are off-plane to provide focal length constraint
    - Original: 4 cameras × 40 images × 6000×4000 px; reduced to 2 cameras × 20 images × 2000×1333 px
    - Camera: Nikon D5600, 24 mm (equiv. 35 mm) / actual 16 mm focal length
    - No EXIF metadata in images — must be provided via `CalcMTD.xml`
    - Camera group identifier: first 3 digits of image filename (e.g. `043_*`, `671_*`)

---

## Step 1 — Define the coding system

MMVII's coding system is flexible (number of bits, redundancy, run length, geometry).
Here we use the existing CERN 14-bit encoding.

Generate the encoding (list of valid bit-vectors):

```bash
MMVII CodedTargetGenerateEncoding CERN 14
```

Output: `CERN_Nbb14_Freq14_Hamm1_Run1000_1000_SpecEncoding.xml`

Generate the full target specification (geometry + radiometry):

```bash
MMVII CodedTargetGenerate CERN_Nbb14_Freq14_Hamm1_Run1000_1000_SpecEncoding.xml
```

Optional — generate a printable image of a specific target:

```bash
MMVII CodedTargetGenerate CERN_Nbb14_Freq14_Hamm1_Run1000_1000_SpecEncoding.xml PatIm=001
```

---

## Step 2 — Extract targets from images

Single image:

```bash
MMVII CodedTargetCircExtract 043_0005_Scaled.tif \
      CERN_Nbb14_Freq14_Hamm1_Run1000_1000_FullSpecif.xml DiamMin=8
```

`DiamMin=8` is needed because the downscaled images produce small targets.

Results are written to `MMVII-PhgrProj/ObjMesInstr/Std/`:

| File | Content |
|------|---------|
| `MesIm-043_0005_Scaled.tif.xml` | 2D target positions (used in standard processing) |
| `Attribute-MesIm-043_0005_Scaled.tif.xml` | Ellipse geometry (used for completion/refinement) |

Visualise extraction result:

```bash
MMVII CodedTargetCircExtract 043_0005_Scaled.tif \
      CERN_Nbb14_Freq14_Hamm1_Run1000_1000_FullSpecif.xml DiamMin=8 VisuEllipse=1
```

Process all images in parallel (limit to 2 cores, custom output folder):

```bash
MMVII CodedTargetCircExtract ".*_Scaled.tif" \
      CERN_Nbb14_Freq14_Hamm1_Run1000_1000_FullSpecif.xml \
      DiamMin=8 NbProc=2 OutObjMesInstr=Test
```

---

## Step 3 — Set up metadata

Images have no EXIF data. Copy the pre-provided metadata file:

```bash
cp Data-Aux/CalcMTD.xml MMVII-PhgrProj/MetaData/Std/
```

Or create it via commands:

```bash
MMVII EditCalcMTDI Std ModelCam ImTest=043_0005_Scaled.tif \
      Modif=[.*_Scaled.tif,"NIKON D5600",0] Save=1

MMVII EditCalcMTDI Std Focalmm ImTest=043_0005_Scaled.tif \
      Modif=[.*_Scaled.tif,24,0] Save=1

# AdditionalName distinguishes camera groups (043_* vs 671_*)
MMVII EditCalcMTDI Std AdditionalName ImTest=043_0005_Scaled.tif \
      Modif=["(.*)_.*_.*","\$1",0] Save=1
```

Copy 3D target coordinates to the correct folder:

```bash
cp Data-Aux/MesGCP-AICON-CERN-Pannel.xml MMVII-PhgrProj/ObjCoordWorld/Test/
```

---

## Step 4 — Pose and calibration estimation (11P method)

### Single image

```bash
MMVII OriPoseEstim11P 043_0005_Scaled.tif Test 11P
```

Results in `MMVII-PhgrProj/Ori/11P/`:

- `Calib-PerspCentral-043_0005_Scaled.tif.xml` — internal calibration
- `Ori-PerspCentral-043_0005_Scaled.tif.xml` — pose + reference to calibration

### All images

```bash
MMVII OriPoseEstim11P .*_Scaled.tif Test 11P
```

Results include per-image calibrations **and** per-camera group calibrations
(e.g. `CalibIntr_CamNIKON_D5600_Add043_Foc24.xml`), named to encode focal,
camera model, and group identifier.

### Handling degenerate images

Images where all visible targets are coplanar give unreliable focal estimates.
Identify outliers from the printed focal values, then build a filtered image set:

```bash
MMVII EditSet ImOk.xml = ".*Scaled.tif"
MMVII EditSet ImOk.xml -= 043_0031_Scaled.tif
MMVII EditSet ImOk.xml -= 671_0013_Scaled.tif
MMVII EditSet ImOk.xml -= 671_0025_Scaled.tif
MMVII EditSet ImOk.xml -= 671_0031_Scaled.tif
MMVII OriPoseEstim11P ImOk.xml Test 11P
```

### Estimating non-linear distortion

```bash
# Standard photogrammetric model (3 radial + 1 affine + 2 decentring):
MMVII OriPoseEstim11P ImOk.xml Test 11P DegDist=[3,1,1]

# No distortion:
MMVII OriPoseEstim11P ImOk.xml Test 11P DegDist=[0,0,0]

# Freeze a subset of distortion parameters:
MMVII OriPoseEstim11P ImOk.xml Test 11P DegDist=[3,1,1] PatFrozen="(b|p).*|K3"
```

---

## Step 5 — Refine with space resection + bundle adjustment

Once initial internal calibration is available, estimate all poses with the more stable
space resection method (calibration is shared, not re-estimated per image):

```bash
MMVII OriPoseEstimSpaceResection .*Scaled.tif Test 11P Resec
```

Now run full bundle adjustment with GCP weights:

```bash
MMVII OriBundleAdj ".*_Scaled.tif" Resec BA \
      GCP2D=[[Test,1]] GCP3D=[[Test,1]]
```

---

## Step 6 — Complete uncoded targets

With a reliable orientation, propagate observations to uncoded targets:

```bash
MMVII CodedTargetCompleteUncoded .*_Scaled.tif BA 1.0 \
      InObjMesInstr=Test InObjCoordWorld=Test
```

Results are stored in the `Completed` folder. Run a final bundle adjustment with the
extended measurement set:

```bash
MMVII OriBundleAdj ".*_Scaled.tif" BA BA2 \
      GCP2D=[[Completed,1]] GCP3D=[[Test,1]]
```
