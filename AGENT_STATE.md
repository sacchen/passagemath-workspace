# Agent State

## 1. PROJECT DIRECTIVES
- **Search Tooling**: Use `Grep` (content) and `Glob` (discovery) tools specifically. Avoid raw `bash` for searching unless piping is required.
- **Environment**: Use `uv` exclusively for Python environment management.
- **Commit Quality**: Adhere to Simon Willison's "Perfect Commit" rule: atomic changes, bundled tests, docs, and issue links.
- **Verification**: "Prove it works" via manual and automated tests before shipping.
- **Architectural Awareness**: Prioritize understanding over volume; focus on modular packaging correctness.

## 2. REVISED LEVERAGE FRAMEWORK (S.N.T.)
- **SCALE**: Infrastructure depth involving `.m4` templates for `pyproject.toml` generation across 100+ modular packages in `pkgs/`.
- **NEGLECTED**: "Modularization Blind Spots" where `except ImportError: pass` blocks at module level result in late-binding `NameError` during runtime in modular installs (e.g., Issue #2243).
- **TRACTABLE**: Surgical fixes for missing fallback logic in `src/sage/` and environment-specific hardcoding in build scripts.

## 3. THE "HIGH-LEVERAGE" DISCOVERY SCAN
### Candidate A (Neglected): `ImportError` NameErrors
- **File**: `passagemath/src/sage/combinat/partition.py` (Line 10060)
- **Finding**: `cached_number_of_partitions` is defined inside a `try` block but lacks a fallback in `except ImportError: pass`. This causes a `NameError` in `cardinality()` when `passagemath-flint` is not installed.
- **Action**: Provide a pure-python fallback for `cached_number_of_partitions`.

### Candidate B (Neglected): Implicit Module Dependencies
- **File**: `passagemath/src/sage/rings/polynomial/polynomial_element_generic.py` (Line 1631)
- **Finding**: Silent `except ImportError: pass` on module-level imports without setting a default value for names used in the file.
- **Action**: Audit for similar patterns where optional dependencies are not safely handled.

### Candidate C (Scale): `pkg_resources` remnants
- **File**: `passagemath/src/sage/repl/ipython_kernel/kernel.py` (Line 27)
- **Finding**: References to `pkg_resources` in warning filters. While not functional, these indicate areas where legacy packaging assumptions persist.
- **Action**: Clean up warning filters or modernize to `importlib.metadata`.

### Candidate D (Tractable): Hardcoded `SAGE_ROOT` in scripts
- **File**: `passagemath/pkgs/sage-conf_conda/setup.py` (Line 23)
- **Finding**: Hardcoded logic for `SAGE_ROOT` path joining that might fail in non-standard or VPATH builds.
- **Action**: Generalize path handling to use standard environment variables or discovery.

### Candidate E (Scale): `.m4` vs `pyproject.toml` synchronization
- **Path**: `passagemath/pkgs/*/pyproject.toml.m4`
- **Finding**: 113 packages use `.m4` templates. Discrepancies between the template and generated `pyproject.toml` can cause silent build regressions.
- **Action**: Audit for packages where the generated `pyproject.toml` contains stale metadata or missing dependencies found in the `.m4`.

## 4. KNOWLEDGE GRAPH
- **passagemath (Monorepo)**: The central source for core logic (`src/`) and modular packages (`pkgs/`).
- **sage-numerical-interactive-mip (External)**: An independent package (v0.3.0) that is NOT generated from the monorepo. It acts as a consumer/plugin for `sage.numerical.mip`.
- **Relationship**: `passagemath` provides the backend interfaces; `mip` provides high-level interactive optimization tools. Bug fixes in `mip` (like PR #6) improve the interactive experience, while monorepo fixes (like PR #2237) improve the underlying infrastructure.

## 5. AGENT MEMORY LOOP
| Agent | Role | Contribution |
| :--- | :--- | :--- |
| Claude | Logic | PR #2237 logic, Issue #2243 root cause analysis. |
| Codex | Boilerplate | (Pending) |
| Gemini | Discovery | Audit of `ImportError` patterns and `SAGE_ROOT` hardcoding. |

## 6. ACTIVE QUEUE
1. **`passagemath/src/sage/combinat/partition.py`**: Implement fallback for `cached_number_of_partitions` to resolve #2243.
2. **`passagemath/src/sage/rings/polynomial/polynomial_element_generic.py`**: Investigate if `ImportError: pass` blocks cause runtime failures in modular environments.
