# pm-explore

## What it is

A CLI tool that generates an interactive Jupyter notebook from any passagemath source file.
Given a `.py` or `.pyx` file, it extracts the module description, public classes and functions,
and their doctest examples — then writes a runnable notebook where every example is a pre-populated cell.

**The goal:** make it fast and easy to discover what a file/feature does without reading source,
without searching docs, and without having to figure out the right imports or kernel.

## Current state

- Code lives in `tools/explore.py` + `tools/pyproject.toml`
- Install once: `uv tool install /path/to/passagemath-workspace/tools/ --force --reinstall`
- Run from anywhere, but the most convenient workflow is:
  - `cd ../passagemath/src/sage/combinat/ && pm-explore partition.py`
  - `cd ../passagemath/src/sage/graphs/ && pm-explore graph.py`
- Notebook lands in `~/.local/share/pm-explore/` by default. If a notebook with the same name exists, a numeric suffix is added (e.g. `explore_partition_1.ipynb`) to prevent overwriting your notes.
- Kernel: `passagemath (explore)` — uses `passagemath-standard`. The tool automatically ensures the kernel remains valid even after reinstalling the tool (repair is automatic and safe across concurrent runs).
- Hybrid import model: For `.py` files, the notebook runs your local target file inside the installed Sage runtime. Concretely: it preloads the installed `sage.all` environment (caching all Cython extensions into `sys.modules`), evicts the target module from the cache, then reimports the target from your local `src/` checkout. The target module's `__file__` points to your local checkout; transitive imports (sibling modules, parent packages, Cython extensions) come from the installed package. If local import still fails, it falls back to the installed package entirely and prints a warning. If the installed package import also fails, the notebook raises an explicit error. This logic does not apply to `.pyx` files, which always run the installed extension code.
- `--no-open` skips launching JupyterLab and just prints the notebook path
- `--overwrite` overwrites the existing scratch notebook instead of generating a new one with a numeric suffix
- If a compatible Jupyter server is already running, `pm-explore` reuses it; otherwise it starts a dedicated server
- `--new-lab` forces a fresh JupyterLab server
- Tested on `partition.py`: 170 cells → 90 cells after all filtering

## Design decisions made

**Static analysis only** — the tool parses the file with AST (`.py`) or regex (`.pyx`) without
importing it. This means it works even when the environment is broken or imports fail.

**Local path injection with merged namespace** — for pure Python (`.py`) files, the generated import cell loads `sage.all` from the installed package first (caching all Cython extensions into `sys.modules`), evicts the target module from the cache, then re-imports it from your local `src/` checkout. This is a deliberate hybrid: the target file comes from your local checkout (`__file__` confirmed), but transitive imports — sibling modules, parent packages, Cython extensions — come from the installed environment. It does not guarantee a clean local-only import; it gives you the target module's local code running inside an installed Sage runtime. This tradeoff is acceptable for exploration (where you want things to run), but should not be confused with verifying local import correctness. It does mean startup is meaningfully slower (~3× measured on `partition.py`) because `sage.all` is preloaded. If local import still fails, the cell falls back to the installed package and prints a warning. If both fail, it raises one explicit error. Cython (`.pyx`) files always use the installed extensions.

**Safe naming** — to protect user notes and experiments, `pm-explore` never silently overwrites an existing notebook. It checks for collisions and generates a new unique filename if needed.

**`passagemath-standard`** as the single dependency — covers all 38 packages (pari, singular,
gap, flint, schemes, etc.) so the user never has to think about which package a file needs.

**Internal class filtering** — classes matching `CamelCase_lowercase_suffix` (e.g. `Partitions_n`,
`RegularPartitions_all`) are hidden. These are parametrized factory implementations, not things
a user calls directly. Snake_case functions are always shown. If a module defines `__all__`,
that takes precedence as the authoritative export list for locally defined names. Pure re-export
modules can still end up with no items because `pm-explore` does not import code.

**Each `sage:` statement is its own cell** — rather than grouping all lines in an EXAMPLES:: block
into one big cell. Multi-line statements (with `....:` continuations) stay together. Makes every
cell immediately runnable and scannable.

