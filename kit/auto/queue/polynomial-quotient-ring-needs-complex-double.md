---
slug: polynomial-quotient-ring-needs-complex-double
state: scoped
issue:
pr:
branch: fix/polynomial-quotient-ring-needs-complex-double
venv: .venv
tier: beginner
snt: neglected
files:
  - src/sage/rings/polynomial/polynomial_quotient_ring.py
doctest_cmd: sage -t --optional=sage,sage.libs.pari,sage.rings.complex_double src/sage/rings/polynomial/polynomial_quotient_ring.py
repro: kit/auto/artifacts/polynomial-quotient-ring-needs-complex-double/repro.py
negative_control: n/a
repro_status: reproduced
deliverable: pr
expected_failure: ModuleNotFoundError: No module named 'sage.rings.complex_double'
---

# polynomial_quotient_ring: add # needs sage.rings.complex_double to absolute_degree doctest

## Symptom

In a modular installation where `passagemath-categories` and `passagemath-pari` are installed without `passagemath-modules`, running `sage -t` on `src/sage/rings/polynomial/polynomial_quotient_ring.py` fails with:

```text
File "sage/rings/polynomial/polynomial_quotient_ring.py", line 2471, in sage.rings.polynomial.polynomial_quotient_ring.PolynomialQuotientRing_field.absolute_degree
Failed example:
    S = R.quotient(x^2 + 1)
Exception raised:
    ...
    ModuleNotFoundError: No module named 'sage.rings.complex_double'
```

Observed in CI on `test-mod (sagemath_pari-check)` for PR #2700 (job 99024864906) and noted by mkoeppe on PR #2293.

## Root cause

`src/sage/rings/polynomial/polynomial_quotient_ring.py`: `PolynomialQuotientRing_field.absolute_degree` contains a doctest example with `R.<x> = PolynomialRing(RR); S = R.quotient(x^2 + 1)` (lines 2470–2473). In modular environments without `passagemath-flint` or `passagemath-mpfr`, `RR` aliases `RDF` (`src/sage/rings/all__sagemath_categories.py:89`).

`PolynomialQuotientRingFactory.create_object()` calls `polynomial.is_irreducible()`. `Polynomial.is_irreducible` (`src/sage/rings/polynomial/polynomial_element.pyx:10261`) calls `self.factor()`, which calls `RealDoubleField_class._factor_univariate_polynomial()` (`src/sage/rings/real_double.pyx:660`). That method requires `from sage.rings.complex_double import CDF` to compute roots.

`sage.rings.complex_double` is packaged in `passagemath-modules` (`pkgs/sagemath-modules/MANIFEST.in:255`), which is not a dependency of `passagemath-categories` or `passagemath-pari`. The doctest lacks `# needs sage.rings.complex_double`.

## Approach

Add `# needs sage.rings.complex_double` to the `RR` block in
`PolynomialQuotientRing_field.absolute_degree`. The two neighbouring blocks in
the same docstring already carry `# needs sage.rings.number_field` and
`# needs sage.rings.finite_rings`, so the guard matches house style and the
diff is one line.

Beginner tier by the effort scale in `kit/strategy.md`, and worth doing
anyway. The failing job is `test-mod (sagemath_pari-check)`, which runs on
every PR to the monorepo, so the false failure costs every contributor a log
read. PR #2700 carried 43 red checks and merged regardless, which is what
happens once a red CI stops meaning anything. One line removes one of those.

## Evidence

Verified 2026-08-29.

- claim: sage.rings.complex_double ships in passagemath-modules
  check: `grep -rn complex_double pkgs/*/MANIFEST.in` -> one hit, `pkgs/sagemath-modules/MANIFEST.in:255`
- claim: sage.rings.complex_double is a valid doctest feature tag
  check: `src/sage/features/sagemath.py:932` defines `sage__rings__complex_double`, registered in the feature list at line 1413
- claim: the RR block carries no needs guard while its neighbours do
  check: `sed -n '2462,2478p' src/sage/rings/polynomial/polynomial_quotient_ring.py` -> the `PolynomialRing(RR)` block is unguarded between two guarded blocks
- claim: the repro fails with ModuleNotFoundError
  check: `.venv/bin/python kit/auto/artifacts/polynomial-quotient-ring-needs-complex-double/repro.py` -> exit 1 (run by Gemini)
- claim: no issue exists for this yet
  check: `gh search issues --repo passagemath/passagemath polynomial_quotient_ring --state open` and `--state closed` -> both empty

## Log

- 2026-08-28 scoped by Gemini from CI on PR #2700 (job 99024864906) and mkoeppe's comment on PR #2293
- 2026-08-29 verified: feature tag exists, packaging confirmed, no duplicate issue. Retiered intermediate -> beginner (effort only)
- 2026-08-29 deliverable set to pr: the reserve-beginner-work-for-students rule no longer applies
