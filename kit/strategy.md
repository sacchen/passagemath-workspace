# Strategy: Multiplier on a Research Team

## Context

**Group:** Matthias Köppe, UC Davis. Polyhedral Geometry and Optimization.
**Project spec:** https://github.com/passagemath/passagemath/issues/2269
**Team:** 8 students total. Heavy mix of levels. No one else has passagemath context yet.
**Your edge:** Weeks of codebase knowledge, merged PRs, org membership, AI-assisted analysis.
**Role:** Multiplier — find and scope work, others execute.

---

## The job

You are the person who knows the terrain. The other 7 students don't.
Your output is work that others can pick up without needing to reverse-engineer the codebase.

Two tracks:

### Track 1: Onboarding infrastructure (do first, before students arrive)

They have no passagemath context. They need:
- How to install and run passagemath (uv, which venv, which package)
- How the modular package structure works (what's in sagemath-plot vs sagemath-combinat vs sagemath-polyhedra)
- How to run a doctest on a file they changed
- How to file a PR (fork, branch, push, open)
- Where issues live, what labels mean, how to claim one

This is a single doc or notebook. Spend time on it once; it unblocks everyone.
File it somewhere Matthias can point students to — either as a repo doc or a marimo/Jupyter notebook.

### Track 2: Work queue (ongoing)

Maintain a backlog of shovel-ready GitHub issues, tiered by difficulty.

**What shovel-ready means:**
- Clear problem statement (what's wrong, what's the expected behavior)
- Root cause or implementation direction (they shouldn't have to figure this out)
- Exact files and line numbers to touch
- Verification method (how to know it worked)

**Tiering matters** because of the mixed skill levels:
- **Beginner:** Single-file change, no architecture knowledge needed, doctest verification.
  Example: fix a doctest that hardcodes a line number, add a missing `# needs` tag.
- **Intermediate:** Understand one module, fix a real bug with a clear pattern to follow.
  Example: `_repr_png_()` on Graphics — the spec is already written in `nerdsnipe/plot-repr-png.md`.
- **Advanced:** Cross-module change, requires understanding the modular install architecture.
  Example: new backend for MixedIntegerLinearProgram, Normaliz interface extension.

Your job is to keep the queue populated and tiered. Not to assign work — students self-select.

---

## Your own contributions

Same rule as before: reactive, quality over quantity.

- Take issues that require your specific analytical skill (AI-assisted systematic search,
  cross-file root cause analysis, CI forensics). These are hard for students to do.
- Implement things from your own nerdsnipe queue when they interest you.
- Let the course teach you the math. Build notebooks alongside it.

---

## Coordination mechanism

GitHub issues + labels. No Slack, no spreadsheet, no standup.

When you scope a piece of work: file a well-written issue, apply a difficulty label,
let students claim it. If two people accidentally work on the same thing, that's a
merge conflict, not a catastrophe. Keep it lightweight.

---

## What to do now (before term starts)

1. **Write the onboarding doc.** Get students productive in day one, not week two.
2. **File 5-10 scoped issues** at varying difficulty from your existing nerdsnipe queue.
   `nerdsnipe/plot-repr-png.md` → one issue. The #2256 doctest regressions pattern → several beginner issues.
3. **Let #2282 and #2283 land.** Don't open new PRs until those resolve.

---

## Avoid

| Action | Why |
|---|---|
| Assigning work to specific students | Project management you don't want |
| Taking beginner-tier issues yourself | Leaves nothing for students who need entry points |
| PEP8 / docstring sweeps | Still low signal, still unwelcome |
| Manufacturing work | File issues only for real problems you've verified |
