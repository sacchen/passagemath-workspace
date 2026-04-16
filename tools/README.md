# tools

Command-line tools for working with the passagemath source code.

---

## pm-explore

Generates an interactive Jupyter notebook from any passagemath source file, so you can explore the codebase and try out features without worrying about environments, kernels, or imports. Each public class and function gets a section with its description and runnable examples drawn from its docstring. The notebook opens in JupyterLab ready to run, reusing an existing server if one is already running.

### Prerequisites

- [`uv`](https://docs.astral.sh/uv/getting-started/installation/) installed on your machine
- A local clone of `passagemath/`

No separate JupyterLab install needed — it's bundled with the tool.

### Install

```bash
# from passagemath-workspace/
uv tool install tools/
```

### Usage

Navigate into the passagemath source tree and run `pm-explore` with the filename:

```bash
cd ../passagemath/src/sage/combinat/
pm-explore partition.py
```

Or pass a full path from anywhere:

```bash
pm-explore ../passagemath/src/sage/combinat/partition.py
```

The notebook is saved to `~/.local/share/pm-explore/` and opens in JupyterLab. Your local `.py` file runs inside the installed Sage runtime, so examples have access to common Sage names (`graphs`, `Partitions`, `Graph`) without any extra setup. For `.pyx` files, the installed extension is used directly.

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

After a `git pull` in `passagemath-workspace/`, reinstall from its root:

```bash
# from passagemath-workspace/
uv tool install tools/ --force --reinstall
```

`--force` alone hits `uv`'s package cache and won't pick up local edits; `--reinstall` forces a fresh build from disk.
