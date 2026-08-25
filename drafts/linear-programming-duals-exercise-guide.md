# The Dual-Values Documentation Exercise

**What this guide teaches:** How to add a small doc section on dual values to `linear_programming.rst`, while learning the actual modeling stack behind it.

**Why it matters:** Right now, a user can solve an LP and retrieve row duals through the backend, but that path is not obvious from the docs. The educational value here is not just "write docs." It is learning where the frontend stops, where the backend begins, and why dual values have to be documented carefully.

**Structure:** encounter -> trace -> verify -> write -> review. Work in order.

## Section 1: The actual problem

Here is the practical gap you are trying to close:

- A user can solve an LP in Sage / Passagemath.
- A user can retrieve dual values from the backend in some supported cases.
- But this is hard to discover from `linear_programming.rst`.

That sounds like a documentation problem. It is, but only partly.

It is also a learning problem:

- What exactly is being documented?
- Is this a frontend feature or a backend feature?
- Are these LP dual values, MIP dual values, or something more subtle?
- What claims are mathematically and technically safe to make?

Your goal is to learn those answers by tracing the code and testing a tiny example.

## Section 2: Start with a prediction

Before you read any code, write down your current guess.

Answer these from memory:

1. If I build a `MixedIntegerLinearProgram`, where do dual values live?
2. Do I expect a high-level method like `p.get_dual_values()`?
3. If not, where do I think the numbers come from?
4. Do I think this should work for arbitrary integer programs?
5. What do I think a dual value means in plain English?

Do not skip this. The point is to catch yourself making assumptions.

## Section 3: Find the docs target

Now go to the real `passagemath` repository and locate the file you would edit:

```sh
rg --files | rg 'linear_programming\.rst$'
```

Open that file and read it all the way through before drafting anything.

As you read, write down:

- where examples are placed,
- whether advanced topics already appear,
- whether backend access is already mentioned,
- how verbose the page is,
- what doctest style it uses.

Checkpoint:

By the time you finish reading, you should be able to answer:

1. Where would a small dual-values section naturally fit?
2. Would a worked example feel normal on this page?
3. Would a backend-specific note need a warning block or just careful wording?

## Section 4: Encounter the missing path

Pretend you are a user who wants shadow prices.

Ask yourself:

- If I only read `linear_programming.rst`, would I know how to get dual values?
- Would I know whether they are part of the high-level API?
- Would I know whether they depend on the solver backend?

If the answer is "no" to those, you have identified the real user-facing problem.

That is the thing your doc patch should solve.

Not:

- redesigning the MIP frontend,
- creating a new abstraction,
- promising a future roadmap.

Just making an existing supported path discoverable, with honest scope.

## Section 5: Trace the implementation

Now search the code:

```sh
rg -n 'get_row_dual|simplex_or_intopt|dual' src
```

Your job here is not just to find strings. It is to understand the boundary.

Work outward from the user-facing object:

- `MixedIntegerLinearProgram`
- solve call
- backend retrieval
- row dual retrieval

Questions to answer from the code:

1. Where is `get_row_dual` implemented?
2. Is it exposed on the high-level modeling class, or only on the backend?
3. Which backend supports it?
4. Does the code suggest any restrictions on when the result is meaningful?
5. Does the solver mode affect availability?
6. How is row indexing defined?

Write each answer in one sentence. If you cannot write the sentence confidently, you do not understand that part yet.

## Section 6: First lesson — frontend vs backend

This is one of the main educational payoffs.

If the path looks like:

```python
p.solve()
b = p.get_backend()
b.get_row_dual(0)
```

then the docs should teach something subtle:

- the user models the problem through the frontend,
- but dual values are being read from a backend object,
- so this is not automatically a generic high-level API promise.

That distinction matters for both accuracy and maintenance.

Reflection question:

Why is "document an existing backend-supported workflow" safer than "advertise dual values as a standard MIP frontend capability"?

Write your answer before moving on.

## Section 7: Build a tiny LP

Before writing docs, build the smallest example that teaches you the concept.

Do not start with your full coursework model.

Use:

- a tiny LP,
- a clear objective,
- 2 constraints,
- a right-hand side you can perturb by `+1`.

What you want to observe:

1. The LP solves.
2. You can retrieve row duals.
3. The dual value behaves like a shadow price.

The example is not just for the docs. It is for your understanding.

## Section 8: Verify the meaning, not just the API

This is the most important experiment in the whole exercise.

Suppose the solver reports:

```python
b.get_row_dual(0) == 100
```

Do not stop there.

Change the first constraint's right-hand side by `+1`, solve again, and compare the objective value.

