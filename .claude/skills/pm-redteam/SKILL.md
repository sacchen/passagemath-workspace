---
name: pm-redteam
description: Adversarially review an implemented passagemath task across relevance, scope, accuracy, approach, execution, source style, public-prose style, and wording. Use when asked to red team a change, a PR body, or an issue draft before it goes out. Records all eight axes on the task file.
---

Argument: a task slug, or the highest-priority `state: implemented` task.

Read `kit/auto/playbooks/redteam.md` and work the eight axes in order:
relevance, scope, accuracy, approach, execution, source-style, style, wording.

Attack the work. The goal is to find what a reviewer would find, before the
reviewer does. Recording "looks good" on an axis without having tried to
break it is the failure mode this stage exists to prevent.

Run, do not assume:

- `kit/auto/checks/negative_control.sh kit/auto/queue/<slug>.md` — the doctest must fail on unpatched code. This is the execution axis and it is not optional.
- `kit/auto/checks/source-style.sh kit/auto/queue/<slug>.md` — inspect only added source documentation and configuration lines, resolve every error, and record the decision for every warning.
- `kit/auto/checks/prose.py` on every draft — style and wording.
- `kit/auto/checks/claims.py --list` on every draft, then check each flagged claim against a command and record it under `## Evidence`.

For an outside pass, `kit/auto/checks/redteam-prompt.sh` writes the prompt to
hand to Codex or another agent. Triage the response by the rules in the
playbook: verify every BLOCKER against the code before acting, drop
PREFERENCE findings, park out-of-scope ones as new tasks, and never accept a
finding that asks for more words.

Write one `- [x] <axis>: <what was attacked, what survived, what changed>`
line per axis on the task file, then set `state: redteamed`.

Those eight lines are what the gate can see, which makes them the easy thing
to optimize and the wrong thing to start from. Do the pass first and write
down what it turned up. An axis where the attack found nothing says what was
attacked and why it held; an axis that was never worked says so and the task
stays at `implemented`. A full task file is not the deliverable, a change
that survives mkoeppe is.
