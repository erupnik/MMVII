# Installation

## Prerequisites

The following tools must be present on your system:

| Tool | Purpose | Platform |
|------|---------|----------|
| C++ compiler (g++, clang, MSVC++) | Compilation | All |
| [Git](https://git-scm.com/) | Clone repository | All |
| [CMake](https://cmake.org/) | Build configuration | All |
| make or [ninja](http://www.gnu.org/software/make) | Build system | Linux |
| [vcpkg](https://github.com/microsoft/vcpkg) | Library manager | Windows |
| [ccache](https://ccache.dev/) | Recompilation cache | Linux (optional) |
| [OpenMP](https://www.openmp.org/) | Parallel processing | All (optional) |
| [Doxygen](https://www.doxygen.nl/) | API docs generation | All (optional) |

Required libraries:

| Library | Purpose |
|---------|---------|
| [PROJ](http://trac.osgeo.org/proj/) | Coordinate system conversion |
| [GDAL](https://gdal.org/) | Image file handling |
| [PROJ grids](https://download.osgeo.org/proj/) | Coordinate transformations (optional) |

---

## Linux (Ubuntu)

```bash
# Install dependencies
sudo apt install pkg-config libproj-dev libgdal-dev libxerces-c-dev

# Clone and build
cd MMVII
mkdir build && cd build
cmake ..
make full -j$(nproc)
```

Add MMVII binaries to your PATH (adapt the path):
```bash
echo 'export PATH=/home/src/MMVII/bin:$PATH' >> ~/.bashrc
```

### Build options

Configure via `ccmake ..` or `cmake-gui ..`. Key options:

| Option | Values | Default |
|--------|--------|---------|
| `CMAKE_BUILD_TYPE` | `Debug`, `RelWithDebInfo`, `Release` | `RelWithDebInfo` |
| `CMAKE_CXX_COMPILER` | g++, clang | system default |

Useful build targets:
```bash
make clean          # delete build products
make distclean      # delete build products and generated code
cmake --build . -j N --target cleanall
```

Using Ninja instead of make:
```bash
cmake -G Ninja ..
```

### OpenMP with Clang
If using Clang version XX with OpenMP:
```bash
sudo apt install libomp-XX-dev
```

---

## Windows

### Step 1 — Install vcpkg

```bash
git clone https://github.com/microsoft/vcpkg.git
cd vcpkg
./bootstrap-vcpkg.bat
vcpkg.exe integrate install
```

### Step 2 — Build MMVII

```bash
cd MMVII
mkdir build && cd build
"[CMAKE_DIR]/cmake.exe" .. "-DCMAKE_TOOLCHAIN_FILE=[VCPKG_DIR]/vcpkg/scripts/buildsystems/vcpkg.cmake"
"[CMAKE_DIR]/cmake.exe" --build . --target full --config Release
```

Add `MMVII\bin` to the Windows PATH via **Advanced system settings**.

### Binary installer (Windows only)

Pre-compiled binaries are available [here](https://github.com/micmac-V2/MMVII/releases/download/Windows_MMVII_build/mmvii_windows.zip).  
Extract and add the `bin/` folder to your PATH.

---

## MicMac V1 API (optional)

Some legacy commands require the MicMac V1 library. To enable:

```bash
cmake .. -DMMVII_KEEP_LIBRARY_MMV1=on -DMMV1_PATH=<path_to_micmac_v1>
```

---

## Graphical Interface (vMMVII)

The `vMMVII` GUI helps compose MMVII commands. To build it:

```bash
cmake .. -DvMMVII_BUILD=ON
```

On Ubuntu 22.04, install Qt5 first:
```bash
sudo apt install qtbase5-dev
```

---

## Verify Installation

```bash
MMVII Bench 1
```

The test passes if execution does **not** end with a `Level=[UserEr:...]` error block.

---

## Command Completion (Linux)

Requirements: `bash-completion`, `python-is-python3` (installed by default on Ubuntu).

Add to `~/.bashrc` (adapt the path):
```bash
[ -f ${HOME}/<MICMAC_SOURCE_DIR>/MMVII/bash-completion/mmvii-completion ] && \
  . ${HOME}/<MICMAC_SOURCE_DIR>/MMVII/bash-completion/mmvii-completion
```