Ask:

- Did the objective increase by about `100`?
- If so, over what range does that interpretation seem to hold?
- If not, did I misunderstand the constraint, the indexing, or the model class?

This is how you learn what the number means.

Without this step, you only learn a retrieval recipe.

## Section 9: Second lesson — LP duals are not generic MIP duals

This is the other big educational point.

You need to be able to explain, in your own words, something like:

- dual values are natural sensitivity information for LPs,
- but one must be careful not to market them as a general "MIP duals" feature,
- especially when integer constraints are involved.

That does not require a full course in optimization theory. It does require honest wording.

Write a one- or two-sentence explanation for yourself:

"Why should the docs talk about LP dual values carefully if the modeling class is named `MixedIntegerLinearProgram`?"

If your answer is vague, go back and tighten your understanding.

## Section 10: Third lesson — solver mode matters

If the code or experiment shows that a solver parameter like `simplex_or_intopt` matters, that is not an incidental detail.

It is part of the documented workflow.

Your task is to learn:

- what parameter is being set,
- why it is being set,
- whether it is specific to GLPK,
- what happens if you do not set it.

Run both cases if you can:

1. solve with the relevant simplex mode,
2. solve without it.

Then write down what changed.

That comparison is educational because it turns a magic incantation into a reasoned step.

## Section 11: Design the doc addition

Only after the code trace and the tiny experiment should you decide what to write.

A good first patch is probably small:

- one short subsection,
- one worked example,
- one note or warning block.

The section should likely answer, in order:

1. What is a dual value?
2. In what situation are dual values available here?
3. How do I retrieve them in the supported workflow?
4. What does one of the reported values mean?
5. What limitations should I know before relying on this?

If your draft starts sounding like a proposal for broader MIP ergonomics work, pull it back.

## Section 12: Write a worked example with interpretation

Your example should do more than print numbers.

It should let the reader understand one number in plain English.

Good shape:

- create a small LP,
- add constraints in explicit order,
- solve with the appropriate backend settings,
- retrieve `get_row_dual(0)`,
- explain what that number means,
- optionally confirm it by changing the RHS.

The educational move is the interpretation sentence.

For example:

- "A dual value of 100 means that increasing this capacity by one unit raises the optimal objective by 100, at least locally."

Do not put that sentence in until you have verified it yourself.

## Section 13: Add caveats without being timid

The docs should be honest, not vague.

That means you should probably say some version of:

- this workflow uses the backend object,
- this example is for an LP solve in a supported solver/backend path,
- row duals are not being presented as a universal frontend API,
- if the model began life as a MIP, the interpretation needs care.

The goal is not to scare the reader off.

The goal is to tell the truth cleanly enough that the page remains accurate even if the frontend architecture changes later.

## Section 14: Exercise

Before you draft the final prose, answer these in your own words.

1. Why is this doc contribution still worthwhile even if the long-term MIP frontend may change?
2. Why is a backend-specific explanation acceptable here?
3. Why is a worked example better than just documenting `get_row_dual(i)` mechanically?
4. What exact sentence would you use to distinguish LP shadow prices from a generic MIP feature claim?

Do not look at your draft while answering.

If you cannot answer cleanly, you are not ready to write the docs yet.

## Section 15: Write the smallest honest patch

Now draft the new section.

Aim for:

- small,
- precise,
- local to `linear_programming.rst`,
- consistent with the rest of the page,
- educational without becoming a mini textbook.

Use this filter for every sentence:

- Did I verify this in code?
- Did I verify this experimentally?
- Or is this just what I wish were true?

Only keep the first two kinds.

## Section 16: Review your own patch like a maintainer

Read the draft again and ask:

1. Does this document current behavior rather than advocate for a larger frontend investment?
2. Is the solver/backend scope obvious?
3. Would a reader come away understanding what the numbers mean?
4. Have I accidentally implied support broader than what I verified?
5. Would this still read as accurate if Sage later adopted a different frontend?

If the answer to any of these is "no," revise.

## Section 17: Final verification

Before opening a PR:

- run the relevant doctests or doc checks,
- make sure the example output is stable,
- reread the new section without thinking about your own effort,
- ask whether a new user would find the path discoverable from the page alone.

That is the standard you are aiming for.

## Summary

If you work through this exercise properly, you should finish with more than a doc patch.

You should understand:

- why dual values live where they do in the current stack,
- why backend-specific documentation can still be valuable,
- why LP sensitivity information needs careful wording in a MIP-oriented interface,
- how to write a small contribution that is technically useful without overcommitting the project.

That is the educational value here.
