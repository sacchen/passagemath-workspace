---
name: pm-scope
description: Find the next passagemath contribution worth making and write it up as a queue task. Use when asked to find work, triage CI failures or review comments, or refill the passagemath queue. Produces kit/auto/queue/<slug>.md at state scoped, or reports that nothing qualified.
---

Read `kit/auto/playbooks/scope.md` and follow it.

Load first: `kit/AGENTS.md`, `kit/AGENT_STATE.md`, `kit/claude-memories/MEMORY.md`.

Hard rules for this stage:

- Producing no task is a correct outcome. Never manufacture work to fill the queue.
- Rank by impact, not by size. Tier is an effort estimate, not a filter.
- A candidate becomes a task only with a named symptom, a named root cause, a file list, and a repro that has been run. Otherwise it is `state: blocked` with the reason.
- Read-only against GitHub. No comments, no issues filed at this stage.

Finish by reporting the slug and the one-line symptom, or by saying nothing qualified and why.
