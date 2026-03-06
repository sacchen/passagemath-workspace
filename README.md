# passagemath-workspace

active research workbench for [passagemath](https://github.com/passagemath/passagemath). this is a live stream of logic trails, agentic workflows, and debugging logs. **the primary value is in the logs; the code is secondary infrastructure.**

---

## research stream (`/logs`)

unstructured markdown mirrored from local obsidian.

* **llm logs:** raw traces and reasoning chains from gemini, claude, and gpt.
* **logic trails:** messy proofs, modularization strategies, and bug forensics.
* **temporal tracking:** use git history to follow real-time progress on specific sub-problems.

## agent infra (`/src`)

roles optimized for subscription quota and logic depth:

| agent | identity | domain |
| --- | --- | --- |
| **gemini** | **the scout** | repo-wide forensics & "neglected" pattern discovery. |
| **claude** | **the architect** | high-logic python/cython refactoring. |
| **sonnet** | **the draftsman** | feature implementation & "tractable" bug fixes. |
| **gpt-5 mini** | **the polisher** | documentation & `uv` config updates. |

## leverage (s.n.t. framework)

contributions prioritized by:

1. **scale:** infrastructure/dependency depth (e.g., `.m4` templates).
2. **neglected:** modularization blind spots (e.g., silent `ImportError` masks).
3. **tractable:** surgical fixes with minimal review burden.

## setup

clone outside the monorepo and symlink to avoid pollution.

```bash
# 1. sync logs (via uv run sync.py)
# 2. symlink for context
ln -s ~/passagemath-workspace/logs/AGENT_STATE.md .

```

add `AGENT_STATE.md` to your `~/.gitignore_global`.

---

*maintained by [sacchen*](https://github.com/sacchen)

