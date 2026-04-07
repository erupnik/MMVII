# Serialization

## What is serialization?

Serialization is the mechanism by which an object describes itself as a sequence of atomic
values. A *receiver* (called an **archive** in MMVII) consumes this description and does
something with it — typically writing to or reading from a file.

The key insight is the **N+M translator** pattern: rather than writing $N \times M$
format-specific serializers, each object implements one description method,
and each archive implements one interpretation. The description acts as a universal language.

MMVII currently supports the following archive types:

| Archive | Mode | Description |
|---------|------|-------------|
| XML | read/write | Tagged human-readable format |
| JSON | read/write | Tagged human-readable format |
| Binary `.dmp` | read/write | Compact binary format (used for large data) |
| Raw text | read/write | Untagged text format |
| Hash | write | Accumulates a hash code from object content |

---

## Core design

### The archive base class — `cAr2007`

All archives inherit from `cAr2007`, a pure abstract interface. Each archive overrides
`RawAddDataTerm` for every atomic type (`int`, `double`, `std::string`, `size_t`, ...):

```cpp
// In cAr2007 (pure virtual):
virtual void RawAddDataTerm(int & anI) = 0;

// Binary write:
void cOBin_Ar2007::RawAddDataTerm(int & anI) { mMMOs.Write(anI); }
// Binary read:
void cIBin_Ar2007::RawAddDataTerm(int & anI) { mMMIs.Read(anI); }
// Text write:
void cOBaseTxt_Ar2007::RawAddDataTerm(int & anI) { Ofs() << anI; }
// Text read:
void cIBaseTxt_Ar2007::RawAddDataTerm(int & anI) { FromS(GetNextStdString(), anI); }
```

### The `AddData` function

Every type to be serialized defines a free function:

```cpp
void AddData(const cAuxAr2007 & anAux, MyType & aVal);
```

There are four categories:

**1. Atomic types** — delegate directly to the archive:
```cpp
void AddData(const cAuxAr2007 & anAux, int & aVal)
{
    anAux.Ar().RawAddDataTerm(aVal);
}
```

**2. Types cast to atomic** — use `TplAddDataTermByCast`:
```cpp
void AddData(const cAuxAr2007 & anAux, tU_INT1 & aVal)
{
    anAux.Ar().TplAddDataTermByCast(anAux, aVal, (int*)nullptr);
}
```

**3. Standard template containers** — provided in `MMVII_2Include_Serial_Tpl.h`:
```cpp
template <class T>
void AddData(const cAuxAr2007 & anAux, std::vector<T> & aL)
{
    StdContAddData(anAux, aL);
}
```

**4. User-defined types** — compose from member `AddData` calls:
```cpp
// cTestSerial0 is composed of mP1, mI1, mR4, mP2
void AddData(const cAuxAr2007 & anAux, cTestSerial0 & aTS0)
{
    AddData(cAuxAr2007("P1", anAux), aTS0.mP1);
    anAux.Ar().AddComment("This is P1");
    AddData(cAuxAr2007("I1", anAux), aTS0.mI1);
    AddData(cAuxAr2007("R4", anAux), aTS0.mR4);
    AddData(cAuxAr2007("P2", anAux), aTS0.mP2);
}
```

### Tags — `cAuxAr2007`

`cAuxAr2007` wraps an archive with an optional tag string. Tags:

- In **tagged formats** (XML, JSON): written as field names in write mode; verified for integrity in read mode
- In **untagged formats** (binary, raw text): ignored entirely

The `"P1"`, `"I1"` strings in the example above become XML/JSON field names but are no-ops in binary.

---

## Practical usage

To make a class serializable, define `AddData` for it (pattern 4 above).
The same function works for reading and writing — the direction is determined by the archive type.

To save/load to file:

```cpp
// Write to XML:
SaveInFile(myObject, "output.xml");

// Read from XML:
ReadFromFile(myObject, "output.xml");
```

The binary format (`.dmp`) is used for large objects (point clouds, dense data) where
XML overhead would be prohibitive.

---

## Key files

| File | Contents |
|------|----------|
| `include/MMVII_Ar2007.h` | `cAr2007`, `cAuxAr2007` declarations |
| `include/MMVII_2Include_Serial_Tpl.h` | `AddData` for STL containers |
| `Serial/uti_e2string.cpp` | Enum/string conversion registry |
| `src/TutoBench/TutoSerial.cpp` | Worked tutorial — read this first |
