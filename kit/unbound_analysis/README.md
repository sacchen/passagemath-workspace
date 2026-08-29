# Unbound Variable Analysis (PassageMath Modularization)

This directory contains the scripts and data from an investigation into a recurring modularization bug in the `passagemath` codebase.

## Context
When splitting SageMath into modular packages, many `try...except ImportError: pass` blocks were left intact. If an optional dependency (like `pari` or `sympy`) fails to import, the name is left unbound. In a monolithic install, this was rare. In a modular install without these optional packages, calling code paths that use these unbound variables results in a `NameError` rather than a graceful missing-feature warning (e.g., `FeatureNotPresentError`).

This is the generalized antipattern from Issue `#2243`.

## Contents

### Scripts
*   `find_unbound.py`: An AST parser that scans `passagemath/src/sage/` for `try` blocks that catch `ImportError` but fail to provide a fallback assignment, leaving the imported name unbound, and then verifies that the name is used elsewhere in the file outside of `else` blocks and control-flow terminators.
*   `triage.py` & `triage2.py`: Helper scripts to aggregate, sort, and filter the output of `find_unbound.py`.
*   `check_*.py`: Various scratch scripts used to manually verify the AST output against the actual source files (`matrix_space.py`, `number_field.py`, `assumptions.py`, `chart_func.py`).

### Data
*   `unbound_results.txt`: The raw initial output of the AST parser (contained many false positives due to ignoring control flow).
*   `unbound_results_v2.txt`: The refined output after adding control-flow and `else` block awareness. This represents ~45 files and ~85 variables.

### Tier List Context
*   `tierlist.py`, `tierlist.md`, `issues.json`, `prs.json`: Artifacts from an earlier analysis generating an S.N.T. (Scale, Neglected, Tractable) based tier list of all open PassageMath issues and PRs.

## Current State

PR #2253 (the canonical `#2243` fix) is open. Meta-issue #2254 is filed with the three verified critical cases. The strategic pause is over.

**Next step:** Complete the full triage of `unbound_results_v2.txt` (~45 files, ~85 variables) and update #2254 with the complete prioritized list.

## Known weaknesses in `find_unbound.py`

Before using the script for a CI contribution (vs. internal triage), these should be fixed:

1. **False positives from try-body usages.** The script counts usages of the imported name anywhere in the file, including inside the `try` block itself (after the import line). Those usages are safe — the import succeeded. The fix is to exclude nodes inside `node.body` from the usage scan, mirroring how `node.orelse` is already excluded.

2. **No nested-scope awareness.** A usage of `pari` inside a nested function or class that locally defines `pari` is counted as a hit. True positives only exist at module scope or in functions that close over the module-level name without rebinding it.

3. **`has_terminator` is shallow.** Only checks top-level statements in the except block. An `if condition: raise` is not recognized as a terminator, producing false positives.

4. **Hardcoded path.** `src_dir` is hardcoded to a local filesystem path. Must be parameterized before the script can be contributed upstream or run in CI.

5. **No severity ranking in output.** All hits are printed equally. For triage purposes, sort by usage count descending — high-usage names on default code paths are the critical hits.

The script is **fit for internal triage** in its current form. It is **not yet fit for upstream contribution** as a CI lint tool without addressing at least issues 1, 4, and 5.
