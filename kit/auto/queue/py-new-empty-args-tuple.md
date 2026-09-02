---
slug: py-new-empty-args-tuple
state: implemented
issue:
pr: 2786
branch: fix/py-new-empty-args-tuple
venv:
tier: advanced
snt: tractable
files:
  - src/sage/ext/stdsage.pxd
doctest_cmd: >-
  sage -t --optional=sage,sage.misc.cython src/sage/ext/stdsage.pxd
repro: kit/auto/artifacts/py-new-empty-args-tuple/repro/run.sh
repro_status: reproduced
expected_failure: import of the user module exits 139, Segmentation fault
negative_control: unrun
---

# PY_NEW passes NULL where tp_new requires an argument tuple

## Symptom

On the `cython-3.3` branch, importing `sage.rings.padics.common_conversion`
segfaults. The module's line 52 is a module-level
`cdef Rational rat_temp = PY_NEW(Rational)`, so the call runs at import.

## Root cause

`PY_NEW()` in `src/sage/ext/stdsage.pxd` called
`(<PyTypeObject*>t).tp_new(t, <PyObject*>NULL, <PyObject*>NULL)`. Cython 3.3
routes `tp_new` through `__Pyx_CallTpnewAsVectorcall()`, which reads the
argument tuple's size with no `NULL` check.

Whether the read faults depends on the compiler. For a no-argument
`__cinit__`, Cython marks the wrapper's `args`/`nargs` `CYTHON_UNUSED`, so the
size is dead and `-O3` deletes it. Below `-O3` it survives and the read
faults. This is why the bug presents as build-dependent, and why a first pass
at `-O3` found only the `__cinit__(self, *args)` shape.

## Approach

Pass `()`, which Cython compiles to the module's shared `__pyx_empty_tuple`.

Rejected: adding a `NULL` guard inside `PY_NEW` before the call. That leaves
every other `newfunc` caller free to pass `NULL` and does not fix the contract
violation, which is the actual defect.

## Evidence

Verified 2026-09-02. Repro at `artifacts/py-new-empty-args-tuple/repro/`,
Python 3.14.7, Cython 3.3.0, GCC 16.1.1, aarch64.

- claim: passes `NULL` where `tp_new` requires an argument tuple
  check: `src/sage/ext/stdsage.pxd:23` before the change --
    `tp_new(t, <PyObject*>NULL, <PyObject*>NULL)`
- claim: reads the argument tuple's size with no `NULL` check
  check: generated `variants_before.c`, `__Pyx_CallTpnewAsVectorcall` --
    `Py_ssize_t a_size = __Pyx_PyTuple_GET_SIZE(a);` with no guard, while the
    keyword dict above it is read as `k ? __Pyx_PyDict_GET_SIZE(k) : 0`
- claim: that read lands above the one check the function does make
  check: `objdump -d ratlike.so` at `-O2`, `__Pyx_CallTpnewAsVectorcall` --
    `ldr x19, [x2, #16]` (x2 = args, offset 16 = ob_size) precedes
    `cbz x3` (x3 = kwargs)
- claim: follows `CYTHON_VECTORCALL` for non-limited-API CPython builds
  check: `gcc -E -dM` on the generated C -> `CYTHON_VECTORCALL 1`,
    `CYTHON_USE_TYPE_SPECS 0`, `CYTHON_ASSUME_SAFE_SIZE 1`; the version gate
    on `CYTHON_VECTORCALL_TPNEW` applies only when type specs are on
- claim: which Cython compiles to the shared `__pyx_empty_tuple`
  check: generated C for the patched header --
    `tp_new(..., ((PyObject *)__pyx_mstate_global->__pyx_empty_tuple), ...)`,
    and the tuple is built in module-state init, before the module body runs
- claim: so construction stays a single load rather than an allocation
  check: same line; a module-state field load, no `PyTuple_New` at the call site
- claim: `PY_SET_TP_NEW()` swaps the `tp_new` pointer and is unchanged
  check: `git diff` on the branch touches only the `PY_NEW` body and its
    docstring
- claim: replace `tp_new` at import with a `cdef fast_tp_new`
  check: `src/sage/rings/integer.pyx:7832` and `:7854` (module-level
    `hook_fast_tp_functions()`); `src/sage/rings/real_double.pyx:2190`
