# Project: Fix plot display in plain Python kernels

**For:** A Python developer comfortable with Jupyter internals — IPython display
protocol, `_repr_*` methods, how notebooks decide what to show.

**Effort:** Half a day. Two files, ~15 lines each.

**Issue:** https://github.com/passagemath/passagemath/issues/2236

---

## What's wrong

In JupyterLite, Google Colab, marimo, or any VS Code notebook using a plain Python
kernel, this:

```python
from passagemath_plot import *
line([(0, 0), (1, 1)])
```

displays as:

```
Graphics object consisting of 1 graphics primitive
```

instead of an image.

## Why

`Graphics` implements `_rich_repr_()` — Sage's custom display protocol, which only
fires when the Sage kernel has installed `SageDisplayFormatter`. In a plain Python
kernel, IPython looks for `_repr_png_()`, `_repr_svg_()`, or `_repr_mimebundle_()`.
`Graphics` has none of these, so IPython falls back to `__repr__()` — the text string.

No risk of double-display in the Sage kernel: `SageDisplayFormatter` calls
`_rich_repr_()` first and returns early if it produces output, before IPython's
formatter (which would call `_repr_png_()`) is ever reached.

## The fix

Add `_repr_png_()` to `Graphics` and `MultiGraphics`. Each method calls
`self.matplotlib()` (already exists, returns a `matplotlib.figure.Figure`),
saves to an in-memory buffer, and returns PNG bytes.

**`src/sage/plot/graphics.py`** — add after `_rich_repr_()`:

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

**`src/sage/plot/multigraphics.py`** — add after `_rich_repr_()`:

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

## Verify

Install the package and test the method directly:

```bash
uv venv .venv
source .venv/bin/activate
uv pip install passagemath-plot
```

```python
from sage.plot.line import line
G = line([(0, 0), (1, 1)])
png = G._repr_png_()
assert png is not None
assert png[:8] == b'\x89PNG\r\n\x1a\n'
print(f"OK — {len(png)} bytes")
```

To run the doctests, you need the monorepo checked out locally (the installed package
doesn't include the source tree):

```bash
git clone https://github.com/YOUR_USERNAME/passagemath
cd passagemath
python -m sage.doctest src/sage/plot/graphics.py
python -m sage.doctest src/sage/plot/multigraphics.py
```

## Notes

- `_extra_kwds` — dict of display options (`figsize`, `aspect_ratio`, etc.) stored
  on the `Graphics` object. All keys are accepted by `matplotlib()`.
- `MultiGraphics.matplotlib()` takes no positional args — call with no arguments.
- `plt.close(fig)` prevents memory leaks in long-running kernels.
- The `try/except` ensures graceful fallback to text if rendering fails (headless CI).
- Does not affect 3D graphics (`plot3d/`) — separate display system.

## Contact

File a PR against [passagemath/passagemath](https://github.com/passagemath/passagemath).
Reference issue #2236 in the commit message.
Matthias Köppe (mkoeppe) reviews fast — one issue per comment, expects short replies.
