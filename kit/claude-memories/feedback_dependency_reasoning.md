---
name: Dependency availability reasoning in passagemath
description: How to correctly determine whether a package is safe to assume present — build/pkgs/type is irrelevant for pip packages
type: feedback
---

To determine whether a package is always available in a given passagemath context, check `pkgs/<containing-package>/pyproject.toml.m4`, NOT `build/pkgs/<dep>/type`.

**Why:** `build/pkgs/*/type` (e.g. `type=standard`) is a SageMath monolithic build system concept — it means the package ships in the standard Sage tarball. In passagemath's pip-installable world this file is inherited metadata that has no bearing on what's installed. What matters is whether the *containing* passagemath package declares the dep as a required dependency in its `pyproject.toml.m4` `[project] dependencies` list.

**How to apply:** Before claiming "X is always present so this try/except is dead code", trace: which `pkgs/sagemath-*` package contains the file in question? Then check that package's `pyproject.toml.m4` — is X in `dependencies`? If yes, it's safe to assume. If it's only in `[project.optional-dependencies]` or absent, it's optional.

**Origin:** In PR #2283, cited `build/pkgs/sympy/type = standard` as evidence that a try/except around `import sympy` in `chart_func.py` was dead code. Matthias corrected: the actual evidence is `pkgs/sagemath-symbolics/pyproject.toml.m4:32` declaring sympy a required dep. The conclusion was right but the reasoning was wrong.
