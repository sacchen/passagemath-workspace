# GPU math visualization: the gap

You built a graphing calculator. Now consider the same problem with geometry
that lives in 10 dimensions, is defined by exact rational arithmetic, and
needs to run in a browser tab with no server.

The current solution for 3D math visualization in the browser is a Java applet
from 2002. It doesn't run in browsers anymore. The fallback is CPU-side
Three.js. In JupyterLite — Jupyter running fully in the browser via WASM —
3D visualization falls back to ASCII.

Nobody has replaced it. That's the gap.

---

## Why math geometry is a different problem

Game geometry is approximate. Triangulate, texture, light, done. Close enough
is fine.

Mathematical objects are not close enough:

**Polytopes** are defined by linear inequalities over exact rationals, not by
a mesh someone made in Blender. A 600-cell — a 4D regular polytope with 600
tetrahedral cells projected to 3D — has exact combinatorial structure. Naive
float conversion throws that away. For objects with known symmetry groups you
can do better.

**Algebraic surfaces** like `x⁴ + y⁴ + z⁴ = 1` have no natural triangulation.
The right approach is implicit surface ray-marching — evaluate the equation
per pixel in a compute shader, find the zero crossing, shade it. WebGPU
compute shaders can do this. Nobody has done it in a browser math context.

**Hyperbolic geometry.** SageMath plots things in hyperbolic space — geodesics,
tilings, fundamental domains. Hyperbolic geometry doesn't embed cleanly in
Euclidean 3D. The Poincaré disk and upper half-plane models have their own
rendering math. On the GPU this is its own problem with no off-the-shelf
solution.

**High-dimensional projections.** A polytope in 10 dimensions projected to 3D
has combinatorial explosion in its face structure. Real LOD and culling logic
matters.

---

## The technical situation

WebGPU is stable in Chrome, Safari, and Firefox. Vulkan-level control, compute
shaders, runs in the browser.

What exists:
- `passagemath-plot` — Python package that produces 3D plot objects
- Three.js integration — works, CPU-side, no WebGPU
- Jmol — dead

What doesn't exist:
- A WebGPU renderer for mathematical objects in JupyterLite
- Implicit surface ray-marching in a browser math notebook
- Anything that uses the GPU for this class of geometry

The interesting build: a WebGPU backend for `passagemath-plot`. Polytope
wireframes and faces from exact coordinates → GPU buffer. Implicit surfaces
via compute shader ray-march. Works in a notebook cell. Falls back to Three.js
when WebGPU isn't available.

---

## Why now

WebGPU shipped stable in 2023. JupyterLite is production-ready. passagemath
is actively being ported to WASM by a math professor at UC Davis (Matthias
Köppe) who cares about this layer and takes contributors seriously.

The gap exists because the people who maintain the math don't do GPU
programming, and the people who do GPU programming don't work on math
platforms. That intersection is empty.

The moment where WebGPU, JupyterLite, and an active WASM port are all
simultaneously ready is now.
