# passagemath exercises

Hands-on notebooks for core passagemath contribution patterns.

## Setup

Each exercise has its own directory and `pyproject.toml`. To set up an exercise:

```bash
cd exercises/<exercise-name>
uv sync
uv run jupyter lab
```

**On a remote server (cloud droplet, VM, etc.):** start Jupyter without a browser, then forward the port from your local machine.

On the server:
```bash
cd exercises/<exercise-name>
uv sync
uv run jupyter lab --no-browser --port 8888
```

On your local machine (in a separate terminal):
```bash
ssh -L 8888:localhost:8888 your-user@your-server-ip
```

Then open the URL printed by Jupyter (e.g. `http://127.0.0.1:8888/lab?token=...`) in your local browser. Keep the SSH tunnel terminal open while you work.

## Notebooks

| Notebook | Topic |
|---|---|
| [importerror-fix-pattern](importerror-fix-pattern/) | The `except ImportError: pass` antipattern — why it breaks modular installs and how to fix it with `FeatureNotPresentError` |
| [needs-sage-guards](needs-sage-guards/) | The `# needs sage.X` doctest guard — why missing guards cause `NameError` on the wrong line in CI, and how to add them correctly |
| [ci-failure-discovery](ci-failure-discovery/) | Reading CI logs — why test-mod fails when local passes, how to find `New failures, not in baseline`, and how to trace a NameError back to its cause |
| [rg-codebase-search](rg-codebase-search/) | Searching with rg — the two-question model ("where is X defined?" / "what calls X?") applied to finding a bug class across 47 files |
| [linear-programming-duals](linear-programming-duals/) | Dual values in linear programming — how to retrieve row duals from the backend, verify them as shadow prices, and write honest docs for the current workflow |
| [interactive-simplex](interactive-simplex/) | The simplex method step by step — pivot-by-pivot dictionaries, feasibility checks, and dual shadow prices via `InteractiveLPProblem` |
