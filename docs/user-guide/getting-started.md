# My First Command: Set Editing

This page introduces the `EditSet` command and the general conventions of the MMVII
command-line interface. Concepts covered here — argument syntax, help system, global
parameters, error codes — apply to every MMVII command.

---

## Concepts

Almost all MMVII commands require one or more **sets of files** (typically images) as input.
For simple cases a regular expression suffices — for example `".*JPG"` selects all files
with a `.JPG` extension.

For more complex cases you may want to:

- build a set from a pattern;
- add or subtract files incrementally;
- save and reuse the result.

The `EditSet` command handles this: it builds and manipulates an **XML file** that stores a
named set of files, which can then be passed to any other command instead of a plain pattern.

---

## Basic usage

### Invoking MMVII

MMVII is a single command-line executable. Any command `OneCmd` is called as:

```bash
MMVII OneCmd [args...]
```

Running `MMVII` with no arguments lists all available commands with a short description:

```
Bench   => This command execute (many) self verification on MicMac-V2 behaviour
EditSet => This command is used to edit set of file
EditRel => This command is used to edit set of pairs of files
...
```

### Getting help

Add `help` anywhere after the command name to display its full parameter list:

```bash
MMVII EditSet help
```

```
**********************************
*   Help project 2007/MMVII      *
**********************************

  For command : EditSet
   => This command is used to edit set of file
   => Srce code entry in : src/Appli/cMMVII_CalcSet.cpp

 == Mandatory unnamed args : ==
  * string [FDP] :: Full Name of Xml in/out
  * OpAff :: Operator
  * string [MPF0] :: Pattern or Xml for modifying

 == Optional named args : ==
  * [Name=Show] int :: Show detail of set before/after, 0->none, (1) modif, (2) all, [Default=0]
  * [Name=Out] string :: Destination, def=Input, no save for NONE
  * [Name=FFI0] string [FFI0] :: File Filter Interval, Main Set
```

The help output has three parts:

- a short description and the C++ source file entry point;
- **mandatory** positional arguments (matched by order);
- **optional** named arguments, passed as `Name=Value`.

`help` can appear at any position after the command name, so this is valid:

```bash
MMVII EditSet File.xml = "F[0-3].txt" help
```

### Operators

`EditSet` takes three mandatory arguments: the XML file, an operator, and a pattern (or
another XML set file). The operator controls how the pattern modifies the existing set:

| Operator | Effect |
|----------|--------|
| `=`  | Overwrite — the set becomes the pattern |
| `+=` | Union — add the pattern to the set |
| `-=` | Difference — remove the pattern from the set |
| `*=` | Intersection — keep only elements in both |
| `=0` | Empty — clear the set regardless of the pattern |

### Example

From the folder `MMVII-TestDir/Input/Files`:

```bash
MMVII EditSet File.xml = "F[0-3].txt"
```

This creates (or overwrites) `File.xml` with all files in the folder matching `F[0-3].txt`:

```xml
<?xml version="1.0" encoding="ISO8859-1" standalone="yes" ?>
<MMVII_Serialization>
   <SetOfName>
      <Nb>4</Nb>
      <el>F0.txt</el>
      <el>F1.txt</el>
      <el>F2.txt</el>
      <el>F3.txt</el>
   </SetOfName>
</MMVII_Serialization>
```

Note that patterns act as **filters on existing files**, not glob expansions — `"F([0-3]|[a-z]).txt"` would yield the same result if no additional files are present.

### Exercises

Try the following sequence and inspect `File.xml` after each step:

```bash
MMVII EditSet File.xml  = "F[0-3].txt"
MMVII EditSet File.xml += "F[7-9].txt"
MMVII EditSet File.xml -= "F8.txt"
MMVII EditSet File.xml *= "F[02468].txt"
MMVII EditSet File.xml =0 ".*"
```

---

## Optional parameters

### `Out` — write to a different file

By default the XML file is used as both input and output. Use `Out` to leave the input
unchanged and write the result elsewhere:

```bash
MMVII EditSet File.xml  = "F[0-3].txt"
MMVII EditSet File.xml += "F[7-9].txt"  Out=File2.xml
```

`File.xml` still has 4 names; `File2.xml` has 7.

When the pattern argument is itself an XML set file produced by MMVII, the contained names
are used rather than the filename itself. All operations are set operations in the
mathematical sense — no duplicates are introduced:

```bash
MMVII EditSet File1.xml  = "F[0-3].txt"
MMVII EditSet File2.xml  = "F[7-9].txt"
MMVII EditSet File1.xml += File2.xml   Out=File3.xml   # 7 names
MMVII EditSet File3.xml += File2.xml   Out=File4.xml   # still 7 names
```

### `Show` — visualise changes

`Show=1` prints only the modifications; `Show=2` prints the full before/after state:

```bash
MMVII EditSet File.xml =0 ".*"
MMVII EditSet File.xml  = "F[0-4].txt"
MMVII EditSet File.xml += "F[0-6].txt"  Show=1
-+ F5.txt
-+ F6.txt
MMVII EditSet File.xml *= "F[02468].txt"  Show=2
 ++ F0.txt
 ++ F2.txt
 ++ F4.txt
 ++ F6.txt
 +- F1.txt
 +- F3.txt
 +- F5.txt
```

