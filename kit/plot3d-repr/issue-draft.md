# Ctrl-C during ParametricSurface.triangulate() can corrupt the surface; re-rendering then crashes Python

Pressing Ctrl-C while a `ParametricSurface` is triangulating leaves the object
broken. If the interrupt lands in the face-construction loop, rendering the
same object again kills the Python process with SIGSEGV or SIGBUS in
`IndexFaceSet._separate_creases`. `sig_check()` runs inside that loop for every
surface, so no color function is needed and every `ParametricSurface` subclass
is affected. Observed on passagemath 10.8.10
(macOS arm64, Python 3.12); `parametric_surface.pyx` is unchanged on current
main (c5807b06c8).

The try/except in `triangulate()` covers only `realloc()` and `eval_grid()`.
The face-construction loop after it can also raise, through `sig_check()` on
every iteration and through a user-supplied color function. `realloc()` sets
`fcount` before any face is filled in, so an exception in the loop leaves
`fcount = m*n` with `face.vertices` unassigned past the failure point.

The retry crashes instead of raising again because of the check at the top of
`triangulate()`: `if self.render_grid == (urange, vrange) and self.fcount:
return`. For a surface built from a function, `render_grid` already holds the
domain from `__init__`, and `fcount` is nonzero from the failed attempt, so the
second call returns immediately and the renderer walks the half-built mesh. A
milder symptom of the same corruption: `face_list()` raises `IndexError`.

The script below reproduces the crash deterministically. The color function is
only a convenient way to raise inside the face loop: the `KeyboardInterrupt`
comes from the same loop iteration where `sig_check()` raises on a real Ctrl-C,
a few statements later, and any exception there, such as a `ValueError` from a
real color function, crashes the same way.

```python
from sage.all__sagemath_plot import *
from sage.plot.plot3d.parametric_surface import ParametricSurface

calls = [0]
def c(u, v):
    calls[0] += 1
    if calls[0] == 200:
        raise KeyboardInterrupt("simulating Ctrl-C in the face loop")
    return 0.5

P = ParametricSurface(lambda u, v: (u, v, u*v),
                      (srange(0, 5, 0.1), srange(0, 5, 0.1)),
                      color=(c, colormaps.gist_rainbow))
try:
    P.triangulate()
except KeyboardInterrupt:
    pass
P.save('/tmp/out.png')   # hard crash
```

The fix is to extend the existing guard to cover the whole triangulation, so
the `fcount = vcount = 0` reset also runs when the face loop raises. One change
from the current except block: `render_grid` must be left alone. `get_grid()`
returns `render_grid` for function-based surfaces, so setting it to `None`
makes every later render fail with `NotImplementedError`. That is a second,
pre-existing problem with the current guard: an interrupt that lands in
`eval_grid()` instead of the face loop does not crash, but the object can never
be rendered again. A PR with the fix and a regression doctest is ready.
