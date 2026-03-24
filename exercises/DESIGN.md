# How to build an exercise notebook

Notes from building `importerror-fix-pattern.ipynb`. Apply to future notebooks in this series.

---

## Structure: encounter → trace → fix → verify → exercise

Don't open with "here is the pattern." Open with the bug. Let the reader hit the error first, then explain what happened. By the time you show the fix, they already want it.

The full arc:
1. **Encounter** — run code, get a confusing error
2. **Trace** — explain mechanically why the error happens
3. **Fix** — show the endorsed solution
4. **Verify** — run both the broken and fixed versions, compare output
5. **Exercise** — apply the pattern to a different instance of the same bug

---

## Synthetic reproduction

When the real bug can't be reproduced in the teaching environment (e.g., the optional library happens to be installed), build a minimal synthetic example that mirrors the exact structure. `raise ImportError(...)` stands in for a real missing package. Keep it short — 5-8 lines max. The structure should map directly to the real code.

---

## Use real code from git history

The "before fix" code should come from `git show <commit>`. Not a paraphrase. If readers trace it in the real repo they should find the same thing. The answer cell should be the actual committed diff, with a link to the PR.

This is more motivating than invented examples and forces accuracy.

---

## Pause points

Before revealing the fix, ask the reader to attempt it. Be explicit: "try writing the fix before reading on." Give them a broken code cell to work in. Make the broken state obvious — comment marking what to fix, clear goal stated.

Don't give a pause point after every cell. One before the main fix reveal (Section 4→5) and one at the exercise (Section 8) is enough.

---

## Self-contained cells

Any cell that demonstrates something should work regardless of kernel state. Don't rely on names defined in earlier cells inside demonstration cells — redeclare them inline. Use distinct variable names (prefixed `_`) to avoid collisions.

---

## Show the error contrast

The payoff of any fix is the difference in error messages. Always show both:
- The broken version's error (what the user sees now)
- The fixed version's error (what they should see)

Put them side by side. A table works well for this.

Know exactly which error type the broken code raises. `TypeError`, `NameError`, and `AttributeError` are different. Getting this wrong breaks the "you've got it right when..." check at the exercise.

---

## The interesting detail

Every bug pattern has one thing that makes it genuinely surprising. Find it and put it in. For the ImportError pattern it was the intermittent masking — same install, different call order, different behavior. That's what makes the notebook memorable rather than just instructional.

---

## Kernel and setup first

Always put a setup cell that fails loudly on the wrong kernel. Don't let the reader get five cells in before discovering the environment is wrong.

---

## Tone

- Casual, interested, showing something cool
- Short sentences
- "Plot twist" not "Note that"
- Don't re-explain what the cell output already shows
- Don't moralize about good practices ("the kind of thing you only find by...")
- Let the code and the contrast do the work

---

## Exercise framing

Be explicit about what's already done vs. what the reader needs to do. If step 1 of the fix is already set up for them (e.g., the `= None` binding), say so. Don't make them repeat steps they already practiced — give them the next hard thing.

The success condition should be specific: "once your cell raises X instead of Y, you've got it."

---

## Evaluating educational value before building

Before building an exercise, ask: does understanding this pattern let the reader do something they couldn't do before — independently, in code they haven't seen?

The ImportError pattern passes this test. It teaches something about Python itself — name binding, what `pass` actually does to scope — that transfers to any project. After the exercise, you can find new instances with the AST checker and fix them without guidance.

The `# needs sage.X` guard pattern doesn't pass it. The lesson is a single rule: guard every line that uses a name bound under a dep. Once you've seen the trap, you know the rule. There's no concept underneath it to reason about, and you only encounter it reactively (when CI fails). It's a convention, not a pattern.

The distinction:
- **Concept** — something about how Python or the system works. Generalizes. Worth an exercise.
- **Convention** — a project-specific rule. Doesn't generalize. Worth a short reference doc, not an exercise.

A good topic also gives the reader agency: they can go find more instances and fix them. If the skill is only useful when CI hands you a specific failure, the exercise isn't opening a door — it's just explaining a sign on a door you may never reach.

When in doubt: if you can fully convey the lesson in a page of prose, it's a reference doc. An exercise earns its length by requiring the reader to reason, not just recognize.

---

## pyproject.toml

Each exercise folder gets its own `pyproject.toml` with the minimal deps needed. `uv sync` + kernel registration should be the entire setup. Don't pull in more than needed — it slows install and obscures what the notebook actually depends on.
