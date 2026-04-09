# Agent State — 2026-04-09

## Active PRs (waiting on CI / review)

- **#2356 (Draft)**: Fix complex-tolerance comparison in numerical point filtering (`abs()` fix for `affine_homset.py` and `projective_homset.py`).

## Recently merged

| PR | Title | Merged |
|----|-------|--------|
| #2354 | Add missing sage.libs.linbox doctest guards in modsym and geometry/cone | 2026-04-08 |
| #2353 | LP docs: dual values, matrix patterns, simplex_or_intopt/get_row_dual | 2026-04-08 |
| #2292 | docs, tox: document check_unbound_imports | 2026-04-04 |
| #2293 | polynomial_quotient_ring: # needs sage.modules on string-conversion doctests | 2026-03-23 |

## Multiplier infrastructure (complete)

All pre-term multiplier work is done:

- **Onboarding doc** — `passagemath-workspace/onboarding.md` — live at https://github.com/sacchen/passagemath-workspace/blob/main/onboarding.md
- **Project specs** — `passagemath-workspace/projects/` — plot display, weighted adjacency matrix, WASM recipe, OER adaptation
- **Shovel-ready queue** — fully posted at https://github.com/passagemath/passagemath/issues/2269#issuecomment-4070368357
  - #2236 (plot `_repr_png_()`) — intermediate
  - #2108 (`weighted_adjacency_matrix` crash) — intermediate
  - #2284 (WASM recipe) — advanced
  - #2290 (sage-discrete-math OER) — beginner

## What's next

- **LP Level 1 complete** — #2353 merged. Now at Level 1 → Level 2 threshold.
- **Finish dual-value notebook** (`exercises/linear-programming-duals/`) — uncommitted changes in progress. This is the learning artifact that sharpens Level 2 design opinions.
- **Schedule mkoeppe meeting** — come with: friction points in `mip.py`, candidate interfaces for ergonomic helpers, concrete MAT 168 problems as test cases. No Level 2 code before this.
- **#2356 (Draft)**: Wait for CI; respond to mkoeppe review.
- Issue #2291 (polyhedral geometry meta-issue) — skim for course-adjacent items.

## Session summary (2026-04-08 — PR #2356 Red-teaming)

- **Red-Teamed PR #2356**: Investigated the `abs(g(list(S))) < zero_tol` fix for numerical point filtering in `affine_homset.py` and `projective_homset.py` (Issue #2355).
- **Findings**: 
  - The fix correctly addresses a **false positive** vulnerability where `CDF` and `CC` objects bypass the `<` operator via real-part evaluation (e.g., `CDF(1e-12 + 1000j) < 1e-9` returns `True`). This allows non-roots with massive imaginary components or large negative real residuals to mistakenly pass as valid points.
  - The fix is mathematically sound but strictly more restrictive (pruning).
  - On Gemini's container (does not reproduce the bug): the 100-point doctest passes under both old and new logic; max absolute residual across all 100 roots was ~`9.15e-10`, comfortably under `1e-9`. The bug is likely environment-specific (Python 3.14 CI builds per issue #2355).
  - **Open question**: whether `abs()` actually fixes the 99-count failure on the affected environment. Mathematically, `abs()` is strictly more restrictive than real-part comparison, so it cannot recover a root dropped by the old filter. CI on the PR will be the ground truth.
- **Testing Discoveries**: Found the correct `--environment` flag for `sage/schemes/` files (`sage.all__sagemath_schemes`). `# needs sage.libs.singular` tests are still skipped without `passagemath-singular` installed — that install path remains unresolved. See AGENTS.md.

## Session summary (2026-04-08)

- **Bottleneck Investigation:** Analyzed CI noise blocking PRs. Discovered the bottleneck shifted from scoping work to verification throughput (the "Triage Tax"). 
- **CI Stabilization:** Identified two active `ModuleNotFoundError` crashes in `sagemath_schemes-check` related to missing `sage.libs.linbox` guards. 
- **Shipped PR #2354:** Added `# needs sage.libs.linbox` guards to `modsym/tests.py` and `geometry/cone.py`. Flagged numerical drift in `affine_homset.py` (line 414) in the PR description as a maintainer note for mkoeppe.
- Investigated local doctest setup. `sage.all_cmdline` lives in `sagemath-repl`
  (pure Python). Two paths to get doctests working: install `passagemath-repl`
  via uv, or use `--environment` flag on the doctest runner. Documented in
  AGENTS.md under "Running doctests". Try Path B first.
- PR #2292 still open, needs ping to mkoeppe. CI failures are pre-existing noise.

## Previous session summary (2026-03-24)

- Created `exercises/ci-failure-discovery/` notebook (notebook 3): teaches how to find real failures in noisy CI logs, why test-mod fails when local passes, and how to trace NameError back to missing guard
- Resolved git rebase conflict when remote restructured exercises into per-subdirectory format
- Ported kit/claude-memories/ into new memory system at ~/.claude/projects/.../memory/

## Previous session summary (2026-03-22)

- Confirmed all multiplier work is done: onboarding doc live, project specs in workspace, shovel-ready queue posted on GitHub
- Updated CLAUDE.md to reference AGENTS.md with full absolute path
- Updated AGENTS.md with workspace repo location and full shovel-ready queue details

## Session summary (2026-03-21)

Shipped two PRs after #2283 merged:
- **#2292**: documented `tools/check_unbound_imports.py` in `tools.rst` + added tox env
- **#2293**: fixed `polynomial_quotient_ring.py` — 3 string-conversion doctests in `_element_constructor_` needed `# needs sage.modules`

Investigated #2288 (cellular_basis): math correctness bug, not our wheelhouse. Posted raw log facts without diagnosis.

## Workspace repo note

Use `kit/AGENT_STATE.md` as the authoritative current-state file.