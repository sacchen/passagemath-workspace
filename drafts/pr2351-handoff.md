# PR #2351 Handoff Note

## PR
passagemath/passagemath#2351
Branch: `fix/graphics-repr-png-plain-kernels` on `sacchen/passagemath`
Repo on disk: `/home/dev/sandbox/passagemath`

## What the PR does
Adds `_repr_png_()` and `_render_png_()` to `Graphics` and `MultiGraphics` so plots display
as images in plain Python Jupyter kernels (xeus-python, JupyterLite, Colab, marimo) that don't
use Sage's rich output system. Also fixes `show()` to use an IPython display fallback in those
environments.

## mkoeppe's review comments (as of 2026-04-08)

1. **[00:43]** `polytopes.hypercube(2).plot().show()` still doesn't work — just prints the string
   repr. (This was before the `show()` fix was committed; that fix is now in.)

2. **[02:21]** Doctest failure in `src/sage/plot/graphics.py` line ~2271:
   ```
   circle((0,0), 1).show()  # IPython fallback; no stdout output
   Expected nothing
   Got:
       <IPython.core.display.Image object>
   ```
   mkoeppe suggested `# not tested`.

3. **[02:41]** Same doctest failure in `src/sage/plot/multigraphics.py` line ~702:
   ```
   graphics_array([circle((0,0),1), line([(0,0),(1,1)])]).show()
   Expected nothing
   Got:
       <IPython.core.display.Image object>
   ```

## Root cause of doctest failures

The `show()` fallback condition was:
```python
if OutputImagePng not in dm._backend.supported_output() and dm.preferences.graphics != 'disable':
    from IPython.display import display, Image
    display(Image(self._render_png_(**kwds)))
    return
```

This fires whenever the backend lacks PNG — including in the Sage doctest runner when
`BackendSimple` is switched in. In that context `display(Image(...))` prints
`<IPython.core.display.Image object>` to stdout (no real Jupyter frontend).

The fix is to narrow the condition to real Jupyter kernels only using `get_ipython()`:

```python
if OutputImagePng not in dm._backend.supported_output() and dm.preferences.graphics != 'disable':
    try:
        from IPython import get_ipython
        ip = get_ipython()
        if ip is not None and hasattr(ip, 'kernel'):
            from IPython.display import display, Image
            display(Image(self._render_png_(**kwds)))
            return
    except Exception:
        pass
```

- Sage doctest (InteractiveShell, no `kernel` attr) → fallback doesn't fire → falls through to `dm.display_immediately()` → plain text
- Real Jupyter kernel (Colab, standard Jupyter) → `hasattr(ip, 'kernel')` True → fallback fires → image renders inline
- xeus-python → `get_ipython()` is None → fallback doesn't fire, but `_repr_png_()` already handles cell-result display

The doctests are then updated to match the new non-kernel behavior (plain-text output from the backend).

## Changes already made locally (NOT yet committed)

Both files edited at `/home/dev/sandbox/passagemath/src/sage/plot/`:

### `graphics.py` — `show()` docstring + implementation (~line 2259)
- Updated prose: explains fallback only fires in real IPython kernels with `kernel` attr
- Doctest changed to:
  ```python
  sage: from sage.repl.rich_output.backend_base import BackendSimple
  sage: from sage.repl.rich_output import get_display_manager
  sage: dm = get_display_manager()
  sage: previous = dm.switch_backend(BackendSimple())
  sage: circle((0,0), 1).show()
  Graphics object consisting of 1 graphics primitive
  sage: _ = dm.switch_backend(previous)
  ```
- Implementation: added `get_ipython()` + `hasattr(ip, 'kernel')` guard

### `multigraphics.py` — `show()` docstring + implementation (~line 693)
- Same prose update
- Doctest changed to:
  ```python
  sage: from sage.repl.rich_output.backend_base import BackendSimple
  sage: from sage.repl.rich_output import get_display_manager
  sage: dm = get_display_manager()
  sage: previous = dm.switch_backend(BackendSimple())
  sage: graphics_array([circle((0,0),1), line([(0,0),(1,1)])]).show()
  Graphics Array of size 1 x 2
  sage: _ = dm.switch_backend(previous)
  ```
- Implementation: same `get_ipython()` + `hasattr(ip, 'kernel')` guard

## Next step
Commit these changes and push to the PR branch:
```
cd /home/dev/sandbox/passagemath
git add src/sage/plot/graphics.py src/sage/plot/multigraphics.py
git commit -m "plot/graphics: gate show() IPython fallback on real Jupyter kernel"
git push
```

Then reply to mkoeppe's comments on the PR explaining the diagnosis and fix.

## Key style notes
- Use `mkoeppe` not first name in any public-facing text
- PR body lines should be single paragraphs (no hard wraps); use `--body-file` with `gh pr`
