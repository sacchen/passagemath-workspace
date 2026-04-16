# tools

Command-line tools for exploring the passagemath source code.

---

## pm-explore

Generates an interactive Jupyter notebook from any passagemath source file. Each public class and function gets a section with its one-line description and runnable examples drawn from its docstring. The notebook opens in JupyterLab, ready to run.

### Prerequisites

- [`uv`](https://docs.astral.sh/uv/getting-started/installation/) installed on your machine
- A local clone of `passagemath/`

No separate JupyterLab install needed — it's bundled with the tool.

### Install

From the root of `passagemath-workspace/`:

```bash
uv tool install tools/
```

This downloads `passagemath-standard` and installs `pm-explore` globally.

### Usage

Navigate into the passagemath source tree and run `pm-explore` with the filename:

```bash
cd ../passagemath/src/sage/combinat/
pm-explore partition.py
```

`pm-explore` generates the notebook, saves it to `~/.local/share/pm-explore/`, and opens it in JupyterLab. If a JupyterLab server is already running and can see the notebook directory, it reuses it; otherwise it starts a dedicated server.

You can also pass a full path from anywhere:

```bash
pm-explore ../passagemath/src/sage/combinat/partition.py
```

**The notebook runs your local `.py` file inside the installed Sage runtime**, so doctest examples have access to common Sage names (`graphs`, `Partitions`, `Graph`) without manual setup. For `.pyx` files, the installed extension code is used directly.

#### Options

| Flag | Effect |
|---|---|
| `--no-open` | Generate the notebook but don't launch JupyterLab |
| `--overwrite` | Overwrite the existing notebook instead of creating a numbered copy |
| `--new-lab` | Force a new JupyterLab server even if one is already running |

To write notebooks somewhere other than `~/.local/share/pm-explore/`, set `PM_EXPLORE_SCRATCH_DIR`.

#### First run

The first time you run `pm-explore`, it registers a Jupyter kernel called `passagemath (explore)`. This happens automatically and only once.

### Known limitations

- `.pyx` support is partial: top-level docstrings are extracted, but method-level coverage is still shallow.
- Method cells may depend on earlier cells (e.g. a variable defined in a class-level example). Running top-to-bottom always works; individual cells may not.
- Pure re-export modules may show little or nothing, because `pm-explore` reads the file statically without importing it.

### Updating

After a `git pull` in `passagemath-workspace/`, reinstall from its root with both flags:

```bash
uv tool install tools/ --force --reinstall
```

`--force` alone hits `uv`'s package cache and won't pick up local edits; `--reinstall` forces a fresh build from disk.
