---
name: pm-redteam
description: Adversarially review an implemented passagemath task across relevance, scope, accuracy, approach, execution, style, and wording. Use when asked to red team a change, a PR body, or an issue draft before it goes out. Records all seven axes on the task file.
---

Argument: a task slug, or the highest-priority `state: implemented` task.

Read `kit/auto/playbooks/redteam.md` and work the seven axes in order:
relevance, scope, accuracy, approach, execution, style, wording.

Attack the work. The goal is to find what a reviewer would find, before the
reviewer does. Recording "looks good" on an axis without having tried to
break it is the failure mode this stage exists to prevent.

Run, do not assume:

- `kit/auto/checks/negative_control.sh kit/auto/queue/<slug>.md` — the doctest must fail on unpatched code. This is the execution axis and it is not optional.
- `kit/auto/checks/prose.py` on every draft — style and wording.
- `kit/auto/checks/claims.py --list` on every draft, then check each flagged claim against a command and record it under `## Evidence`.

For an outside pass, `kit/auto/checks/redteam-prompt.sh` writes the prompt to
hand to Codex or another agent. Triage the response by the rules in the
playbook: verify every BLOCKER against the code before acting, drop
PREFERENCE findings, park out-of-scope ones as new tasks, and never accept a
finding that asks for more words.

Write one `- [x] <axis>: <what was attacked, what survived, what changed>`
line per axis on the task file. Set `state: redteamed`.