**Caps per item:**
- 6 statements per top-level class/function
- 3 methods shown per class (public, non-`__init__`)
- 3 statements per method

**Example filtering and deduplication:**
- Comment-only statements dropped (e.g. `# needs sage.libs.gap` as a standalone line)
- `TestSuite(...)` calls dropped (internal test scaffolding)
- Trailing `# needs ...` / `# optional - ...` annotations stripped from code lines —
  these are optional-package guards that `passagemath-standard` makes irrelevant
- Method examples that duplicate class-level examples are dropped
- Duplicate statements within an item are dropped (preserving order)

**`__init__` excluded from methods** — class construction is shown in class-level examples;
`__init__` method sections add noise without new information.

**Table of contents** — a markdown cell after the header lists all user-facing names with their
one-line description. Gives you the shape before scrolling.

**Stable output dir** — notebooks always go to a user-owned directory, `~/.local/share/pm-explore/` by default, instead of any git repo. This keeps `pm-explore` safe to run from inside `passagemath/` while still allowing the convenient `cd ... && pm-explore filename.py` workflow.

**Existing-server reuse** — `pm-explore` checks for running Jupyter servers using its bundled Jupyter executable. If one can already see the generated notebook directory, it opens the notebook there instead of spawning another server. If not, it falls back to starting a dedicated JupyterLab server rooted at the notebook directory.

## Known issues / open design questions

**`uv tool install` update story** — editing `explore.py` requires `--force --reinstall` to pick
up changes (not just `--force`, which hits a cache). Documented in README. During active
development, run directly: `python tools/explore.py src/sage/...`

**`.pyx` parsing is shallow** — the regex approach for Cython files only catches top-level
`class`/`def` with docstrings in a specific format. Method-level examples in `.pyx` files
are not extracted.

**Classes with no class-level examples** — if a class has no EXAMPLES:: block at the top level
(only in methods), the section header appears immediately above the first method subsection,
which looks slightly odd. E.g. `RegularPartitions` in `partition.py`.

**Whitespace-only dedup misses** — deduplication is exact-string. Examples that are semantically
identical but differ in whitespace (e.g. `(2, 2)` vs `(2,2)`) are not caught.

**Method cells can depend on class-level cells** — doctest examples in a class often build on
each other (e.g. `P = Partitions(5)` in the class EXAMPLES:: block, then `P.list()` in a method
block). Since each `sage:` statement becomes its own cell, running a method cell in isolation can
raise `NameError`. There's no indication in the notebook of which cells must be run first. Running
all cells top-to-bottom always works; individual cells may not.

**JupyterLab startup is still best-effort** — if `pm-explore` needs to start a dedicated server, it
still uses `Popen`, so startup failures are not fully surfaced in the terminal. Reuse avoids this in
the common “JupyterLab already running” case, and `--no-open` remains the escape hatch when you want
to manage the notebook yourself.

**Some modules still fail in the bundled environment** — `pm-explore` can now distinguish between
local-checkout import failures and failures in the installed `passagemath-standard` environment, and
it raises one explicit error when both paths fail. That makes the failure mode much clearer, but it
does not solve underlying environment-level import problems for specific modules.

## Audience

Primary: sacchen and research teammates exploring the passagemath source.
All teammates are expected to have `passagemath-workspace` cloned locally (it's the onboarding hub).
Setup instructions live in `tools/README.md`.

## Likely next bets

1. **VSCode integration** — instead of opening JupyterLab in a browser, surface the notebook
   directly in the VSCode Jupyter extension. Would avoid the browser tab and kernel selection step.

2. **Method prioritization** — currently shows the first 3 public methods with examples. Could
   prioritize domain-specific methods over generic ones (e.g. prefer `ferrers_diagram` over `subset`).

3. **`.pyx` method-level extraction** — Cython files currently only get top-level class/function
   docstrings. Full method extraction would require a more robust parser.

4. **Notebook refresh ergonomics** — solved via `--overwrite` flag.
