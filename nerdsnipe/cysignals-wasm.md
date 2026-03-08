# Ctrl-C in a machine with no signals

You've run Python on your own hardware. You know what happens when you press
Ctrl-C mid-computation — SIGINT fires, the signal handler runs on a separate
stack, a Python exception gets injected into whatever's executing. Clean.

Now remove the OS. Remove signals entirely. That's WebAssembly.

---

## The problem

SageMath is a math research platform that runs long computations — integrating
complex functions, computing Gröbner bases, factoring polynomials. Minutes or
hours. Ctrl-C has to work. Not "kill the process" — cleanly interrupt, return
to the shell, keep the session alive.

The library that makes this work is **cysignals** — C/Cython, installs POSIX
signal handlers, catches SIGINT, uses `sigaltstack` for safe delivery on a
separate stack, raises a clean Python exception mid-computation across C
extensions and Cython code. Solid.

passagemath is being ported to run entirely in the browser via WebAssembly.
No server. Math in a browser tab.

The current solution in the WASM branch:

```c
// [EMSCRIPTEN]: Do not use sigaltstack
// meson.build: Do not use threads on emscripten
```

Ctrl-C does nothing. You just wait.

---

## Why it's actually hard

WASM is cooperative. Execution runs to completion unless you yield. The
browser event loop cannot interrupt a running WASM computation. There is no
signal delivery, no async exception injection, no safe point mechanism. The
spec deliberately excludes these primitives.

The options, none of them clean:

**Asyncify** — Emscripten transforms the WASM bytecode to allow suspension
and resumption at any point. Yields back to the browser event loop. Cost:
significant binary bloat, performance hit, has to be applied to the entire
call stack. Cython-generated code interacts with this badly.

**SharedArrayBuffer + Web Workers** — run computation in a Worker, use a
SharedArrayBuffer as a stop flag. Main thread sets it, Worker checks it at...
where? You need explicit check points in C/Cython code. Cooperative interrupts,
which means modifying cysignals' signal check sites throughout.

**CPython's eval breaker** — CPython checks an "eval breaker" flag between
bytecodes. Hookable for pure Python. Useless for long-running C extensions
that never call back into Python. Which is most of the interesting math code.

**Give up** — what the branch currently does.

---

## The interesting version of this problem

WASM's execution model is clean and well-specified. That's precisely what
makes this hard — there's no undefined behavior to exploit, no OS side channel
to reach through. You work with the primitives the spec gives you or you don't.

Someone who designed an instruction set from scratch has had to think about
what primitives you actually need for safe interruption. WASM made a deliberate
choice about which ones to include. There might be a cleaner answer than
Asyncify's blunt bytecode transformation — something that works with the
cooperative model instead of fighting it.

There's also an open ABI incompatibility: the WASM branch diverged from
released cysignals ≤ 1.12.5, breaking downstream Cython extensions compiled
against the old ABI. Two separate problems, both open.

---

The project is **passagemath** — maintained by a math professor at UC Davis
(Matthias Köppe). The fork is `passagemath/upstream-cysignals`, branch
`passagemath`. He responds fast, takes contributors seriously, undergrads
have ended up as named authors.

The problem is open. Nobody has solved it cleanly.
