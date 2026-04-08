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
than five superficial ones. Current focus: shovel-ready issues and multiplier
work — scoping problems so others can execute. Direct technical contributions
are reactive.

## Work classification (S.N.T.)

Use this lens when evaluating candidates for contribution:

* **Scale** — touches infrastructure shared across many packages (e.g. `.m4`
  templates, `sage-conf`, CI workflows). High impact per fix.
* **Neglected** — modularization blind spots: `except ImportError: pass`
  blocks that leave names unbound, causing `NameError` at runtime in partial
  installs. High value because they require architectural awareness to find.
* **Tractable** — surgical fixes in `src/sage/` with clear scope, testable
  in the local venv, low risk of reviewer pushback.

### Interpreting CI Noise (The "Triage Tax")

When reviewing failed CI runs (especially `test-mod` jobs), distinguish between three types of noise:

1. **Modularity Gaps (High Value):** A partial install lacks an optional dependency (e.g., `linbox`), but a test hits a code path requiring it, raising `ModuleNotFoundError`. These are "asymmetric dependencies." **Fix:** Add a surgical `# needs sage.libs.X` guard to the `sage:` line initiating the test.
2. **Baseline Drift (Do Not Touch):** Numerical drift or library updates causing output mismatches (e.g., `Got: 99` vs `Expected: 100`), flagged as "New failures" because `known-test-failures.json` is out of sync. **Do NOT edit the baseline JSON yourself.** If it appears in your PR's CI: mention it in the PR description and note it's pre-existing. If mkoeppe confirms it's a separate issue, open one — do not fold it into your current PR.
3. **Log Clutter (Ignore):** Logs are flooded with `Warning: The tag '# needs X' may no longer be needed`. These are false positives — do not mistake them for actual missing dependencies when grepping logs via `gh api`.

---

## Working principles

* **Simon Willison's "Perfect Commit"**: each commit changes one thing,
  bundles tests + implementation + documentation, links to an issue. Atomic.
  Reviewable. Provably working.
* **Prove it works**: manual test first, then automated test. Do not ship
  unverified diffs.
* **No unsolicited cleanup**: PEP8 sweeps, typo PRs, docstring reformatting
  are explicitly rejected.
* **Understand before touching**: read the code, trace the execution path,
  understand the architecture before proposing any change.

### Display / notebook fixes

* For rich-output or notebook-display changes, verify both the intended
  frontend context and a nearby non-target context (for example the doctest
  runner or `BackendSimple`).
* Do not use backend capability alone as a proxy for frontend behavior. A
  backend that lacks a rich output type may appear in non-notebook contexts
  too.
* When environment detection is needed, prefer existing Sage helpers over
  introducing a new heuristic.

---

## GitHub identity

* Account: `sacchen`
* Org member: `passagemath`
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

* Clone `passagemath/passagemath` — shallow blobless clone is sufficient for most contribution work.

* uv venvs (create as needed):
  * `.venv-contrib` (Python 3.12) — **contribution testing venv**:
    passagemath-repl, passagemath-combinat, passagemath-plot,
    passagemath-polyhedra, passagemath-glpk. Use this for doctests.
  * `.venv` (Python 3.12) — passagemath-polyhedra + glpk
  * `.venv311` (Python 3.11) — passagemath-polyhedra + glpk
  * `.venv-explore` (Python 3.12) — passagemath-combinat, passagemath-plot,
    ipykernel; register as a Jupyter kernel for notebook work

* Cannot run `sage -t` (no full sage CLI in modular installs)

### Running doctests

No full build required. Install `passagemath-repl` (pure Python) into the
working venv, then use `--environment sage.all__sagemath_<package>` matching
the file's package:

```bash
uv pip install passagemath-repl --python .venv/bin/python
python -m sage.doctest --environment sage.all__sagemath_combinat src/sage/combinat/partition.py
```

The `all__sagemath_<package>` modules live in the venv's `sage/` root and
populate the doctest global namespace with that package's symbols. Use the
one matching the package of the file under test:

| File in...           | Environment                     |
| -------------------- | ------------------------------- |
| `sage/combinat/`     | `sage.all__sagemath_combinat`   |
| `sage/categories/`   | `sage.all__sagemath_categories` |
| `sage/numerical/`    | install `passagemath-polyhedra` |

**Do not use:**
- `sage.repl.ipython_kernel.all_jupyter` — still requires `sage.all_cmdline`
- `sage.doctest.all` — too minimal, math symbols not in scope
- `sage.all__sagemath_repl` — repl-only, same problem

