## passagemath: onboarding & technical matrix
**project context**
- **objective:** modularize the sagemath monolith. sever legacy c/c++ dependencies to enable cross-platform execution (specifically windows and webassembly/pyodide).
- **directive:** prioritize lasting structural improvements over throwaway academic exercises.
## issue triage & bug forensics

**1. configure build failures (tier 1)**
- **target:** issue #2163 / pr #2237.
- **cause:** `setuptools >= 82.0.0` dropped `pkg_resources`, fatally breaking `m4/sage_python_package_check.m4` on rolling distros (gentoo, arch). `config.venv` drops pip, stripping external packaging libs.
- **fix:** inject hybrid python snippet using stdlib `importlib.metadata.version()` + `packaging.requirements.Requirement`. resolves the blocker while aligning with the unofficial pypa consensus (#664), intentionally omitting recursive dependency resolution to maintain pip's responsibility boundaries.

**2. windows ci breakage (tier 1)**
- **target:** issue #2239.
- **cause:** invalid uri encoding on windows (`PIP_FIND_LINKS=file://$SAGE_SPKG_WHEELS`). silently broke all windows spkg builds across 96 files.

**3. modular install masking bugs (tier 2)**
- **context:** bugs isolated to the modularization transition. silent `except ImportError: pass` blocks swallow missing c-libraries, triggering `NameError` downstream on default execution paths.
- **bug A (`sage.combinat.partition`):** `Partitions(n).cardinality()` raises `NameError` if `sage.libs.flint` is absent. **footgun:** bug is masked if `.list()` is executed first via `_cardinality_from_list`.
- **bug B (`sage.schemes.elliptic_curves.ell_point`):** `elliptic_logarithm()` raises `NameError` on default algorithm (`'pari'`) over real embeddings if `cypari2` is missing.
- **fix pattern:** assign `None` in the exception block. evaluate at the call site and raise a targeted `FeatureNotPresentError` directing the user to the missing spkg.
## development tracks
**tier 1: build system infrastructure**
- **focus:** highest leverage, highest difficulty. fixing setuptools breakages, m4 macros, and core deployment mechanisms.

**tier 2: jupyter exposition & rendering**
- **focus:** high visibility. migrating combinatorics and 3d rigids from terminal ascii art to inline rendering.
- **action:** implement `_repr_mimebundle_`, `_repr_png_`, or `_repr_svg_` dunder methods on combinatorial objects. bridge outputs to `ipywidgets` or webgl backends (three.js).

**tier 3: legacy refactoring**
- **focus:** steady-state janitorial work.
- **action:** audit standalone packages in `pkgs/` for broken exception semantics (`AttributeError` vs `ValueError`), resolve circular imports, and enforce pep-517 compliance in m4-generated `pyproject.toml` files.
## environment & workflow
**claude desktop bloat reduction (arm64 macos)**
strip the electron runtime to arm64 to minimize disk footprint.
```bash
cd /Applications/Claude.app/Contents/MacOS
sudo cp Claude Claude.backup
sudo lipo -remove x86_64 Claude -output Claude.arm64
sudo mv Claude.arm64 Claude
sudo codesign --force --deep --sign - /Applications/Claude.app
```

_verification:_ `lipo -info /Applications/Claude.app/Contents/MacOS/Claude`.

**sync protocol**
- **research:** draft in obsidian. execute `reap` (alias for `sync.py`) to push stream.
- **agent logic:** edit `AGENTS.md` in the monorepo. commit manually:

```bash
cd ~/foundry/sandbox/passagemath-workspace
git add kit/
git commit -m "feat: improve agent math-check reasoning"
git push
```
