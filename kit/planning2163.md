# Tomorrow's Brief

## Where we left off

PR #6 is filed and waiting for review:
https://github.com/passagemath/passagemath-pkg-numerical-interactive-mip/pull/6

That's done. Don't touch it.

---

## The next target: Issue #2163

https://github.com/passagemath/passagemath/issues/2163

**The one-line summary**: setuptools 82.0.0 (Feb 8, 2026) removed `pkg_resources`
entirely. Sage's `./configure` script calls `pkg_resources.require()` in an M4 macro
and now crashes on any modern system. This breaks Gentoo, Arch, and anyone on a
rolling-release distro.

**The file to fix**: `m4/sage_python_package_check.m4` line 69.
It's not Python source. It's M4 autoconf. The Python lives inside a `-c` one-liner.

**The replacement is not a one-liner swap.** `importlib.metadata.version()` only
returns a version string. `pkg_resources.require()` also checks version constraints.
You need `packaging.requirements.Requirement` to do it correctly.

**The blocker you have to resolve first**: `packaging` may not be importable in
the cold `config.venv` environment. The venv is created with `--system-site-packages`
but pip is NOT installed into it. `packaging` might only exist inside
`pip._vendor.packaging` (not importable). You cannot ship an unconditional
`from packaging.requirements import Requirement` without solving this.

**Before writing any code, do this**:

```bash
cd ~/foundry/sandbox/passagemath/passagemath
./bootstrap   # generates the SPKG_INSTALL_REQUIRES_* variable values
grep "SPKG_INSTALL_REQUIRES_numpy\|SPKG_INSTALL_REQUIRES_scipy" config.status 2>/dev/null \
  || grep "SPKG_INSTALL_REQUIRES" configure | head -20
```

You need to see what the actual expanded requirement strings look like — are they
`'numpy'` (no version spec) or `'numpy>=1.21.0,<2'` (complex spec)? That determines
whether a stdlib regex fallback is even feasible.

**Gemini's proposed hybrid fix has three bugs**: (1) treats the requirement tuple as
a single string, (2) the fallback silently accepts wrong versions, (3) redundant
exception type. Don't use it verbatim.

**The right architecture** (once you understand the actual spec format):
1. Try `from packaging.requirements import Requirement`
2. If that fails (ImportError), decide: fallback or hard fail
3. Iterate over the full tuple of requirements, not just one
4. Never pass silently without actually checking the version constraint

---

## Rules for tomorrow

- Read the issue comments before writing anything — mkoeppe may have already
  commented with his preferred approach.
- Run `./bootstrap` before claiming to understand the M4 expansion.
- Do not touch issue #2225 (Windows REPL bug, needs Windows environment).
- Do not touch CI workflows (mkoeppe is driving the uv migration himself).
