# Contributing to passagemath — Getting Started

## Setup

You need [uv](https://docs.astral.sh/uv/) and a fork of the monorepo.

```bash
# Fork passagemath/passagemath on GitHub first, then:
git clone https://github.com/YOUR_USERNAME/passagemath
cd passagemath
```

Then create a venv and install the package you want to work on:

```bash
uv venv .venv
source .venv/bin/activate

# Pick one:
uv pip install passagemath-combinat   # combinatorics
uv pip install passagemath-plot       # plotting
uv pip install passagemath-polyhedra  # linear programming / polyhedra
```

## Repo structure

```
src/sage/          # all source code
pkgs/              # one subdirectory per installable package
```

A function in `src/sage/combinat/partition.py` ships in `passagemath-combinat`.
To find which package a file belongs to, search `pkgs/sagemath-*/MANIFEST.in`.

## Run a doctest

```bash
python -m sage.doctest src/sage/combinat/partition.py
```

Or in a Python shell for quick manual checks:

```python
from sage.combinat.partition import Partitions
Partitions(5).cardinality()   # should return 7
```

## Find work

Issues: https://github.com/passagemath/passagemath/issues

Filter by [`good first issue`](https://github.com/passagemath/passagemath/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22).
Claim an issue by commenting "I'm working on this." One issue per person at a time.

## Make a PR

```bash
git checkout -b fix/short-description

# make your change, run the doctest on the file you changed
python -m sage.doctest src/sage/path/to/file.py

git add src/sage/path/to/file.py
git commit -m "Fix: short description (#ISSUE_NUMBER)"
git push -u origin fix/short-description
# then open a PR on GitHub
```

One PR = one issue. Include the issue number in the commit message.

## What a good PR looks like

- Fixes exactly one thing
- Includes a doctest that would have caught the bug
- Links to the issue in the commit message
- Passes the doctest on the changed file

## What to avoid

- PEP8 / style-only PRs (not welcome)
- Docstring reformatting with no behavior change
- Changing code you haven't read and tested
