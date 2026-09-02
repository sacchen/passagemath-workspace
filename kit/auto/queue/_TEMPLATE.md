---
slug: short-kebab-name
state: proposed            # proposed -> scoped -> implemented -> redteamed -> ready -> shipped | blocked | parked
issue:                     # upstream issue number, blank until filed
pr:                        # upstream PR number, blank until opened (human opens it)
branch: fix/short-kebab-name
venv: .venv                # venv name under the sandbox, e.g. .venv311, .venv-plot3d
tier: intermediate         # beginner | intermediate | advanced -- effort estimate, not a filter
snt: neglected             # scale | neglected | tractable
files:                     # every path the diff is allowed to touch, repo-relative
  - src/sage/...
doctest_cmd: >-
  sage -t --optional=sage src/sage/...
repro: kit/auto/artifacts/short-kebab-name/repro.py
repro_status: unrun        # unrun | reproduced | NOT-REPRODUCIBLE
expected_failure:          # what the repro should print or raise, before it is run
negative_control: unrun    # unrun | fail-on-unpatched | DOES-NOT-DISCRIMINATE
---

# Title

## Symptom

What a user sees, and the install configuration that produces it. If this
section cannot name a configuration, the item is scanner noise, not a bug.

## Root cause

Named functions and fields. Where control flow goes wrong.

## Approach

The fix, and the alternative that was rejected with the reason. Traps that
apply (see kit/auto/playbooks/redteam.md, Approach).

## Evidence

Every checkable claim that will appear in the issue, commit, or PR body.
`claims.py` matches flagged sentences against the `claim:` lines here.

- claim: <substring that appears in the prose>
  check: `<command>` -> <result, exit code>

## Log

- YYYY-MM-DD scoped

## Red team

Filled in from `playbooks/redteam.md`, after each pass, with what was
attacked and what survived. Ticking the boxes is not the stage.

- [ ] relevance:
- [ ] scope:
- [ ] accuracy:
- [ ] approach:
- [ ] execution:
- [ ] source-style:
- [ ] style:
- [ ] wording:
