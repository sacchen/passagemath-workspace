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
