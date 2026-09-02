# PY_NEW passes NULL where tp_new requires a tuple

Evidence for passagemath#2786. `PY_NEW()` in `sage/ext/stdsage.pxd` called
`tp_new(t, NULL, NULL)`. Cython 3.3 routes `tp_new` through
`__Pyx_CallTpnewAsVectorcall()`, which reads the argument tuple's size with
no `NULL` check.

## What this mirrors

`ratlike.pyx` stands in for `rational.pyx`: several `cdef` classes in one
module, the constructed one having a no-argument `__cinit__` like
`Rational`'s. `user_*.pyx` stands in for `common_conversion.pyx:52`, where
`cdef Rational rat_temp = PY_NEW(Rational)` sits at module level and so runs
at import.

Both halves matter. A single-module version of the same test does not
segfault at `-O2`, because whether the dead size load survives is a
per-translation-unit inlining decision. `PY_NEW` is inlined into the user
module rather than cimported so the repro needs no sage tree; the generated
call site is the same either way.

## Run

Needs Python 3.14.7 and Cython 3.3.0 on the path.

```
sh run.sh
```

## Result

Measured on aarch64, GCC 16.1.1, Python 3.14.7, Cython 3.3.0.

`before`/`after` construct `Ratlike`, whose `__cinit__` takes no arguments,
like `Rational`'s. `before_va`/`after_va` construct `Helper2`, whose
`__cinit__` takes `*args`.

| variant | -O0 | -O1 | -O2 | -O3 |
|---|---|---|---|---|
| before | SIGSEGV | SIGSEGV | SIGSEGV | ok |
| after | ok | ok | ok | ok |
| before_va | SIGSEGV | SIGSEGV | SIGSEGV | SIGSEGV |
| after_va | ok | ok | ok | ok |

At `-O3` the compiler deletes the size load, which is dead for a no-argument
`__cinit__`, and the crash disappears. That is why the bug presents as
build-dependent, and why a first pass at `-O3` found only the `*args` shape,
where the size is live and the crash reproduces at every level.

## The read

`__Pyx_CallTpnewAsVectorcall` compiled at `-O2`, from `objdump -d` on
`ratlike.so`. `x2` is the argument tuple and `x3` the keyword dict; offset 16
is `ob_size`.

```
ldr x19, [x2, #16]   ; args->ob_size
cbz x3, ...          ; only then: is kwargs NULL?
```

The source checks the keyword dict for `NULL` and never checks the argument
tuple. The compiler hoisted the unchecked read above the check that exists.

## Scope

`CYTHON_VECTORCALL_TPNEW` resolves to `CYTHON_VECTORCALL`, which is 1, when
`CYTHON_USE_TYPE_SPECS` is 0, as it is for non-limited-API CPython builds.
The version gate on that macro only applies under type specs. So the path
arrives with Cython 3.3 rather than with Python 3.14.

Not verified against a built sage tree; there was none available. The
`common_conversion` import crash reported on the branch is explained by this
mechanism rather than reproduced in situ.
