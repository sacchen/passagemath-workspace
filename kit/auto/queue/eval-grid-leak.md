---
slug: eval-grid-leak
state: shipped
issue: 2777
pr: 2778
branch: fix/eval-grid-leak
venv: .venv-plot3d
tier: intermediate
snt: neglected
files:
  - src/sage/plot/plot3d/parametric_surface.pyx
doctest_cmd: >-
  sage -t --optional=sage,sage.symbolic src/sage/plot/plot3d/parametric_surface.pyx
repro: kit/auto/artifacts/eval-grid-leak/repro.py
negative_control: fail-on-unpatched
---

# eval_grid() leaks ulist/vlist when an exception escapes

## Symptom

Memory grows on every interrupted or failed 3D plot evaluation. Confirmed by
linear RSS growth over 30 injected failures. Affects subclasses where `f` is
None and fast tuple surfaces; plain callables never allocate.

## Root cause

`parametric_surface.pyx`: `ulist` and `vlist` are allocated by
`to_double_array()` and `sig_free` runs only on the normal exit. Six
`sig_check()` calls sit between them, and `eval_c()`, `Wrapper_rdf.call_c()`
and any Python component function can raise as well.

## Approach

`try/finally` around the body. The pointers are NULL-initialized and
`sig_free(NULL)` is safe, so a single finally covers both allocation sites.

Pre-existing on main and deliberately kept out of PR #2700, which was scoped
to the `triangulate()` corruption.

## Evidence

Verified 2026-09-01 against `upstream/main` at commit d7de09b6b3b's parent.
Line numbers are on the branch unless stated otherwise.

- claim: reaches `sig_free()` only on the normal exit
  check: `git show upstream/main:src/sage/plot/plot3d/parametric_surface.pyx | grep -n sig_free` -> 781, 782 only, both after the branch bodies
- claim: frees them only on the normal exit
  check: same as above
- claim: allocates ulist and vlist through
  check: `parametric_surface.pyx:747,748` and `:766,767` -- the two `to_double_array()` pairs; `to_double_array` is defined at `:952`
- claim: Six `sig_check()` calls sit between the two
  check: `awk 'NR>=720 && NR<=821 && /sig_check\(\)/ {print NR}' src/sage/plot/plot3d/parametric_surface.pyx` -> 754, 774, 784, 794, 804, 816; count 6. The same count on `upstream/main` inside `eval_grid`: 6.
- claim: and any Python component function can raise as well
  check: `parametric_surface.pyx:806-811` calls `fx(uu, vv)`, `fy(uu, vv)`, `fz(uu, vv)`; `:817` calls `self.f(uu, vv)`; `:826` `eval_c` is `except -1` and calls `self.eval`
- claim: Every one of those paths leaves both arrays allocated
  check: `repro.py` run 1 against the installed pristine extension -> `subclass growth=40108032`, `tuple growth=40009728`, exit 1
- claim: Every one of those paths skips both frees
  check: same as above
- claim: Two of the three evaluation branches allocate
  check: `parametric_surface.pyx:746` (`self.f is None`) and `:765` (`if fast_x or fast_y or fast_z`) call `to_double_array`; the `else` branch at `:812` and the slow-tuple block guarded at `:800` do not
- claim: is the path taken by the library's
  check: `grep -rn "ParametricSurface)" src/sage/plot/plot3d/*.pyx src/sage/plot/plot3d/*.py | grep class` -> Cone, Cylinder, Sphere, Torus in shapes.pyx; MoebiusStrip in parametric_surface.pyx. Each leaves `f` unset: `shapes.pyx` Cone:71, Cylinder:65, Sphere:46 call `ParametricSurface.__init__(self, **kwds)`, Torus:63 passes `None` explicitly, and MoebiusStrip is `parametric_surface.pyx:904`. Narrowed from "covers every subclass": `f` is a public constructor argument at `:227`, so a user subclass that passes one takes the tuple or callable branch instead. `implicit_plot3d` was checked and dropped: it returns `ImplicitSurface`, and `ParametricSurface not in ImplicitSurface.__mro__`.
