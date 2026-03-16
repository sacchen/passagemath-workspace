# Contributing to passagemath

## Setup

Fork [passagemath/passagemath](https://github.com/passagemath/passagemath) on GitHub, then:

```bash
git clone https://github.com/YOUR_USERNAME/passagemath
cd passagemath
uv venv .venv
source .venv/bin/activate
uv pip install passagemath-combinat   # or passagemath-plot, passagemath-polyhedra
```

## Repo structure

```
src/sage/          # all source code
pkgs/              # one subdirectory per installable package
```

`src/sage/combinat/partition.py` ships in `passagemath-combinat`. To find which package owns a file, search `pkgs/sagemath-*/MANIFEST.in`.

## Run a doctest

```bash
python -m sage.doctest src/sage/combinat/partition.py
```

Quick manual check in a Python shell:

```python
from sage.combinat.partition import Partitions
Partitions(5).cardinality()
# 7
```

## Find work

Open issues: https://github.com/passagemath/passagemath/issues

[`good first issue`](https://github.com/passagemath/passagemath/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22) is the right filter to start. Comment "I'm working on this" to claim one.

## Make a PR

```bash
git checkout -b fix/short-description

# edit, then verify
python -m sage.doctest src/sage/path/to/file.py

git add src/sage/path/to/file.py
git commit -m "Fix: short description (#ISSUE_NUMBER)"
git push -u origin fix/short-description
```

One PR, one issue. One issue number in the commit message.

## What good looks like

Each commit should change one thing, include a doctest that would have caught the bug, and link to the issue. If you can't write a doctest that demonstrates the fix, the fix isn't done yet.

Don't submit style-only changes, docstring reformatting, or changes to code you haven't run.
