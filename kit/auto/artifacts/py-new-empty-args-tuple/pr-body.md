Refs #2762. `PY_NEW()` passes `NULL` where `tp_new` requires an argument tuple.

Cython 3.3 routes `tp_new` through `__Pyx_CallTpnewAsVectorcall()`, which reads the argument tuple's size with no `NULL` check. Compiled at `-O2`, that read lands above the one check the function does make, on the keyword dict: `ldr x19, [x2, #16]` for `args->ob_size`, then `cbz x3` for `kwargs`. The switch selecting this path, `CYTHON_VECTORCALL_TPNEW`, follows `CYTHON_VECTORCALL` for non-limited-API CPython builds, so it arrives with Cython 3.3 rather than with Python 3.14.

The call now passes `()`, which Cython compiles to the shared `__pyx_empty_tuple`, so construction stays a single load rather than an allocation. `PY_SET_TP_NEW()` swaps the `tp_new` pointer and is unchanged.

This explains the import crash in `sage.rings.padics.common_conversion` reported on this branch. `Integer` and `RealDoubleElement` replace `tp_new` at import with a `cdef fast_tp_new` that ignores its arguments, so they are unaffected. `Rational` does not, and line 52 is a module-level `cdef Rational rat_temp = PY_NEW(Rational)` that runs at import.

Reproduced standalone with Python 3.14.7, Cython 3.3.0 and GCC, mirroring that layout: a class with `__cinit__(self)` in one module, `PY_NEW` at module level in another. Unpatched, the import segfaults at `-O0`, `-O1` and `-O2`; patched, it is clean. At `-O3` GCC deletes the size load, which is dead for a no-argument `__cinit__`, and the crash disappears. That is why the added doctest uses `__cinit__(self, *args)`, the shape where the size is live and the crash reproduces at every level.
