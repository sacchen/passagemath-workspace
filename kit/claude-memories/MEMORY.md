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

No open PRs (as of 2026-04-08). Open issues:

- **Issue #2254** — complete triage comment posted. All ~45 scanner hits classified. No remaining actionable bugs.
- **Issue #2269** — research team onboarding. Shovel-ready queue posted at https://github.com/passagemath/passagemath/issues/2269#issuecomment-4070368357 — covers #2236, #2108, #2284, #2290 with full specs.

## Completed work (details in project_completed_prs.md)

- PR #2354 (linbox `# needs` guards in modsym and geometry/cone): MERGED 2026-04-08
- PR #2353 (LP docs: dual values, matrix patterns, `simplex_or_intopt`/`get_row_dual`): MERGED 2026-04-08
- PR #2293 (polynomial_quotient_ring: `# needs sage.modules` on string-conversion doctests): MERGED 2026-03-23
- PR #2292 (docs + tox env for `check_unbound_imports`): MERGED 2026-04-04
- PR #2287 (calculus_method: fix pickling regression from lazy_import sympy_latex): MERGED
- PR #2283 (unbound imports fix + `check_unbound_imports` AST tool): MERGED 2026-03-21
- PR #2282 (pari NameError → FeatureNotPresentError): MERGED 2026-03-16
- PR #2253 (Partitions.cardinality without flint): MERGED
- PR #2237 (importlib.metadata in configure): MERGED, in 10.8.2.rc2
- Issue #2239 (PIP_FIND_LINKS Windows): acted on by mkoeppe in 35 min, credited by name
- PR #6 (exception types, external mip package): MERGED
- Issue #2244 (Marimo backend): RESOLVED by PR #2255 (merged 2026-03-08)

## Repo architecture

- `passagemath/passagemath` — monorepo with `src/` and `pkgs/`. Uses `.m4` templates for `pyproject.toml`. All packages on `setuptools.build_meta`.
- `passagemath-pkg-numerical-interactive-mip` — independent external package, NOT a monorepo mirror. Predates the fork (2016).
- Mirrored packages (e.g. `sagemath-polyhedra`) are separate repos but read-only mirrors.

## Environment

- Clone `passagemath/passagemath` (shallow blobless is sufficient).
- **passagemath-workspace** — public contributor resource repo (github.com/sacchen/passagemath-workspace). Agent context: `kit/AGENTS.md`, state: `kit/AGENT_STATE.md`. mkoeppe forked it and reads it seriously.
- uv venvs (create as needed — see `kit/AGENTS.md` for full layout):
  - `.venv-contrib` (Python 3.12): contribution testing — passagemath-repl, combinat, plot, polyhedra, glpk
  - `.venv311` (Python 3.11): polyhedra + glpk; can import `MixedIntegerLinearProgram`
- No `sage -t`; doctests run via `python -m sage.doctest --environment sage.all__sagemath_<package>`

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
- **Baseline format:** `known-test-failures.json` `{'ntests': N}` = total tests run, not failure count. Say "new failures beyond baseline." Do NOT edit `known-test-failures.json` yourself. If numerical drift appears in your PR's CI: flag it in the PR description as pre-existing. If mkoeppe confirms it's a separate issue, open one — do not fold it into your current PR.
- **CI log extraction:** `gh api "repos/.../actions/jobs/{JOB_ID}/logs" -H "Accept: application/vnd.github.v3.raw"` — filter Docker internal IP noise. Grep `New failures, not in baseline` then `-A 30`. Be aware of **Log Clutter**: logs are flooded with "Warning: The tag '# needs X' may no longer be needed", which will hijack simple greps for package names.
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
