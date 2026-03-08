# passagemath — Agent Context

This file is the authoritative context document for AI agents working in this
directory. Claude Code also reads `CLAUDE.md` (which points here).

---

## Agent roles

Each agent has a defined scope. If a task falls outside your scope, stop and
tell the user to switch.

| Agent             | Scope                                                        | Hand off when                                             |
| ----------------- | ------------------------------------------------------------ | --------------------------------------------------------- |
| Gemini CLI        | Repo-wide search, log forensics, locating neglected patterns | Files identified — pass to Claude or Copilot to implement |
| Claude Code       | Complex refactors, `sage.categories`, Python/Cython logic   | Task is tests or docs — switch to Copilot to save quota   |
| Copilot (Sonnet)  | Feature implementation, tractable bug fixes, boilerplate    | Need monorepo-wide reference — switch to Gemini           |
| Copilot (GPT-5m)  | Docs, docstrings, `uv` config, Perfect Commit assembly      | Logic changes required — switch to Sonnet                 |

---

## Project directives

### Search tooling

* Use the `Grep` tool (not `Bash` + `rg`) for content search.
* Use the `Glob` tool (not `Bash` + `fd`/`find`) for file discovery.
* When `rg` or `fd` must be used in `Bash` (piped processing or features the
  dedicated tools don't expose), pass `--no-heading` for machine-readable
  output.

### Environment

* Prefer `uv` for all Python environment management. Never suggest `pip` as a
  primary tool.

---

## User goals

Quality over quantity. One correct, architecturally-aware PR is worth more
than five superficial ones.

## Work classification (S.N.T.)

Use this lens when evaluating candidates for contribution:

* **Scale** — touches infrastructure shared across many packages (e.g. `.m4`
  templates, `sage-conf`, CI workflows). High impact per fix.
* **Neglected** — modularization blind spots: `except ImportError: pass`
  blocks that leave names unbound, causing `NameError` at runtime in partial
  installs. High value because they require architectural awareness to find.
* **Tractable** — surgical fixes in `src/sage/` with clear scope, testable
  in the local venv, low risk of reviewer pushback.

---

## Working principles

* **Simon Willison's "Perfect Commit"**: each commit changes one thing,
  bundles tests + implementation + documentation, links to an issue. Atomic.
  Reviewable. Provably working.
* **Prove it works**: manual test first, then automated test. Do not ship
  unverified diffs.
* **No unsolicited cleanup**: PEP8 sweeps, typo PRs, docstring reformatting
  are explicitly rejected. Math maintainers read these as "I ran a linter."
* **Understand before touching**: read the code, trace the execution path,
  understand the architecture before proposing any change.

---

## GitHub identity

* Account: `sacchen`
* Fork of monorepo: `sacchen/passagemath`
* Fork of mip package: `sacchen/passagemath-pkg-numerical-interactive-mip`

---

## Repo architecture (verified)

* `passagemath/passagemath` — monorepo. Source of truth for core library
  (`src/`) and modular packages (`pkgs/`). Uses `.m4` template files for
  `pyproject.toml` generation. All packages use `setuptools.build_meta`.
* `passagemath/passagemath-pkg-numerical-interactive-mip` — independent
  external package, NOT a generated mirror. Predates the fork (2016). Version
  0.3.0. Files there do NOT exist in the monorepo.
* Monorepo's generated/mirrored packages (e.g. `sagemath-polyhedra`) ARE
  separate repos but ARE read-only mirrors. The distinction matters.

---

## Local environment

* Cloned repos at `/Users/goddess/foundry/sandbox/passagemath/`
  * `passagemath/` — shallow blobless clone of monorepo
  * `sage-numerical-interactive-mip/` — full clone, working tree with fix
    committed

* uv venvs:
  * `.venv` (Python 3.12) — passagemath-polyhedra + glpk
  * `.venv311` (Python 3.11) — passagemath-polyhedra + glpk
  * `.venv-explore` (Python 3.12) — passagemath-combinat, passagemath-plot,
    ipykernel; used for exploratory testing

* `from sage.numerical.mip import MixedIntegerLinearProgram` works in
  `.venv311`
* Cannot run `sage -t` (no full sage CLI); doctests verified manually via
  Python shell
* Test runner for mip package: `tox -e passagemath`
* Jupyter at `/Users/goddess/foundry/sandbox/jupyter-sandbox/` (Python 3.13);
  `.venv-explore` registered as kernel "passagemath"

---

## Completed contributions

### PR #6 — exception types in mip backends (Open)

* **PR:** https://github.com/passagemath/passagemath-pkg-numerical-interactive-mip/pull/6
* **Issue:** https://github.com/passagemath/passagemath-pkg-numerical-interactive-mip/issues/5
* **Branch:** `fix/exception-types-backend-dictionaries`
* Summary: Corrected `AttributeError` to `ValueError`/`RuntimeError` in
  `abstract_backend_dictionary.py` and `glpk_backend_dictionary.py`.

### PR #2237 — replace pkg_resources at configure time (Merged)

* **PR:** https://github.com/passagemath/passagemath/pull/2237
* **Lesson:** Configure-time deps need registration in: 1. the M4 macro,
  2. `pkgs/sage-conf/pyproject.toml.m4`, 3. `.github/workflows/mingw.yml`.

### Issue #2239 — PIP_FIND_LINKS invalid URI on Windows

* Acted on by Matthias within 35 minutes of report.

### PR #2253 — Fix NameError in Partitions.cardinality() (Filed)

* **PR:** https://github.com/passagemath/passagemath/pull/2253
* **Issue:** https://github.com/passagemath/passagemath/issues/2243
* **Branch:** `fix/partitions-cardinality-no-flint-2243`
* **File:** `src/sage/combinat/partition.py`
* Summary: `except ImportError: pass` → `cached_number_of_partitions = None`.
  `cardinality()` falls back to `_cardinality_from_iterator()` for n≤10,
  raises `FeatureNotPresentError` for n>10. Same guard added to
  `random_element_uniform()` and `number_of_partitions()`.

### Issue #2254 — Meta: NameError antipattern in modular installs (Filed)

* **Issue:** https://github.com/passagemath/passagemath/issues/2254
* Tracks the broader `except ImportError: pass` → unbound name → NameError
  bug class. Confirmed real cases: `ell_point.py` (pari, 5+ methods),
  `number_field.py` (pari, ~24–25 executable non-doctest uses).
* `chart_func.py` (sympy) — **false positive**: sympy is a standard
  dependency, always present. Do not file a PR for this.
* Next PRs should fix `ell_point.py` and `number_field.py` using the pattern
  from #2253.

---

## The FeatureNotPresentError fix pattern

Matthias endorsed this in #2243. Apply it to all future unbound-import bugs:

```python
# module level
except ImportError:
    x_func = None          # bind to None, NOT pass

# usage site
if x_func is None:
    from sage.features.sagemath import sage__libs__X
    sage__libs__X().require()
```

For cardinality-style methods with a small-n enumerable fallback:
```python
if x_func is None:
    if self.n <= 10:
        return self._cardinality_from_iterator()
    sage__libs__X().require()
```

---

## Dependency facts (verified)

* **sympy**: standard pip dependency (`build/pkgs/sympy`, type=`standard`).
  Always available when `passagemath-symbolics` is installed. Any
  `try: import sympy / except ImportError: pass` blocks are legacy no-ops.
  `chart_func.py` sympy diagnosis was a false positive.
* **pari / cypari2**: optional, gated by `passagemath-pari`. The
  `try/except ImportError` pattern in `ell_point.py` and `number_field.py`
  genuinely leaves `pari` unbound — those are real bugs.

## Known false positives — do not file PRs

* `chart_func.py` — sympy is always present (see above)
* grep count for `pari` uses in `number_field.py`: raw `grep -v "sage:"` does
  NOT exclude indented doctest lines (`            sage: pari(...)`). Real
  executable count is ~24–25, not the inflated "43" or "27" figures.

## Dead ends — do not revisit

* **uv CI migration**: Matthias has issue #2094 open. He will drive this.
* **PEP517/setup.py audit**: already on `setuptools.build_meta`. Non-issue.
* **Issue #2225 and Windows doctest quirks (#2222, #2227, #2223)**: need
  Windows environment. Unresolvable locally.
* **Contributing to upstream SageMath**: CONTRIBUTING.md says "not a safe
  environment as of 2026." Do not cross-post.
* **Docstring typo / PEP8 sweeps**: explicitly rejected strategy.
