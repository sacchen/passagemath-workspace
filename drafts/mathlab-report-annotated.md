# Davis Math Lab Project Report, Spring 2026

**[Your Name], Undergraduate Scholar**
**Matthias Köppe, Faculty Mentor**

> 💬 **TODO:** Drop in your real name. Confirmed: you + Köppe only, no graduate mentor.

---

## Introduction

Passagemath is a math software. It is modular and pip installable and can be used on Colab. Educators and students use it as a teaching and learning tool for things like the simplex method in linear programming. Math researchers use it to work with combinatorics and algebraic objects.

> 💬 **WORK ON THIS — weakest paragraph in the report.** "A math software" tells a cold reader nothing, and this is the first thing the Math Lab audience reads. They've never heard of passagemath. Answer one question concretely: *what can you do with passagemath that you can't easily do with plain Sage?* Raw material: it's a modular, pip-installable repackaging of SageMath (~40 packages) that runs in plain Python environments (Colab, JupyterLite) without installing all of Sage. The "modular" point isn't trivia — it's what makes your biggest PR theme (modular-install bugs) make sense later, so it earns its place here.

The main purpose of the passagemath group is to add features or fix bugs in the software and use passagemath as a tool for math interests.

> 💬 "math interests" is vague — same issue as "algebraic objects" above. Either name 1–2 concrete areas or cut the phrase.

I made code contributions, made onboarding documents and exercises, and explored the ideas of making linear programming easier to use in passagemath and the connection between backpropagation and linear programming.

> 💬 **DECISION NEEDED — backprop/LP.** You mention it here, but there's only a bare heading and no content for it later in the draft. A reader will expect the report to deliver on what the intro promises. Two clean options: (1) cut the backprop mention from this sentence so the intro matches the body, or (2) keep it and write a real 2–4 sentence paragraph below (what the connection is, what you explored, where you stopped). A promised-but-undelivered topic reads worse than not mentioning it. Note: the earlier handoff had this marked "cut" — your call to revive it, but it can't stay as a dangling heading.

---

## Progress

I made 13 pull requests that were merged into the passagemath codebase. The code contributions fall into four themes.