- claim: which is the path the library's
  check: same as above
- claim: nothing reclaims it
  check: the arrays are `sig_malloc`ed in `to_double_array` and reachable only through the two locals; no other reference exists, so an escaping exception drops the only pointer
- claim: A try/finally around the body covers both allocation sites
  check: `git diff -w upstream/main..HEAD` -> the only non-docstring change is `try:` at `:745` and `finally:` at `:819`, enclosing both `to_double_array` pairs
- claim: covers both allocation sites at once
  check: same as above
- claim: Both pointers are NULL-initialized before the
  check: `parametric_surface.pyx:741,742` -- `cdef double* ulist = NULL` and `cdef double* vlist = NULL`, both above the `try` at `:745`. `cysignals/memory.pxd` defines `sig_free` as `free(ptr)`, and `free(NULL)` is a no-op in C.
- claim: git diff -w reports 40 added lines
  check: `git diff -w --stat upstream/main..HEAD` -> `40 insertions(+), 1 deletion(-)`
- claim: grows by under 4 MB across 50 failed triangulations
  check: `parametric_surface.pyx:551` -- `assert growth < 4_000_000, growth`, and `:545` `for _ in range(50)`
- claim: by under 4 MB across 50 failed triangulations
  check: same as above
- claim: the file goes from 117 doctests to 119
  check: `sage -t --optional=sage,sage.symbolic --environment sage.all__sagemath_plot src/sage/plot/plot3d/parametric_surface.pyx`, base docstrings -> `[117 tests, 28 failures]`; branch docstrings -> `[119 tests, ...]`
- claim: reports 35078144 bytes on aarch64 Linux
  check: five consecutive runs of the branch docstrings against the pristine build reported 35061760, 35356672, 34766848, 35700736 and 34865152 bytes. The figure is a measurement and varies by about 1 MB between runs, so no exact byte count is quoted in the drafts.
- claim: Against the unpatched extension the new test fails with
  check: same command, branch docstrings against the pristine build -> `[119 tests, 29 failures]`, the extra item being `ParametricSurface.triangulate` with `AssertionError: 35078144`; against the rebuilt patched extension -> `[119 tests, 28 failures]` and `triangulate` absent from the failure list
- claim: by about 40 MB on current
  check: `repro.py` run 1 -> `growth=40108032` and `growth=40009728`; predicted `8 * (100000 + 2) * 50 = 40000800`
- claim: The 28 other failures in that run are present on `main` too
  check: base docstrings against the pristine build -> `[117 tests, 28 failures]`; the failing items are json_repr (7), x3d_geometry (4), tachyon_repr (4), obj_repr (4), jmol_repr (4), threejs_repr (3), and the class docstring (2), none of them touched by this change

- claim: only on the normal exit
  check: `git show upstream/main:src/sage/plot/plot3d/parametric_surface.pyx | grep -n sig_free` -> 781, 782 only, both below every branch body
- claim: on both only after the evaluation loops finish
  check: same as above
- claim: calls sit between the allocation and the free
  check: the six `sig_check()` lines 754, 774, 784, 794, 804, 816 all sit between `to_double_array` at `:747` and the frees at `:820,821`
- claim: each interrupted or failed 3D plot evaluation
  check: `repro.py` drives `triangulate()` to raise 50 times per case and measures 40108032 and 40009728 bytes of growth against the pristine build
- claim: drives both branches that allocate
  check: `parametric_surface.pyx:534-554` -- `check(FailingSurface(None, grid))` for the `self.f is None` branch and `check(ParametricSurface((fast, fast, failing_function), grid))` for the fast tuple branch, where `fast_callable(u + v, domain=float)` is a `Wrapper_rdf`
- claim: and the fast tuple branch allocates when at least one component is a
  check: `parametric_surface.pyx:765` -- `if fast_x or fast_y or fast_z:` guards the second `to_double_array` pair

- claim: then frees them only after the evaluation loops finish
  check: `git show upstream/main:src/sage/plot/plot3d/parametric_surface.pyx | grep -n sig_free` -> 781, 782 only, both below every branch body
