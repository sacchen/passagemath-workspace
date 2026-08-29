"""
demo.py -- run with:  python3 demo.py
Requires: pip install micrograd sage-numerical-interactive-mip
"""
from lp_layer import lp_value
from micrograd.engine import Value

A = [[1, 2], [2, 1]]

# 1) Backprop a downstream loss THROUGH the LP, gradient-checked ----------------
b = [Value(7.0), Value(5.0)]      # right-hand sides  (grads come from DUALS)
c = [Value(4.0), Value(5.0)]      # objective coeffs  (grads come from PRIMAL)

v = lp_value(A, b, c)             # LP optimum, as a differentiable Value
target = 25.0
loss = (v - target) * (v - target)
loss.backward()

print(f"p* = {v.data},  loss = {loss.data}")
print(" analytic  dL/db =", [round(p.grad, 4) for p in b],
      " dL/dc =", [round(p.grad, 4) for p in c])

def loss_only(bv, cv):
    vv = lp_value(A, [Value(x) for x in bv], [Value(x) for x in cv])
    d = vv - target
    return (d * d).data

eps, b0, c0 = 1e-6, [7.0, 5.0], [4.0, 5.0]
num_b = [(loss_only([b0[0]+eps*(i==0), b0[1]+eps*(i==1)], c0) - loss.data)/eps for i in range(2)]
num_c = [(loss_only(b0, [c0[0]+eps*(j==0), c0[1]+eps*(j==1)]) - loss.data)/eps for j in range(2)]
print(" numeric   dL/db =", [round(x, 4) for x in num_b],
      " dL/dc =", [round(x, 4) for x in num_c])

# 2) A few steps of gradient descent on the right-hand sides --------------------
print("\nLearning b to drive p* toward the target:")
b = [Value(7.0), Value(5.0)]
lr = 0.05
for step in range(8):
    for p in b:
        p.grad = 0
    v = lp_value(A, b, c)
    d = v - target
    (d * d).backward()
    for p in b:
        p.data -= lr * p.grad
    print(f"  step {step}: p*={v.data:6.3f}  b=({b[0].data:.3f}, {b[1].data:.3f})")

# 3) The kink: the gradient (dual) is only valid within one basis --------------
from sage.all__sagemath_polyhedra import QQ
from sage_numerical_interactive_mip import InteractiveLPProblem
print("\nVarying b1 -> watch the dual (=gradient) jump at the basis change:")
for b1 in range(7, 12):
    P = InteractiveLPProblem(A, [QQ(b1), QQ(5)], [QQ(4), QQ(5)], variable_type=">=")
    print(f"  b1={b1:2d}  p*={str(P.optimal_value()):>4}  "
          f"x*={P.optimal_solution()}  dual={P.dual().optimal_solution()}")