> 💬 **COUNT CONFIRMED: 13 merged PRs in passagemath/passagemath** (plus #6 in the external numerical-interactive-mip repo, so 14 total if you count that). The "13" is correct for the main repo. #2239 is an *issue* you diagnosed (Köppe wrote the fix), not one of the 13. **BUT "four themes" no longer quite holds:** PR #2356 (affine_homset complex-tolerance fix) doesn't fit modular / build-CI / plot / LP. Options: add a short fifth category, fold #2356 into one sentence, or change "four themes" to "mainly four areas."

### Modular installation

Since Sage installs everything, but passagemath only imports packages you need, a common bug was a function trying to import an optional package, but the import doesn't happen, and the function is called but was never assigned. I fixed this pattern for different files relating to combinatorics, number theory, and others. To help with this, I made `check_unbound_imports.py`, an abstract syntax tree tool that scans the codebase for this pattern, and categorized things into things that needed attention or just false positives.

> 💬 Strong section — clearest explanation of any theme. Minor: "a common bug was a function trying to import... but the import doesn't happen, and the function is called but was never assigned" is one long run-on. Consider splitting into two sentences. Otherwise leave it; the content is right.

### Build and CI infrastructure

A newer version of setuptools deprecated a thing and this caused Linux build crashes. I replaced it with the `importlib.metadata` API. I also discovered a Windows CI failure caused by an invalid path format that affects multiple packages across many releases. Professor Köppe made the fix based on this diagnosis.

> 💬 "deprecated a thing" — name it (it was `pkg_resources`, per PR #2237). One concrete noun makes you sound like you knew what you were doing, which you did.

### Plotting in Python kernels

In Colab and JupyterLite, passagemath plots used to show up as text (`Graphics object consisting of 1 graphics primitive`) instead of as images. The fix was to add a method to the `Graphics` class so Python knew where to get the images.

> 💬 Good and concrete. The text-instead-of-image detail is vivid — keep it. Optional: name the method (`_repr_png_` / `_repr_svg_`) for the technical reader.

### LP ergonomics

I documented dual values in the passagemath linear programming guide.

> 💬 Fine as a one-line theme summary since you expand it in the dedicated section below. (You don't have a "see below" pointer in this pasted version — consider adding one so the reader knows more is coming.)

### Research approach

My approach to choosing what to work on was to prioritize based on scale, neglectedness, and fit. This included infrastructure problems that affected many areas and bugs from passagemath being modular. I used AI tools to find widespread codebase errors and read long CI logs that made it more feasible to work on the most important things. This was very good for getting to know the codebase and getting contributions.

Later, my approach was to help my teammates get started fast. This looked like making a list of shovel-ready issues with descriptions of the problem and a potential solution, making onboarding documents, and exercises.

Eventually the returns leveled out. I didn't feel like I was learning generalized software engineering skills or math.

> 💬 **REVISIT — this is now the trickiest call in the report.** Earlier you wanted to reframe this as a pivot into LP ergonomics. But you've since said you're *not* continuing passagemath and LP is too hard — so there's no pivot to point to; that framing would be untrue. For a public retrospective, this bare line reads as a complaint a reader can't contextualize. Cleanest options: (a) cut it, and let the report stand on the work; or (b) soften to a neutral reflection on diminishing returns from incremental bug-fixing without the self-critical edge. Don't claim a pivot that didn't happen.

### Onboarding documents and exercises

When students joined the group at the beginning of Spring 2026, I made documents to help teammates set up the passagemath environment and also made exercises that introduced generalized bug patterns as a way to get teammates touching the codebase fast.

A common problem was getting the environment set up. This involved jupyter, git, and things tended to get messy.

I also helped a teammate, Runze (Tony) Yu navigate the codebase and git workflow while he worked on a pull request.

> 💬 Good. Tiny grammar: "Runze (Tony) Yu navigate" → "Runze (Tony) Yu navigate" needs a comma: "...teammate, Runze (Tony) Yu, navigate..."

### pm-explore

The first assignment Professor Köppe gave us was to make a notebook exploring some part of passagemath. Getting the environment to work with the right kernel got a lot of people stuck and a lot of time was spent on debugging environment problems. This inspired me to make pm-explore which automates this.

Given any passagemath file, pm-explore automatically generates a jupyter notebook with the environment set up so people can see what methods the file has and can immediately run and modify methods. It uses an abstract syntax tree to look at the text, so it works even when the environment is broken. Afterwards, I learned that this is similar to the runnable code in the passagemath documentation website. The explore-pm tool is good for having it work on your own computer like a student researcher who wants to explore the codebase would use. It is also interactive and you can make changes to play around with the methods.

> 💬 Good section. Two fixes: (1) naming — you write "pm-explore" twice then "explore-pm" once. Pick one (it's pm-explore) and use it everywhere. (2) Last two sentences are a bit redundant ("interactive / run and modify / play around" all say the same thing). Tighten to one.

### Research approach and experience

The stuff about breadth/depth and research approach.
This was very good for getting to know the codebase and getting contributions. My approach was choosing high leveraged things based on scale, neglectedness, and fit.

> 💬 **DELETE THIS WHOLE SUBSECTION — it's a duplicate.** "The stuff about breadth/depth and research approach" is a placeholder note to yourself, and the rest just repeats your earlier "Research approach" section almost word for word. Merge anything unique into the first one and remove this heading.

### LP ergonomics

I was taking MAT 168 Optimization and tried to use passagemath instead of cvxpy. You had to write nested loops and keep track of indices often, which made it difficult to use. Some methods you would like easy access to like getting dual values had to be found in the backend. (Issue #2347).

I thought it could be worth working on because this was a place where passagemath could really be improved. Passagemath can handle symbolics and is integrated with other math things. This whole idea is very big though. There would be architectural and frontend changes that would take careful design considerations. I would have to familiarize myself with what was currently going on. My plan was to edit the documentation so it would be easier to find the dual values (PR #2353). Next, I tried tracing through the backend with the goal of understanding what was going on. It was very difficult. The files were scattered. The next step was to work through linear programming problems myself to identify specific pain points to eventually bring up and propose potential solutions. This was something I wasn't naturally doing. I was doing cvxpy for class and doing it in passagemath was difficult.

> 💬 This is honest and reads well as a *retrospective* — "I scoped a hard problem, did Level 1 (docs), looked at the backend, and found it bigger than expected." That's a legitimate research finding. Since you're not continuing, keep it firmly in past tense and don't end on "the next step was..." (which implies you'll do it). One concrete strength worth adding: passagemath's real edge over cvxpy is *exact arithmetic over QQ / number fields* — cvxpy is float-only. That one sentence explains why this is worth anyone's effort at all.

I also presented the plotting fix to the mid-quarter presentations.

> 💬 This sentence is stranded under the LP section but is about plotting. Move it — either to the Plotting theme above, or into a short "presentations/outreach" note. As written it looks misplaced.

connection between backpropagation and linear programming

> 💬 **DECISION (ties to the intro note).** This is a bare heading with no content. Either write the paragraph — what the connection is, what you explored, what you found, why you stopped — or cut both this and the intro mention. Right now it's the most visibly unfinished part of the draft.

---

## Future Plans

I plan to present work at the Math Lab poster session in Fall 2026.

> 💬 **This needs to reflect reality: you're not continuing passagemath.** That's fine — a short, honest Future Plans is better than inventing work you won't do. Right now it's a single sentence, which is thin but at least true. Two ways to make it stronger without lying: (1) frame the poster as the natural capstone — what you'd present and why it's useful to the Math Lab audience; (2) optionally note the open directions you *identified* (ergonomic LP helpers, the cvxpy-style frontend, the backprop/LP connection) as things "worth pursuing" — left for future contributors, not committed to by you. Don't write "I will continue LP ergonomics" — that's the part that's no longer true.

---

## References

> 💬 Empty. Drop in the list below (gathered from your actual PRs/issues). Decide on a style — grouping by theme like this matches your Progress structure and reads well. Re-confirm the PR count here against the "13" claim above.

**Modular installation robustness**
- #2253 — Fix NameError in `Partitions.cardinality()` when passagemath-flint is absent — https://github.com/passagemath/passagemath/pull/2253
- #2282 — Fix unbound pari NameError in five modules; lazy-import sympy in calculus_method — https://github.com/passagemath/passagemath/pull/2282
- #2283 — Fix unbound NameError in padic_extension_leaves and multi_polynomial_ideal; add AST checker — https://github.com/passagemath/passagemath/pull/2283
- #2287 — Fix pickling regression introduced by lazy_import in calculus_method.py — https://github.com/passagemath/passagemath/pull/2287
- #2293 — polynomial_quotient_ring: add `# needs sage.modules` doctest guards — https://github.com/passagemath/passagemath/pull/2293
- #2292 — docs, tox: document check_unbound_imports and add tox env — https://github.com/passagemath/passagemath/pull/2292
- #2354 — Add missing sage.libs.linbox doctest guards in modsym and geometry/cone — https://github.com/passagemath/passagemath/pull/2354

**Build / CI**
- #2237 — build: replace pkg_resources with importlib.metadata in configure check — https://github.com/passagemath/passagemath/pull/2237
- #2239 — `PIP_FIND_LINKS=file://$SAGE_SPKG_WHEELS` yields invalid uri on Windows (issue you diagnosed; Köppe wrote the fix) — https://github.com/passagemath/passagemath/issues/2239

**Plot display**
- #2351 — Fix plot display in plain Python Jupyter kernels — https://github.com/passagemath/passagemath/pull/2351
- #2366 — plot: add `_repr_svg_()` for plain Python Jupyter kernels — https://github.com/passagemath/passagemath/pull/2366
- #2368 — plot: fix circular import in plain Python by pre-importing sage.structure.element — https://github.com/passagemath/passagemath/pull/2368

**LP ergonomics**
- #2353 — glpk_backend: document `get_row_dual` via MixedIntegerLinearProgram — https://github.com/passagemath/passagemath/pull/2353
- #2347 — MIP workflow is harder than cvxpy for matrix-structured LP problems (motivating issue) — https://github.com/passagemath/passagemath/issues/2347

**Numerical correctness (doesn't fit the four themes — see note above)**
- #2356 — affine_homset: fix complex-tolerance comparison in numerical point filtering — https://github.com/passagemath/passagemath/pull/2356

**External package**
- numerical-interactive-mip #6 — backends: correct exception types in dictionary constructors and pivot update — https://github.com/passagemath/passagemath-pkg-numerical-interactive-mip/pull/6
