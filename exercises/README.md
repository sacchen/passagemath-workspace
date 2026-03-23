# passagemath exercises

Hands-on notebooks for core passagemath contribution patterns.

## Setup

```bash
cd exercises
uv sync
uv run python -m ipykernel install --user --name passagemath-exercises --display-name "passagemath (exercises)"
uv run jupyter notebook
```

Select the **passagemath (exercises)** kernel when opening a notebook.

## Notebooks

| Notebook | Topic |
|---|---|
| [importerror-fix-pattern.ipynb](importerror-fix-pattern.ipynb) | The `except ImportError: pass` antipattern — why it breaks modular installs and how to fix it with `FeatureNotPresentError` |
| [needs-sage-guards.ipynb](needs-sage-guards.ipynb) | The `# needs sage.X` doctest guard — why missing guards cause `NameError` on the wrong line in CI, and how to add them correctly |
