---
name: pm-implement
description: Implement a scoped passagemath queue task as one atomic commit with its doctest. Use when asked to implement or fix a task from kit/auto/queue. Takes a slug; leaves the branch committed locally at state implemented, never pushed.
---

Argument: a task slug, or the highest-priority `state: scoped` task if none given.

Read `kit/auto/playbooks/implement.md` and follow it.

Hard rules for this stage:

- Read and trace the code before editing it.
- One commit: implementation, doctest, and documentation together. A second problem found along the way gets its own task file, never a ride-along.
- The doctest must be the one that would have caught the bug.
- Prove the edit is live before believing a green run. `sage -t` imports code from site-packages, not from the repo file. Copy the `.py` in, or rebuild the `.pyx` with `kit/plot3d-repr/rebuild.sh`. Run a pristine control.
- Run `kit/auto/checks/source-style.sh kit/auto/queue/<slug>.md` before committing. Fix deterministic errors; carry contextual warnings into the separate source-style red-team pass.
- Write the commit message to `kit/auto/artifacts/<slug>/commit.txt` and commit with `git commit -F`. Follow `~/.claude/commit-pr-style.md`.
- Do not push. Do not open anything.

Then run `kit/auto/checks/hygiene.sh kit/auto/queue/<slug>.md` and fix what it reports before setting `state: implemented`.