- claim: Two of the three branches allocate
  check: `parametric_surface.pyx:746` (`self.f is None`) and `:765` (`if fast_x or fast_y or fast_z`) call `to_double_array`; the `else` branch at `:812` and the slow-tuple block guarded at `:800` do not
- claim: the library's subclasses use
  check: Cone, Cylinder, Sphere, Torus in `shapes.pyx` and MoebiusStrip at `parametric_surface.pyx:904` all leave `f` unset, so all take the `self.f is None` branch. Narrowed from "every subclass": `f` is a public constructor argument at `:227`.
- claim: Both pointers are NULL-initialized and
  check: `parametric_surface.pyx:741,742` -- `cdef double* ulist = NULL` and `cdef double* vlist = NULL`, both above the `try` at `:745`. `cysignals/memory.pxd` defines `sig_free` as `free(ptr)`, and `free(NULL)` is a no-op in C.
- claim: by under 4 MB over 50 failed triangulations
  check: `parametric_surface.pyx:551` -- `assert growth < 4_000_000, growth`, and `:545` `for _ in range(50)`
- claim: On the unpatched extension the new test fails with
  check: `sage -t --optional=sage,sage.symbolic --environment sage.all__sagemath_plot src/sage/plot/plot3d/parametric_surface.pyx`, branch docstrings against the pristine build -> `[119 tests, 29 failures]`, the extra item being `ParametricSurface.triangulate` with `AssertionError: 35078144`; against the extension rebuilt from HEAD -> `[119 tests, 28 failures]` with `triangulate` absent
- claim: The other 28 failures in that run are present on
  check: base docstrings against the pristine build -> `[117 tests, 28 failures]`; the failing items are json_repr (7), x3d_geometry (4), tachyon_repr (4), obj_repr (4), jmol_repr (4), threejs_repr (3), and the class docstring (2), none of them touched by this change

- claim: Kept out of #2700, which was scoped to the
  check: `gh pr view 2700 --repo passagemath/passagemath --json title,state,files` -> "Fix crash when re-rendering an interrupted ParametricSurface", MERGED, and the only file is `src/sage/plot/plot3d/parametric_surface.pyx`. Its body opens "Closes #2699" and describes extending the `try/except` in `triangulate()`, with no mention of `eval_grid`. The provenance claim "found during the #2700 review" was dropped from the draft as unverifiable from GitHub; only the scope claim is kept.

### Negative control, built by hand

`checks/negative_control.sh` cannot run on this machine. Its Cython path shells
out to `kit/plot3d-repr/rebuild.sh`, which is macOS-only: `clang++`,
`-undefined dynamic_lookup`, a hardcoded `python3.12` site-packages path and a
`cpython-312-darwin.so` output name. The control was built by hand as
`playbooks/redteam.md` allows, with `cython --cplus -3` plus `g++ -shared`, and
both exit codes recorded above. The doctest-level result is the receipt that
matters: 117 -> 119 tests, unpatched 29 failures, patched 28.

## Red team

- [x] relevance: named the configuration and the action. Any
  `ParametricSurface` subclass (`Sphere`, `Cylinder`, `Cone`, `Torus`,
  `MoebiusStrip`) or any fast tuple surface, rendered in a session where the
  user presses Ctrl-C during a slow plot or a component function raises. That
  is `plot3d`'s ordinary interrupt path, not a contrived one. The plain-callable
  branch is genuinely unaffected, so the claim was narrowed from "3D plotting"
  to the two branches that call `to_double_array`. Duplicate hunt: no open
  issue names `eval_grid`; the leak was found during the #2700 red team and
  deliberately excluded there, which the task recorded from the start. A final
  relevance pass cut one sentence from `pr-body.md`: "The 28 other failures in
  that run are present on `main` too and come from the modular test
  environment" describes this venv, not the change, and a full install does not
  see them. `issue.md` survived the same pass unchanged, since every paragraph
  is diagnosis a maintainer needs to triage.
