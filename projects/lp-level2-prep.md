# Level 2 Investigation Guide

Reference for understanding the existing passagemath LP stack before designing
ergonomic helpers. The sections build on each other, so the reading order matters.

---

## Architecture overview

passagemath's LP stack has three layers:

```
User code
    │  MixedIntegerLinearProgram (mip.pyx)
    │      Translates user-facing Python into backend calls
    │      Manages variables, constraints, objective as LinearFunction objects
    │
    ├── GenericBackend (generic_backend.pyx)
    │       Abstract interface — defines what every backend must implement
    │       Pure Cython (cpdef methods)
    │
    └── Specific backends (glpk_backend.pyx, highs_backend.pyx, ppl_backend.pyx, ...)
            Each wraps a solver library
            May expose extra methods beyond GenericBackend (e.g. get_row_dual)
```

`MixedIntegerLinearProgram` only calls methods that exist on `GenericBackend`.
Anything that's only on a specific backend (like `get_row_dual`) requires the
caller to use `p.get_backend()` and access the specific type directly — that's
why the current dual workflow involves so much boilerplate.

---

## 1 — `mip.pyx`: the user-facing layer

**File:** `src/sage/numerical/mip.pyx`

This is Cython (`.pyx`). The `cdef`/`cpdef` keywords are performance annotations;
the `def` methods are the public Python API.

### Variables

`new_variable` is at line ~718. `MIPVariable` is at line ~3223.

`MIPVariable` is a subclass of `FiniteFamily` — a Sage dict-like container. When
you write `x = p.new_variable()` and then `x[0]`, `x[1,2]`, etc., you're working
with `LinearFunction` objects keyed in a dict. The variable's position in the
solver's internal column array is implicit.

**`new_variable(indices=...)`** pre-declares a fixed set of keys and locks the
variable to those keys — accessing any other key raises an error. It's a
validation mechanism, not a shape declaration. The keys can be arbitrary
hashables, so `indices=[(i,j) for i in range(m) for j in range(n)]` works, but
`MIPVariable` has no notion of a 2D shape. A matrix extraction helper would need
the shape passed separately.

### Constraints

`add_constraint` is at line ~1874.

It has a `return_indices=True` keyword argument — when set, it returns the integer
indices of the constraints just added. This is the existing constraint handle
mechanism.

Three caveats from the source:

**Backend-dependent.** The docstring says it returns indices only "if the backend
guarantees that removing them again yields the original MIP", and `None` otherwise.
Which backends actually return indices is worth checking.

**Ranged constraints add two rows.** The doctest shows `0 <= x[0] <= 3` with
`return_indices=True` returns `[1, 2]` — one index per bound. If ranged
constraints are in scope for a vectorized wrapper, the return structure becomes
more complex.

**Indices shift on removal.** The doctest shows `p.remove_constraint(1)` called
twice to remove what were originally indices 1 and 2, because the first removal
shifts everything down. Constraint handles are fragile to subsequent removes.

### Solution extraction

`get_values` is at line ~1542.

It accepts a `MIPVariable` or list thereof, and returns a dict mapping each key
to its solution value. The result is always a flat dict. For a variable indexed
as `x[i,j]`, the keys are `(i,j)` tuples — so matrix reconstruction requires an
explicit comprehension over the known index structure.

---

## 2 — `generic_backend.pyx`: the contract

**File:** `src/sage/numerical/backends/generic_backend.pyx`

This is the abstract interface every backend implements. Skim the method list.

There is no dual-related method on `GenericBackend` — no `get_row_dual`, no
`dual`, no `get_dual`. `get_row_dual` is a backend-specific extension. Any
`MixedIntegerLinearProgram`-level dual helper would need to either dispatch
conditionally by backend type, or require the caller to have already retrieved the
backend.

The post-solve query methods that *do* exist on the generic interface
(`get_objective_value`, `get_variable_value`, ...) are worth listing — these are
the only ones a `MixedIntegerLinearProgram`-level helper can call unconditionally.

---

## 3 — `glpk_backend.pyx` and `highs_backend.pyx`: duals in practice

**Files:**
- `src/sage/numerical/backends/glpk_backend.pyx`, line ~2593 (`get_row_dual`)
- `src/sage/numerical/backends/highs_backend.pyx`, line ~1049 (`get_row_dual`)

