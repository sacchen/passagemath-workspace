# Educational Guide: Adding Dual-Value Documentation to `linear_programming.rst`

This file is for learning-by-doing. The goal is not just to land a doc patch, but to understand:

- where the documentation lives,
- how `MixedIntegerLinearProgram` relates to solver backends,
- when dual values are mathematically meaningful,
- why the current pattern is solver-specific.

Use this as a checklist while working in the real `passagemath` repository.

## Goal

Add a small, accurate, educational section to `linear_programming.rst` that shows how to retrieve dual values for a linear program and explains what those values mean.

Keep the scope tight:

- document an existing capability,
- do not imply there is a generic high-level dual API if there is not,
- make the GLPK-specific nature explicit if that is what the code supports.

## What You Should Learn

By the end, you should be able to answer these questions in your own words:

1. Where does `linear_programming.rst` live in the source tree?
2. What is the boundary between `MixedIntegerLinearProgram` and the backend object?
3. Where is `get_row_dual` implemented?
4. Why are dual values natural for LPs but not something you should casually advertise for arbitrary MIPs?
5. Why does the solver mode matter for getting row duals?
6. What does a dual value mean as a shadow price in a worked example?

If you cannot answer one of these clearly, stop and go back to the code or a tiny experiment.

## Phase 1: Find the Right Files

Open the real `passagemath` repo and locate the documentation file:

```sh
rg --files | rg 'linear_programming\.rst$'
```

Then locate the dual-related implementation:

```sh
rg -n 'get_row_dual|simplex_or_intopt|dual' src
```

What you are trying to identify:

- the documentation page you want to edit,
- the backend file that exposes `get_row_dual`,
- any tests or examples that already reference dual values,
- whether `simplex_or_intopt` is documented or only visible in code.

Write down the answers in a scratch note before editing anything.

## Phase 2: Read Before You Write

Read `linear_programming.rst` from top to bottom.

While reading, note:

- what level of user the page assumes,
- whether examples are small mathematical toy problems or larger applied examples,
- how doctests are formatted,
- whether backend access is already discussed elsewhere on the page,
- where a new subsection would fit naturally.

Questions to answer:

1. Is there already a place where “advanced / backend-specific” material belongs?
2. Would a dual-values section interrupt the flow if inserted too early?
3. Is there already a worked example style you should imitate?

Do not draft prose yet. First understand the page’s structure and tone.

## Phase 3: Trace the Feature in the Code

This is the core educational step.

Start from the user-facing object:

- `MixedIntegerLinearProgram`

Then trace how the code reaches the backend:

- solver selection,
- solve call,
- backend retrieval,
- row-dual retrieval.

What to determine from the source:

1. Is `get_row_dual` a generic backend method or only implemented by some backends?
2. Is there a documented guarantee about row numbering?
3. Does the method require a pure LP solve, simplex mode, or something similar?
4. Are there comments or tests explaining intended use?

When you read the code, summarize each finding in one sentence. Example structure:

- “`get_row_dual` is exposed on the backend object, not on `MixedIntegerLinearProgram` itself.”
- “The GLPK path uses simplex mode to make row duals available.”
- “Row indices correspond to the order in which constraints are added.”

If you cannot justify a sentence from code or experiment, do not put it in the docs.

## Phase 4: Build a Tiny Example First

Before touching the docs, build the smallest example that teaches you the concept.

Use a tiny LP, not your full coursework model.

Suggested shape:

- 2 variables,
- 2 constraints,
- objective easy to reason about,
- one constraint with an interpretable marginal value.

Your goals:

1. Solve the LP.
2. Retrieve row duals.
3. Verify that changing one right-hand side by `+1` changes the objective by about that dual value.

That last step matters. It turns API usage into understanding.

### Example workflow

The exact numbers are less important than the method:

1. Build a small LP.
2. Add constraints in a known order.
3. Set the GLPK solver parameter for simplex mode.
4. Solve.
5. Call `p.get_backend().get_row_dual(0)` and `get_row_dual(1)`.
6. Increase one RHS by `1`.
7. Re-solve and compare the objective difference.

Questions to answer from the experiment:

1. Which constraint gets which row index?
2. Does the dual value match the marginal objective change?
3. If a constraint is nonbinding, is its dual value zero?
4. What changes if you do not force the relevant solver mode?

## Phase 5: Decide the Right Documentation Scope

Your patch should probably be small.

A good first contribution would be:

- one short subsection in `linear_programming.rst`,
- one worked example,
- one note or warning block.

Avoid turning this into a large tutorial on LP duality unless the page already supports that style.

The purpose of the section is practical discoverability:

