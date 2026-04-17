# tools

Command-line tools for working with passagemath.

## pm-explore

Generates an interactive Jupyter notebook from any passagemath source file. Given a `.py` or `.pyx` file, it extracts public classes, functions, and doctest examples into runnable cells — no environment setup needed.

See [pm-explore/README.md](pm-explore/README.md) for install and usage instructions.

## dep-graph

Extracts and visualizes the `install_requires` dependency graph across all passagemath distribution packages.

- `extract-dep-graph.py` — reads all `pkgs/*/pyproject.toml` files from a local passagemath clone and outputs the full dependency graph as JSON
- `dep-graph-full-LR.mmd` — Mermaid visualization of 43 packages with required edges, color-coded by layer (foundation, math libs, linear algebra, CAS, domain, specialist tools, apex); generated for [passagemath/passagemath#2360](https://github.com/passagemath/passagemath/issues/2360)
