# Project Management

---

## File formats

### Human-readable vs binary

A photogrammetric pipeline is a multi-step process: each computation writes results to
files that the next step reads back. MMVII uses two families of files:

- **Human-readable** — calibrations, poses, and other structured data are stored in tagged
  text formats (XML or JSON). These can be inspected and edited manually.
- **Binary** — dense data (point clouds, depth maps, etc.) is stored in binary format for
  efficiency. A text version exists for import/export but is not intended for human reading.

### XML and JSON

MMVII supports both XML and JSON as tagged formats. The default is XML; this can be changed
via a user profile (see [User parametrization](#user-parametrization) below). It is
recommended to pick one format and stick with it to avoid compatibility issues.

Sample files in both formats are provided under `MMVII-UseCaseDataSet/SampleFiles`.

!!! note "Comments in JSON"
    XML allows real comments. Since JSON does not, MMVII uses special comment tags such as
    `"<!--comment6-->":"(X,0)"` (corresponding to `<!--(X,0)-->` in XML).

### Rules for editing serialized files

MMVII files are designed to be readable and editable. Starting from a valid file, the
following modifications are safe:

- Change the value of an atom while respecting its type (float, int, string…).
- Add or remove an element in a **sequence** (tagged `<el>` in XML) or a **map** (tagged `<K>/<V>`).
- Add or remove comments.
- Add or remove an optional value — detectable because its tag starts with `Opt:`.

The following are **not** allowed:

- Producing an invalid XML/JSON file.
- Swapping two elements with different tags.
- Removing a non-optional tag.
- Adding or removing a value from a fixed-size array (used for 3D points, etc.).

### File structure

Every MMVII serialized file has the following structure:

```xml
<?xml version="1.0" encoding="ISO8859-1" standalone="yes" ?>
<Root>
   <Type>"MMVII_Serialization"</Type>
   <Version>"0.00"</Version>
   <Data>
      <!-- actual data here -->
   </Data>
</Root>
```

| Node | Role |
|------|------|
| `Type`    | Must be `"MMVII_Serialization"` — identifies the file as MMVII output |
| `Version` | Version number for forward compatibility (unused at present) |
| `Data`    | The actual payload — typically a single tagged node for type-checking at load time |

---

## User parametrization

Some global defaults can be configured per-user via a **profile** — an XML file that MMVII
reads at startup. Configurable settings include:

- Maximum number of processors for parallel computations.
- Default human-readable format (`xml` or `json`).
- User name (used by developers for debug breakpoints personal to them).

### Profile structure

The active profile is determined by `MMVII-CurentPofile.xml` (or
`Default-MMVII-CurentPofile.xml` if the former does not exist). This file names a folder:

```xml
<?xml version="1.0" encoding="ISO8859-1" standalone="yes" ?>
<Root>
   <Type>"MMVII_Serialization"</Type>
   <Version>"0.00"</Version>
   <Data>
      <NameProfile>"Default"</NameProfile>
   </Data>
</Root>
```

Inside the named folder (e.g. `MMVII-LocalParameters/Default/`), the file
`MMVII-UserOfProfile.xml` holds the actual settings:

```xml
<?xml version="1.0" encoding="ISO8859-1" standalone="yes" ?>
<Root>
   <Type>"MMVII_Serialization"</Type>
   <Version>"0.00"</Version>
   <Data>
      <UserName>"Unknown"</UserName>
      <NbProcMax>1000</NbProcMax>
      <SerialMode>"xml"</SerialMode>
   </Data>
</Root>
```

### Creating a profile

1. Create `MMVII-CurentPofile.xml` if it does not already exist.
2. Set `<NameProfile>` to the name of your profile folder.
3. Create `MMVII-UserOfProfile.xml` inside that folder with your settings.

You can maintain several profiles in different folders and switch between them by editing
`MMVII-CurentPofile.xml`.

!!! warning
    `Default-MMVII-CurentPofile.xml` is a git-tracked file. Do not modify it unless you
    are a developer.

---

## Data organisation

For any given project, MMVII stores all generated files under a single root folder named
`MMVII-PhgrProj`. Within it, sub-folders are named by **data type** — the names are fixed
by MMVII and cannot be changed by the user:

| Folder | Content |
|--------|---------|
| `Ori`            | Camera orientations (poses) |
| `ObjCoordWorld`  | 3D point coordinates |
| `ObjMesInstr`    | Point measurements in image space |
| `MetaData`       | Image metadata |
| `Reports`        | Processing reports |

Within each type folder, **sub-folders are named by the user** — typically one per
pipeline step, where the output of one step becomes the input of the next.

### Example: coded-target use case

A typical orientation pipeline (see `MMVII-UseCaseDataSet/SampleFiles`) produces four
orientation folders inside `Ori`:

| Step | Folder | Description |
|------|--------|-------------|
| 1 | `11P`   | Initial pose from uncalibrated space resection (11-parameter method) |
| 2 | `Resec` | Calibrated space resection, using calibration from `11P` |
| 3 | `BA`    | Bundle adjustment, initialised from `Resec` |
| 4 | `BA2`   | Second bundle adjustment, with additional uncoded targets detected using `BA` poses |

---

## The `Bench` command

`Bench` runs MMVII's internal self-verification tests. It is the recommended way to check
that a build is working correctly.

```bash
MMVII Bench 1   # quick checks
MMVII Bench 2   # full standard suite
```

Useful options:

```bash
# Run only benchmarks matching a regex
MMVII Bench 2 PatBench=".*Der.*"  Show=0

# List all available benchmarks (pattern with no match prints the list)
MMVII Bench 1 PatBench=XXX

# Force a specific error to test error handling
MMVII Bench 2 KeyBug=Debord_M1

# List all error keys that can be forced
MMVII Bench 1 KeyBug=XXXX

# Run a named inspection function (exact name required)
MMVII Bench 1 PatBench=InspectCube
```
