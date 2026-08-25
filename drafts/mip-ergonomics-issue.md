MIP workflow gaps I hit doing LP coursework in passagemath

Writing this to get a sense of what's in scope before opening any PRs.

I'm working through Vanderbei's airline revenue management problem in passagemath for MAT168. A few things slowed me down.

## Getting dual values

The cvxpy version ends with:

```python
print(constraints[0].dual_value)  # shadow price of the Ithaca-Newark leg
print(constraints[1].dual_value)  # shadow price of the Newark-Boston leg
```

In passagemath I got there, but it took some digging. You have to build the LP relaxation as a separate model, set a solver parameter, and call into the backend directly:

```python
lp = MixedIntegerLinearProgram(maximization=True, solver='GLPK')
xlp = lp.new_variable(nonnegative=True)
# ... repeat all constraints ...
lp.solver_parameter('simplex_or_intopt', 'simplex_only')
lp.solve()
b = lp.get_backend()
print(b.get_row_dual(0))  # 100.0 — one extra seat on Ithaca-Newark is worth $100
print(b.get_row_dual(1))  # 130.0 — one extra seat on Newark-Boston is worth $130
```

The numbers check out. But none of this is in `linear_programming.rst` — I found the pattern by reading the GLPK backend source. Is there a simpler path I missed, or is a worked example in the tutorial worth adding?

## Demand bounds

In cvxpy you write `x <= demand` and it broadcasts across the matrix. In passagemath that's:

```python
for i in range(3):
    for j in range(3):
        p.add_constraint(x[i, j] <= demand[i][j])
```

Is there appetite to close that gap?

## `get_values` returns a dict

After solving, `p.get_values(x)` returns a dict with `(i, j)` keys. To print the solution I ended up writing:

```python
for j, route in enumerate(route_names):
    tickets = {c: int(vals[i, j]) for i, c in enumerate(class_names)}
    print(f"Tickets for {route}: {tickets}")
```

Returning something array-shaped when the variable has 2D indexing would be cleaner — though I imagine this might interact with how the backend stores values.
