# passagemath WebAssembly — nerdsnipe brief

## What is this

passagemath is a modular, pip-installable fork of SageMath — a 30-year-old open-source
math research platform written in Python/Cython/C. One person (Matthias Köppe, math
professor at UC Davis) is doing the modularization essentially alone.

The goal: run passagemath entirely in the browser via WebAssembly. No server. A math
research environment that loads like a webpage.

There is already a live demo: http://passagemath.org/passagemath-jupyterlite-demo/

It works for some packages. Most of the math library stack is not yet ported.

---

## The technical situation

SageMath depends on a large stack of C math libraries: PARI, FLINT, Singular, GAP,
Normaliz, NTL, FLINT, fplll, and ~60 more. Each one needs to be cross-compiled to
wasm32 using Emscripten, packaged as a conda recipe for emscripten-forge (the WASM
equivalent of conda-forge), and wired into the Pyodide/JupyterLite build.

Matthias maintains three repos for this work:
- `passagemath/upstream-cysignals` — fork adding WASM support to the Cython signal layer
- `passagemath/downstream-emscripten-forge-recipes` — WASM package recipes
- `passagemath/downstream-pyodide-recipes` — Pyodide package recipes

The tracking issue is: https://github.com/passagemath/passagemath/issues/1863

---

## The hard problem: cysignals

SageMath relies on C-level signal handling (SIGINT) to interrupt long computations.
Ctrl-C during a 10-minute integral computation should stop it cleanly, not kill the
process.

WASM has no OS signals. The sandboxed stack machine model doesn't support them.

Matthias's fork of cysignals has a `passagemath` branch that disables `sigaltstack`
and removes thread-based signal handling for the Emscripten target. The recent commit
history:

```
src/cysignals/implementation.c [EMSCRIPTEN]: Do not use sigaltstack
meson.build: Do not use threads on emscripten
```

What this means: in the WASM build, long computations are not safely interruptible.
The question of how to implement cooperative interrupts in a sandboxed stack machine
with no OS signals is genuinely open. There's prior art in how Emscripten handles
asyncify and in how browsers implement Web Workers, but nothing clean exists for
Cython-level signal handlers.

There's also an open ABI incompatibility issue (#2):
`cysignals HEAD ABI incompatible with released cysignals <= 1.12.5` — the WASM
branch diverged and downstream packages built against the old ABI break.

---

## The tractable problem: package recipes

Most of the 60+ packages on the checklist are "just" cross-compilation work:
write an emscripten-forge recipe (a conda-build recipe targeting wasm32), get
the C library to compile under Emscripten, handle any POSIX/signal/filesystem
assumptions that break under WASM.

Some have upstream WASM work already:
- **PARI**: upstream has a WASM demo at https://pari.math.u-bordeaux.fr/gpexpwasm.html
  — patches exist, need packaging
- **FLINT / python-flint**: CI workflow exists, PRs in flight
- **GAP**: prototype at https://wangyenshu.github.io/gap-wasm/

Many have no work done at all and are just waiting for someone to pick them up.

---

## Why it's interesting (systems angle)

- The Emscripten compilation pipeline (C/Cython → LLVM → wasm32) is non-trivial.
  Each library has POSIX assumptions (filesystem, threads, signals, mmap) that need
  to be audited and patched.
- The cysignals signal problem is genuinely hard: you want preemptible computation
  in a cooperative multitasking environment with no OS support. Asyncify is one
  direction; SharedArrayBuffer + Web Workers is another.
- The ABI stability problem across the cysignals fork is a real systems design
  question — how do you maintain a WASM-diverged fork without breaking downstream
  Cython extensions compiled against the original ABI?
- emscripten-forge is essentially conda-forge for wasm32. Understanding how
  cross-compilation recipes differ from native recipes is its own skill.

---

## Entry points

**Easiest:** pick an unported package from the checklist that has upstream WASM
patches already (PARI, FLINT) and write the emscripten-forge recipe.

**Interesting:** look at the cysignals ABI issue (#2) — understand what diverged
and whether there's a clean path to ABI compatibility between the WASM fork and
the released version.

**Hard:** design a cooperative interrupt mechanism for Cython extensions running
under Emscripten. This is research-level.

---

## Who to talk to

Matthias Köppe — mkoeppe on GitHub. Responds fast. One issue per comment.
Already has a passagemath org where he brings in contributors directly.
