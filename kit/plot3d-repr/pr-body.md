Closes #2699.

Extends the try/except in `triangulate()` to cover the face-construction and
closure-detection loops, so a failure there resets `fcount`/`vcount` and the
next call rebuilds instead of short-circuiting onto a half-built mesh. The
`cdef` declarations move above the `try`; the loop bodies are re-indented but
otherwise unchanged.

Unlike the old except block, `render_grid` is left alone: `get_grid()` returns
it for surfaces built from a function, so clearing it made the object
permanently unrenderable after an interrupt during `eval_grid()`. Resetting
`fcount` alone defeats the short-circuit.

The new doctest raises from a color function inside the face loop and checks
recovery. It fails on unpatched code with `IndexError`. All 117 tests in the
file pass, plus 149 in `index_face_set.pyx`; the script from #2699 crashes on
the unpatched build and renders a valid PNG on this branch.
