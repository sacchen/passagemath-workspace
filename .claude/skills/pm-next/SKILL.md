---
name: pm-next
description: Advance the passagemath queue by exactly one stage and stop. Use under /loop for self-paced autonomous work, or on its own to take the next step. Picks the furthest-along unfinished task, runs its stage, updates state, and reports.
---

One stage per invocation. Do not chain stages.

Read `kit/auto/playbooks/judgment.md` first. It pre-answers the decisions this
loop has to make, so the answer to "use your best judgement" is already
written down. Ask only for what that file says to ask for.

## Pick

Read every `kit/auto/queue/*.md`. Choose in this order, so work in flight
finishes before new work starts:

1. `state: redteamed` -> run `pm-ship`
2. `state: implemented` -> run `pm-redteam`
3. `state: scoped` -> run `pm-implement`
4. `state: proposed` -> run its repro, set `repro_status:`, promote to
   `scoped` or `blocked`. An outside agent proposed it and could not execute.
5. nothing above -> run `pm-scope`

Skip `blocked`, `parked`, `ready`, and `shipped`. `ready` means the stage
stopped for a human to push; `shipped` means they did, and `ship-commands.sh`
told them to record it. Neither comes back to this loop. When every task is
one of those four and `pm-scope` finds nothing, report that the queue is
drained and stop; do not lower the bar to produce a task.

## Run

Invoke the one stage. Update the task's frontmatter `state:` and append a
dated line to `## Log`. A stage that fails its checks leaves the state
unchanged and records what failed. That is a normal outcome, not an error to
work around.

## Boundary

Never push, file an issue, open a PR, or post a comment. `state: ready` is a
terminal state for the autonomous loop. Reading GitHub is fine; writing to it
is not.

## Report

Three lines: which task, which stage ran, what the next stage is. If a task
reached `ready`, include the output of `kit/auto/checks/ship-commands.sh`.
If a stage was blocked, say what would unblock it.

## Under /loop

Nothing to poll. Pick a long delay, 1800s or more, unless waiting on a
specific CI run whose duration is known.