- [x] scope: `git diff --name-only upstream/main..HEAD` returns exactly
  `src/sage/plot/plot3d/parametric_surface.pyx`, the one path on `files:`. One
  commit ahead of `upstream/main`. `git diff -w` is 40 added and 1 removed, so
  the 104/65 plain stat is entirely the indentation the `try` forces and no
  reformatting rides along. Two neighbouring bugs were found and kept out:
  the `m == 0` segfault in `triangulate()` and the `to_double_array()`
  conversion-error leak. Both need their own issues; neither is in this commit.
- [x] accuracy: two claims died here. "a 500 by 500 surface loses about 4 MB
  per interrupted render" was wrong by a factor of 500: the arrays hold one
  double per grid line, so that case leaks `8 * (500 + 500)` = 8000 bytes, not
  4 MB. Replaced with the per-failure formula, which `repro.py` confirms
  (predicted 40000800, measured 40108032). "including MoebiusStrip and
  implicit_plot3d output" was false: `implicit_plot3d` returns an
  `ImplicitSurface`, and `ParametricSurface not in ImplicitSurface.__mro__`.
  Replaced with the five real subclasses. The `sig_check()` count was recounted
  and is 6, not the 5 an initial too-narrow line window suggested.
  `claims.py --task` reports 0 unevidenced across all three drafts.
- [x] approach: the rejected alternative is a per-branch `except BaseException:
  sig_free(...); raise`, which needs the same indentation, repeats the frees
  twice and leaves the `to_double_array(vrange)` partial-failure window
  uncovered in each copy. A narrower fix confined to the `self.f is None`
  branch was also rejected: the fast tuple branch leaks the same way, measured
  at 40009728 bytes. Asked what the fix breaks: nothing reads `ulist`/`vlist`
  after the loops, so moving the frees into a `finally` cannot shorten a
  lifetime. `sig_free(NULL)` was already relied on by the pre-fix code, since
  the plain-callable and slow-tuple branches reached the same two calls with
  both pointers NULL.
- [x] execution: negative control run in both directions, doctest level:
  unpatched `[119 tests, 29 failures]` with `AssertionError: 35078144` on
  `ParametricSurface.triangulate`, patched `[119 tests, 28 failures]` with
  `triangulate` gone from the list. Read the generated C rather than trusting
  the source: the `finally` emits `sig_free` on both the normal-exit and the
  exception-exit path, and the exception is re-raised through
  `__Pyx_ErrRestore` with `__pyx_lineno`, `__pyx_clineno` and `__pyx_filename`
  preserved, so nothing is swallowed. Checked the things a diff hides: no
  `return` inside the `try`, both pointers assigned exactly once so no double
  free, and `sig_check()` raises an ordinary Python exception rather than using
  `setjmp`, which is what makes `try/finally` safe here. Behaviour is unchanged
  on all five evaluation paths (callable, subclass, tuple-slow, tuple-fast,
  tuple-mixed): identical face counts and bounding boxes before and after, and
  20 triangulations take 0.095s unpatched against 0.098s patched.
- [x] source-style: `checks/source-style.sh` reports 0 errors and 0 warnings on
  the changed lines. Read the added docstring paragraph cold: it names the two
  branches it covers ("subclasses and fast callable tuples") rather than saying
  "the evaluation", which is the vaguer phrasing the first draft used. The
  added test lines are doctest input, not prose, so the markup conventions in
  `review-conventions.md` do not apply to them. Sibling scan of the touched
  docstring found `:issue:` used on the neighbouring 2699 test; this test has
  no issue number yet, so the reference is deferred to the amend step rather
  than invented.
- [x] style: `prose.py` reports 0 errors and 0 warnings on `pr-body.md` and
  `issue.md`, and 0 errors with 2 accepted warnings on `commit.txt`
  (`Co-Authored-By`, matching the merged precedent in #2698, #2700 and #2708;
  and `Refs:` rather than `Fixes #N`, which is the placeholder until the issue
  is filed). The first `pr-body.md` draft ran to five paragraphs and was cut to
  four by deleting the follow-up paragraph whole rather than compressing the
  survivors, per the drift rule; the two follow-ups live on this task instead.
  Also cut a "Reviewing with git diff -w is worth it" sentence that `prose.py`
  flagged as signposting.
