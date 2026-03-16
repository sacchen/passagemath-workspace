# Fix: plot display in plain Python / xeus-python kernels

**Issue:** https://github.com/passagemath/passagemath/issues/2236

## Problem

In JupyterLite (xeus-python), Google Colab, marimo, VS Code notebooks — any plain Python
kernel — Sage `Graphics` objects display as the text string
`"Graphics object consisting of 1 graphics primitive"` instead of as images.

**Root cause:** `Graphics` implements `_rich_repr_()` (Sage's custom protocol), which
only fires when the Sage kernel has installed `SageDisplayFormatter`. In a plain Python
kernel, IPython looks for `_repr_png_()`, `_repr_svg_()`, `_repr_html_()`, or
`_repr_mimebundle_()`. Graphics has none of these → falls back to text.

## Fix

Add `_repr_png_()` to `Graphics` and `MultiGraphics`. Two methods, two files, ~15 lines each.

Uses `self.matplotlib(**self._extra_kwds)` (existing method that returns a
`matplotlib.figure.Figure`) + `BytesIO` + `fig.savefig(format='png')`. Matplotlib's Agg
backend supports in-memory rendering and works in WASM (xeus-python in JupyterLite).

No risk of double-display in the Sage kernel: `SageDisplayFormatter` short-circuits
before `_repr_png_()` can be called.

## Files to change

- `src/sage/plot/graphics.py` — add after `_rich_repr_()` at line 1012
- `src/sage/plot/multigraphics.py` — add after `_rich_repr_()` at line 212

## Code

### `Graphics._repr_png_()` (graphics.py)

```python
def _repr_png_(self):
    r"""
    Return a PNG representation of this graphics object.

    This allows ``Graphics`` objects to display as images in plain Python
    Jupyter kernels (e.g. xeus-python in JupyterLite, Google Colab, marimo)
    that do not use Sage's rich output system.

    OUTPUT: ``bytes`` -- PNG image data, or ``None`` if rendering fails

    EXAMPLES::

        sage: G = line([(0, 0), (1, 1)])
        sage: png = G._repr_png_()
        sage: png[:8] == b'\x89PNG\r\n\x1a\n'
        True
    """
    from io import BytesIO
    buf = BytesIO()
    try:
        fig = self.matplotlib(**self._extra_kwds)
        fig.savefig(buf, format='png', bbox_inches='tight')
        import matplotlib.pyplot as plt
        plt.close(fig)
    except Exception:
        return None
    return buf.getvalue()
```

### `MultiGraphics._repr_png_()` (multigraphics.py)

```python
def _repr_png_(self):
    r"""
    Return a PNG representation of this graphics array.

    This allows ``MultiGraphics`` objects to display as images in plain Python
    Jupyter kernels that do not use Sage's rich output system.

    OUTPUT: ``bytes`` -- PNG image data, or ``None`` if rendering fails

    EXAMPLES::

        sage: G = graphics_array([line([(0,0),(1,1)]), circle((0,0),1)])
        sage: png = G._repr_png_()
        sage: png[:8] == b'\x89PNG\r\n\x1a\n'
        True
    """
    from io import BytesIO
    buf = BytesIO()
    try:
        fig = self.matplotlib()
        fig.savefig(buf, format='png', bbox_inches='tight')
        import matplotlib.pyplot as plt
        plt.close(fig)
    except Exception:
        return None
    return buf.getvalue()
```

## Verification

```python
# In .venv-explore (has passagemath-plot)
from sage.plot.line import line
G = line([(0, 0), (1, 1)])
png = G._repr_png_()
assert png is not None
assert png[:8] == b'\x89PNG\r\n\x1a\n'
print(f"PNG output: {len(png)} bytes")
```

JupyterLite: run `from passagemath_plot import *; line([(0,1),(1,0)])` — should render as image.

## Notes

- `_extra_kwds`: dict of `show()` options (figsize, dpi, etc.) stored on the object.
  `matplotlib()` accepts the same kwargs.
- `MultiGraphics.matplotlib()` takes no user-facing kwds — call with no args.
- `plt.close(fig)` prevents memory leaks in long-running kernels.
- Try/except: graceful fallback to text if rendering fails (headless CI, etc.).
- Does NOT affect 3D graphics (`plot3d/`) — separate display system.
