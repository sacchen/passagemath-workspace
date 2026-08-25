I'm doing MAT168 (Vanderbei's LP course) and trying to use passagemath instead of cvxpy or JuMP. The math works, but the workflow is noticeably harder for matrix-structured problems.

The three places I felt it most:

- **Demand bounds** require a nested loop. cvxpy does `x <= demand` in one line.
- **Dual values** took real digging — I had to find the `simplex_or_intopt` / `get_row_dual` pattern in the GLPK backend source. Nothing in `linear_programming.rst` covers it.
- **`get_values` returns a dict**, so reconstructing the solution matrix requires extra bookkeeping.

Is improving MIP ergonomics for scientific Python users something you'd want contributions toward? Happy to start with a tutorial PR for the dual value pattern if that's useful.
