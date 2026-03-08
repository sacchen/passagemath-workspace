# passagemath — Agent State

Current work queue and findings. Update this file as tasks are completed or
new candidates are discovered.

---

## Strategy note (2026-03-07)

**Comparative advantage:** multi-agent workflow enables systematic, large-scale
analysis across thousands of files in a single session — filling Matthias's
specific bottleneck (scale, triage, cross-platform forensics). He can write
patches; he cannot prioritize mass triage.

**Current contributor identity:** modular packaging correctness bugs. All
merged/acted-on work fits this theme. Matthias has invited @sacchen to the org.

**The conversion question:** technical credibility is established. The next
high-leverage action may be direct outreach (one-paragraph email, ask for 20
min), not more PRs. More individual PRs have steeply diminishing returns for
the goal of lab access.

**If doing more technical work:** prefer systematic artifacts over individual
fixes. One complete triage map > ten individual PRs. The full #2254 triage
(all ~45 candidates in `unbound_results_v2.txt` classified to true/false
positive, severity-ranked) is the right next technical artifact.

**Do not pre-classify `unbound_results_v2.txt` without reading the actual
source.** Raw AST output contains false positives (stdlib conditional imports,
always-available Sage objects, etc.). Only the three cases below are confirmed.

---

## Active queue

The three manually verified cases from meta-issue #2254. Each is a standalone
PR following the fix pattern in AGENTS.md. Do not start these until #2253 is
merged (establishes the pattern).

1. **`src/sage/schemes/elliptic_curves/ell_point.py`** — `pari` left unbound
   (lines 162–166: `PariError` gets fallback but `pari` does not). Five or more
   affected methods: `elliptic_logarithm()` (default `algorithm='pari'`),
   `height()` (default `algorithm='pari'`), `tate_pairing()`,
   `weil_pairing()`, `_compute_order()`. Fix: bind `pari = None`, add
   `sage__libs__pari().require()` guards at each usage site.

2. **`src/sage/rings/number_field/number_field.py`** — `pari` left unbound
   (same pattern). 27 unguarded uses; `pari_bnf()` is the most critical
   (class group / units). Fix: same pattern as above.

3. **`src/sage/manifolds/chart_func.py`** — `sympy` left unbound. `exp()`
   and similar methods check `if _calc_method._current == 'sympy'` then call
   `sympy.X()` directly. Fix: bind `sympy = None`, guard with
   `sage__libs__sympy().require()` (or equivalent feature).

---

## Completed

### A — partition.py NameError → PR #2253 (Done)

* **PR:** https://github.com/passagemath/passagemath/pull/2253
* **Issue:** https://github.com/passagemath/passagemath/issues/2243
* `cached_number_of_partitions` now bound to `None` on ImportError.
  `cardinality()` enumerates for n≤10, raises `FeatureNotPresentError` for
  n>10. `random_element_uniform()` and `number_of_partitions()` raise
  unconditionally when flint absent.

### Meta-issue #2254 (Filed)

* **Issue:** https://github.com/passagemath/passagemath/issues/2254
* Tracks systematic resolution of the `except ImportError: pass` → NameError
  antipattern. Items 1–3 in the active queue above are the next targets.

---

## Discovery scan findings (lower priority)

### B — `polynomial_element_generic.py` implicit deps (Neglected)
* **File:** `src/sage/rings/polynomial/polynomial_element_generic.py` line 1631
* Silent `except ImportError: pass` on module-level imports, no default set
  for names used in the file.
* **Action:** audit for runtime failures; may overlap with #2254 scope.

### C — `pkg_resources` in kernel warning filters (Scale)
* **File:** `src/sage/repl/ipython_kernel/kernel.py` line 27
* References to `pkg_resources` in warning filters. Not functional but
  indicates lingering legacy packaging assumptions.
* **Action:** modernize to `importlib.metadata` or remove.

### D — Hardcoded `SAGE_ROOT` in sage-conf_conda (Tractable)
* **File:** `pkgs/sage-conf_conda/setup.py` line 23
* Hardcoded path-joining logic for `SAGE_ROOT` may fail in non-standard or
  VPATH builds.
* **Action:** generalize to standard env var discovery.

### E — `.m4` vs generated `pyproject.toml` drift (Scale)
* **Path:** `pkgs/*/pyproject.toml.m4` (113 packages)
* Discrepancies between templates and generated files can cause silent build
  regressions.
* **Action:** audit for stale metadata or missing dependencies in generated
  files.
