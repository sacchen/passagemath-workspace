# LP ergonomics in passagemath

## The actual goal

Be good at *doing* optimization — modeling novel problems, solving them, interpreting results. Passagemath is the vehicle because it forces depth (the tooling won't paper over gaps the way cvxpy does) and because contributing back to it is how learning becomes useful to others.

## Why passagemath specifically

The "unique capability" framing is partially true but overstated. Exact LP exists elsewhere (SoPlex, QSopt_ex, PPL backend in passagemath itself). The more honest case:

- **Sage integration**: if your work mixes LP with symbolic computation, number fields, or algebraic certificates, cvxpy can't do that. Passagemath can.
- **Course alignment**: mkoeppe is both maintainer and MAT 168 instructor. PRs in this area get reviewed by the person who most understands the value, and the course provides a steady supply of real test cases.
- **Personal stakes**: deborgen is a real scheduling/allocation problem. Building it in passagemath means the tool gets tested against something that matters.

## The progression

```
docs PR                 ergonomic helpers          cvxpy frontend
(linear_programming.rst) (mip.py)                  (architectural)
weeks                   weeks–months               months
─────────────────────────────────────────────────────────────────►
entry point             only after owning L1        long-term possibility
```

**Level 1 — docs PR** (current)
Document dual values, matrix solution patterns, the `simplex_or_intopt`/`get_row_dual` workflow. Based on #2347 pain points and the dual-value notebook. The docs PR should follow genuine understanding — don't write it until you can explain duals without looking anything up.

**Level 2 — ergonomic helpers**
Vectorized constraint addition, matrix solution extraction, cleaner dual value API in `mip.py`. Design the interface from actual MAT 168 problems. Get mkoeppe's architectural feedback before writing any code. Only pursue this after Level 1 is genuinely understood.

**Level 3 — cvxpy frontend**
mkoeppe sketched this in sagemath/sage#31981: CVXpy parameters instead of float coefficients, Sage wrappers around CVXpy model objects, solver dispatch through passagemath backends. Multi-month. Worth understanding the design even if implementation is far off.

## The organic engine

Do MAT 168 assignments in passagemath. When something is rough, file an issue. When you understand an issue well enough, fix it. #2351 and #2347 both came from this. Don't short-circuit the loop by falling back to cvxpy.

The notebooks are part of this — not prep work before the real contribution. The interactive simplex notebook built real intuition about the algorithm. The dual-value notebook is doing the same for duals. That understanding is what makes the docs PR worth writing.

## Working with mkoeppe

mkoeppe does video meetings only. That means:

- Async (GitHub) is for narrow, well-defined back-and-forth
- Video is for design discussions, architectural questions, course corrections
- Come prepared: "I've been working through X in MAT 168, hit this friction, I'm considering approaches A and B, here's why I lean toward B"
- Accumulate questions through the coursework. Schedule a meeting when you have something concrete enough to discuss.

## What not to do

- Don't take shovel-ready issues unless they're blocking your own work
- Don't do issue mining sessions — existing queue beats what you'll find
- Don't over-invest in student setup — one group session maximum
- Don't touch CI/uv migration (mkoeppe is driving #2094)
- Don't rush to Level 2/3 — they require design opinions you earn by doing Level 1 first
- Don't write the docs PR before you own the material

## Student cohort role

Multiplier *when* unblocked, not a dependency. Keep #2108 and #2290 reserved for them. Offer one synchronous setup session; if they show up, great. Then move on.

## Active threads

- **#2347** — MIP workflow harder than cvxpy for matrix-structured LP. mkoeppe confirmed MIP is underdeveloped and sketched the cvxpy frontend direction.
- **#2351** — Plot display fix in plain Python kernels. Open. Came from coursework hitting a real blocker.
- **dual-value notebook** — `exercises/linear-programming-duals/linear-programming-duals.ipynb`. The learning artifact that precedes the Level 1 docs PR.
- **interactive simplex notebook** — `exercises/interactive-simplex/interactive-simplex.ipynb`. Built real simplex intuition. Model for how the dual-value notebook should feel.
