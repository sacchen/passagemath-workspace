# Stage 2 — Implement

Input: a task file at `state: scoped`. Output: one commit on the task's
branch, `state: implemented`.

## Order of operations

1. **Read the code before touching it.** Trace the execution path. The traps that cost time before were all in this step: `render_grid` doubles as the domain `get_grid()` returns, so clearing it bricks function-based surfaces; `build/pkgs/<dep>/type` says nothing about pip installs, only the containing package's `pyproject.toml.m4` `dependencies` list does.
2. **Branch.** `git checkout -b <branch>` off current `origin/main`.
3. **Fix, then test, then document, in one commit.** In passagemath a doctest is the test and the documentation at once.
4. **The doctest must be the one that would have caught the bug.** Not an example of the feature working. Never raise `KeyboardInterrupt` in a doctest; the forker reads it as a user abort. Use `ValueError` for the same `BaseException` path.
5. **Prove the edit is live.** `sage -t` reads docstrings from the repo file and imports code from site-packages. Copy the edited `.py` into site-packages, or rebuild the `.pyx` with `kit/plot3d-repr/rebuild.sh <venv> <dotted.module> <src-dir>`. Skipping this produces false-green runs. The Cython flag list is not optional and drifts; re-read `src/meson.build` around line 280.
6. **Run a control.** Pristine source through the same rebuild. Compare against that, never against the shipped wheel.

## Known patterns

Unbound import after a failed optional import, endorsed in #2243:

```python
except ImportError:
    x_func = None          # bind to None, never pass

# at the usage site
if x_func is None:
    from sage.features.sagemath import sage__libs__X
    sage__libs__X().require()
```

A modularity claim ("works with only passagemath-plot") cannot be tested by
`sage -t`; the runner always has `passagemath-repl` present. Check with
`python -c "import importlib.util as u; print(u.find_spec('sage.repl'))"`
before believing any boundary result, and prefer a guard that does not
depend on the environment.

## Commit

Follow `~/.claude/commit-pr-style.md`. Write the message to
`kit/auto/artifacts/<slug>/commit.txt` first so `prose.py --commit` can read
it, then `git commit -F` that file. Subject is imperative, at most 72
characters, states the user-visible effect. Body is three short paragraphs:
the bug, the change, the test. Ends `Fixes #NNNN`.

Set `state: implemented` and log the date.
