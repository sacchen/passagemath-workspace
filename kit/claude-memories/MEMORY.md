# passagemath contribution session

## User goals

mkoeppe invited @sacchen to the passagemath GitHub org and research team (issue #2269). Taking Matthias's optimization course for 3 credits (~10 hrs/week) starting ~2026-03-30. Strategy: notebooks alongside the course (primary), deborgen as applied test case (secondary), infrastructure/correctness work reactive. See `strategy.md`.

**Key constraint:** Quality over quantity. One perfect PR > five mediocre ones.

## Working principles

- **Perfect Commit**: one thing, bundles tests + implementation + docs, links to issue. Atomic. Reviewable. Provably working.
- **Prove it works**: manual test first, then automated. Do not ship unverified diffs.
- **uv over pip**: always. Never suggest pip as primary tool.
- **No unsolicited cleanup**: PEP8, typos, docstring reformatting — math maintainers read these as "I ran a linter."
- **Understand before touching**: read the code, trace the execution path, understand the architecture.

## Active PRs / issues

- **PR #2283** — MERGED 2026-03-21.
- **PR #2292** — Open. docs + tox env for `check_unbound_imports` (mkoeppe's post-merge request from #2283).
- **PR #2293** — Open. `polynomial_quotient_ring._element_constructor_` string-conversion doctests need `# needs sage.modules`; root cause PR #2057 + #2069.
- **Issue #2254** — open, complete triage comment posted. All ~45 scanner hits classified. No remaining actionable bugs beyond #2283.
- **Issue #2256** — filed (two doctest regressions in test-mod CI), no PR planned.
- **Issue #2269** — research team onboarding issue. Shovel-ready queue fully posted at https://github.com/passagemath/passagemath/issues/2269#issuecomment-4070368357 — covers #2236, #2108, #2284, #2290 with full specs. New team members: QihanQG, Runze2026.
- **Issue #2290** — OER adaptation. Spec written for sage-discrete-math (CC-BY, PreTeXt). Linked from #2269 shovel-ready comment.
- **Issue #2291** — mkoeppe's polyhedral geometry meta-issue. Just a long task list, not a strategic signal.

## Completed work (details in project_completed_prs.md)

- PR #6 (exception types, external mip package): MERGED
- PR #2237 (importlib.metadata in configure): MERGED, Upstream candidate, in 10.8.2.rc2
- Issue #2239 (PIP_FIND_LINKS Windows): acted on by Matthias in 35 min, credited by name
- PR #2253 (Partitions.cardinality without flint): MERGED, "Looking great, thanks a lot."
- PR #2282 (pari NameError → FeatureNotPresentError): MERGED 2026-03-16
- Issue #2244 (Marimo backend): RESOLVED by PR #2255 (merged 2026-03-08)

## Repo architecture

- `passagemath/passagemath` — monorepo with `src/` and `pkgs/`. Uses `.m4` templates for `pyproject.toml`. All packages on `setuptools.build_meta`.
- `passagemath-pkg-numerical-interactive-mip` — independent external package, NOT a monorepo mirror. Predates the fork (2016).
- Mirrored packages (e.g. `sagemath-polyhedra`) are separate repos but read-only mirrors.

## Environment

- Repos at `~/foundry/sandbox/passagemath/`: `passagemath/` (shallow blobless clone), `sage-numerical-interactive-mip/` (full clone)
- **passagemath-workspace** at `~/foundry/sandbox/passagemath-workspace/` — public contributor resource repo (github.com/sacchen/passagemath-workspace). Onboarding doc at `onboarding.md`, project specs at `projects/`, nerdsnipe at `nerdsnipe/`. Agent context: `kit/AGENTS.md`, state: `kit/AGENT_STATE.md`. mkoeppe forked it and reads it seriously.
- `.venv` (Python 3.12): passagemath-polyhedra + glpk + passagemath-graphs
- `.venv311` (Python 3.11): passagemath-polyhedra + glpk; can import `MixedIntegerLinearProgram`
- `.venv-explore` (Python 3.12): passagemath-combinat, passagemath-plot, ipykernel; registered as "passagemath" Jupyter kernel
- No `sage -t`; doctests run via `python -m sage.doctest`
- Jupyter at `~/foundry/sandbox/jupyter-sandbox/`

## FeatureNotPresentError pattern (Matthias-endorsed)

```python
try:
    from sage.libs.X import x_func
except ImportError:
    x_func = None  # NOT pass

# at usage site:
if x_func is None:
    from sage.features.sagemath import sage__libs__X
    sage__libs__X().require()
```

## Workflow notes

- **PR attribution:** `gh pr view <N> --repo passagemath/passagemath --json files --jq '[.files[].path]'`
- **Baseline format:** `known-test-failures.json` `{'ntests': N}` = total tests run, not failure count. Say "new failures beyond baseline."
- **CI log extraction:** `gh api "repos/.../actions/jobs/{JOB_ID}/logs" -H "Accept: application/vnd.github.v3.raw"` — filter Docker internal IP noise. Grep `New failures, not in baseline` then `-A 30`.
- **GitHub formatting:** backticks must be literal in `gh` input — do NOT escape as `\``. Each paragraph must be one unbroken line — single newlines render as `<br>`. See [feedback_github_formatting.md](feedback_github_formatting.md).
- **Gemini:** good for log forensics and codebase-wide AST analysis. Has made architectural errors — always verify against actual code before filing.
- **mkoeppe review style:** fast, one issue per comment, points at exact log line. Respond in kind.

## Dependency facts

- **sympy**: required dep of `passagemath-symbolics` (`pkgs/sagemath-symbolics/pyproject.toml.m4:32`). Safe to assume present in any file in that package. Legacy `try/except ImportError` around sympy in those files are no-ops. (NOT because `build/pkgs/sympy/type=standard` — that's a monolithic-Sage concept irrelevant for pip packages.)
- **pari/cypari2**: optional (`passagemath-pari`). Real unbound-name risk — fixed in #2282.
- **NTL/FLINT padic modules**: optional. Fixed in #2283.
- **sage.interfaces.singular**: optional. Fixed in #2283.
- **grep false counts:** `grep -v "sage:"` does NOT exclude indented doctest lines. Use AST analysis.

## Dead ends — do not revisit

- **uv CI migration**: Matthias driving via issue #2094. Unsolicited CI rewrites will be closed.
- **Contributing to upstream SageMath**: CONTRIBUTING.md says "not a safe environment as of 2026."
- **Windows doctest issues (#2222, #2223, #2225, #2227)**: need Windows environment.
- **Docstring/PEP8/typo sweeps**: explicitly rejected.

## Extended memory files

- [project_workspace_signal.md](project_workspace_signal.md) — mkoeppe forked passagemath-workspace and made corrections; signal he's using it seriously
- [project_completed_prs.md](project_completed_prs.md) — detailed records of merged PRs
- [project_ast_checker.md](project_ast_checker.md) — `tools/check_unbound_imports.py` details
- [feedback_gemini_verification.md](feedback_gemini_verification.md) — Gemini failure modes, verification discipline
- [feedback_dependency_reasoning.md](feedback_dependency_reasoning.md) — use pyproject.toml.m4 not build/pkgs/type to check if a dep is always present
- [feedback_public_names.md](feedback_public_names.md) — use mkoeppe (not first name) in all public-facing content
- [feedback_commenting_when_unconfident.md](feedback_commenting_when_unconfident.md) — post raw log facts without diagnosis when uncertain; still useful, zero risk
- [feedback_categorical_claims.md](feedback_categorical_claims.md) — never assert "none X" / "all X" until search is confirmed exhaustive; use `gh search code --owner org --limit 100`, not agent web scraping
- [user_profile.md](user_profile.md) — user background, motivation, role preference
