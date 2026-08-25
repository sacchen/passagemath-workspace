# PR draft for issue #2369

**Branch:** `running-in-notebook-kernel-attr` (local, commit `da0037840d6`, on top of upstream/main)
**Target:** `passagemath/passagemath:main`
**Title:** `Fix Graphics.show() in Jupyter kernels not based on ipykernel`
**Open with:** `gh pr create --repo passagemath/passagemath --draft --title "..." --body-file <body below>`

---

Fixes #2369.

From the issue, `_running_in_notebook()` returns False under JupyterLite's xeus-python kernel because ipykernel is not installed there, so the `IPython.display` fallback in `Graphics.show()` never runs.

This changes the check to look for the `kernel` attribute on the shell. ipykernel sets it when constructing `ZMQInteractiveShell` (`kernel=self` in ipkernel.py), and xeus-python sets it in `configure_impl()` in [xinterpreter.cpp](https://github.com/jupyter-xeus/xeus-python/blob/main/src/xinterpreter.cpp) before user code runs. Terminal shells and `SageTestShell` don't have it. Also adds a docstring and doctest for the function.

Tested with the native xeus-python kernel from conda-forge (passagemath-plot 10.8.6 installed, kernel driven via jupyter_client):

- before: `circle((0,0), 1).show()` returns with no `display_data` message (the bug)
- after: same code sends `display_data` with `image/svg+xml`
- a regular ipykernel kernel returns True with both the old and new check, so normal Jupyter is unchanged
- doctests for `sage.repl.ipython_extension` and `sage.plot.graphics` in a modular install: no new failures compared to unpatched

Not tested in an actual browser JupyterLite, only the native build of xeus-python.
