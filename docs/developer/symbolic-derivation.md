# Symbolic Derivation

MMVII computes analytical Jacobians via **symbolic differentiation with C++ code generation**.
This page explains the design and how to add new formulas.

---

## Why symbolic differentiation?

Four approaches exist for computing derivatives in Gauss-Newton solvers:

| Method | Accuracy | Speed | Maintenance |
|--------|----------|-------|-------------|
| Hand-crafted | Exact | Fast (optimised) | Hard — error-prone, breaks on changes |
| Numerical ($\epsilon$ finite diff) | Approximate | Slow ($2N$ evaluations) | Easy but fragile |
| Jet (Ceres-style) | Exact | Medium | Easy |
| **Symbolic + code gen** (MMVII) | Exact | Fast | Easy after initial setup |

MMVII uses symbolic differentiation: formulas are represented as DAGs, differentiated
symbolically, and C++ code is generated once. The generated code is then compiled and
reused at runtime with no overhead beyond arithmetic.

---

## Formula representation — DAG

Formulas are represented as **directed acyclic graphs (DAGs)** rather than trees.
The DAG avoids redundant computation: if the sub-formula $x+y$ appears in both $F$ and
$\partial F / \partial x$, it is computed once and shared.

**Example:** $F(x,y) = (x+y)^2 + x - \cos(x+y)$

In the DAG, $x+y$ is one node with two parents ($(\cdot)^2$ and $\cos$).
A variable $V_{577} = x+y$ is introduced in the generated code and reused.

The efficiency gain from DAG over tree can reach **10×** for complex formulas like
the collinearity equation with many distortion parameters.

---

## Key classes

### `cFormula<T>` and `cImplemF<T>`

`cFormula` is a reference-counted pointer to `cImplemF`, the actual DAG node.
Mathematical operators (`+`, `*`, `cos`, ...) are overloaded on `cFormula` to build the DAG:

```cpp
// Each operator either creates a new node or applies a simplification rule (e.g. F*1 = F)
// If the sub-formula was already created in this computation, the existing node is returned (DAG sharing)
```

Each `cImplemF` derived class overrides three virtual methods:

```cpp
// For cMulF (multiplication):

void ComputeBuf(int aK0, int aK1) override  // interpreted evaluation (batch)
{
    for (int aK = aK0; aK < aK1; aK++)
        mDataBuf[aK] = mDataF1[aK] * mDataF2[aK];
}

cFormula<T> Derivate(int aK) const override  // symbolic differentiation
{
    return mF2 * mF1->Derivate(aK) + mF1 * mF2->Derivate(aK);  // product rule
}

std::string GenCodeDef() const override  // C++ code generation
{
    return "(" + mF1->GenCodeRef() + " * " + mF2->GenCodeRef() + ")";
}
```

---

## Adding a new formula

### Step 1 — Define the formula class

Create a class in `src/SymbDerGen/` (e.g. `Formulas_Geom2D.h`).
It must define five members:

```cpp
class cMyFormula
{
public:
    // Names of unknowns (used as C++ variable names in generated code)
    static std::vector<std::string> VNamesUnknowns()
    {
        return {"x1", "y1", "x2", "y2"};
    }

    // Names of observations (known values passed at runtime)
    static std::vector<std::string> VNamesObs()
    {
        return {"target_dist"};
    }

    // Name used for generated class and file names (alphanumeric + _ only)
    static std::string FormulaName() { return "MyFormula"; }

    // The formula itself — returns a vector of residuals
    // tUk is cFormula<T>; all operators and functions are overloaded on it
    template <typename tUk>
    static std::vector<tUk> formula(
        const std::vector<tUk> & aVUk,   // unknowns
        const std::vector<tUk> & aVObs)  // observations
    {
        auto x1 = aVUk[0], y1 = aVUk[1];
        auto x2 = aVUk[2], y2 = aVUk[3];
        auto d_target = aVObs[0];

        auto dx = x2 - x1, dy = y2 - y1;
        auto dist = sqrt(dx*dx + dy*dy);
        auto residual = dist / d_target - CreateCste(1.0, x1);
        return {residual};
    }
};
```

!!! note "Creating constants"
    Use `CreateCste(value, any_formula_var)` — the second argument indicates the formula type
    but its value does not matter.

### Step 2 — Register for code generation

In `src/SymbDerGen/GenerateCodes.cpp`, add:

```cpp
GenCodesFormula(cMyFormula{}, true);   // true = also generate derivatives
GenCodesFormula(cMyFormula{}, false);  // false = values only (no derivatives)
```

### Step 3 — Generate and compile

```bash
make                          # compile MMVII with the new formula class
MMVII GenCodeSymDer           # run the code generator
make                          # recompile to include generated code
```

Generated files appear in `src/GeneratedCodes/`:
- `CodeGen_MyFormulaVal.cpp` / `.h` — values only
- `CodeGen_MyFormulaVDer.cpp` / `.h` — values + derivatives (if requested)

### Step 4 — Use the generated calculator

```cpp
#include "GeneratedCodes/CodeGen_MyFormulaVDer.h"

cCalculator<double> * aCalc = new cMyFormulaVDer<double>(aNbPoints, false);

// Set observation values for one equation
std::vector<double> aVObs = {target_distance};
aCalc->SetCurParams(aVObs);

// Evaluate: fills values and Jacobian for a batch of unknown blocks
aCalc->CalcBatch(aVUnkVals, aVRes);
```

---

## Debugging generated formulas

Add `SymbComment`, `SymbPrint`, and `SymbPrintDer` calls inside the `formula` method
to annotate or instrument the generated code:

```cpp
SymbComment(dist, "Euclidean distance");         // adds a comment in generated code
SymbPrint(dist, "dist");                         // prints value at runtime when debug enabled
SymbPrintDer(dist, 0, "d(dist)/d(x1)");         // prints derivative at runtime
```

Enable runtime output by calling `SetDebugEnabled(true)` on the calculator instance.

---

## Code location

| Path | Contents |
|------|----------|
| `include/SymbDer/` | Header-only DAG library (reusable outside MMVII) |
| `include/SymbDer/SymbolicDerivatives.h` | `cFormula`, `cImplemF` |
| `src/SymbDerGen/` | Formula specifications and code generation entry point |
| `src/SymbDerGen/Formulas_Geom2D.h` | Example formulas (2D triangulation, distortion, ...) |
| `src/SymbDerGen/GenerateCodes.cpp` | Entry point for `MMVII GenCodeSymDer` |
| `src/GeneratedCodes/` | All generated C++ files (do not edit manually) |
