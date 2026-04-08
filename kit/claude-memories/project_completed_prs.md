---
name: Completed PRs archive
description: Detailed records of merged PRs and resolved issues — preserved for context but not needed in the active index
type: project
---

## PR #6 — exception types in passagemath-pkg-numerical-interactive-mip (MERGED)

**PR:** https://github.com/passagemath/passagemath-pkg-numerical-interactive-mip/pull/6
**Issue:** https://github.com/passagemath/passagemath-pkg-numerical-interactive-mip/issues/5
**Branch:** `fix/exception-types-backend-dictionaries` on `sacchen/passagemath-pkg-numerical-interactive-mip`

- `abstract_backend_dictionary.py`: `AttributeError` → `ValueError` for standard form validation in `__init__`
- `glpk_backend_dictionary.py`: `AttributeError` → `RuntimeError` for `warm_up()` failures; updated doctests
- `coin_backend_dictionary.py`: updated doctest to match `ValueError`

Bug introduced by Matthias in commit `d06701b` (Apr 2016). Kill-shot: EAFP `except AttributeError` already present in `_vendor/interactive_simplex_method.py` — raising `AttributeError` for input validation risks swallowing real missing-attribute bugs.

## PR #2237 — importlib.metadata in configure check (MERGED, Upstream candidate, in 10.8.2.rc2)

**PR:** https://github.com/passagemath/passagemath/pull/2237
**Branch:** `fix/pkg-resources-2163` on `sacchen/passagemath`
**File:** `m4/sage_python_package_check.m4`

Replaced `pkg_resources.require()` (removed in setuptools 82) with `importlib.metadata` + `packaging.requirements.Requirement`. Lesson: new configure-time deps need three registrations: the M4 macro, `pkgs/sage-conf/pyproject.toml.m4`, and `mingw.yml` + `ci-mingw.yml`.

## Issue #2239 / PR #2240 — PIP_FIND_LINKS Windows path bug (acted on by Matthias, credited)

`PIP_FIND_LINKS=file://$SAGE_SPKG_WHEELS` → `file://D:/...` on Windows — pip rejects invalid URI. Fix: drop `file://` prefix; pip `--find-links` accepts bare absolute paths. Affected ~30 `spkg-install.in` + 66 `tox.ini`. Root cause of unexplained Windows CI failures across multiple RC cycles. Matthias responded in 35 minutes.

## PR #2253 — Partitions.cardinality() without flint (MERGED)

**PR:** https://github.com/passagemath/passagemath/pull/2253
**Branch:** `fix/partitions-cardinality-no-flint-2243`
**File:** `src/sage/combinat/partition.py`

`except ImportError: pass` left `cached_number_of_partitions` unbound. Fix: `pass` → `= None`; n≤10 fallback to `_cardinality_from_iterator()`, n>10 calls `sage__libs__flint().require()`. mkoeppe: "Looking great, thanks a lot."

## PR #2282 — pari NameError → FeatureNotPresentError (MERGED 2026-03-16)

**Branch:** `fix/pari-namedror-ell-nf`

- `ell_point.py` (6 methods) + `number_field.py` (8 methods): pari NameError → FeatureNotPresentError
- `integer_mod_ring.py`, `cusps.py`, `binary_qf.py`: same pattern
- `calculus_method.py`: lazy_import for sympy_latex + local import in `_SR_to_Sympy` (mkoeppe's startup-time request)

## Issue #2256 — doctest regressions in test-mod CI (filed, no PR)

1. `automatic_semigroup.py`: PR #2161 added unguarded `S5.rename()` at lines 417 and 524 — need `# needs sage.groups`.
2. `lazy_attribute.pyx`: PR #2148 shifted `banner()` from line 95 to 96 — hardcoded line number in doctest.

## PR #2283 — unbound imports + check_unbound_imports tool (MERGED 2026-03-21)

**PR:** https://github.com/passagemath/passagemath/pull/2283

- `padic_extension_leaves.py`: unbound NTL/FLINT names → FeatureNotPresentError pattern
- `multi_polynomial_ideal.py`: unbound Singular names → same pattern
- `chart_func.py`: removed dead try/except around sympy import (sympy always present in symbolics package)
- `tools/check_unbound_imports.py`: new AST checker that detects the `except ImportError: pass` antipattern leaving names unbound. Documented in `tools.rst`; tox env added in PR #2292.

## PR #2287 — calculus_method pickling regression (MERGED)

**PR:** https://github.com/passagemath/passagemath/pull/2287

- `calculus_method.py`: `lazy_import('sympy', 'latex', as_name='sympy_latex')` introduced a pickling regression — `sympy_latex` became unpicklable. Fix: moved lazy_import line to preserve import order; local import in `_SR_to_Sympy` instead.

## PR #2292 — docs + tox for check_unbound_imports (MERGED 2026-04-04)

**PR:** https://github.com/passagemath/passagemath/pull/2292

- `tools.rst`: documented `check_unbound_imports.py` usage and rationale
- `tox.ini`: added `check-unbound-imports` env + top-level delegating env. mkoeppe requested this post-merge from #2283.

## PR #2293 — polynomial_quotient_ring # needs sage.modules (MERGED 2026-03-23)

**PR:** https://github.com/passagemath/passagemath/pull/2293

- `polynomial_quotient_ring.py`: 3 string-conversion doctests in `_element_constructor_` needed `# needs sage.modules`. Root cause: PRs #2057 + #2069 moved functionality into sage.modules without updating guards.

## PR #2353 — LP docs: dual values and matrix patterns (MERGED 2026-04-08)

**PR:** https://github.com/passagemath/passagemath/pull/2353

- `linear_programming.rst`: documented dual values, `get_row_dual`, matrix solution extraction patterns, `simplex_or_intopt`. Came from pain points in issue #2347 and coursework in MAT 168. Level 1 of LP ergonomics progression complete.

## PR #2354 — sage.libs.linbox guards in modsym and geometry/cone (MERGED 2026-04-08)

**PR:** https://github.com/passagemath/passagemath/pull/2354

- `modsym/tests.py`, `geometry/cone.py`: added `# needs sage.libs.linbox` guards to doctests hitting linbox code paths in partial installs. Surfaced `affine_homset.py` line 414 numerical drift (99 vs 100) — flagged in PR description; mkoeppe confirmed pre-existing, wants separate issue.
