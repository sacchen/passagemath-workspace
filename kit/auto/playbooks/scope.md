# Stage 1 — Scope

Output: one task file in `kit/auto/queue/<slug>.md`, `state: scoped`.
A stage that produces nothing is a correct outcome. Do not manufacture work.

## Where to look, in order

1. **Review comments on open PRs.** `gh pr list --repo passagemath/passagemath --author sacchen --state open`, then `gh pr view N --comments`. An mkoeppe request outranks anything self-generated.
2. **CI on those PRs.** `gh run list --repo passagemath/passagemath --branch <branch>`. Pull the job log with `gh api "repos/passagemath/passagemath/actions/jobs/<JOB_ID>/logs" -H "Accept: application/vnd.github.v3.raw"`, grep `New failures, not in baseline`, read the next 30 lines. `known-test-failures.json` `{'ntests': N}` is the total tests run, not a failure count; say "new failures beyond baseline".
3. **Follow-ups already recorded.** `kit/auto/queue/*.md` with `state: parked`, and the follow-up candidates named in the memory files (for example the `eval_grid()` ulist/vlist leak on exception, confirmed in source and deliberately kept out of PR #2700).
4. **`kit/nerdsnipe/`.** Deep dives with a fix at the end.
5. **Issues mentioning sacchen.** `gh search issues --repo passagemath/passagemath mentions:sacchen --state open`.

## Filter

S.N.T. from `kit/AGENTS.md`. Rank by impact, not by size.

Tier is an effort estimate, not a filter. A one-line `# needs` tag that
unblocks a `test-mod` job for every contributor is high impact and cheap,
which is a reason to take it, not to skip it. The research-team phase that
reserved beginner work for students ended in June 2026.

Then two hard exclusions:

- PEP8, typo, and docstring sweeps are rejected on sight.
- The dead ends in `kit/claude-memories/MEMORY.md` stay dead: unsolicited uv CI rewrites, upstream SageMath, anything needing Windows.

## The bar for writing a task file

A candidate becomes a task only when all four hold. Missing any one means it stays a note, not a queue item.

1. A user-visible symptom, with the install configuration that produces it. "The scanner flags it" is not a symptom.
2. A root cause named at the level of functions and fields.
3. A file list. Every path the diff will touch, and no others.
4. A repro. Write it to `kit/auto/artifacts/<slug>/repro.py`, and state the
   failure it should produce and the venv it needs.

## Who runs the repro

An agent that only reads does not need `uv`, a venv, or a build, and should
not ask for them. Scoping is search and log reading.

So the repro bar splits in two:

- An outside scoping agent writes the repro and fills in `expected_failure:`,
  then stops at `state: proposed`. It executes nothing.
- Whoever holds the environment runs it, sets `repro_status:` to
  `reproduced` or `NOT-REPRODUCIBLE`, and promotes to `state: scoped` or
  `blocked`.

A `proposed` task is a claim, not a finding. Nothing implements from
`proposed`.

## Write it

Copy `kit/auto/queue/_TEMPLATE.md`. Fill the frontmatter, Symptom, Root cause, and the repro line. Leave Approach and Evidence for the next stage. Append a dated line to `## Log`.
