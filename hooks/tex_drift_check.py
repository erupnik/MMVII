"""
MkDocs hook: warn when a .tex source file has been committed more recently
than its paired hand-crafted .md page, indicating the docs may have drifted.

Uses git log timestamps so the check works identically locally and in CI
(filesystem mtimes are unreliable after a fresh checkout).
"""

import subprocess
from pathlib import Path

# (tex source, hand-crafted docs page)
TEX_MD_PAIRS = [
    ("Doc/Programmer/Serialization.tex",       "docs/developer/serialization.md"),
    ("Doc/Programmer/NonLinearOptim.tex",       "docs/developer/nonlinear-optim.md"),
    ("Doc/Programmer/SymbolicDerivation.tex",   "docs/developer/symbolic-derivation.md"),
    ("Doc/Programmer/ImagesClasses.tex",        "docs/developer/image-classes.md"),
    ("Doc/Programmer/Mapping.tex",              "docs/developer/mapping.md"),
    ("Doc/Programmer/Interpolators.tex",        "docs/developer/interpolators.md"),
    ("Doc/Programmer/Graph.tex",                "docs/developer/graph.md"),
    ("Doc/Programmer/PythonAPI.tex",            "docs/developer/python-api.md"),
    ("Doc/Programmer/IntroProg.tex",            "docs/developer/programming-guide.md"),
    ("Doc/Methods/PerspCamModelization.tex",    "docs/theory/camera-modelization.md"),
    ("Doc/Tutorial/TutoOrient.tex",             "docs/tutorials/orientation.md"),
    ("Doc/Tutorial/UseCase01.tex",              "docs/tutorials/use-cases/image-development.md"),
]


def _last_commit_timestamp(path: str) -> int | None:
    """Return the Unix timestamp of the last commit touching *path*, or None."""
    result = subprocess.run(
        ["git", "log", "-1", "--format=%at", "--", path],
        capture_output=True, text=True
    )
    raw = result.stdout.strip()
    return int(raw) if raw else None


def on_pre_build(config):
    drifted = []

    for tex_path, md_path in TEX_MD_PAIRS:
        if not Path(tex_path).exists() or not Path(md_path).exists():
            continue

        tex_ts = _last_commit_timestamp(tex_path)
        md_ts  = _last_commit_timestamp(md_path)

        if tex_ts is None or md_ts is None:
            continue  # untracked file, skip

        if tex_ts > md_ts:
            drifted.append((tex_path, md_path))

    if drifted:
        print("\n" + "=" * 70)
        print("WARNING: the following .tex sources were updated after their")
        print("paired docs pages — manual review may be needed:")
        for tex, md in drifted:
            print(f"  {tex}  →  {md}")
        print("=" * 70 + "\n")
