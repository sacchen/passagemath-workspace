"""
lp_layer.py  -- backprop THROUGH a linear program, using micrograd + passagemath.

The whole trick is the envelope theorem for an LP

        p*(b, c) = max { c . x : A x <= b, x >= 0 }

      d p* / d b_i  =  y*_i      (optimal DUAL variable / shadow price of constraint i)
      d p* / d c_j  =  x*_j      (optimal PRIMAL variable j)

So to make the LP differentiable inside a micrograd graph we just solve it once
(forward) and, in the backward pass, hand each input Value its partial: the dual
for a right-hand-side input, the primal for an objective-coefficient input.

This is exactly the "multiplier = dual = shadow price = backprop error signal"
identity, made executable.
"""

from sage.all__sagemath_polyhedra import QQ
from sage_numerical_interactive_mip import InteractiveLPProblem
from micrograd.engine import Value


def _q(v):
    """micrograd Value (or number) -> exact rational, so Sage stays on the exact path."""
    x = v.data if isinstance(v, Value) else v
    return QQ(float(x))


def lp_value(A, b, c):
    """
    Solve  max c.x  s.t.  A x <= b, x >= 0  and return the optimal value as a
    micrograd Value that is differentiable w.r.t. any Value entries in b and c.

    A : list[list[number]]            (constant matrix; not differentiated)
    b : list[Value | number]         right-hand sides
    c : list[Value | number]         objective coefficients
    """
    Aq = [[QQ(float(a)) for a in row] for row in A]
    bq = [_q(bi) for bi in b]
    cq = [_q(cj) for cj in c]

    P = InteractiveLPProblem(Aq, bq, cq, variable_type=">=")
    x_star = P.optimal_solution()          # primal  -> grads for c
    y_star = P.dual().optimal_solution()   # dual    -> grads for b
    val = float(P.optimal_value())

    # children = the Value objects we can push gradient into
    parents = [t for t in (*b, *c) if isinstance(t, Value)]
    out = Value(val, tuple(parents), "lp")

    def _backward():
        g = out.grad
        for bi, yi in zip(b, y_star):
            if isinstance(bi, Value):
                bi.grad += float(yi) * g
        for cj, xj in zip(c, x_star):
            if isinstance(cj, Value):
                cj.grad += float(xj) * g

    out._backward = _backward
    return out
