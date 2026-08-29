---
name: pm-wrap
description: Close out a passagemath session so the next one starts oriented. Use when stepping away, ending sessions for the day, or asked to wrap up, hand off, or write down what was learned. Updates queue state and kit/AGENT_STATE.md.
---

"I'm about to step away", "wrap things up for the day", and "how do I get
caught up on what we learned today?" recur across sessions. The cost of a bad
handoff is paid at the start of the next one, re-deriving what was already
known.

Do these in order.

1. **Reconcile the queue.** For every `kit/auto/queue/*.md`, make `state:`
   match reality on disk and on GitHub. A task whose branch has an open PR is
   not `ready`. Append a dated line to each `## Log` that changed.

2. **Rewrite the top of `kit/AGENT_STATE.md`.** Replace the active-work
   section rather than appending to it; a stale table costs more than a
   missing one. It needs: open PRs with their real status, what the queue
   holds and at which state, and the single next action.

3. **Record what was learned, not what was done.** The diff and the git log
   already carry what was done. Write down only what a future session would
   otherwise re-derive: a trap found, a command that works, a claim that
   turned out false, a decision and its reason. If it generalizes past this
   repo, it belongs in the memory directory instead; if it is a fact about
   the code, put it in `kit/AGENTS.md`.

4. **Say what is unfinished and why.** A blocked task with no recorded reason
   reads as abandoned.

5. **Leave the tree clean.** No stray scratch files in the repo. Scratch
   belongs in the session scratchpad, artifacts in
   `kit/auto/artifacts/<slug>/`.

Do not push, file, or post. Report in three lines: what moved, what is next,
what is blocked.
