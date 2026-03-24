# passagemath exercises

Hands-on notebooks for core passagemath contribution patterns.

## Setup

Each exercise has its own directory and `pyproject.toml`. To set up an exercise:

```bash
cd exercises/<exercise-name>
uv sync
uv run python -m ipykernel install --user --name passagemath-<exercise-name> --display-name "passagemath (<exercise-name>)"
uv run jupyter notebook
```

Select the matching kernel when opening the notebook.

## Notebooks

| Notebook | Topic |
|---|---|
| [importerror-fix-pattern](importerror-fix-pattern/) | The `except ImportError: pass` antipattern — why it breaks modular installs and how to fix it with `FeatureNotPresentError` |
| [needs-sage-guards](needs-sage-guards/) | The `# needs sage.X` doctest guard — why missing guards cause `NameError` on the wrong line in CI, and how to add them correctly |
| [ci-failure-discovery](ci-failure-discovery/) | Reading CI logs — why test-mod fails when local passes, how to find `New failures, not in baseline`, and how to trace a NameError back to its cause |