`get_row_dual` exists on GLPK and HiGHS only. PPL, cvxopt, and interactivelp do
not have it. Both implementations take a row (constraint) index and return a
`double` — not a Sage rational, a C double. This is a real constraint for any
exact-arithmetic use case.

**The `simplex_or_intopt` requirement is GLPK-specific.** GLPK's `get_row_dual`
returns `0.0` silently if the simplex algorithm wasn't used — that's why the
`simplex_or_intopt` setup step is required when using GLPK. HiGHS has no
equivalent: its doctest calls `lp.solve()` directly with no pre-solve parameter
and returns correct duals. Any dual wrapper needs to handle these two backends
differently, or document the GLPK-specific precondition explicitly.

**Behaviour before `solve()` is undefined.** Both implementations document this.

**Also check:** `src/sage/numerical/backends/ppl_backend.pyx` and
`interactivelp_backend.pyx`. PPL is the exact rational/number-field backend;
interactivelp is the pure-Python exact backend used in the interactive simplex
notebook. Neither has `get_row_dual`. The implication is that any dual API is
float-only — a constraint worth factoring into the design given that exact
arithmetic is one of passagemath's differentiators.

---

## 4 — sagemath/sage#31981: the CVXpy direction

**URL:** https://github.com/sagemath/sage/issues/31981

The architectural sketch referenced in #2347. Read the full thread.

Relevant questions:
- How does the CVXpy frontend relate to the current `MixedIntegerLinearProgram` API
  — replacement or parallel layer?
- What's the plan for exact arithmetic in that design?
- Does any Level 2 work fit naturally into it, or would it be dead weight?

The answer here shapes a key design choice: whether helpers should be new methods
on `MixedIntegerLinearProgram` (more discoverable, more surface area on a class
that may not be the long-term investment) or a thin module sitting above it
(easier to deprecate or adapt later).

---

## 5 — Work through a matrix-structured problem

The transportation problem from Vanderbei Exercise 1.2 (the origin of #2347) is a
good candidate, as is any assignment problem with a cost matrix and supply/demand
constraints.

The current workflow in passagemath:

```python
p = MixedIntegerLinearProgram(solver='GLPK')
x = p.new_variable(nonnegative=True)

for i in range(m):
    p.add_constraint(sum(x[i,j] for j in range(n)) <= supply[i])
for j in range(n):
    p.add_constraint(sum(x[i,j] for i in range(m)) <= demand[j])

p.set_objective(sum(cost[i][j] * x[i,j] for i in range(m) for j in range(n)))
p.solve()

sol = p.get_values(x)
matrix = [[sol[i,j] for j in range(n)] for i in range(m)]
```

Things to note while working through it:
- What index bookkeeping is manual and error-prone?
- What would the dual retrieval look like for the supply and demand constraints?
  What indices do you need, and how do you get them?

---

## 6 — Open design questions

After working through the above, these are the questions that don't have obvious
answers yet:

**On vectorized constraints:**
- What should `add_constraints` (plural) return — a list of indices, a dict keyed
  by row, something else? How should ranged constraints be handled?
- Which backends actually honor `return_indices=True`?

**On solution extraction:**
- Can `get_values_matrix` be written purely on top of `get_values`, or does it
  need backend access?
- What type does it return — a Python list-of-lists, a Sage `Matrix`, a numpy
  array? (`Matrix` is exact-arithmetic-safe; numpy is not.)

**On duals:**
- Given that `get_row_dual` is GLPK/HiGHS only and returns `double`, what is the
  honest scope of a `dual_values()` helper? Should it require a specific backend?
  Should it live on `MixedIntegerLinearProgram` at all?

**On placement:**
- After reading #31981: new methods on the class, or a separate thin module?

---

## Reading order summary

| Step | File/Resource | Key question |
|------|--------------|--------------|
| 1 | `src/sage/numerical/mip.pyx` | Which backends honor `return_indices=True`? What does `get_values` return for a 2D-indexed variable? |
| 2 | `src/sage/numerical/backends/generic_backend.pyx` | Which post-solve query methods exist on the generic interface? |
| 3 | `glpk_backend.pyx:2593`, `highs_backend.pyx:1049`, `ppl_backend.pyx`, `interactivelp_backend.pyx` | Which backends support duals? PPL and interactivelp (the exact backends) do not. |
| 4 | sagemath/sage#31981 | Does Level 2 fit the CVXpy direction or conflict with it? |
| 5 | Your notebook | What friction points appear in practice? |
