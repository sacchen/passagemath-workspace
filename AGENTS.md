# passagemath — Agent Context

This file is the authoritative context document for AI agents working in this
directory. Claude Code also reads `CLAUDE.md` (which points here).

---

## 🤖 Multi-Agent Orchestration (Roles & Quota Management)

To optimize for **correctness** and **subscription limits**, agents must adhere to these roles. **If a task falls outside your role, you are required to stop and advise the user to switch.**

| Agent/Model | Identity | Primary Domain | When to Delegate/Switch |
| --- | --- | --- | --- |
| **Gemini CLI** | **The Scout** | Repo-wide search, log forensics, finding "Neglected" patterns. | **Delegate implementation** to Claude/Copilot once the files are identified. |
| **Claude Code** | **The Architect** | High-logic refactoring (e.g., `sage.categories`), complex Python/Cython logic. | **Switch to Copilot** for unit tests or documentation to save quota. |
| **Copilot (Sonnet 4.6)** | **The Draftsman** | Standard feature implementation, fixing "Tractable" bugs, boilerplate. | **Switch to Gemini** if you cannot find a reference across the full monorepo. |
| **Copilot (GPT-5 mini)** | **The Polisher** | Documentation, docstrings, `uv` config updates, Simon Willison "Perfect Commit" bundles. | **Switch to Sonnet** if logic changes are required. |

**Standard Protocol**: Before starting any task, state your role: *"I am acting as [Role]. My goal for this session is [Goal]."*

---

## Project directives

### Search tooling

* Use the `Grep` tool (not `Bash` + `rg`) for content search.
* Use the `Glob` tool (not `Bash` + `fd`/`find`) for file discovery.
* When `rg` or `fd` must be used in `Bash` (piped processing or features
the dedicated tools don't expose), pass `--no-heading` for
machine-readable output.

### Environment

* Prefer `uv` for all Python environment management. Never suggest `pip`
as a primary tool.

---

## User goals

The user is contributing to passagemath to demonstrate engineering competence
to Matthias Koeppe (project maintainer, UC Davis). The goal is visibility
through technically correct, architecturally-aware contributions — not
volume.

**Key constraint**: Quality over quantity. One perfect PR > five mediocre
ones. Matthias will see through anything superficial.

---

## Working principles

* **Simon Willison's "Perfect Commit"**: each commit changes one thing,
bundles tests + implementation + documentation, links to an issue. Atomic.
Reviewable. Provably working.
* **"Prove it works"**: manual test first, then automated test. Do not ship
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
* `passagemath/passagemath-pkg-numerical-interactive-mip` — **independent
external package**, NOT a generated mirror. Predates the fork (2016).
Version 0.3.0. Files there do NOT exist in the monorepo.
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

* **PR:** [https://github.com/passagemath/passagemath-pkg-numerical-interactive-mip/pull/6](https://github.com/passagemath/passagemath-pkg-numerical-interactive-mip/pull/6)
* **Issue:** [https://github.com/passagemath/passagemath-pkg-numerical-interactive-mip/issues/5](https://github.com/passagemath/passagemath-pkg-numerical-interactive-mip/issues/5)
* **Branch:** `fix/exception-types-backend-dictionaries`
* Summary: Corrected `AttributeError` to `ValueError`/`RuntimeError` in `abstract_backend_dictionary.py` and `glpk_backend_dictionary.py`.

### PR #2237 — replace pkg_resources at configure time (Merged)

* **PR:** [https://github.com/passagemath/passagemath/pull/2237](https://github.com/passagemath/passagemath/pull/2237)
* **Lesson:** Configure-time deps need registration in: 1. The M4 macro, 2. `pkgs/sage-conf/pyproject.toml.m4`, 3. `.github/workflows/mingw.yml`.

### Issue #2239 — PIP_FIND_LINKS invalid URI on Windows

* **Acted on** by Matthias within 35 minutes of report.

### Issue #2243 — Partitions.cardinality() NameError (Filed)

* **Root Cause**: Silent `except ImportError: pass` at module level results in unbound names (e.g., `cached_number_of_partitions`) being accessed later in modular installs without optional dependencies (like `passagemath-flint`).

---

## Dead ends — do not revisit

* **uv CI migration**: Matthias has issue #2094 open. He will drive this.
* **PEP517/setup.py audit**: already on `setuptools.build_meta`. Non-issue.
* **Contributing to upstream SageMath**: CONTRIBUTING.md says "not a safe environment as of 2026." Do not cross-post.
* **Docstring typo / PEP8 sweeps**: explicitly rejected strategy.

---

# Agent State

## 1. REVISED LEVERAGE FRAMEWORK (S.N.T.)

* **SCALE**: Infrastructure depth involving `.m4` templates across 100+ modular packages.
* **NEGLECTED**: "Modularization Blind Spots" (ImportError masks leading to runtime NameErrors).
* **TRACTABLE**: Surgical fixes for missing fallback logic in `src/sage/`.

## 2. ACTIVE QUEUE

1. **`passagemath/src/sage/combinat/partition.py`**: [DRAFTSMAN] Implement pure-python fallback for `cached_number_of_partitions` to resolve #2243.
2. **`passagemath/src/sage/rings/polynomial/polynomial_element_generic.py`**: [SCOUT] Audit if `ImportError: pass` blocks cause runtime failures in modular environments.