- claim: `Rational` does not
  check: `grep -n "tp_new\|hook_tp_functions" src/sage/rings/rational.pyx`
    -> no hits; `__cinit__(self)` at `rational.pyx:499`
- claim: line 52 is a module-level `cdef Rational rat_temp = PY_NEW(Rational)`
  check: `src/sage/rings/padics/common_conversion.pyx:52`
- claim: the import segfaults at `-O0`, `-O1` and `-O2`; patched, it is clean
  check: `sh repro/run.sh` -> before O0/O1/O2 SIGSEGV, after O0/O1/O2/O3 ok
- claim: the shape where the size is live and the crash reproduces at every level
  check: same run, `before_va` -> SIGSEGV at O0, O1, O2 and O3

### Draft claims

Verbatim, backtick-free substrings of the drafts, which is how `claims.py`
matches a flagged sentence to its evidence.

- claim: requires an argument tuple
  check: `src/sage/ext/stdsage.pxd:23` before the change passed `NULL`; the
    `newfunc` signature is `PyObject *(*)(PyTypeObject *, PyObject *args,
    PyObject *kwds)`
- claim: PY_NEW passed NULL for the positional arguments to tp_new
  check: same line
- claim: which Cython compiles to the shared
  check: generated C for the patched header --
    `tp_new(..., ((PyObject *)__pyx_mstate_global->__pyx_empty_tuple), ...)`
- claim: than an allocation
  check: same line; a module-state field load, no `PyTuple_New` at the call site
- claim: the shape where the size is live and the crash reproduces at every level
  check: `sh repro/run.sh` -> `before_va` SIGSEGV at O0, O1, O2 and O3

### Cython 3.2.9 comparison, 2026-09-02

Built the same repro with Cython 3.2.9 (the `passagemath/.venv` toolchain).
Its generated C contains no `CallTpnewAsVectorcall` at all.

- `before_va` (`__cinit__(self, *args)`): SIGSEGV at -O2 and -O3
- `before` (`__cinit__(self)`): clean at -O2 and -O3

So the `*args` shape faults before Cython 3.3, through the `__cinit__`
wrapper reading the size it actually needs. Cython 3.3 widens the bug from
that one shape to every extension type, because the vectorcall adapter reads
the size even when the wrapper does not use it. `Rational` has a no-argument
`__cinit__`, so the `common_conversion` crash specifically needs 3.3.

This is why the pr-body sentence "it arrives with Cython 3.3 rather than with
Python 3.14" is too strong as written: the adapter arrives with 3.3, the bug
does not.

### Not established

- claim: This explains the import crash in `sage.rings.padics.common_conversion`
  check: NOT reproduced in a built sage tree. The only local build is a
    Cython 3.2.9 wheel install whose `rational.so` is unstripped, keeps 98
    `__Pyx_*` statics and contains zero `CallTpnewAsVectorcall`, so the path
    does not exist there; `padics` is not installed in it at all. The claim
    rests on the mechanism plus the standalone repro, not on an in-situ crash.

## Log

- 2026-09-02 imported at state implemented; PR 2786 already open (opened by
  hand, outside the pipeline, before this task file existed)
- 2026-09-02 two-module repro built; single-module version does not
  discriminate at -O2, so the class and the PY_NEW call must be in separate
  modules to mirror rational.pyx / common_conversion.pyx
- 2026-09-02 pr-body.md and commit.txt rewritten; both disproved claims
  removed (the __cinit__ wrapper does not read the size for a no-arg
  __cinit__; the empty tuple is built in module-state init, not PyInit_)
- 2026-09-02 pr-body.md pushed to PR 2786
- 2026-09-02 a concurrent session amended and force-pushed the branch commit
  to 8fe8898198b at 00:04; its message records the Cython 3.2.9 *args result,
  which this task verified independently. commit.txt here is now stale against
  the branch and the two drafts disagree; do not push either without
  reconciling them

## Red team

- [ ] relevance:
- [ ] scope:
- [ ] accuracy:
- [ ] approach:
- [ ] execution:
- [ ] source-style:
- [ ] style:
- [ ] wording:
