# Project: Port a C math library to WebAssembly

**For:** A systems programmer comfortable with C build systems (autoconf, cmake, meson),
ideally with cross-compilation or Emscripten experience. You don't need to know the math.

**Effort:** One to several days per library, depending on how many POSIX assumptions
need patching. Some have upstream WASM work already — those are the entry points listed
below.

**Tracking issue:** https://github.com/passagemath/passagemath/issues/1863

---

## What's being built

passagemath is a modular, pip-installable fork of SageMath — a 30-year-old math research
platform. The goal is to run it entirely in the browser via WebAssembly: no server,
math in a browser tab.

A live demo already exists for a subset of the packages made available in emscripten-forge:
http://passagemath.org/passagemath-jupyterlite-demo/

Most of the interesting math (number theory, algebraic geometry, combinatorics) depends
on C libraries — PARI, FLINT, GAP, Singular, NTL, and ~60 more. Each one needs to be
cross-compiled to `wasm32` using Emscripten and packaged as a recipe for
[emscripten-forge](https://github.com/passagemath/downstream-emscripten-forge-recipes)
(conda-forge for WASM).

---

## Good first targets

These have upstream WASM work already — patches or CI exist, reducing the unknown:

| Library | What math it enables | Upstream WASM status |
|---|---|---|
| **PARI** | Number theory, elliptic curves | pyodide PR exists; conda-forge recipe has WASM branch |
| **FLINT / python-flint** | Fast integer/polynomial arithmetic | Emscripten CI workflow in upstream repo |
| **GAP** | Group theory, combinatorics | External prototype at wangyenshu.github.io/gap-wasm (not official upstream) |
| **NTL** | Lattices, cryptography | PR open in upstream emscripten-forge/recipes (#4990) |

The checklist at issue #1863 shows the full picture with links to in-progress work.

---

## What a recipe looks like

An emscripten-forge recipe uses the rattler-build format (`recipe.yaml`), targeting
`wasm32-wasi-emscripten`:

```
recipes/
  libpari/
    recipe.yaml       # name, version, source, build (rattler-build format)
    build.sh          # cross-compile script
    patches/          # any POSIX/signal/filesystem fixes
```

The build script cross-compiles the C library using the Emscripten toolchain.
Common issues to handle:
- `sigaltstack`, `SIGINT`, thread-local storage — not supported in WASM
- `mmap` with `MAP_ANONYMOUS` — emulation required
- Filesystem assumptions — replace with Emscripten's virtual FS where needed

Look at existing recipes for patterns. The [emscripten-forge/recipes](https://github.com/emscripten-forge/recipes) repo
is the target repo; mkoeppe submits his recipes through the passagemath fork at https://github.com/passagemath/downstream-emscripten-forge-recipes (instead of a personal fork) for branding purposes.

---

## Verify

A recipe works when:
1. It builds without errors under the Emscripten toolchain
2. The compiled library passes whatever upstream test suite it has (run via `node` for
   WASM or in a minimal Pyodide environment)
3. The corresponding Python package can `import` and run basic operations in
   JupyterLite

The repo has CI; a passing run against your recipe PR is the verification.

---

## Notes

- You don't need to understand the math the library implements — just the build system.
- The emscripten-forge toolchain handles most of the LLVM/wasm32 pipeline; you're
  writing the recipe and fixing the POSIX gaps.
- Matthias Köppe (mkoeppe) organizes the passagemath WASM effort.
  One issue per comment; responds fast.

## Contact

Open a PR against
[passagemath/downstream-emscripten-forge-recipes](https://github.com/passagemath/downstream-emscripten-forge-recipes)
or comment on issue #1863 to claim a library before starting.
