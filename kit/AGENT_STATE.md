# passagemath — Agent State

Current work queue and findings. Update this file as tasks are completed or
new candidates are discovered.

---

## Current strategy (2026-03-16)

**Phase:** multiplier. Current focus is making work available for others —
scoping shovel-ready issues with root cause, exact files, and verification
method. Direct technical contributions are reactive.

**Upcoming:** Matthias's optimization course starts 2026-03-30. Primary
deliverable: computational notebooks built alongside the course.
Secondary: deborgen (distributed compute cooperative) as applied LP/scheduling
test case.

**Open PRs to watch:** #2282 and #2283. Don't open new PRs until those land.

---

## Active queue

Nothing currently in flight. Next technical work is reactive — CI regressions,
issues filed by the maintainer, or course-adjacent bugs.

---

## Completed

### A — partition.py NameError → PR #2253 (Merged)

* **PR:** https://github.com/passagemath/passagemath/pull/2253
* `cached_number_of_partitions` now bound to `None` on ImportError.

### B — Meta-issue #2254 (Closed, PRs filed)

* **Issue:** https://github.com/passagemath/passagemath/issues/2254
* Full triage of ~45 scanner hits posted.
* **PR #2282:** ell_point.py + number_field.py pari NameError
* **PR #2283:** padic_extension_leaves.py, multi_polynomial_ideal.py,
  chart_func.py, tools/check_unbound_imports.py

### C — Shovel-ready issues (Filed 2026-03-16)

* **#2236** comment: full `_repr_png_()` implementation spec for Graphics
* **#2284**: WASM recipe contribution guide

### D — Onboarding and workspace infrastructure (Done 2026-03-16)

* `passagemath-workspace/onboarding.md` — install, doctests, PR workflow,
  Perfect Commit
* `passagemath-workspace/approach.md` — contributing philosophy
* `passagemath-workspace/projects/` — shovel-ready project cards

---

## Discovery scan findings (lower priority, unverified)

### E — `polynomial_element_generic.py` implicit deps (Neglected)
* **File:** `src/sage/rings/polynomial/polynomial_element_generic.py` line 1631
* Silent `except ImportError: pass`, no default set for names used in file.
* **Action:** audit for runtime failures; may overlap with #2254 scope.

### F — `pkg_resources` in kernel warning filters (Scale)
* **File:** `src/sage/repl/ipython_kernel/kernel.py` line 27
* References to `pkg_resources` in warning filters.
* **Action:** modernize to `importlib.metadata` or remove.

### G — Hardcoded `SAGE_ROOT` in sage-conf_conda (Tractable)
* **File:** `pkgs/sage-conf_conda/setup.py` line 23
* **Action:** generalize to standard env var discovery.

### H — `.m4` vs generated `pyproject.toml` drift (Scale)
* **Path:** `pkgs/*/pyproject.toml.m4` (113 packages)
* **Action:** audit for stale metadata or missing dependencies.
