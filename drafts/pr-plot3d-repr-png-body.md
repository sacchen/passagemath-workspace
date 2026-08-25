Follow-up to #2351 and #2366, for the 3D part of #2236.

In a plain Python Jupyter kernel (Google Colab, marimo, VS Code with a Python kernel), evaluating a `Graphics3d` object displays the text `Graphics3d Object` instead of an image. Plain kernels look for `_repr_png_()` and friends; `Graphics3d` only implements Sage's `_rich_repr_()` protocol, which those kernels never call.

This adds `Graphics3d._repr_png_()` to `src/sage/plot/plot3d/base.pyx`. It reuses the existing `_rich_repr_tachyon()` to produce a static PNG, and returns `None` if rendering fails — for example when the tachyon executable is not available — matching the IPython `_repr_png_` protocol. This was the implementation suggested in https://github.com/passagemath/passagemath/issues/2236#issuecomment-4211169055.

```python
from sage.plot.plot3d.shapes2 import sphere
sphere()  # now displays a PNG in Colab etc., given passagemath-tachyon
```

The Sage kernel is unaffected: `SageDisplayFormatter.format()` returns early with the rich output (the Three.js scene) before IPython's formatter would look up `_repr_png_`, so there is no double display and interactive 3D works as before.

Testing done, in a venv with `passagemath-plot` built from this branch and `passagemath-tachyon` installed:

- `IPython.core.formatters.DisplayFormatter().format(sphere())` returns `image/png` (valid PNG header) plus `text/plain`.
- Same for a `Graphics3dGroup` (`sphere() + sphere((2,0,0))`).
- With the tachyon binary removed from the environment, `_repr_png_()` returns `None` and display falls back to the text repr, as before this change.
- The new doctest passes when run in isolation. The full `sage.doctest` run on this file could not be executed locally (the doctest runner segfaults at startup on Python 3.14 in `sage.cpython.atexit`, for unmodified files as well) — relying on CI for that.

One note for review: when `display_manager.preferences.graphics == 'disable'` in a Sage kernel, `_rich_repr_()` produces plain text only, the formatter falls through to IPython, and the PNG hook fires anyway. The 2D `_repr_png_()` from #2351 has the same structure, so this does not introduce a new behavior class, but flagging it in case it should be handled for both.

Not included here: a notebook fallback for `Graphics3d.show()` (analogous to the 2D one in #2351) — deferred until #2479 settles the kernel-detection pattern — and interactive Three.js output via `_repr_html_()` for plain kernels, which is a separate problem.
