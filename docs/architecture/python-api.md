# Python API

A subset of MMVII's C++ classes is accessible from Python via a module generated with
[pybind11](https://github.com/pybind/pybind11).

---

## Using the Python API

For build instructions and usage, see `MMVII/apib11/README.md`.

Examples covering the available classes are in `MMVII/apib11/examples/`.

---

## Extending the Python API

### Source files

The classes exported to Python are declared in:

```
MMVII/apib11/py_MMVII*.cpp
```

The main entry point is `MMVII/apib11/py_MMVII.cpp`, which calls one `pyb_init_*` function
per module file. Each file defines which C++ classes and methods are exposed.

### Adding a new class

A minimal export (from `py_MMVII_Aime.cpp` as example):

```cpp
// In py_MMVII_Aime.cpp
void pyb_init_Aime(py::module_ & m)
{
    py::class_<cAimeDescriptor>(m, "AimeDescriptor",
                                DOC(MMVII_cAimeDescriptor, cAimeDescriptor))
        .def(py::init<>())
        .def("ILP", &cAimeDescriptor::ILP, DOC(MMVII_cAimeDescriptor, ILP));
}
```

1. Declare the function in `MMVII/apib11/py_MMVII.h`
2. Call it from `MMVII/apib11/py_MMVII.cpp`

### Key patterns

**Inheritance:** if `Bar` extends `Foo` and `Foo` is already exposed:
```cpp
py::class_<Bar, Foo>(m, "Bar", ...)
```

**Named parameters:**
```cpp
.def("toFile", &tPCIC::ToFile, "filename"_a, DOC(...))
```

**`__repr__`:**
```cpp
.def("__repr__", [](const tMPP2I & m) {
    std::ostringstream ss;
    ss << "MapPProj2Im(" << m.F() << ",(" << m.PP().x() << "," << m.PP().y() << "))";
    return ss.str();
})
```

**Templates:** use a unique Python name per instantiation
(see `MMVII/apib11/py_MMVII_Mappings.cpp`).

**NumPy compatibility:** see pybind11 numpy documentation for direct array access.

### Documentation

MMVII uses [pybind11_mkdoc](https://github.com/pybind/pybind11_mkdoc) to pull Doxygen
comments into the Python module automatically via the `DOC(namespace, name)` macro.

!!! warning "pybind11_mkdoc is sensitive to Doxygen syntax"
    If two different comment styles are used for the same symbol, the documentation
    tool may refuse both. Keep C++ Doxygen comments consistent.

### Return value policy

Always specify `py::return_value_policy` for methods returning references or pointers
to avoid crashes and memory corruption.
See the [pybind11 documentation](https://pybind11.readthedocs.io/en/stable/advanced/functions.html).

---

## Key files

| File | Contents |
|------|----------|
| `apib11/README.md` | Build and usage instructions |
| `apib11/py_MMVII.h` | Declaration of all `pyb_init_*` functions |
| `apib11/py_MMVII.cpp` | Module entry point |
| `apib11/py_MMVII_Aime.cpp` | Example: exporting feature descriptor class |
| `apib11/py_MMVII_Mappings.cpp` | Example: exporting template mapping classes |
| `apib11/py_MMVII_Ptxd.cpp` | Example: pythonic point class with `__repr__` and tuple init |
| `apib11/examples/` | Usage examples for all exported classes |