| Prefix | Meaning |
|--------|---------|
| `-+`   | Absent before, present after |
| `++`   | Present before and after |
| `+-`   | Present before, absent after |

---

## Global parameters

These optional parameters are common to **all** MMVII commands.

### `DirProj` — project directory

MMVII ties a project to a directory. The project directory is normally inferred from the
first file argument (marked `[FDP]` in the help). It can be overridden with `DirProj`:

```bash
# Both commands below are equivalent (run from MMVII-TestDir/Input/)
MMVII EditSet Files/FileX.xml = "F[0].txt"
MMVII EditSet FileX.xml       = "F[0].txt"  DirProj=Files/
```

### `FFI0` / `FFI1` — interval filtering

Commands that accept a main image set (marked `[MPI0]` in the help) can be filtered by a
lexicographic interval passed as `FFI0`. Interval syntax uses `[` for closed bounds and `]`
for open bounds:

| Syntax | Meaning |
|--------|---------|
| `[a,b]`  | $a \leq S \leq b$ |
| `]a,b[`  | $a < S < b$ |
| `[a,[`   | $S \geq a$ (no upper bound) |
| `],b]`   | $S \leq b$ (no lower bound) |

Concatenate intervals for unions: `],a110.jpg[ [a140.jpg,[` means $S < a110.jpg$ **or** $S \geq a140.jpg$.

```bash
MMVII EditSet File.xml = "F.*txt"  FFI0="[F1.txt,F3.txt[]F7.txt,["
# Result: F1.txt  F2.txt  F8.txt  F9.txt
```

A second set (marked `[MPI1]`) can be filtered with `FFI1`. See `EditRel` for an example.

### `StdOut` — redirect output

| Value | Effect |
|-------|--------|
| `StdOut=File.txt`    | Append to file |
| `StdOut=+File.txt`   | Append to file and keep console output |
| `StdOut=0File.txt`   | Overwrite file |
| `StdOut=0+File.txt`  | Overwrite file and keep console output |
| `StdOut=NONE`        | Suppress all output |

Note: filenames used with `StdOut` cannot begin with `+` or `0`.

### `NumVOut` — serialization format version

MMVII V1 and V2 files can coexist. The export version is chosen as follows:

1. If `NumVOut` is set explicitly (`1` or `2`), use that.
2. Else if any V2 file was read, export as V2.
3. Else if any V1 file was read, export as V1.
4. Otherwise, default to V2.

---

## Extended help

MMVII has three help levels:

| Keyword | Shows |
|---------|-------|
| `help`  | Standard parameters only |
| `Help`  | Standard + common parameters |
| `HELP`  | All parameters including internal ones (prefixed `### INTERNAL`) |

Help can be filtered with a regex: `HELP=F.*` shows only parameters whose name matches
`F.*`:

```bash
MMVII EditSet File.xml *= "F[02468].txt"  HELP=F.*
 == Optional named args : ==
  * [Name=FFI0] string :: File Filter Interval, Main Set   ### COMMON
  * [Name=FFI1] string :: File Filter Interval, Second Set   ### COMMON
```

---

## Predefined semantics

Parameters that appear in many commands carry a **predefined semantic tag** shown in square
brackets after the type in the help output:

| Tag | Meaning |
|-----|---------|
| `[FDP]`  | This argument fixes the project directory |
| `[MPI0]` | Main image pattern/set (filterable by `FFI0`) |
| `[MPI1]` | Second image pattern/set (filterable by `FFI1`) |
| `[FFI0]` | Interval filter for the main image set |
| `[FFI1]` | Interval filter for the second image set |
| `[DP]`   | Project directory override |

---

## Error reference

When a command fails, MMVII prints a structured error block:

```
Level=[UserEr:BadBool]
Mes=[Bad value for boolean :[tru]]
```

`Level` is either `[Internal Error]` (a bug — report it) or `[UserEr:CODE]` (a usage
mistake). The error codes for common mistakes are listed below.

| Code | Cause | Example |
|------|-------|---------|
| `BadBool`     | Boolean parameter given an invalid string (valid: `0`, `1`, `false`, `true`) | `ShowAll=tru` |
| `BadOptP`     | Optional parameter name does not match any known parameter | `AllShow=true` instead of `ShowAll=true` |
| `MultOptP`    | Same optional parameter specified more than once | `NumVOut=1 NumVOut=1` |
| `OpenFile`    | Cannot open a file (directory missing, disk full, permissions) | `Out=o/o.xml` when `o/` does not exist |
| `InsufP`      | Fewer arguments than mandatory parameters | Omitting the operator in `EditSet` |
| `BadEnum`     | String does not match a valid enum value | `eq` instead of `=` |
| `FileSetN`    | A file exists but is not a valid MMVII XML set | Using a corrupt or foreign XML file |
| `IntWithoutS` | `FFI1` used but the command has no `[MPI1]` parameter | `FFI1=[,]` on `EditSet` |
