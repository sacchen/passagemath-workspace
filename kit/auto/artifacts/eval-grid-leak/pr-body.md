Fixes #2777. Kept out of #2700, which was scoped to the `triangulate()` corruption.

`ParametricSurface.eval_grid()` allocates `ulist` and `vlist` through `to_double_array()` and reaches `sig_free()` only on the normal exit. Six `sig_check()` calls sit between the two, and `eval_c()`, `Wrapper_rdf.call_c()` and any Python component function can raise as well. A `KeyboardInterrupt` from a slow plot, or an error out of a user-supplied function, leaks both arrays.

Two of the three evaluation branches allocate: the one where `self.f` is None, which is the path the library's `ParametricSurface` subclasses take, and the fast tuple branch when at least one component is a `Wrapper_rdf`. A tuple of plain Python callables reaches neither `to_double_array()` call, so that branch is unaffected.

Both pointers are NULL-initialized before the `try`, and `sig_free(NULL)` is `free(NULL)`, so the finally is correct whichever branch ran, and correct when `to_double_array(vrange)` raises after `ulist` was already allocated. `git diff -w` reports 40 added lines and 1 removed; the rest of the diff is the indentation the `try` forces.

A doctest in `triangulate()` drives both allocating branches, a subclass whose `eval()` raises and a tuple of two `Wrapper_rdf` components with one raising callable, and asserts that the resident set high-water mark grows by under 4 MB across 50 failed triangulations. Under `sage -t --optional=sage,sage.symbolic src/sage/plot/plot3d/parametric_surface.pyx` the file goes from 117 doctests to 119. Against the unpatched extension the new test fails with `AssertionError: 35078144` on aarch64 Linux; against the patched one it passes.
