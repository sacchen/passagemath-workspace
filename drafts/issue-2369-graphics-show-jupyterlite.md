# Issue #2369: Graphics.show() does not work in JupyterLite (XPython)

## Status (2026-07-16)

Issue comment posted 2026-05-14 (root cause only). Fix implemented locally in
`src/sage/repl/ipython_extension.py`, **verified empirically** (see below), NOT yet pushed/PR'd.
Local passagemath main fast-forwarded to upstream (10.8.6.rc2 era, merge of #2478);
fix reapplied cleanly. Upstream has not touched `_running_in_notebook` — fix still needed.

## Verification (2026-07-16) — all four claims confirmed empirically

1. **Live ipykernel** (jupyter_client + real ZMQInteractiveShell, ipykernel 7.2.0):
   old check True, new check True → no regression for normal Jupyter users.
   Source-confirmed: `ipykernel/ipkernel.py` passes `kernel=self` at shell construction,
   so the `kernel = Any()` trait (default None) is set before any user code runs.
2. **TerminalInteractiveShell** instance: new check False. `SageTestShell` extends
   `TerminalInteractiveShell` (`src/sage/repl/interpreter.py:315`) → also False.
3. **XPythonShell** (real xeus-python-shell package): fresh instance → False
   (`self.kernel = None` in `__init__`); after `ip.kernel = XKernel()` → True.
   xeus-python `xinterpreter.cpp` `configure_impl()` does
   `m_ipython_shell.attr("kernel") = XKernel()` during interpreter init, before any
   execute request — so user code always sees a live kernel object.
4. Old check in an env without ipykernel: ImportError → False (reproduces the bug).

## Red-team / end-to-end verification (2026-07-16) — REAL xpython kernel

xeus-python ships as a **native** kernel on conda-forge; ran the real thing locally
(micromamba env, xeus-python + passagemath-plot/repl 10.8.6, driven via jupyter_client):

- **Bug reproduced unpatched**: `circle((0,0),1).show()` in real xpython kernel →
  show() returns, **zero display_data messages emitted**. Exactly the reported symptom.
- **Fix verified patched**: same kernel, same code, patched `_running_in_notebook` →
  `display_data` with `image/svg+xml` emitted. Complete fix demonstration.
- **display() plumbing confirmed**: `IPython.display.display(Image(png))` in xpython
  publishes real display_data (`image/png`). Shell reports `kernel=XKernel` at user-code time.
- **Doctests, patched vs unpatched: zero delta.**
  `ipython_extension.py` (env sage.all__sagemath_repl): 8 failures both ways — all
  pre-existing environmental (`%%fortran` needs meson; non-preparsed int has no .factor()).
  `graphics.py` (env sage.all__sagemath_plot): 1 failure — the known pre-existing
  tachyon `_rich_repr_` warning in `display_immediately` (documented before this fix existed).
- **Call-site audit (current upstream)**: the `display()` fallback in graphics.py:2356 /
  multigraphics.py:779 is already upstream and wrapped in `except Exception: pass`, so a
  wrong True degrades to old behavior, never crashes. cython `--view-annotate auto` site
  now picks `displayhtml` in xpython — correct direction.
- **Behavior-change matrix**: old→new flips only for shells with `.kernel` that aren't
  `ZMQInteractiveShell` (XPythonShell — intended). ipykernel-based shells (Jupyter, Colab,
  Spyder, VS Code) already True both ways. Terminal/doctest/marimo False both ways.
  old=True→new=False would need a ZMQInteractiveShell constructed without `kernel=` —
  ipykernel itself always passes it (ipkernel.py shell construction).

**Residual risk (only gap):** native xpython ≠ WASM build in an actual browser JupyterLite.
Same C++ interpreter code path (`configure_impl` sets `.kernel`) and frontend rendering of
display_data is kernel-independent, so risk is minimal — but a true in-browser JupyterLite
smoke test has not been run.

**Unrelated observation (out of scope, possibly worth its own issue):** cysignals'
interrupt handler aborts the native xpython kernel with SIGABRT on shutdown/interrupt
(`python_check_interrupt` → pybind11 terminate). Pre-existing, unrelated to this fix.

## Issue comment draft

Tracked this down to `_running_in_notebook()` in `src/sage/repl/ipython_extension.py`:

```python
def _running_in_notebook():
    try:
        from ipykernel.zmqshell import ZMQInteractiveShell
    except ImportError:
        return False
    return isinstance(get_ipython(), ZMQInteractiveShell)
```

JupyterLite's XPython kernel doesn't use `ipykernel`. It uses [xeus-python-shell](https://github.com/jupyter-xeus/xeus-python-shell), whose `XPythonShell` subclasses `IPython.core.interactiveshell.InteractiveShell` directly, not `ZMQInteractiveShell`. So in a JupyterLite environment `ipykernel` isn't installed, the import raises `ImportError`, and `_running_in_notebook()` returns `False`. The `show()` fallback that calls `IPython.display.display(...)` never fires.

One approach: check for the `.kernel` attribute instead:

```python
def _running_in_notebook():
    ip = get_ipython()
    if ip is None:
        return False
    return getattr(ip, 'kernel', None) is not None
```

Both `ZMQInteractiveShell` (ipykernel) and `XPythonShell` (xeus-python) have `.kernel` set to a live kernel object at execution time — xeus-python's C++ layer sets it in [xinterpreter.cpp](https://github.com/jupyter-xeus/xeus-python/blob/main/src/xinterpreter.cpp) immediately before any user code runs. `TerminalInteractiveShell` and Sage's doctest shell don't set it. No `ipykernel` import needed, so no `ImportError` in JupyterLite.

Marimo doesn't use IPython's shell at all — `get_ipython()` returns `None` there regardless, so it's unaffected either way.

---

## Fix

File: `src/sage/repl/ipython_extension.py`, lines 77–82.

```diff
 def _running_in_notebook():
-    try:
-        from ipykernel.zmqshell import ZMQInteractiveShell
-    except ImportError:
+    ip = get_ipython()
+    if ip is None:
         return False
-    return isinstance(get_ipython(), ZMQInteractiveShell)
+    return getattr(ip, 'kernel', None) is not None
```

`get_ipython` is already imported at the top of the file (`from IPython.core.getipython import get_ipython`). No new dependencies.

## Call sites

`_running_in_notebook()` has four call sites:

1. `ipython_extension.py:508` — `%%cython --view-annotate auto` magic: chooses `displayhtml` vs `webbrowser`. In xeus-python, now correctly uses `displayhtml`. **Behavior change is correct.**
2. `graphics.py:2282` — `Graphics.show()` fallback: calls `IPython.display.display(SVG/Image)` when rich output manager can't handle PNG. This is the primary fix target.
3. `multigraphics.py:715` — same fallback for `MultiGraphics.show()`.

## Verification notes

- `SageTestShell` (doctest runner) extends `TerminalInteractiveShell` — no `.kernel` attribute → returns `False`. Existing doctest in `show()` still passes.
- `ZMQInteractiveShell` (ipykernel, Sage Jupyter kernel) has `.kernel = Any()` set to live `IPythonKernel` → returns `True`. No regression for normal Sage kernel users.
- `XPythonShell` (xeus-python): `self.kernel = None` at `__init__`, but C++ layer sets it to `XKernel()` immediately before any user code runs → returns `True`. Fixes the bug.
- `TerminalInteractiveShell` (IPython CLI): no `.kernel` → returns `False`. No regression.
- marimo: `get_ipython()` returns `None` → returns `False`. Unaffected.

## Pre-PR checklist

- [ ] `git merge upstream/main` (local main is ~15 commits behind; upstream has #2366, #2368, and others)
- [ ] Post issue comment first (above draft)
- [ ] Open PR targeting `passagemath/passagemath:main`
- [ ] PR description: reference issue #2369, explain xeus-python class hierarchy
