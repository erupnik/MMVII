# Use Case: Image Development

This use case demonstrates how to create a **developed (unfolded) surface** from a stereoscopic
image acquisition of a deformed map. The dataset (`DevlopImage`) contains 74 images of a map
with smooth but significant surface deformation.

!!! info "Dataset"
    - 74 images, artificially downscaled by factor 4 to reduce repository size
    - Acquired under natural lighting (non-professional conditions); results are not representative of production quality
    - Each folder contains an `Info.txt` with all commands and commentary
    - Interactive steps (3D mask seizing) are pre-provided in `DataAux/` for reproducibility; the interactive command is commented out and replaced by a `cp` call

---

## Pipeline overview

```
MicMac V1: tie points → orientation → 3D mesh
        ↓
MMVII: import → mesh correction → unfolding → texture mapping → developed image
```

---

## Part 1 — MicMac V1 (orientation and dense matching)

### Tie points

Images have no EXIF metadata; a descriptor file provides the sensor information:

```
mm3d Tapioca MulScale ".*jpg" 400 1500 @SFS
```

`@SFS` (Scale Factor Search) is used because of low image contrast.

### Orientation and calibration

```
Tapas FraserBasic "P.*jpg" Out=AllRel
```

### Georeferencing

Seize the baselining transformation interactively (replaced here by `cp` from `DataAux`):

```bash
# Interactive (commented out for reproducibility):
# mm3d SaisieMasqQT AperiCloud_Basc.ply

cp DataAux/AperiCloud_Basc_* .
mm3d SBGlobBascule P.*jpg Ori-AllRel/ MesBasc-S2D.xml Basc PostPlan=Plan DistFS=10
```

### Dense point cloud and mesh

```bash
AperiCloud "P.*jpg" Ori-Basc/                         # sparse cloud for mask seizing
# mm3d SaisieMasqQT AperiCloud_Basc.ply               # interactive mask (replaced by cp)
cp DataAux/AperiCloud_Basc_polyg3d.xml .

mm3d C3DC BigMac P.*jpg Ori-Basc/ Masq3D=AperiCloud_Basc_selectionInfo.xml
TiPunch C3DC_BigMac.ply Filter=0                      # mesh from dense cloud
```

---

## Part 2 — MMVII processing

### Import orientation

```bash
MMVII OriConvV1V2 Ori-Basc/ Basc
```

The converted orientation is written to `MMVII-PhgrProj/Ori/Basc/`.

### Mesh correction and clipping

```bash
# Fix topological issues
MMVII MeshCheck C3DC_BigMac_mesh.ply Out=Correc-C3DC_BigMac_mesh.ply Bin=1

# Clip to the useful zone (Poisson reconstruction creates border artefacts)
MMVII MeshCloudClip Correc-C3DC_BigMac_mesh.ply AperiCloud_Basc_polyg3d.xml
```

### Mesh development (unfolding)

```bash
MMVII MeshDev Clip_Correc-C3DC_BigMac_mesh.ply
```

Two outputs are generated:

| File | Description |
|------|-------------|
| `Dev2D_Clip_Correc-C3DC_BigMac_mesh.ply` | The developed (2D) surface |
| `Dev3D_Clip_Correc-C3DC_BigMac_mesh.ply` | The corresponding subset of the 3D mesh |

!!! note
    The 2D mesh may contain fewer triangles than the 3D input when the surface has connectivity problems.

### Visibility and radiometry computation

```bash
MMVII MeshProjImage "P.*jpg" Dev3D_Clip_Correc-C3DC_BigMac_mesh.ply Basc DEV OutRadData=R0
```

- `DEV` — output data folder
- `OutRadData=R0` — compute and store radiometric equalisation data in folder `R0`

### Radiometric equalisation

Because images contain no EXIF metadata, aperture must be specified manually:

```bash
cp DataAux/CalcMTD.xml MMVII-PhgrProj/MetaData/Std/
# or equivalently:
MMVII EditCalcMTDI Std Aperture "Modif=[P.*.jpg,11,0]" Save=1
```

Create initial radiometric model (degree 2 per image):

```bash
MMVII RadiomCreateModel P.*jpg Init2 Basc DegIma=2
```

Compute equalisation:

```bash
MMVII RadiomComputeEqual P.*jpg R0 Init2 Equal Basc
```

### Texture mapping

```bash
MMVII MeshImageDevlp Dev2D_Clip_Correc-C3DC_BigMac_mesh.ply DEV InRadModel=Equal
```

Result: `MMVII-PhgrProj/MeshDev/DEV/DevIm.tif` — the developed surface with equalised radiometry.
