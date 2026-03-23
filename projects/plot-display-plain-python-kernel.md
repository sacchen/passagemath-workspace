# Project: Fix plot display in plain Python kernels

**For:** A Python developer comfortable with Jupyter internals — IPython display
protocol, `_repr_*` methods, how notebooks decide what to show.

**Effort:** Half a day. Two files, ~30 lines each.

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

**Refactor `_rich_repr_()` to go through `_repr_png_()`** — not a standalone addition.
mkoeppe's direction: `_repr_png_()` becomes the canonical PNG implementation;
`_rich_repr_()` calls it for the PNG case. One implementation, two protocols.

Two files to touch: `src/sage/plot/graphics.py` (`Graphics`) and
`src/sage/plot/multigraphics.py` (`MultiGraphics`). Same changes in each.

### Step 1: Add `_repr_png_()` (insert after `_rich_repr_()` in each class)

The implementation replicates the PNG path from `save()` using `BytesIO` instead of
a temp file. Match `save()` closely: merge options the same way, back up rcParams,
set `FigureCanvasAgg`, call `tight_layout()`, restore rcParams in a `finally` block.

**`src/sage/plot/graphics.py`** — `Graphics._repr_png_()`:

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
    from matplotlib import rcParams
    from matplotlib.backends.backend_agg import FigureCanvasAgg
    options = {}
    options.update(self.SHOW_OPTIONS)
    options.update(self._extra_kwds)
    dpi = options.pop('dpi')
    transparent = options.pop('transparent')
    fig_tight = options.pop('fig_tight')
    rc_backup = (rcParams['ps.useafm'], rcParams['pdf.use14corefonts'],
                 rcParams['text.usetex'])
    try:
        figure = self.matplotlib(**options)
        figure.set_canvas(FigureCanvasAgg(figure))
        figure.tight_layout()
        opts = {'dpi': dpi, 'transparent': transparent}
        if fig_tight:
            opts['bbox_inches'] = 'tight'
        if self._bbox_extra_artists:
            opts['bbox_extra_artists'] = self._bbox_extra_artists
        buf = BytesIO()
        figure.savefig(buf, format='png', **opts)
        return buf.getvalue()
    except Exception:
        return None
    finally:
        (rcParams['ps.useafm'], rcParams['pdf.use14corefonts'],
         rcParams['text.usetex']) = rc_backup
```

**`src/sage/plot/multigraphics.py`** — `MultiGraphics._repr_png_()`:

`MultiGraphics.save()` reads `dpi/transparent/fig_tight` from `Graphics.SHOW_OPTIONS`
(not `self._extra_kwds`) and calls `self.matplotlib()` with no extra kwargs — match that:

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
    from matplotlib import rcParams
    from matplotlib.backends.backend_agg import FigureCanvasAgg
    dpi = Graphics.SHOW_OPTIONS['dpi']
    transparent = Graphics.SHOW_OPTIONS['transparent']
    fig_tight = Graphics.SHOW_OPTIONS['fig_tight']
    rc_backup = (rcParams['ps.useafm'], rcParams['pdf.use14corefonts'],
                 rcParams['text.usetex'])
    try:
        figure = self.matplotlib()
        figure.set_canvas(FigureCanvasAgg(figure))
        if isinstance(self, GraphicsArray):
            figure.tight_layout()
        opts = {'dpi': dpi, 'transparent': transparent}
        if fig_tight:
            opts['bbox_inches'] = 'tight'
        buf = BytesIO()
        figure.savefig(buf, format='png', **opts)
        return buf.getvalue()
    except Exception:
        return None
    finally:
        (rcParams['ps.useafm'], rcParams['pdf.use14corefonts'],
         rcParams['text.usetex']) = rc_backup
```

### Step 2: Refactor `_rich_repr_()` in each class to call `_repr_png_()`

The loop currently calls `graphics_from_save` for every format. Change it so the `.png`
case goes through `_repr_png_()` instead. `OutputBuffer` accepts bytes directly — no
temp file needed.

Replace the loop body in **both** `Graphics._rich_repr_()` (graphics.py:1009) and
`MultiGraphics._rich_repr_()` (multigraphics.py:208):

```python
for file_ext, output_container in preferred:
    if output_container in display_manager.supported_output():
        if file_ext == '.png':
            png_data = self._repr_png_()
            if png_data is not None:
                from sage.repl.rich_output.buffer import OutputBuffer
                return output_container(OutputBuffer(png_data))
        else:
            return display_manager.graphics_from_save(
                self.save, kwds, file_ext, output_container)
```

Non-PNG formats (SVG, PDF, JPG) are unchanged — they still go through `graphics_from_save`.

## Verify

```bash
cd passagemath   # monorepo root
uv venv .venv && uv pip install -e pkgs/sagemath-plot
```

Manual smoke test (no Sage kernel needed):

```python
from sage.plot.line import line
from sage.plot.multigraphics import graphics_array
from sage.plot.circle import circle

G = line([(0, 0), (1, 1)])
png = G._repr_png_()
assert png is not None and png[:8] == b'\x89PNG\r\n\x1a\n'
print(f"Graphics OK — {len(png)} bytes")

GA = graphics_array([line([(0,0),(1,1)]), circle((0,0),1)])
png2 = GA._repr_png_()
assert png2 is not None and png2[:8] == b'\x89PNG\r\n\x1a\n'
print(f"MultiGraphics OK — {len(png2)} bytes")
```

Run doctests:

```bash
uv run python -m sage.doctest src/sage/plot/graphics.py
uv run python -m sage.doctest src/sage/plot/multigraphics.py
```

## Notes

- `Graphics._rich_repr_()` is at line 976; `MultiGraphics._rich_repr_()` is at line 170.
- `MultiGraphics.matplotlib()` exists (line 269) and takes `(figure=None, figsize=None, **kwds)`. Call with no args.
- `MultiGraphics` has no `_bbox_extra_artists` — omit that guard in its `_repr_png_()`.
- The `isinstance(self, GraphicsArray)` check in `tight_layout()` mirrors what `MultiGraphics.save()` does.
- `_repr_svg_()` can follow the same refactoring pattern later — out of scope here.
- Does not affect 3D graphics (`plot3d/`) — separate display system, separate effort.
- **passagemath-pkg-* repos checked (2026-03-22):** two external packages implement
  `_rich_repr_()`. Neither is in scope for this PR:
  - `passagemath-pkg-slabbe` (`slabbe/tikz_picture.py`, `TikzPicture`): renders via LaTeX,
    explicitly checks for `BackendIPythonNotebook` — separate LaTeX toolchain concern.
  - `passagemath-pkg-flexrilog` (`NAC_coloring.py`, `graph_motion.py`): `NAC_coloring`
    delegates to `self.plot()._rich_repr_()` and would need its own `_repr_png_()` calling
    `self.plot()._repr_png_()`; `graph_motion` only returns text (SVG path commented out).
  Note: `gh search code` did not index flexrilog — it is not a reliable tool for exhaustive
  org-wide audits.

## Contact

File a PR against [passagemath/passagemath](https://github.com/passagemath/passagemath).
Reference issue #2236 in the commit message.
