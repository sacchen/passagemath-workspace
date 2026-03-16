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

`src/sage/combinat/partition.py` ships in `passagemath-combinat`. To find which package owns a file, search `pkgs/sagemath-*/MANIFEST.in`.

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

## Find work

Start here: [Shovel-ready issues for the Polyhedral Geometry and Optimization team](https://github.com/passagemath/passagemath/issues/2269#issuecomment-4070368357) — curated issues with full specs, tiered by difficulty. Pick one that fits your background and comment "I'm working on this" to claim it.

## The perfect commit

A good commit has three parts: **implementation**, **tests**, and **documentation** — all in one commit, all linked to an issue. If any part is missing, the commit isn't done.

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

The test passes if the output matches. The reader sees exactly what to expect. One artifact, two jobs.

**The rule:** don't ship a fix without a doctest that would have caught the bug before you fixed it. If you can't write one, the fix isn't finished.

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

A good commit stands alone: what changed, why, and a doctest showing it works. Style-only changes, docstring reformatting, and untested edits aren't contributions here.
