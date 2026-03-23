# Agent State — 2026-03-22

## Active PRs (waiting on CI / review)

| PR | Title | Status |
|----|-------|--------|
| #2292 | docs, tox: document check_unbound_imports | Open, CI running |
| #2293 | polynomial_quotient_ring: # needs sage.modules on string-conversion doctests | Open, CI running |

## Multiplier infrastructure (complete)

All pre-term multiplier work is done:

- **Onboarding doc** — `passagemath-workspace/onboarding.md` — live at https://github.com/sacchen/passagemath-workspace/blob/main/onboarding.md
- **Project specs** — `passagemath-workspace/projects/` — plot display, weighted adjacency matrix, WASM recipe, OER adaptation
- **Shovel-ready queue** — fully posted at https://github.com/passagemath/passagemath/issues/2269#issuecomment-4070368357
  - #2236 (plot `_repr_png_()`) — intermediate
  - #2108 (`weighted_adjacency_matrix` crash) — intermediate
  - #2284 (WASM recipe) — advanced
  - #2290 (sage-discrete-math OER) — beginner

## Team members (introduced in #2269)

- **QihanQG** — CS/Math major
- **Runze2026** (Tony) — Math + CS minor

## What's next

- Wait for CI on #2292, #2293; respond to any mkoeppe review
- Optimization course starts 2026-03-30 — notebook work begins then
- Issue #2291 (mkoeppe's polyhedral geometry meta-issue) — long task list, skim for course-adjacent items

## Recent session summary (2026-03-22)

- Confirmed all multiplier work is done: onboarding doc live, project specs in workspace, shovel-ready queue posted on GitHub
- Updated CLAUDE.md to reference AGENTS.md with full absolute path
- Updated AGENTS.md with workspace repo location and full shovel-ready queue details

## Previous session summary (2026-03-21)

Shipped two PRs after #2283 merged:
- **#2292**: documented `tools/check_unbound_imports.py` in `tools.rst` + added tox env
- **#2293**: fixed `polynomial_quotient_ring.py` — 3 string-conversion doctests in `_element_constructor_` needed `# needs sage.modules`

Investigated #2288 (cellular_basis): math correctness bug, not our wheelhouse. Posted raw log facts without diagnosis.

## Workspace repo note

`passagemath-workspace` is at `/Users/goddess/foundry/sandbox/passagemath-workspace/`.
Its own `kit/AGENT_STATE.md` is stale (2026-03-16) — this file is authoritative.
