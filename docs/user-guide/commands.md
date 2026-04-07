# Command Reference

## General syntax

```bash
MMVII <CommandName> [positional args...] [Name=Value ...]
MMVII <CommandName> HELP    # show full parameter list
```

Image sets can be specified as glob patterns (`".*jpg"`) or as XML set files (see [`EditSet`](#editset)).

---

## Orientation

Commands for estimating and manipulating camera poses and calibrations.

| Command | Description |
|---------|-------------|
| [`OriPoseEstim11P`](#oriposeestim11p) | Pose + calibration estimation from GCPs, uncalibrated case (DLT / 11-parameter method) |
| [`OriPoseEstimSpaceResection`](#oriposeestimspaceresection) | Pose estimation from GCPs with known calibration (space resection) |
| [`OriPoseEstimRel2Im`](#oriposeestimrel2im) | Relative orientation of 2 images (essential/fundamental matrix) |
| [`OriPoseEstimRel3Im`](#oriposeestimrel3im) | Relative orientation of 3 images (triplet) |
| [`OriPoseEstimRelAllPairs`](#oriposeestimrelallpairs) | Relative orientation for all pairs in a file |
| [`OriPoseEstimRelAllTriplets`](#oriposeestimrelalltriplets) | Relative orientation for all triplets in a file |
| [`OriPoseEstimRelPairsOf1Im`](#oriposeestimrelpairsof1im) | Relative orientation for all pairs involving one image |
| [`OriPoseEstimRelTripletssOf1Im`](#oriposeestimreltripletssof1im) | Relative orientation for all triplets involving one image |
| [`OriBundleAdj`](#oribundleadj) | Bundle adjustment (images + GCPs + topo + clino constraints) |
| [`HierarchicalSfm`](#hierarchicalsfm) | Global orientation from a graph of relative motions |
| [`OriCreateCalib`](#oricreatecalib) | Create an initial internal calibration |
| [`OriChSysCo`](#orichsysco) | Change coordinate system of an orientation |
| [`OriParametrizeSensor`](#oriparametrizesensor) | Import an external sensor parametrisation |
| [`OriPoseSelecAllPAir`](#oriposeselecallpair) | Select image pairs using different heuristics |
| [`OriPoseEstimCheckGCPDist`](#oriposeestimcheckgcpdist) | Check GCP distribution for pose estimation |

### OriPoseEstim11P

Estimates pose and internal calibration simultaneously from 2D/3D GCP correspondences using the 11-parameter (DLT) method. The camera matrix $M$ is solved by least squares; physical parameters ($R$, $C$, $K$) are extracted by RQ decomposition.

```bash
MMVII OriPoseEstim11P <Images> <GCPDir> <OutOri> [DegDist=[r,a,d]] [DoMedianCalib=bool] [PatFrozen=regex]
```

Key options:

| Option | Description |
|--------|-------------|
| `DegDist=[r,a,d]` | Distortion model: `r` radial coefficients, `a` affine, `d` decentring. Default `[0,0,0]` |
| `DoMedianCalib` | Compute a median calibration across all images (default true for multi-image runs) |
| `PatFrozen` | Regex pattern of distortion parameters to freeze during estimation |

!!! warning "Degenerate case"
    When all 3D points are coplanar, focal length estimation is unreliable. Use `EditSet` to exclude such images.

### OriPoseEstimSpaceResection

Estimates pose from 2D/3D correspondences with a **fixed** internal calibration. More robust than 11P for already-calibrated cameras. Solves the P3P system (degree-4 polynomial).

```bash
MMVII OriPoseEstimSpaceResection <Images> <GCPDir> <InOri> <OutOri>
```

### OriBundleAdj

Full photogrammetric bundle adjustment. Jointly optimises camera poses, internal calibrations, and 3D point positions. Supports GCPs, tie points, topometric observations, and clinometer constraints.

```bash
MMVII OriBundleAdj <Images> <InOri> <OutOri> \
      [GCP2D=[[Dir,Weight],...]] \
      [GCP3D=[[Dir,Weight],...]] \
      [PPFzCal=regex] \
      [TopoFile=file] \
      [ClinoDirIn=dir] [ClinoDirOut=dir] \
      [InMeasureClino=dir]
```

Key options:

| Option | Description |
|--------|-------------|
| `GCP2D=[[Dir,w]]` | 2D GCP measurement directory + weight |
| `GCP3D=[[Dir,w]]` | 3D GCP coordinate directory + weight |
| `PPFzCal=.*` | Freeze internal calibration (regex on calibration names) |
| `TopoFile` | Topometric OBS file for topo constraints |
| `ClinoDirIn/Out` | Input/output clinometer boresight matrices |

### HierarchicalSfm

Constructs a globally consistent orientation from a graph of pairwise relative motions. Alternative to incremental SfM for large blocks.

```bash
MMVII HierarchicalSfm <Images> <RelOri> <OutOri>
```

---

## Coded Targets

Commands for generating, detecting, and completing coded and uncoded circular targets.

| Command | Description |
|---------|-------------|
| [`CodedTargetGenerateEncoding`](#codedtargetgenerateencoding) | Generate a bit-vector encoding specification |
| [`CodedTargetGenerate`](#codedtargetgenerate) | Generate full target specification (geometry + radiometry) |
| [`CodedTargetCircExtract`](#codedtargetcircextract) | Detect coded targets in images |
| [`CodedTargetCompleteUncoded`](#codedtargetcompleteuncoded) | Propagate detection to uncoded targets using known orientation |
| [`CodedTargetRefineCirc`](#codedtargetrefinecircx) | Refine target detection using 3D-predicted shape |
| [`CodedTargetCheckBoardExtract`](#codedtargetcheckboardextract) | Extract checkerboard coded targets |
| [`CodedTargetSimul`](#codedtargetsinul) | Simulate images of coded targets with ground truth |

### CodedTargetGenerateEncoding

Generates the list of valid bit-vectors for a given coding system.

```bash
MMVII CodedTargetGenerateEncoding <System> <NbBits>
# Example:
MMVII CodedTargetGenerateEncoding CERN 14
```

Output: `<System>_Nbb<N>_..._SpecEncoding.xml`

### CodedTargetGenerate

Generates the full target specification combining encoding with geometric and radiometric parameters.

```bash
MMVII CodedTargetGenerate <SpecEncoding.xml> [PatIm=NNN]
```

`PatIm=NNN` generates a printable image of target number NNN.

### CodedTargetCircExtract

Detects coded circular targets in images. Results are written to `MMVII-PhgrProj/ObjMesInstr/<OutDir>/`.

```bash
MMVII CodedTargetCircExtract <Images> <FullSpecif.xml> \
      [DiamMin=N] [NbProc=N] [VisuEllipse=bool] [OutObjMesInstr=Dir]
```

| Option | Description |
|--------|-------------|
| `DiamMin` | Minimum target diameter in pixels (needed for downscaled images) |
| `NbProc` | Number of parallel processes |
| `VisuEllipse` | Generate visualisation image with extracted ellipses |

### CodedTargetCompleteUncoded

Uses a known orientation to identify and validate uncoded targets (second pass after coded targets are matched).

```bash
MMVII CodedTargetCompleteUncoded <Images> <Ori> <Scale> \
      [InObjMesInstr=Dir] [InObjCoordWorld=Dir]
```

---

## Dense Matching

Commands for computing dense depth maps and disparity fields.

| Command | Description |
|---------|-------------|
| `DenseMatchEpipGen` | Generic epipolar dense matching |
| `DenseMatchEpipEval` | Evaluate dense matching quality against a reference |
| `DM01DensifyRefMatch` | Densify a sparse (e.g. LIDAR) reference map with or without images |
| `DM0BisTestHypStep` | Compute statistics to fix hidden-part/step-parallax relation |
| `DM0FormatTD_MDLB` | Format Middlebury training data to MMVII format |
| `DM0FormatTD_WT` | Format Wu-Teng training data to MMVII format |
| `DM1ExtractVecLearn` | Extract ground-truth vectors for dense matching learning |
| `DM2CalcHistoCarac` | Compute and save 1D histograms of matching characteristics |
| `DM3CalcHistoNDim` | Compute and save N-dimensional histograms |
| `DM4FillCubeCost` | Fill a cost cube with matching costs |
| `DM4MatchMultipleOrtho` | Compute similarity of overlapping ortho images |
| `DM5StatMatch` | Evaluate dense matching with a reference |

---

## Mesh

Commands for processing, developing, and texturing 3D meshes.

| Command | Description |
|---------|-------------|
| [`MeshCheck`](#meshcheck) | Check and optionally correct topological errors in a mesh |
| [`MeshCloudClip`](#meshcloudclip) | Clip a mesh to a 3D region |
| [`MeshDev`](#meshdev) | Compute planar development (unfolding) of a 3D mesh |
| [`MeshDevGen`](#meshdevgen) | Generate a synthetic developable mesh for testing |
| [`MeshProjImage`](#meshprojimage) | Assign best images to triangles and compute radiometric data |
| [`MeshImageDevlp`](#meshimagedevlp) | Generate the developed (textured) 2D image |

### MeshCheck

Detects and optionally corrects topological problems in meshes generated by Poisson reconstruction (e.g. duplicate vertices within a triangle, non-orientable surface).

```bash
MMVII MeshCheck <Mesh.ply> [Out=Correc.ply] [Bin=bool] [Correct=bool] [Do2DC=bool]
```

### MeshCloudClip

Clips a mesh to a 3D region of interest, removing the border artefacts produced by Poisson reconstruction.

```bash
MMVII MeshCloudClip <Mesh.ply> <Region3D.xml> [Out=Clipped.ply] [Bin=bool]
```

### MeshDev

Computes the 2D planar development of a 3D mesh by minimising isometric deformation energy. For each triangle, a local perfect 2D development is computed; the global optimisation finds the set of 2D positions and per-triangle rotations that best satisfy all local constraints simultaneously.

```bash
MMVII MeshDev <Mesh.ply> [Out=Dev.ply] [WDistE=0] [WRot=1] [NbCByS=3] [NbIE=N]
```

| Option | Description |
|--------|-------------|
| `WDistE` | Weight on edge distance constraint |
| `WRot` | Weight on triangle rotation constraint (default 1, generally preferred) |
| `NbCByS` | Number of compensation steps per iteration |

Output: two meshes — `Dev2D_*.ply` (2D developed surface) and `Dev3D_*.ply` (corresponding 3D subset).

### MeshProjImage

For each triangle in a mesh, determines which image provides the best resolution and visibility (via Z-buffer). Optionally computes tie-point sampling for radiometric equalisation.

```bash
MMVII MeshProjImage <Images> <Mesh3D.ply> <Ori> <OutDir> \
      [OutRad=RadDir] [ResZBuf=3] [DoIm=bool]
```

### MeshImageDevlp

Produces the final developed image by texture-mapping each triangle with its best image, optionally applying radiometric equalisation.

```bash
MMVII MeshImageDevlp <Dev2D.ply> <MeshDevDir> [InRad=RadDir]
```

---

## Point Cloud

Commands for importing, processing, and simulating point clouds in MMVII's internal `.dmp` format.

| Command | Description |
|---------|-------------|
| [`ImportTxtCloud`](#importtxtcloud) | Import a text/PLY point cloud into MMVII format |
| [`CloudMMVIIClip`](#cloudmmviiclip) | Clip a cloud to a relative bounding box |
| [`CloudMMVII2Ply`](#cloudmmvii2ply) | Export MMVII cloud to standard PLY format |
| [`CloudMMVIIColorate`](#cloudmmviicolorate) | Compute illumination colours for each point |
| [`CloudMMVIIEdit`](#cloudmmviiedit) | Inspect or edit a cloud file |
| [`CloudMMVII_GT_EpipOrthoC`](#cloudmmvii_gt_epiporthoC) | Generate orthographic epipolar image pairs with ground-truth disparity |
| [`CloudMMVII_GT_MultiView`](#cloudmmvii_gt_multiview) | Generate multi-view perspective images with ground-truth from a cloud |
| [`CloudMMVIISimulSin`](#cloudmmviiSimulSin) | Generate a simulated sine-wave cloud |

### ImportTxtCloud

Imports a PLY or similar text point cloud into MMVII's internal binary format. Supports offset handling for large geographic coordinates.

```bash
MMVII ImportTxtCloud <file.ply> "XYZBla" [NumL0=N] [OffsetIsP0=bool] [Bytes8=bool]
```

| Option | Description |
|--------|-------------|
| `"XYZBla"` | Column format: `X`,`Y`,`Z` = read coordinate; other letters = skip |
| `NumL0` | Number of header lines to skip |
| `OffsetIsP0` | Subtract first point as offset (needed for geographic coordinates) |
| `Bytes8` | Coordinates stored as 8-byte doubles (default) or 4-byte floats |

### CloudMMVIIClip

```bash
MMVII CloudMMVIIClip <file.dmp> [x0,y0,x1,y1]   # relative box in [0,1]
```

### CloudMMVII2Ply

```bash
MMVII CloudMMVII2Ply <file.dmp>
```

### CloudMMVIIColorate

Computes simulated illumination colours for each point (used before image generation). Models sky as a uniform hemisphere and optionally a directional sun source.

```bash
MMVII CloudMMVIIColorate <file.dmp> [NbSampS=N] [Sun=[T,P,W]]
```

`Sun=[T,P,W]`: direction given by $\theta = T\frac{\pi}{2}$, $\phi = \frac{\pi}{2} + P$; $W$ is sun weight relative to sky.

---

## Radiometry

| Command | Description |
|---------|-------------|
| [`RadiomCreateModel`](#radiomcreatemodel) | Create an initial (neutral) radiometric model |
| [`RadiomComputeEqual`](#radiomcomputeequal) | Estimate radiometric equalisation model |

### RadiomCreateModel

Creates the initial radiometric model structure before equalisation.

```bash
MMVII RadiomCreateModel <Images> <ModelName> <Ori> [DegIma=N]
```

`DegIma`: polynomial degree per image (e.g. `2` = quadratic vignetting model).

### RadiomComputeEqual

Estimates the equalisation model from radiometric tie points computed by `MeshProjImage`.

```bash
MMVII RadiomComputeEqual <Images> <RadData> <InitModel> <EqualModel> <Ori>
```

---

## Topography & Survey

Commands for integrating topometric and inclinometer measurements.

| Command | Description |
|---------|-------------|
| [`TopoAdj`](#topoadj) | Standalone topo adjustment (no photogrammetry) |
| [`ImportOBS`](#importobs) | Import OBS topometric measurement file |
| [`ClinoInit`](#clinoinit) | Initialise boresight matrices between camera and clinometers |
| [`ImportMeasuresClino`](#importmeasuresclino) | Import raw clinometer measurements to MMVII format |
| [`BlockCamInit`](#blockcaminit) | Compute initial calibration of a rigid camera block |
| [`BlockInstrEdit`](#blockinstreditEdit) | Create/edit a block of instruments |
| [`BlockInstrInitCam`](#blockinstreditinitcam) | Initialise camera poses within an instrument block |
| [`BlockInstrInitClino`](#blockinstreditinitclino) | Initialise clinometer poses within an instrument block |
| [`BlockInstrReport`](#blockinstreditreport) | Report on instrument block vs. data |
| [`ReportClino`](#reportclino) | Report on clinometer calibration and measurements |

### TopoAdj

Standalone topometric adjustment using OBS files. Supports distances, horizontal angles, zenithal angles, and direct Euclidean vector observations. Can also be run jointly with photogrammetric data via `OriBundleAdj TopoFile=...`.

```bash
MMVII TopoAdj <ObsDir> <OutOri>
```

Measurement types in OBS files (Comp3D format):

| Code | Type | Unit |
|------|------|------|
| 1 | Distance | m |
| 2 | Horizontal angle | gon |
| 3 | Zenithal angle | gon |
| 4 | Direct Euclidean vector | m |

### ClinoInit

Computes initial boresight matrices between camera and clinometers from approximate orientation.

```bash
MMVII ClinoInit <ClinoMeasDir> [idx1,idx2] <Ori> <OutDir> [Rel12=expr]
```

---

## Coordinate Systems

| Command | Description |
|---------|-------------|
| [`SysCoCreateRTL`](#syscocreaterlT) | Create a local tangent frame (RTL) from camera positions |
| [`SysCoCreateAlias`](#syscocreatealias) | Save a coordinate system definition with a short name |
| [`OriChSysCo`](#orichsysco-1) | Transform an orientation from one SysCo to another |
| [`GCPChSysCo`](#gcpchsysco) | Transform GCP coordinates from one SysCo to another |
| [`TestProj`](#testproj) | Test a PROJ transformation and diagnose installation |

Supported SysCo types:

| Type | Description |
|------|-------------|
| `Local` | Arbitrary Euclidean frame, no georeferencing |
| `GeoC` | Geocentric (ECEF) coordinates |
| `RTL` | Local tangent frame: Z normal to ellipsoid, X east |
| `LEuc` | Local Euclidean with affine transform to geocentric |
| `Proj` | Any system supported by the PROJ library (e.g. `EPSG:4326`, `IGNF:LAMB93`) |

SysCo definitions can be:

```bash
SysCo=L93                          # named alias in MMVII-RessourceDir/SysCo/
SysCo=IGNF:LAMB93                  # PROJ string
SysCo=RTL*657700*6860700*0*IGNF:LAMB93   # RTL at given origin
SysCo=LocalPanel                   # unnamed local frame
SysCo=GeoC                         # geocentric
```

### SysCoCreateRTL

Creates a local tangent RTL frame from the average camera position (or a fixed point) and saves it to `MMVII-PhgrProj/SysCo/`.

```bash
MMVII SysCoCreateRTL <Ori> <Name> [InSysCo=def]
```

### TestProj

Tests a coordinate transformation between two SysCo definitions and diagnoses PROJ installation (missing grid files, etc.).

```bash
MMVII TestProj <SysCoIn> <SysCoOut> [TestPoint=[X,Y,Z]]
```

---

## Import / Export / Convert

| Command | Description |
|---------|-------------|
| `ImportGCP` | Import GCP file to MMVII format |
| `ImportMesImGCP` | Import image point measurements for GCPs |
| `ImportOri` | Import orientation file to MMVII format |
| `ImportAiconCalib` | Import Aicon camera calibration |
| `ImportInitExtSens` | Import initial external sensor (e.g. RPC) — assumes WGS84 input |
| `ImportLine` | Import extracted line segments |
| `ImportM32` | Import 3D/2D correspondences |
| `ImportTiePMul` | Import multiple-image tie points |
| `ImportTripletV1` | Import triplets from MicMac V1 format |
| `ImportTxtCloud` | Import text/PLY point cloud (see [Point Cloud](#point-cloud)) |
| `ImportStaticScan` | Import static LIDAR scan in instrument raster geometry |
| `ImportORGI` | Import ORGI-format data |
| `ImportOBS` | Import OBS topometric measurement file |
| `ExportUndistMesIm` | Export image measurements corrected for distortion |
| `V1OriConv` | Convert MicMac V1 orientation to MMVII format |
| `V1ConvertGCPIm` | Convert V1 image and ground measurements to V2 format |
| `V2ImportCalib` | Import a calibration from another MMVII project |
| `MMV2_MesIm_2_MMV1` | Export image measurements from MMVII to MicMac V1 format |
| `GCPAbsOri` | Compute absolute orientation via 3D similarity from GCPs |
| `MergeMesImGCP` | Merge multiple GCP image measurement files |
| `TiePConvert` | Convert tie points between formats |
| `TieP2PMul` | Convert tie points from by-pair to multiple format |

---

## Reports

| Command | Description |
|---------|-------------|
| `ReportGCP` | GCP reprojection residuals |
| `ReportTieP` | Tie point reprojection residuals |
| `ReportMesIm` | Image measurements vs. a reference |
| `ReportPoseCmp` | Pose comparison between two orientations |
| `ReportClino` | Clinometer calibration and measurement residuals |
| `ReportBlock` | Measurements for a rigid camera block |
| `ReportSegIm` | Segment image comparison |

---

## Editing & Utilities

| Command | Description |
|---------|-------------|
| [`EditSet`](#editset) | Create and edit sets of image files |
| [`EditRel`](#editrel) | Create and edit sets of image pairs |
| [`EditCalcMTDI`](#editcalcmtdi) | Create/edit image metadata (camera model, focal, etc.) |
| `ExifData` | Display EXIF metadata from an image file |
| `ImageScale_Std` | Downscale images (Gauss filter + integer decimation) |
| `ImageScale_Basic` | Downscale images (basic, for backward compatibility) |
| `ImageStack` | Stack a series of images |
| `ImageCalcDisc` | Compute discontinuity values in images |
| `PseudoIntersect` | Convert 2D image points to 3D coordinates |
| `DeplStack` | Stack multi-date displacement series |
| `UtiRename` | Rename files using regex and arithmetic |
| `UtiDicoRename` | Build a renaming dictionary from a file |
| `MediaCat` | Concatenate media files (interface to ffmpeg) |
| `MediaReduceVideo` | Reduce video file size |

### EditSet

Creates and manipulates named sets of image files, stored as XML. Supports adding patterns, subtracting individual files, and combining sets.

```bash
MMVII EditSet ImOk.xml = ".*jpg"       # create from pattern
MMVII EditSet ImOk.xml -= bad.jpg      # remove one file
MMVII EditSet ImOk.xml += extra.jpg    # add one file
```

Use the resulting XML file wherever a pattern is expected in other commands.

### EditCalcMTDI

Creates or modifies the `CalcMTD.xml` metadata file used when images lack EXIF data.

```bash
MMVII EditCalcMTDI Std ModelCam ImTest=img.tif Modif=[pattern,"CameraModel",0] Save=1
MMVII EditCalcMTDI Std Focalmm  ImTest=img.tif Modif=[pattern,24,0] Save=1
MMVII EditCalcMTDI Std Aperture ImTest=img.tif Modif=[pattern,11,0] Save=1
MMVII EditCalcMTDI Std AdditionalName ImTest=img.tif Modif=["(.*)_.*_.*","\$1",0] Save=1
```

`AdditionalName` is used to distinguish groups of images from different camera instances with the same model and focal length.

---

## Simulation & Testing

| Command | Description |
|---------|-------------|
| `Bench` | Run MMVII self-verification tests |
| `SimulDispl` | Generate smooth displacement fields and deformed images |
| `SimulImageSphere` | Simulate images of spheres with perspective and distortion |
| `SimulOriPerturbRandom` | Randomly perturb an orientation (for simulation experiments) |
| `CloudMMVII_GT_EpipOrthoC` | Generate epipolar ortho image pairs + ground-truth disparity from point cloud |
| `CloudMMVII_GT_MultiView` | Generate perspective multi-view images + ground truth from point cloud |
| `CodedTargetSimul` | Simulate images of coded targets with known ground truth |

### Bench

```bash
MMVII Bench 1   # basic correctness test
MMVII Bench 2   # extended tests
```

The test passes if execution does **not** end with a `Level=[UserEr:...]` block.

---

## Internal / Developer Commands

These commands are primarily for internal development and testing. They are documented here for completeness.

| Command | Description |
|---------|-------------|
| `GenCodeSymDer` | Generate C++ code for symbolic derivatives |
| `GenerateSpecifSerial` | Generate serialization specifications and samples |
| `GenArgsSpec` | Generate argument specifications |
| `TutoSerial` | Tutorial for serialization framework |
| `TutoFormalDeriv` | Tutorial for formal derivation |
| `TestSensor` | Test orientation functions (direct/inverse coherence, 2D/3D ground truth) |
| `TestEigen` | Experiments with the Eigen matrix library |
| `TestProj` | Test PROJ coordinate transformation (also useful in production, see [Coordinate Systems](#coordinate-systems)) |
| `TestGraphPart` | Test graph partitioning |
| `TestElemBundle` | Test elementary bundle adjustment |
| `TestMPD` | Quick developer test entry point |
| `Cpp11` | Test C++11 features |
| `___OriPoseArboTriplet` | Build triplet arborescence (internal) |
| `___TransformPoses` | Align two pose sets (internal) |
| `___VisSfm` | Generate PLY with poses and 3D structure (internal) |
