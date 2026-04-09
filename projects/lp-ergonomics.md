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

**Level 1 — docs PR** ✓ DONE — PR #2353 merged 2026-04-08
Documented dual values, matrix solution patterns, the `simplex_or_intopt`/`get_row_dual` workflow in `linear_programming.rst`.

**Level 2 — ergonomic helpers** (current — pre-proposal phase)
Vectorized constraint addition, matrix solution extraction, cleaner dual value API in `mip.py`. Design the interface from actual MAT 168 problems. Get mkoeppe's architectural feedback before writing any code.

### Pain points from #2347 (what Level 2 addresses)

| Pain point | Status |
|---|---|
| Dual value discoverability (`simplex_or_intopt`/`get_row_dual`) | Fixed by #2353 |
| Vectorized constraint addition — cvxpy does `x <= demand` in one line; passagemath requires a nested loop | Open |
| `get_values` returns a flat dict — reconstructing a solution matrix takes extra bookkeeping | Open |
| Dual value API is clunky even when documented — no `dual_values()` parallel to `get_values()` | Open |

### Design considerations

**Number field generality.** cvxpy is float-only. Any helper that accepts numpy arrays will silently coerce rationals to floats. Sage `Matrix` over `QQ` is the right coefficient type. JuMP is type-parameterized and is the closer model here.

**mkoeppe's investment horizon.** He has explicitly said MIP is underdeveloped and he'd rather adopt CVXpy long-term (sagemath/sage#31981). Prefer thin wrapper functions over new methods on `MixedIntegerLinearProgram` — easier to replace later.

**Constraint handle → dual linkage.** `add_constraint` returns an integer index. A vectorized `add_constraints` should return a structured handle (list or dict of indices) so that `dual_values(handle)` can mirror `get_values`. This is JuMP's named-constraint pattern.

**Where it lives.** Two options to put to mkoeppe:
- New methods on `MixedIntegerLinearProgram` — more discoverable, more surface area on a class he'd rather not grow
- Thin module (`sage.numerical.mip_tools` or similar) — easier to deprecate, doesn't touch the class

**Inspiration split.** cvxpy for variable shape declaration and solution extraction syntax. JuMP for constraint naming and dual access pattern.

### Pre-proposal homework (do before meeting mkoeppe)

- [ ] Read `src/sage/numerical/mip.py` — understand existing API surface, what already exists
- [ ] Check which backends expose `get_row_dual` — is it GLPK-only? Constrains the dual API design
- [ ] Read sagemath/sage#31981 — mkoeppe's CVXpy architectural sketch, understand Level 3 shape before proposing Level 2
- [ ] Work through a MAT 168 problem that hits the vectorized-constraint friction — have a concrete "I had to write this loop" example
- [ ] Sketch a concrete API proposal (even rough) — the meeting needs something to react to

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

- **#2347** — MIP workflow harder than cvxpy for matrix-structured LP. mkoeppe confirmed MIP is underdeveloped and sketched the cvxpy frontend direction. Now the source of Level 2 scope.
- **#2351** — Plot display fix in plain Python kernels. Open. Came from coursework hitting a real blocker.
- **dual-value notebook** — `exercises/linear-programming-duals/linear-programming-duals.ipynb`. Done. Built intuition for duals; informed #2353.
- **interactive simplex notebook** — `exercises/interactive-simplex/interactive-simplex.ipynb`. Done. Built real simplex intuition.
