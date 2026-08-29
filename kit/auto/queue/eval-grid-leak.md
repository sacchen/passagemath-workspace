---
slug: eval-grid-leak
state: scoped
issue:
pr:
branch: fix/eval-grid-leak
venv: .venv-plot3d
tier: intermediate
snt: neglected
files:
  - src/sage/plot/plot3d/parametric_surface.pyx
doctest_cmd: >-
  sage -t --optional=sage,sage.symbolic src/sage/plot/plot3d/parametric_surface.pyx
repro: kit/auto/artifacts/eval-grid-leak/repro.py
negative_control: unrun
---

# eval_grid() leaks ulist/vlist when an exception escapes

## Symptom

Memory grows on every interrupted or failed 3D plot evaluation. Confirmed by
linear RSS growth over 30 injected failures. Affects subclasses where `f` is
None and fast tuple surfaces; plain callables never allocate.

## Root cause

`parametric_surface.pyx`, verified against `origin/main` on 2026-08-29:
`ulist` and `vlist` are allocated by `to_double_array` at lines 708/709 and
727/728, and `sig_free` runs only on the normal exit at 781/782. Six
`sig_check()` calls sit between them, at 715, 735, 745, 755, 765, and 777.
Any of them can raise and skip both frees.

## Approach

`try/finally` around the body. The pointers are NULL-initialized and
`sig_free(NULL)` is safe, so a single finally covers both allocation sites.

Pre-existing on main and deliberately kept out of PR #2700, which was scoped
to the `triangulate()` corruption.

## Evidence

- claim: sig_free runs only on the normal exit at 781/782
  check: `git show origin/main:src/sage/plot/plot3d/parametric_surface.pyx | grep -n sig_free` -> 781, 782 only

## Log

- 2026-08-29 scoped; found by an outside red team during #2700, re-confirmed against origin/main