- “Here is how to get dual values in this supported case.”
- “Here is what they mean.”
- “Here are the limits.”

## Phase 6: Write the Section in the Right Order

Draft the subsection in this order:

1. State what dual values are.
2. State when they are available.
3. Show how to obtain them in the supported backend.
4. Explain how row indices are determined.
5. Interpret one dual value in plain English.
6. State limitations clearly.

That ordering matters. Users need the concept, then the mechanics, then the caveats.

## Phase 7: What the Section Should Probably Say

Here is the substance you are likely trying to communicate:

- Dual values, or shadow prices, measure the marginal change in the optimal objective when a constraint’s right-hand side changes.
- In Passagemath, these are obtained from the backend in supported cases rather than through a generic high-level method on `MixedIntegerLinearProgram`.
- With GLPK, you solve the LP in the appropriate simplex mode, then inspect row duals from the backend.
- The row index matches the order in which constraints were added.
- These values should be presented as LP sensitivity information, not as a general “MIP duals” feature.

Do not copy this verbatim into the docs. Rephrase it after verifying it yourself.

## Phase 8: A Good Worked Example

Choose an example with interpretation, not just mechanics.

Good examples:

- a tiny production LP,
- a transportation LP with a capacity constraint,
- your airline seat-allocation LP if it can be made concise enough.

The worked example should let you say something like:

- “The dual value of 100 means one extra unit of this resource increases the objective by 100.”

That sentence is educational value. Without it, the example is just backend plumbing.

## Phase 9: Caveats You Should Include

Your note or warning block should likely cover these points:

- This is backend-specific, not a universal high-level API.
- Dual values are naturally tied to LP solves.
- If the model originated as a MIP, explain whether you are examining the LP relaxation rather than the integer optimum.
- Solver parameters may matter for whether row duals are available.

Be precise. “Available for GLPK in this pattern” is stronger and safer than “available in Passagemath.”

## Phase 10: Verify Every Claim

Before opening a PR, check each sentence in the new docs against one of:

- source code,
- a doctest-sized runnable example,
- a direct numerical experiment.

A useful self-check table:

- Claim: where did I verify it?
- API behavior: source or experiment?
- mathematical interpretation: experiment?
- solver limitation: source or experiment?
- row ordering: source or experiment?

If you cannot point to evidence, weaken or remove the claim.

## Phase 11: Run the Relevant Tests

At minimum, run doctests or the documentation checks relevant to your change.

You want to confirm:

- the example actually runs,
- the values are stable enough for docs,
- the page renders correctly,
- there are no formatting issues in the RST.

If a number is sensitive to solver behavior, choose an example with clean, stable output.

## Phase 12: Write the PR Description

Keep the PR description modest and concrete.

Suggested structure:

- this documents an existing dual-value retrieval pattern,
- current discoverability is poor,
- the new section adds a worked example and explicit caveats,
- the example is intentionally scoped to LP / backend-supported usage.

Do not oversell the feature. Accurate framing matters more than ambitious framing here.

## A Good Working Checklist

Use this list while you work:

- [ ] I found the real `linear_programming.rst`.
- [ ] I read the whole page before editing.
- [ ] I found where `get_row_dual` is implemented.
- [ ] I understand whether the API is generic or backend-specific.
- [ ] I understand why simplex mode matters here.
- [ ] I built a tiny LP and retrieved dual values.
- [ ] I verified one dual value by perturbing the RHS.
- [ ] I know how row indices are assigned.
- [ ] My draft says what the numbers mean, not just how to print them.
- [ ] My draft includes limitations.
- [ ] I ran the relevant doctests or doc checks.
- [ ] Every claim in the new section is justified by code or experiment.

## Questions To Ask Yourself While Writing

Use these to keep the patch educational instead of merely procedural:

1. If a new user reads this, will they understand what a dual value means?
2. Will they understand why the example uses an LP rather than a generic MIP solve?
3. Will they understand that backend access is part of the story?
4. Am I documenting a stable supported pattern, or just exposing an implementation accident?
5. If the docs are read a year from now, will this wording still be accurate?

## If You Get Stuck

If you get stuck, narrow the problem:

1. Stop writing prose.
2. Reproduce the behavior in the smallest runnable example.
3. Read the backend code again.
4. Write a one-sentence explanation in your own words.
5. Only then return to the docs.

That loop is how you turn confusion into understanding.

## Recommended End State

A successful first patch here is not a giant rewrite. It is:

- a small doc addition,
- mathematically honest,
- solver-specific where necessary,
- backed by a clean worked example,
- useful to the next person who would otherwise have to read backend source code.

That is enough.
