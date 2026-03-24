---
name: AST checker for unbound-import bugs
description: Context for tools/check_unbound_imports.py — what it does, known limitations, and how it was built
type: project
---

# tools/check_unbound_imports.py

Added in PR #2283 (`fix/unbound-imports-followup-2254`). Identifies the
`except ImportError: pass` pattern that leaves imported names unbound.

## What it handles correctly

- `ast.ClassDef`, `ast.FunctionDef`, `ast.AsyncFunctionDef` in except blocks
  (fallback class/function definitions)
- `ast.Import` / `ast.ImportFrom` in except blocks (fallback import aliases)
- Multiple `try/else` blocks in the same scope importing the same name
  (cross-contamination prevention via `extended_safe` set)
- Exits 1 on findings; suitable for manual triage runs

## Known false-positive categories (require control flow analysis to fix)

| Pattern | Example |
|---|---|
| Local re-import at usage site | `matrix_space.py` line 306: `from . import matrix_integer_dense` immediately before use |
| Algorithm selection guards usage | `generic_graph.py`: `canonical_form` only reachable when `algorithm == 'bliss'`, set only when import succeeded |
| stdlib imports that never fail | `sageinspect.py` (`importlib.machinery`), `forker.py` (`signal`) |
| Module-level fallback before the try | `widgets_sagenb.py`: `Color = None` at line 49, before the try block |

## NOT suitable as blocking CI check without a per-file exclusion list.

## Full triage result (as of 2026-03-16)

All ~45 scanner hits from `src/sage/` classified and posted to:
https://github.com/passagemath/passagemath/issues/2254#issuecomment-4069471772

After PRs #2282 + #2283 merge, no remaining actionable unbound-import bugs
exist in `src/sage/`. All remaining scanner output is false positives from
the categories above.

## How Gemini's errors were caught

Gemini originally wrote `lazy_import('', 'sympy')` for chart_func.py —
empty string module name, would fail at runtime. Replaced with `import sympy`
(sympy is type=standard, no laziness needed). Always verify `lazy_import`
calls: first arg is the module to import FROM, second is the name to bind.
`lazy_import('sympy', 'latex', as_='sympy_latex')` → `from sympy import latex as sympy_latex`.
`lazy_import('', anything)` is always wrong.
