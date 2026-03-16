# Contributing to passagemath

## Setup

Fork [passagemath/passagemath](https://github.com/passagemath/passagemath) on GitHub, then:

```bash
git clone https://github.com/YOUR_USERNAME/passagemath
cd passagemath
uv pip install passagemath-combinat   # or passagemath-plot, passagemath-polyhedra
source .venv/bin/activate
```

uv creates `.venv` automatically on first install.

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
python -m sage.doctest src/sage/path/to/file.py

git add src/sage/path/to/file.py
git commit -m "Fix: short description (#ISSUE_NUMBER)"
git push -u origin fix/short-description
```

One PR, one issue, one issue number in the commit message. The commit message explains *why* the change was made, not just what changed.

## What good looks like

The reviewer should be able to read the commit and know: what was wrong, what the fix is, and that it works — without asking you anything. The doctest is your proof.

Don't submit style-only changes, docstring reformatting, or changes to code you haven't run.
