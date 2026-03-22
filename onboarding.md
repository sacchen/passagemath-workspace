# Contributing to passagemath

## What is this

[SageMath](https://www.sagemath.org/) is a 30-year-old open-source math platform — a unified interface to hundreds of math libraries (PARI, FLINT, GAP, Singular, ...) plus a large Python library covering combinatorics, number theory, geometry, algebra, and more. It has always been installed as one giant monolithic package.

passagemath is a fork that breaks SageMath into small, pip-installable pieces. Instead of installing everything, you install only what you need:

```
passagemath-combinat     # combinatorics
passagemath-polyhedra    # polyhedral geometry, linear programming
passagemath-plot         # 2D/3D plotting
passagemath-pari         # number theory via PARI/GP
...
```

The source code lives in one monorepo (`passagemath/passagemath`). Each package is a different slice of `src/sage/`. Contributing means fixing bugs or adding features in `src/sage/` — the packages are generated from the same source.

## Setup

Install [uv](https://docs.astral.sh/uv/) (see the docs for Windows instructions):

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Fork [passagemath/passagemath](https://github.com/passagemath/passagemath) on GitHub, then:

```bash
git clone https://github.com/YOUR_USERNAME/passagemath
cd passagemath
uv venv
uv pip install passagemath-combinat   # or passagemath-plot, passagemath-polyhedra
```

No activation needed — prefix commands with `uv run`.

## Repo structure

```
src/sage/          # all source code
pkgs/              # one subdirectory per installable package
```

`src/sage/combinat/partition.py` ships in `passagemath-combinat`. The shovel-ready issues specify which file to edit — install the package that matches (e.g. `passagemath-polyhedra` if you're editing files under `src/sage/geometry/`).

## Find work

Start here: [Shovel-ready issues for the Polyhedral Geometry and Optimization team](https://github.com/passagemath/passagemath/issues/2269#issuecomment-4070368357) — curated issues with full specs, tiered by difficulty. Pick one that fits your background and comment "I'm working on this" to claim it.

## Run a doctest

```bash
uv run python -m sage.doctest src/sage/combinat/partition.py
```

Quick manual check:

```bash
uv run python -c "
from sage.combinat.partition import Partitions
print(Partitions(5).cardinality())  # 7
"
```

## The perfect commit

A good commit has three parts: **implementation**, **tests**, and **documentation** — all in one commit, all linked to an issue.

In passagemath, doctests are tests and documentation at the same time. A doctest lives in the docstring of the function you changed and shows exactly what the fixed behavior looks like:

```python
def cardinality(self):
    """
    Return the number of partitions of n.

    EXAMPLES::

        sage: Partitions(5).cardinality()
        7
    """
```

The `sage:` prompt is passagemath's doctest syntax — it's like a Python `>>>` prompt but runs in the Sage environment. Each `sage:` line is executed and the next line is the expected output.

A good heuristic: the doctest should be something that would have caught the bug before you fixed it.

## Make a PR

```bash
git checkout -b fix/short-description

# edit, then verify
uv run python -m sage.doctest src/sage/path/to/file.py

git add src/sage/path/to/file.py
git commit -m "Fix: short description (#ISSUE_NUMBER)"
git push -u origin fix/short-description
```

One PR, one issue, one issue number in the commit message. The commit message explains *why* the change was made, not just what changed.

After pushing, go to your fork on GitHub — there'll be a banner prompting you to open a pull request.

## CI

When you push and open a PR, CI runs automatically — it reruns the doctests for the files you touched (and more) in a clean environment. Green = your change didn't break anything. Red = something needs attention.

**Common situation:** CI fails on something unrelated to your change. This happens — pre-existing flakiness, infrastructure noise, unrelated modules. Open the failed job logs and search for `New failures, not in baseline`. The ~30 lines after that are what matter. If the failures are in files you didn't touch, note that in a PR comment and ask.

If CI is red on something you did touch: fix it locally, run the doctest again, push. CI reruns automatically on each push.

## End to end: a real example

[PR #2253](https://github.com/passagemath/passagemath/pull/2253) is a good example of a complete contribution. Here's what the cycle looked like:

**1. Find the issue.** Running basic commands in a notebook surfaced a `NameError` from `Partitions(5).cardinality()` in environments without `passagemath-flint`. Filed it as issue #2243 and investigated.

**2. Reproduce it.** In a venv with `passagemath-combinat` but not `passagemath-flint`:

```python
from sage.combinat.partition import Partitions
Partitions(5).cardinality()  # NameError: name 'cached_number_of_partitions' is not defined
```

**3. Read the code.** Traced `cached_number_of_partitions` to a module-level `try/except ImportError` block that ended with `pass`. If the import failed, the variable was never bound.

**4. Fix it.** Changed `pass` to `cached_number_of_partitions = None`, then added a guard at the usage site to raise a clear `FeatureNotPresentError` instead of a cryptic `NameError`.

**5. Write the doctest.** Added an example in the docstring showing `Partitions(5).cardinality()` returns `7` — exactly the case that was broken.

**6. Verify locally.**

```bash
uv run python -m sage.doctest src/sage/combinat/partition.py
```

**7. Push and open the PR.** Title: `Fix NameError in Partitions.cardinality() when passagemath-flint is absent`. Linked to issue #2243 in the commit message.

**8. CI passed.** No failures in files touched.

**9. Review.** mkoeppe reviewed and merged the same day. This was a clean case — review is often a process with back-and-forth, and a few days between rounds is normal.

## When stuck

GitHub issue comments work well — the answer stays visible for others.

- **Confused about the issue spec** — comment on the GitHub issue. Say what you tried, what you expected, what you got.
- **CI is failing and you don't know why** — comment on the PR with the specific failure. mkoeppe will respond.
- **Not sure where to start** — comment on the [project tracker](https://github.com/passagemath/passagemath/issues/2269) and describe your background.
