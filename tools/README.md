# tools

Command-line tools for exploring the passagemath source code.

---

## pm-explore

Generates an interactive Jupyter notebook from any passagemath source file. Each public class and function gets a section with its description and runnable examples pre-populated from its docstring.

**What it does for you:** picks the kernel, uses the bundled passagemath environment, figures out the right imports, and opens JupyterLab — reusing an existing server when possible so you can start running examples immediately with less friction.

### Prerequisites

- [`uv`](https://docs.astral.sh/uv/getting-started/installation/) installed on your machine
- A local clone of `passagemath/`

No separate JupyterLab install needed — it's bundled with the tool.

### Install (once per machine)

```bash
uv tool install /path/to/passagemath-workspace/tools/
```

Replace `/path/to/passagemath-workspace/` with wherever you cloned this repo. For example:

```bash
uv tool install ~/code/passagemath-workspace/tools/
```

This downloads passagemath-standard (all packages) and installs `pm-explore` globally. Takes a few minutes the first time.

### Usage

From `passagemath-workspace/`, the easiest workflow is to navigate into your sibling `passagemath/` clone, then run `pm-explore` with just the filename:

```bash
cd ../passagemath/src/sage/combinat/
pm-explore partition.py

cd ../passagemath/src/sage/graphs/
pm-explore graph.py
```

You can still pass a longer path when convenient:

```bash
pm-explore ../passagemath/src/sage/combinat/partition.py
```

JupyterLab opens with a notebook ready to run. If you already have a compatible JupyterLab server running, `pm-explore` reuses it; otherwise it starts a dedicated server for the generated notebook. The notebook is always saved to a user-owned directory, `~/.local/share/pm-explore/` by default, so using `pm-explore` inside `passagemath/` never writes into the source tree.

If you already have JupyterLab running, or just want to generate the notebook file, use:

```bash
pm-explore --no-open partition.py
```

To customize where notebooks are written, set `PM_EXPLORE_SCRATCH_DIR`.

If you want to force a fresh JupyterLab server even when one is already running, use:

```bash
pm-explore --new-lab partition.py
```

The first time you run `pm-explore`, it registers a Jupyter kernel called `passagemath (explore)`. This takes a moment but only happens once.

### Known limitations

- `.pyx` support is partial: top-level docstrings are extracted, but method-level coverage is still shallow.
- Some generated method cells depend on setup from earlier cells, so running the notebook top-to-bottom works more reliably than running random cells in isolation.
- Pure re-export modules may show little or nothing, because `pm-explore` does not import the target module.

### Updating

If `explore.py` changes (e.g. after a `git pull` in passagemath-workspace), reinstall:

```bash
uv tool install /path/to/passagemath-workspace/tools/ --force --reinstall
```

Both flags are required. `--force` alone hits `uv`'s package cache and won't pick up local source changes; `--reinstall` is what forces a fresh build from disk.