`sage.all_cmdline` does NOT exist in a modular passagemath install. It is
only present in the full monolithic SageMath build.

### Testing local source changes

The modular venv runs doctests against the **installed** package in
`site-packages`, not the local `src/` tree. Using `PYTHONPATH=src` fails
because unbuilt compiled modules (`sage.cpython.atexit`,
`sage.structure.element`, etc.) are missing.

To test a patch against local changes without a full build:
1. Copy the modified file(s) into the installed site-packages location
2. Run doctests there
3. Restore the originals

For most pure-Python PRs, CI is the authoritative test of the actual patch.
Local doctests can verify the installed baseline and catch obvious breakage,
but they do not run against your working tree.

---

## Completed contributions

### PR #6 — exception types in mip backends (Merged)

* **PR:** https://github.com/passagemath/passagemath-pkg-numerical-interactive-mip/pull/6
* **Issue:** https://github.com/passagemath/passagemath-pkg-numerical-interactive-mip/issues/5
* Summary: `AttributeError` → `ValueError`/`RuntimeError` in
  `abstract_backend_dictionary.py` and `glpk_backend_dictionary.py`.

### PR #2237 — replace pkg_resources at configure time (Merged)

* **PR:** https://github.com/passagemath/passagemath/pull/2237
* **Lesson:** Configure-time deps need registration in: 1. the M4 macro,
  2. `pkgs/sage-conf/pyproject.toml.m4`, 3. `.github/workflows/mingw.yml`.

### Issue #2239 — PIP_FIND_LINKS invalid URI on Windows (Acted on)

* Fix credited in PR #2240. Responded to within 35 minutes of filing.

### PR #2253 — Fix NameError in Partitions.cardinality() (Merged)

* **PR:** https://github.com/passagemath/passagemath/pull/2253
* **Issue:** https://github.com/passagemath/passagemath/issues/2243
* **Branch:** `fix/partitions-cardinality-no-flint-2243`
* **File:** `src/sage/combinat/partition.py`
* Summary: `except ImportError: pass` → `cached_number_of_partitions = None`.
  `cardinality()` falls back to `_cardinality_from_iterator()` for n≤10,
  raises `FeatureNotPresentError` for n>10.

### Issue #2254 — Meta: NameError antipattern in modular installs (Open)

* **Issue:** https://github.com/passagemath/passagemath/issues/2254
* Full triage of ~45 scanner hits posted. PRs #2282 and #2283 address the
  confirmed cases.

### PR #2282 — pari NameError in ell_point.py and number_field.py (Open)

* **PR:** https://github.com/passagemath/passagemath/pull/2282
* **Branch:** `fix/pari-namedror-ell-nf`
* ell_point.py (6 methods) + number_field.py (8 methods) + integer_mod_ring.py,
  cusps.py, binary_qf.py, calculus_method.py

### PR #2283 — unbound imports followup (Open)

* **PR:** https://github.com/passagemath/passagemath/pull/2283
* **Branch:** `fix/unbound-imports-followup-2254`
* padic_extension_leaves.py, multi_polynomial_ideal.py, chart_func.py cleanup,
  tools/check_unbound_imports.py AST checker

### Issue #2256 — doctest regressions in test-mod CI (Closed/fixed by PR #2257)

* automatic_semigroup.py missing `# needs sage.groups` guards
* lazy_attribute.pyx hardcoded line number

### Shovel-ready issues filed

* **#2236** — plot display in plain Python kernels (implementation spec in comments)
* **#2284** — WASM recipe contribution guide

---

## The FeatureNotPresentError fix pattern

Endorsed in #2243. Apply to all future unbound-import bugs:

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
* **pari / cypari2**: optional, gated by `passagemath-pari`. The
  `try/except ImportError` pattern in `ell_point.py` and `number_field.py`
  genuinely leaves `pari` unbound — real bugs, addressed in PR #2282.

## Known false positives — do not file PRs

* `chart_func.py` — sympy is always present
* grep count for `pari` uses in `number_field.py`: raw `grep -v "sage:"` does
  NOT exclude indented doctest lines. Real executable count is ~24–25.

## Dead ends — do not revisit

* **uv CI migration**: tracked in issue #2094. Will be driven upstream.
* **PEP517/setup.py audit**: already on `setuptools.build_meta`. Non-issue.
* **Issue #2225 and Windows doctest quirks (#2222, #2227, #2223)**: need
  Windows environment. Unresolvable locally.
* **Contributing to upstream SageMath**: CONTRIBUTING.md says "not a safe
  environment as of 2026." Do not cross-post.
* **Docstring typo / PEP8 sweeps**: explicitly rejected strategy.
