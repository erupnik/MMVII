# Programming Guide

This section documents MMVII's internal architecture for developers who want to contribute
new commands, extend existing functionality, or understand the codebase.

## Contents

| Topic | Description |
|-------|-------------|
| [Adding a command](#adding-a-command) | How to register a new MMVII command |
| [Programming style](#programming-style) | Naming conventions, error handling, utilities |
| [Serialization](serialization.md) | How MMVII objects describe, save, and load themselves |
| [Non-linear optimisation](nonlinear-optim.md) | Gauss-Newton solver, Schur complement, class interfaces |
| [Symbolic derivation](symbolic-derivation.md) | Automatic differentiation via symbolic DAGs and code generation |
| [Image classes](image-classes.md) | Image data structures, numerical types, filters |
| [Mapping framework](mapping.md) | Abstract smooth mappings: projection, distortion, geodetic transforms |
| [Interpolators](interpolators.md) | Kernel-based image interpolation theory and classes |
| [Graph library](graph.md) | Templated graph structure: vertices, edges, shortest path, MST |
| [Python API](python-api.md) | Python bindings via pybind11 and how to extend them |

---

## Adding a command

### Principle: one command / one class

Each MMVII command is implemented as a class inheriting from `cMMVII_Appli`.
By convention the class is named `cAppli_<CommandName>` and defined in a `.cpp` file.

```cpp
class cAppli_EditSet : public cMMVII_Appli
{
public:
    cAppli_EditSet(const std::vector<std::string> & aVArgs,
                   const cSpecMMVII_Appli & aSpec);
    int Exe() override;
    cCollecSpecArg2007 & ArgObl(cCollecSpecArg2007 &) override;
    cCollecSpecArg2007 & ArgOpt(cCollecSpecArg2007 &) override;
private:
    std::string mXmlIn, mOp, mPat;
    int    mShow = 0;
    std::string mXmlOut;
};
```

The three methods to implement:

| Method | Purpose |
|--------|---------|
| `Exe()` | Execute the command logic; return 0 on success |
| `ArgObl()` | Declare mandatory (positional) parameters |
| `ArgOpt()` | Declare optional (`Name=Value`) parameters |

### Declaring parameters

Parameters are declared using `Arg2007` (mandatory) and `AOpt2007` (optional).
Both are templates that adapt to the type of the target variable.

```cpp
cCollecSpecArg2007 & cAppli_EditSet::ArgObl(cCollecSpecArg2007 & anArgObl)
{
    return anArgObl
        << Arg2007(mXmlIn, "Full Name of Xml in/out", {eTA2007::FileDirProj})
        << Arg2007(mOp,    "Operator in (" + StrAllVall<eOpAff>() + ")")
        << Arg2007(mPat,   "Pattern or Xml for modifying", {{eTA2007::MPatIm,"0"}});
}

cCollecSpecArg2007 & cAppli_EditSet::ArgOpt(cCollecSpecArg2007 & anArgOpt)
{
    return anArgOpt
        << AOpt2007(mShow,   "Show", "Show detail: 0=none, 1=modif, 2=all", {})
        << AOpt2007(mXmlOut, "Out",  "Destination, def=Input", {});
}
```

Predefined semantics (`eTA2007` enum) provide automatic handling of common patterns:

| Semantic | Effect |
|----------|--------|
| `eTA2007::FileDirProj` | First argument sets the working project directory |
| `eTA2007::MPatIm` | Argument is treated as the main image pattern/set |

### Registering the command

1. Create an allocator function and a `cSpecMMVII_Appli` object in the same `.cpp` file:

```cpp
tMMVII_UnikPApli Alloc_EditSet(const std::vector<std::string> & aVArgs,
                                const cSpecMMVII_Appli & aSpec)
{
    return tMMVII_UnikPApli(new cAppli_EditSet(aVArgs, aSpec));
}

cSpecMMVII_Appli TheSpecEditSet(
    "EditSet",
    Alloc_EditSet,
    "This command is used to edit set of file",
    {eApF::Util}, {eApDT::Xml}, {eApDT::Xml},
    __FILE__
);
```

2. Add a single line in `src/Appli/cSpecMMVII_Appli.cpp`:

```cpp
TheRes.push_back(&TheSpecEditSet);
```

That is all — MMVII discovers the command automatically from this list at startup.

---

## Programming style

### Naming conventions

- Classes: `cMyClass` (prefix `c`)
- Methods: `CamelCase` starting with uppercase
- Member variables: `mMyVar` (prefix `m`)
- Local variables: `aMyVar` (prefix `a`)
- Free functions: `CamelCase`

### I/O — never use `std::cout` or `printf`

Use MMVII's output facilities instead:

```cpp
MMVII::StdOut() << "message" << std::endl;
```

This ensures output is properly routed and can be suppressed or redirected.

### Error handling

Errors are signalled via MMVII's internal exception mechanism, not raw C++ exceptions.
Use the macros in `MMVII_Error.h`.

### Random numbers

MMVII uses a pseudo-random generator with a fixed default seed (for reproducible debugging).
To seed from time, pass a negative value to the `SeedRand` parameter in the relevant command.

### Enum ↔ string conversion

The `Serial/uti_e2string.cpp` file provides MMVII's enum/string conversion infrastructure.
For each enum that needs string conversion, register it there.

### Memory leak detection

Set the debug level in `MMVII_Error.h`:

```cpp
#define The_MMVII_DebugLevel The_MMVII_DebugLevel_InternalError_micro
```

Run the leaking command once — the identifier of the first un-freed object is printed:

```
========================== Ident of Non Freed object  102
```

Then run under `gdb` with `NTOC4ML=102` to break at the allocation site:

```bash
gdb MMVII
run <CommandArgs> NTOC4ML=102
```
