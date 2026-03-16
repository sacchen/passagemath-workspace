# How I contribute to passagemath

I use a framework borrowed from EA cause prioritization: importance, scale, neglectedness, tractability. The question is where time has the highest return, and what I'm specifically positioned to do.

## Finding the work

I look for work in three categories:

**Scale** — infrastructure problems that affect every package, every install, every platform. A bug in `.m4` template generation or a broken CI path is a multiplier on everyone downstream.

**Neglected** — problems that are hard to see without architectural context. The `except ImportError: pass` pattern that leaves names unbound in partial installs is invisible if you only test against full SageMath. Finding it systematically requires understanding the modular install model.

**Tractable** — verifiable, reviewable, low rejection risk.

## Comparative advantage

My edge is AI-assisted systematic analysis — AST scanners across the whole codebase, CI log forensics across platforms, triaging 45 hits in an afternoon. Matthias can write patches; the bottleneck is triage at scale. That's the gap I fill.

## Shifting gears

The highest-leverage thing shifts over time. Right now it's making work available for others — scoping issues with root cause, exact files, and verification method so people newer to the codebase can contribute without spending a week orienting. One well-scoped issue unblocks multiple people.

## Quality bar

One commit, one change, one test, one issue. If the test doesn't exist yet, the commit isn't done.
