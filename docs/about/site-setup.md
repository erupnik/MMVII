# Documentation Site Setup

This page describes how the MMVII documentation website was built, what tools are used, and how the automated deployment works.

---

## Technology stack

| Tool | Role |
|------|------|
| [MkDocs](https://www.mkdocs.org/) | Static site generator — converts Markdown files into a website |
| [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/) | Theme — provides the visual design, navigation, search, dark mode |
| [Doxygen](https://www.doxygen.nl/) | API reference — generates HTML from C++ source comments |
| [GitHub Actions](https://docs.github.com/en/actions) | CI/CD — automatically builds and deploys the site on every push |
| [GitHub Pages](https://pages.github.com/) | Hosting — serves the built site at `erupnik.github.io/MMVII` |

**Why MkDocs + Material?**  
MkDocs is Python-based, requires no database, and turns plain Markdown files into a full documentation website. The Material theme is widely used in scientific and engineering projects (Open3D, GTSAM, etc.) and provides out-of-the-box: full-text search, sidebar navigation, dark/light mode toggle, code copy buttons, and responsive layout.

**Why keep Doxygen separate?**  
MMVII already had a working `Doxyfile`. Rather than replacing it, the workflow runs Doxygen independently and embeds its HTML output as a sub-site at `/api/doxygen/`. This means C++ API docs stay auto-generated from source comments with zero extra effort.

---

## Repository structure

The following files were added to the repository:

```
MMVII/
├── mkdocs.yml                          # MkDocs configuration
├── docs/                               # All documentation source files
│   ├── index.md                        # Landing page
│   ├── user-guide/
│   │   ├── installation.md             # Build instructions (Linux + Windows)
│   │   └── commands.md                 # Command reference overview
│   ├── tutorials/
│   │   ├── index.md
│   │   ├── orientation.md
│   │   ├── bundle-adjustment.md
│   │   └── topometry.md
│   ├── architecture/
│   │   ├── index.md                    # Codebase overview
│   │   └── programming-guide.md
│   ├── api/
│   │   └── index.md                    # Entry point linking to Doxygen
│   └── about/
│       └── site-setup.md               # This page
└── .github/
    └── workflows/
        └── docs.yml                    # GitHub Actions deployment workflow
```

The existing `Doxyfile` at the repository root was reused without modification.

---

## MkDocs configuration (`mkdocs.yml`)

The configuration file controls:

- **`site_name`, `site_url`, `repo_url`** — metadata shown in the header and used for canonical URLs
- **`theme`** — selects Material for MkDocs with a dark/light mode toggle and indigo palette
- **`features`** — enables tab-based top navigation, sticky sidebar, search suggestions, and code copy buttons
- **`nav`** — defines the navigation tree explicitly (order, grouping, labels)
- **`markdown_extensions`** — enables admonitions (note/warning boxes), syntax highlighting, tabbed content blocks, and permalinks on headings

---

## GitHub Actions workflow (`.github/workflows/docs.yml`)

The workflow is triggered on every push to the `er_docs` branch and runs two jobs:

### Job 1 — `build`

```
Checkout code
  → Install Python + mkdocs-material
  → Install Doxygen + Graphviz
  → Run: doxygen Doxyfile          (outputs to doxygen/html/)
  → Run: mkdocs build              (outputs to site/)
  → Copy doxygen/html/ → site/api/doxygen/
  → Upload site/ as a Pages artifact
```

### Job 2 — `deploy`

```
Download the Pages artifact
  → Deploy to GitHub Pages via actions/deploy-pages
```

The two-job structure is required by GitHub: only the `deploy` job runs in the `github-pages` environment, which holds the deployment credentials. The `build` job produces the artifact; the `deploy` job publishes it.

### Permissions

The workflow declares:
```yaml
permissions:
  contents: read   # read the repository
  pages: write     # write to GitHub Pages
  id-token: write  # authenticate with GitHub's OIDC token (required by deploy-pages)
```

### Why "GitHub Actions" as Pages source?

GitHub Pages offers two deployment modes:
- **Deploy from a branch** — you maintain a `gh-pages` branch manually or via a bot
- **GitHub Actions** — the workflow pushes built output directly via `actions/deploy-pages`

The second mode is the modern approach: no orphan branch to maintain, no commit history of compiled HTML, and full control over the build process in the workflow.

---

## How to add or edit content

1. Edit or create `.md` files inside `docs/`
2. If adding a new page, register it in the `nav:` section of `mkdocs.yml`
3. Commit and push to `er_docs`
4. GitHub Actions builds and deploys automatically — no manual steps needed

To preview locally before pushing:
```bash
pip install mkdocs-material
mkdocs serve
# Open http://127.0.0.1:8000
```

---

## How to move to the main MMVII repository

When ready to make the docs official:

1. Open a pull request from `er_docs` into `main` on `micmac-V2/MMVII`
2. In the repository settings of `micmac-V2/MMVII`, enable GitHub Pages with source "GitHub Actions"
3. Update `site_url` in `mkdocs.yml` to the new target URL
4. Update the workflow trigger branch from `er_docs` to `main` (or whichever branch the team decides on)
