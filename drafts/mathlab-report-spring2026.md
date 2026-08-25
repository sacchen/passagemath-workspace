# Davis Math Lab Project Report, Spring 2026
## Contributing to passagemath: Infrastructure, Tooling, and LP Ergonomics

**[Your Name], Undergraduate Scholar**
**Matthias Köppe, Faculty Mentor**

---

## Introduction

Passagemath is a modular, pip-installable version of SageMath, the open-source mathematics software system. Where SageMath is a monolithic install, passagemath breaks it into about 40 smaller packages that can be installed independently and used in standard Python environments---including Google Colab, JupyterLite, and marimo. This makes it possible to use powerful mathematical tools like symbolic computation, combinatorics, and linear programming without a full SageMath installation.

The passagemath research group, led by Professor Matthias Köppe, works on extending passagemath's functionality, fixing bugs, and making it easier to use for students and researchers. The group also uses passagemath as a vehicle for exploring mathematics directly---writing notebooks, running experiments, and building intuition alongside the software work.

My contributions this term fell into three areas: fixing bugs in the codebase, building tools and materials to help the group work more effectively, and exploring how to make linear programming easier to use in passagemath.

---

## Progress

### Code contributions

I made 13 pull requests that were merged into the passagemath codebase. They fall into four themes.

**Modular install robustness** (PRs #2253, #2282, #2283, #2287, #2293, #2292, #2354). This was the largest cluster of work. Passagemath's modular design means code that was written assuming a full SageMath install can silently break when only part of it is present. A common pattern: a function tries to import an optional library, the import fails silently with `except ImportError: pass`, and a name is left unbound---causing a confusing error later when that name is actually used. I fixed this pattern across combinatorics, number theory, calculus, and geometry. Along the way I also wrote `check_unbound_imports.py`, an AST analysis tool that detects this antipattern automatically across the whole codebase, and contributed documentation and a tox environment for it.

**Build and CI infrastructure** (PR #2237, issue #2239). A configure-time API that was removed in a newer version of setuptools was causing Linux build crashes; I replaced it with the current `importlib.metadata` API. I also diagnosed a Windows CI failure caused by an invalid URI format in a path variable that was affecting multiple packages across many RC cycles---Professor Köppe wrote the fix based on my diagnosis.

**Plot display in plain Python kernels** (PRs #2351, #2366). In plain Python environments like Google Colab or JupyterLite, passagemath plots were showing up as text (`Graphics object consisting of 1 graphics primitive`) instead of as images. The issue was that passagemath's `Graphics` class implemented Sage's custom display protocol but not the standard IPython protocols that plain Python kernels use. I fixed this in both `Graphics` and `MultiGraphics`. This came directly from hitting the bug while doing coursework.

**LP ergonomics** (PR #2353). I documented dual values and matrix solution patterns in the passagemath linear programming guide. This is described in more detail in the LP ergonomics section below.

I also fixed exception types in the interactive simplex backends in an external passagemath package (PR #6 in `passagemath-pkg-numerical-interactive-mip`).

My approach to finding this work was to prioritize by scale and neglectedness---infrastructure problems that affected every install or every platform, and bugs that were hard to see without understanding the modular architecture. Using AI tools made some of this feasible: running static analysis across hundreds of files and triaging CI logs across multiple platforms to find root causes.

### Onboarding and exercises

When the group expanded to include several new students in spring 2026, getting everyone set up was a recurring bottleneck. Jupyter kernels, git, and virtual environments have a lot of places to go wrong. I wrote setup documentation and an onboarding guide for the group to reduce the troubleshooting time.

I also built a series of exercise notebooks introducing common bug patterns in passagemath. Each exercise follows the same structure: encounter the bug first, trace why it happens mechanically, fix it, verify the result. The goal was to give new contributors something concrete to do quickly---touching real code, fixing a real pattern---rather than spending the first weeks just reading documentation. I also helped a teammate, Runze Yu, navigate the codebase and git workflow while he worked on a pull request.

### pm-explore

The first assignment of the term was to make a notebook exploring some part of passagemath. Getting the environment right for that---the right packages installed, the right kernel registered, imports working---took longer than the actual exploration. So I built pm-explore, a CLI tool that automates this.

Given any passagemath source file, pm-explore generates a Jupyter notebook with the environment already configured, all public classes and functions listed, and their example code pre-populated as runnable cells. It works through static analysis of the file, so it doesn't require importing it---which means it works even when the environment isn't fully set up. It also handles a tricky problem for local development: it loads the installed Sage runtime first, then injects your local version of the target file, so you can test local changes against the full runtime without rebuilding everything.

The tool ended up being useful beyond the original assignment. Any time a teammate wanted to understand what a file does without reading the source, pm-explore gives a fast interactive starting point. I later learned the passagemath documentation website has a similar feature for browsable examples; pm-explore fills the same role for working locally and experimenting with changes.

### LP ergonomics

I was taking MAT 168 (Linear and Nonlinear Optimization) and wanted to do the coursework in passagemath rather than cvxpy. The math worked, but the workflow was noticeably harder.

Three specific friction points came up. Adding constraints for matrix-structured problems required nested loops and manual index tracking, where cvxpy does it in one line. Getting dual values---which come up constantly in LP---required finding an undocumented pattern buried in the GLPK backend source. And reconstructing a solution matrix required extra bookkeeping because `get_values()` returns a flat dictionary rather than something shaped like the original variable.

I filed issue #2347 describing these pain points. Professor Köppe confirmed that the MIP interface is underdeveloped, and sketched a longer-term direction: a cvxpy-style frontend backed by passagemath's exact arithmetic and symbolic integration. This is something cvxpy can't do because it only works with floating-point numbers; passagemath can work over the rationals or number fields, which matters for algebraic certificates and exact solutions.

My first step was PR #2353, which added the dual values workflow to `linear_programming.rst` so it would at least be findable. The deeper work---vectorized constraint addition, a cleaner dual values API, eventually a higher-level frontend---requires understanding the existing backend architecture and designing the interface carefully before writing code. I traced through the backends to understand the current call paths. The right approach going forward is to accumulate concrete pain points from working through real LP problems, then bring a specific proposal to Professor Köppe before implementing anything.

I also presented this work to the group---the plotting fix in particular---to share what I had learned about how passagemath's display system works across different kernel environments.

---

## Future Plans

The main thread to continue is LP ergonomics. The immediate next step is working through more LP problems directly in passagemath, letting specific friction points accumulate, and then proposing targeted improvements---vectorized constraint addition and a dual values API that mirrors `get_values()`---for design feedback before any implementation. This is Level 2 of a three-level progression: documentation (done), ergonomic helpers (next), and eventually a higher-level frontend aligned with Professor Köppe's longer-term architectural direction.

I also plan to present this work at the Math Lab poster session in Fall 2026.

---

## References

- passagemath repository: https://github.com/passagemath/passagemath
- Issue #2347 (MIP ergonomics): https://github.com/passagemath/passagemath/issues/2347
- PR #2353 (LP docs): https://github.com/passagemath/passagemath/pull/2353
- SageMath: https://www.sagemath.org