- [x] wording: hunted overstatement. The title says "when evaluation raises",
  not "fixes a memory leak in plot3d", which would overstate the reach past the
  two allocating branches. "never allocate" survives on the plain-callable
  branch because it is literally true and evidenced at `:812`. Dropped "so
  memory grows on every interrupted or failed 3D plot evaluation" in favour of
  past tense for the bug and present tense for the fix. The remaining
  categorical, "Every one of those paths", is checked by `repro.py` covering
  both branches rather than asserted. A final pass before shipping caught one
  more: "covers every `ParametricSurface` subclass" was true of the five
  subclasses in the library but not of the class, since `f` is a public
  constructor argument and a subclass that passes one takes a different
  branch. Narrowed to "the path the library's subclasses take" in both
  `pr-body.md` and `issue.md`. The same pass caught the exact byte count being
  quoted as if reproducible: five runs gave 35061760, 35356672, 34766848,
  35700736 and 34865152, a spread of about 1 MB. Softening it to "about 35 MB"
  tripped the drift check for lost specifics, so the number stays and carries
  the qualifier "on aarch64 Linux" instead, which is specific and tells a
  reviewer the figure is one platform's measurement. Everything was validated
  on a single configuration: aarch64, glibc 2.43, CPython 3.14, and a 16 KB
  page size, which is not the 4 KB most Linux CI runs on. The signal-to-noise
  margin makes a page-size difference immaterial to the verdict (noise 0 to
  426 KB, threshold 4 MB, signal 35 to 40 MB, so roughly nine times headroom
  on each side), but the exact byte count is not reproducible off this box,
  and macOS and Windows were not exercised at all.

## Log

- 2026-08-29 scoped; found by an outside red team during #2700, re-confirmed against origin/main
- 2026-09-01 implemented; try/finally plus a two-branch memory doctest; commit d7de09b6b3b
- 2026-09-01 red teamed on all eight axes; two accuracy errors corrected (the 4 MB
  per-render figure and the implicit_plot3d subclass claim)
- 2026-09-01 issue #2777 filed; commit amended to Fixes #2777; branch pushed to
  the fork; draft PR #2778 opened; state -> shipped
- 2026-09-01 relevance pass: cut the 28-other-failures sentence from pr-body.md
  as local-environment detail; issue.md unchanged
- 2026-09-01 pr-body.md shortened for mkoeppe by dropping three sentences whole
  (generated-C internals, the per-call leak size, the try/finally topic
  sentence); survivors kept verbatim so drift reports 0 needing re-verification.
  Byte count qualified "on this machine" after five runs showed 1 MB of variance
- 2026-09-01 final wording pass: narrowed "covers every ParametricSurface subclass"
  to the library's subclasses in pr-body.md and issue.md
- 2026-09-01 negative control built by hand (rebuild.sh is macOS-only) and run in
  both directions: unpatched 29 failures, patched 28; state -> ready

## Follow-ups, not in this commit

- `triangulate()` dereferences `self._faces[0]` when `vrange` holds one value.
  `m` is then 0, `realloc()` allocated no faces, and the wrap-around loop at
  `:650` reads unallocated memory. Segfaults on `upstream/main` and on this
  branch alike; reproduced with a subclass whose `eval()` returns normally on a
  `(range(2000), [0.0])` grid, exit 139.
- `to_double_array()` leaks its own buffer if the `for a in py_list` conversion
  raises. Not reachable through `triangulate()`, which floats both ranges
  first, so it needs its own issue rather than a guard here.

## Before pushing

`origin/main` is 27 commits behind `upstream/main`, so `checks/gate.sh` reports
spurious `[scope]`, `[atomic]` and `[compile]` failures against the default
base. Either sync the fork's `main` or run the gate with
`PM_BASE=upstream/main`. `PM_REPO` must also point at the branch worktree; the
default `_find_repo` picks the first checkout holding `src/sage`, which may be
a different branch.
