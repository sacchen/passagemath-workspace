---
name: pm-ship
description: Run the full ship gate on a red-teamed passagemath task and prepare the outward drafts. Use when asked to prepare a PR, issue, or commit for posting. Stops before pushing; prints the commands for the human to run.
---

Argument: a task slug, or the highest-priority `state: redteamed` task.

Read `kit/auto/playbooks/ship.md` and follow it.

Write to the budget the first time. Do not draft long and cut: in past
sessions that pass is where claims broke. `commit.txt` is a subject plus at
most three short paragraphs, `pr-body.md` is `Closes #N.` plus at most three,
`issue.md` is at most five plus one code block. No headings, no bullet lists
standing in for paragraphs. Check with `prose.py --kind`.

If shortening anyway, snapshot first with `drift.py --save`, then delete
claims whole rather than compressing them, and rerun `drift.py` to confirm no
surviving sentence got broader.

Write the drafts in `kit/auto/artifacts/<slug>/`, then run:

```
kit/auto/checks/gate.sh kit/auto/queue/<slug>.md
```

Fix failures and rerun. Do not rationalize past a gate; if a gate is wrong,
fix the check and say so.

**This stage does not push, file, comment, or open anything.** On a pass, set
`state: ready`, run `kit/auto/checks/ship-commands.sh` and hand back its
output verbatim along with the slug, branch, and one-line summary.
