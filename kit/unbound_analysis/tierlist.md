# PassageMath Issues and PRs Tier List
> Ranked based on Leverage, Scale, Neglectedness, and Tractability.

## S (Highest Impact, High Need/Neglected) Tier (23 items)

- **Issue #546**: passagemath-topcom wheels are much too large *(Updated: 2024-12-12, Labels: None)*
- **Issue #556**: CI Linux: "optional" tests need to install more prereqs *(Updated: 2024-12-13, Labels: None)*
- **Issue #621**: build/pkgs/giac: Remove use of `libusb` on macOS *(Updated: 2024-12-30, Labels: None)*
- **Issue #671**: wheels: gap help not available *(Updated: 2025-01-21, Labels: bug)*
- **Issue #729**: pkgs/*/README.rst: Indicate versions of dependencies shipped in the wheels *(Updated: 2025-05-05, Labels: None)*
- **Issue #731**: Add simple instructions and tests for installing the passagemath wheels on supported OSes. *(Updated: 2025-05-05, Labels: None)*
- **Issue #732**: Submit passagemath-* distributions for pyopensci.org software peer review *(Updated: 2025-05-06, Labels: None)*
- **Issue #807**: CI: Do not fail when "Merge CI Fixes" fails *(Updated: 2025-05-14, Labels: None)*
- **Issue #804**: ci-wheels: Generalize for testing wheels with user-defined constraints *(Updated: 2025-05-16, Labels: None)*
- **Issue #1053**: CI: Warn when IGNORE_MISSING_SYSTEM_PACKAGES=yes but all packages were found *(Updated: 2025-06-20, Labels: None)*
- **Issue #1242**: Windows x86_64 Python on ARM host: Building cysignals fails with architecture mismatch *(Updated: 2025-07-15, Labels: None)*
- **Issue #678**: conda-forge packaging *(Updated: 2025-07-20, Labels: help wanted)*
- **Issue #704**: Update CI workflows in upstream projects using passagemath's reusable workflows *(Updated: 2025-08-26, Labels: None)*
- **Issue #1585**: Upload sdists to PyPI only after all wheel uploads have succeeded *(Updated: 2025-09-19, Labels: None)*
- **Issue #1548**: Cross build for macOS x86_64 wheels after August 2027 *(Updated: 2025-09-24, Labels: None)*
- **Issue #572**: Use stable/limited API for wheel build *(Updated: 2025-09-29, Labels: help wanted)*
- **Issue #1684**: PARI 2.17.2 testsuite hangs nondeterministically (macOS) *(Updated: 2025-10-17, Labels: bug)*
- **Issue #1776**: ci-wheels may need `export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES` *(Updated: 2025-11-06, Labels: None)*
- **Issue #347**: Upstream projects with missing wheels on PyPI *(Updated: 2025-12-03, Labels: help wanted)*
- **Issue #1241**: Fedora packaging *(Updated: 2026-02-08, Labels: help wanted)*
- **Issue #248**: Curation of downstream projects, adding optional dependencies on passagemath distributions *(Updated: 2026-03-01, Labels: help wanted)*
- **Issue #2155**: Guix packaging *(Updated: 2026-03-02, Labels: help wanted)*
- **Issue #2210**: Gentoo packaging *(Updated: 2026-03-02, Labels: help wanted)*


## A (High Impact or Significant Bugs) Tier (18 items)

- **Issue #135**: Submit PRs marked "Upstream candidate" to sagemath/sage *(Updated: 2024-10-22, Labels: help wanted)*
- **Issue #633**: Detect and abbreviate periodic backtraces *(Updated: 2025-04-27, Labels: help wanted)*
- **Issue #21**: Edit top-level README.md and distributions' README *(Updated: 2025-05-06, Labels: help wanted)*
- **Issue #45**: Set up netlify for doc deployment *(Updated: 2025-05-06, Labels: help wanted)*
- **Issue #1058**: Prepare sagecell for working with passagemath *(Updated: 2025-06-28, Labels: help wanted)*
- **Issue #755**: Use [[tool.cibuildwheel.overrides]] for [tool.cibuildwheel] repair-wheel-command *(Updated: 2025-11-25, Labels: None)*
- **Issue #1841**: passagemath-conf: On non-mingw Windows, automatically install MSYS2 *(Updated: 2025-11-30, Labels: None)*
- **Issue #1861**: passagemath-rankwidth Windows ARM wheels fail to build *(Updated: 2025-12-07, Labels: None)*
- **Issue #1044**: Build Windows wheels for more passagemath distributions *(Updated: 2026-01-10, Labels: None)*
- **Issue #2046**: ci-wheels.yml: Add testing of passagemath-polymake *(Updated: 2026-01-27, Labels: None)*
- **Issue #2077**: passagemath-categories Windows wheels ship `msvcp140.dll` *(Updated: 2026-02-02, Labels: None)*
- **Issue #1892**: Windows wheel test errors *(Updated: 2026-02-03, Labels: bug)*
- **Issue #2079**: `# known bug: macos` interacts poorly with `# needs` *(Updated: 2026-03-02, Labels: bug)*
- **Issue #2219**: Bad SAGE_EXTCODE in simplicial_set_examples *(Updated: 2026-03-02, Labels: bug)*
- **Issue #2221**: sage.parallel needs fallback for Windows *(Updated: 2026-03-02, Labels: bug)*
- **Issue #2227**: Doctest errors on Windows because of bitness *(Updated: 2026-03-02, Labels: bug)*
- **Issue #2223**: `tempfile.NamedTemporaryFile(mode='w+t')` fails on Windows *(Updated: 2026-03-03, Labels: bug)*
- **Issue #2222**: Doctests fail on Windows because of `/` vs. `\` or `\\` and `\n` vs. `\r\n` *(Updated: 2026-03-03, Labels: bug)*


## B (Moderate Impact/Maintenance) Tier (67 items)

- **Issue #36**: toctree contains reference to nonexisting document 'sage/rings/polynomial/pbori/pbori' *(Updated: 2024-10-17, Labels: bug)*
- **Issue #111**: manylinux*_i686 sagemath-modules:: Exception while cythonizing ... numpy ... libopenblas.so.0: cannot open shared object file: No such file or directory *(Updated: 2024-12-12, Labels: bug)*
- **Issue #744**: fedora-42-gcc_spkg: ImportError: /lib64/libharfbuzz.so.0: undefined symbol *(Updated: 2025-05-07, Labels: bug)*
- **Issue #776**: conda-forge-standard: autom4te: error: need GNU m4 1.4 or later *(Updated: 2025-05-10, Labels: bug)*
- **Issue #782**: fricas spkg-configure may hang *(Updated: 2025-05-12, Labels: bug)*
- **Issue #1037**: Segfault related to `contourpy` *(Updated: 2025-06-19, Labels: bug)*
- **Issue #1039**: abort for two-sided limit with giac *(Updated: 2025-06-19, Labels: bug)*
- **Issue #1050**: ubuntu-bionic-toolchain-gcc_9: read jobs pipe: Resource temporarily unavailable.  Stop. *(Updated: 2025-06-20, Labels: bug)*
- **Issue #1330**: passagemath-standard: fplll/strategies/default.json not found *(Updated: 2025-07-28, Labels: bug)*
- **Issue #1328**: passagemath-standard: sage.interfaces.giac.Giac.completions tests fail *(Updated: 2025-07-28, Labels: bug)*
- **Issue #1345**: sage.symbolic.constants: Overflow Error *(Updated: 2025-07-28, Labels: bug)*
- **Issue #1479**: pkgs/sagemath-meataxe: Relocation bug *(Updated: 2025-08-23, Labels: bug)*
- **Issue #1570**: sage -info: Say "However, these system packages will not be used for building Sage" less often *(Updated: 2025-09-14, Labels: bug)*
- **Issue #1584**: SPKG installation records broken for filenames including whitespace *(Updated: 2025-09-19, Labels: bug)*
- **Issue #1587**: "Release" job often fails: `jq: parse error` *(Updated: 2025-09-20, Labels: bug)*
- **Issue #1673**: opensuse-tumbleweed-minimal: curl: checking run-time libs availability... failed *(Updated: 2025-10-14, Labels: bug)*
- **Issue #1731**: Race condition while installing numpy *(Updated: 2025-10-27, Labels: bug)*
- **Issue #1762**: Some doctests in python 3.14 *(Updated: 2025-11-06, Labels: bug)*
- **Issue #1002**: Translate Macaulay2 tutorials to Python *(Updated: 2025-12-31, Labels: help wanted)*
- **Issue #2044**: passagemath-gsl Windows ARM wheels: linker errors *(Updated: 2026-02-04, Labels: None)*
- **Issue #2138**: passagemath-highs fails to build wheel on Windows x86_64: highs.lib: fatal error LNK1127: library is corrupt *(Updated: 2026-02-11, Labels: None)*
- **Issue #2190**: Create separate package index for archiving old binary wheels *(Updated: 2026-02-19, Labels: None)*
- **Issue #2195**: Software curation *(Updated: 2026-02-24, Labels: None)*
- **Issue #2214**: Downstream packaging of passagemath in software distributions *(Updated: 2026-03-02, Labels: None)*
- **Issue #1863**: Port to WebAssembly and package in pyodide, emscripten-forge *(Updated: 2026-03-06, Labels: None)*
- **PR #2141**: ci-linux.yml: Move testing to separate jobs *(Updated: 2026-02-15, Labels: None)*
- **PR #1982**: dist.yml: Build passagemath-polymake wheels *(Updated: 2026-02-15, Labels: None)*
- **PR #1931**: Build Windows wheels for passagemath-libbraiding *(Updated: 2026-02-15, Labels: None)*
- **PR #1920**: ci-mingw.yml: Build and test passagemath-singular *(Updated: 2026-02-15, Labels: None)*
- **PR #1919**: ci-mingw.yml: Build and test passagemath-{ecl,maxima} *(Updated: 2026-02-15, Labels: None)*
- **PR #1865**: dist.yml: Build pyodide wheels *(Updated: 2026-02-15, Labels: None)*
- **PR #1755**: .github/workflows/dist.yml (wheels) [macos]: Use https://github.com/matthew-brett/delocate/pull/260 by @HexDecimal *(Updated: 2026-02-15, Labels: None)*
- **PR #1649**: .github/workflows/dist.yml (noarch-wheels): Parallelize build *(Updated: 2026-02-15, Labels: None)*
- **PR #1380**: Build Windows wheels for passagemath-sirocco *(Updated: 2026-02-15, Labels: None)*
- **PR #1366**: dist-wheels-windows.yml: Use new script tools/cibw_repair_wheel_command_windows.sh *(Updated: 2026-02-15, Labels: None)*
- **PR #1338**: .github/workflows/dist-wheels-windows.yml: Build and test passagemath-libecm *(Updated: 2026-02-15, Labels: None)*
- **PR #1218**: Build Windows wheels for passagemath-gap *(Updated: 2026-02-15, Labels: None)*
- **PR #1175**: Build Windows wheels for passagemath-ntl *(Updated: 2026-02-15, Labels: None)*
- **PR #1145**: Build Windows wheels for passagemath-lcalc *(Updated: 2026-02-15, Labels: None)*
- **PR #1142**: Build Windows wheels for passagemath-pari *(Updated: 2026-02-15, Labels: None)*
- **PR #1124**: Build Windows wheels for passagemath-bliss *(Updated: 2026-02-15, Labels: None)*
- **PR #1117**: Build Windows wheels for passagemath-topcom *(Updated: 2026-02-15, Labels: None)*
- **PR #1116**: Build Windows wheels for passagemath-lrslib *(Updated: 2026-02-15, Labels: None)*
- **PR #1114**: Build Windows wheels for passagemath-qepcad *(Updated: 2026-02-15, Labels: None)*
- **PR #1202**: Build Windows wheels for passagemath-flint *(Updated: 2026-02-15, Labels: None)*
- **PR #1146**: Build Windows wheels for passagemath-sympow *(Updated: 2026-02-15, Labels: None)*
- **PR #1115**: Build Windows wheels for passagemath-frobby *(Updated: 2026-02-15, Labels: None)*
- **PR #1113**: Build Windows wheels for passagemath-rubiks *(Updated: 2026-02-15, Labels: None)*
- **PR #1112**: Build Windows wheels for passagemath-benzene *(Updated: 2026-02-15, Labels: None)*
- **PR #1111**: Build Windows wheels for passagemath-buckygen *(Updated: 2026-02-15, Labels: None)*
- **PR #1107**: Build Windows wheels for passagemath-plantri *(Updated: 2026-02-15, Labels: None)*
- **PR #1105**: Build Windows wheels for passagemath-kissat *(Updated: 2026-02-15, Labels: None)*
- **PR #1104**: Build Windows wheels for passagemath-glucose *(Updated: 2026-02-15, Labels: None)*
- **PR #1103**: Build Windows wheels for passagemath-latte-4ti2 *(Updated: 2026-02-15, Labels: None)*
- **PR #1102**: Build Windows wheels for passagemath-msolve *(Updated: 2026-02-15, Labels: None)*
- **PR #1101**: Build Windows wheels for passagemath-tdlib *(Updated: 2026-02-15, Labels: None)*
- **PR #1100**: Build Windows wheels for passagemath-mcqd *(Updated: 2026-02-15, Labels: None)*
- **PR #1099**: Build Windows wheels for passagemath-coxeter3 *(Updated: 2026-02-15, Labels: None)*
- **PR #1098**: Build Windows wheels for passagemath-palp *(Updated: 2026-02-15, Labels: None)*
- **PR #1097**: Build Windows wheels for passagemath-brial *(Updated: 2026-02-15, Labels: None)*
- **PR #1092**: Build Windows wheels for passagemath-tachyon *(Updated: 2026-02-15, Labels: None)*
- **PR #1089**: Build Windows wheels for passagemath-nauty *(Updated: 2026-02-15, Labels: None)*
- **PR #1086**: Build Windows wheels for passagemath-ecl *(Updated: 2026-02-15, Labels: None)*
- **PR #1085**: Create PEP 503 simple repository for wheels *(Updated: 2026-02-15, Labels: None)*
- **PR #842**: .github/workflows/ci-wheels.yml: Add input field for constraints *(Updated: 2026-02-15, Labels: None)*
- **PR #2208**: pkgs/sagemath-symbolics: Remove required dependencies on -flint, -ntl *(Updated: 2026-03-01, Labels: None)*
- **PR #2209**: .github/workflows/ci-mingw.yml: Add passagemath-symbolics *(Updated: 2026-03-01, Labels: None)*


## C (Standard Updates/Bugs) Tier (31 items)

- **Issue #70**: Eliminate configure tarballs *(Updated: 2024-10-19, Labels: None)*
- **Issue #83**: sdist disjoint partition checker *(Updated: 2024-10-19, Labels: None)*
- **Issue #102**: Files not in any distribution yet *(Updated: 2024-10-20, Labels: None)*
- **Issue #155**: passagemath-standard-no-symbolics sdist is much too large *(Updated: 2024-10-23, Labels: None)*
- **Issue #178**: Put plain `upstream_url` without variables in `checksums.ini` *(Updated: 2024-10-25, Labels: None)*
- **Issue #299**: Use roots/discourse-topic-github-release-action *(Updated: 2024-11-05, Labels: None)*
- **Issue #555**: p_group_cohomology build failure *(Updated: 2024-12-13, Labels: None)*
- **Issue #568**: Incremental build failure (egg-info SOURCES.txt) when source files are removed or renamed *(Updated: 2024-12-15, Labels: None)*
- **Issue #619**: Split `src/sage/libs/singular/singular.pyx` by dependency *(Updated: 2024-12-30, Labels: None)*
- **Issue #714**: `sage --notebook=jupyterlab` does not work *(Updated: 2025-05-01, Labels: None)*
- **Issue #764**: ImportError: dlopen... duplicate LC_RPATH *(Updated: 2025-05-09, Labels: None)*
- **Issue #949**: archlinux-standard: ipykernel: ImportError: .../site-packages/zmq/backend/cython/_zmq.....so: undefined symbol: zmq_join *(Updated: 2025-05-30, Labels: None)*
- **Issue #999**: gfan musllinux x86_64/aarch64: error: 'int64' was not declared in this scope *(Updated: 2025-06-10, Labels: None)*
- **Issue #1028**: Import cycle affecting `sage.groups.perm_gps.permgroup` *(Updated: 2025-06-16, Labels: None)*
- **Issue #1041**: Eliminate use of `sage_eval` *(Updated: 2025-06-20, Labels: None)*
- **Issue #1082**: Connections to the Julia language, use Julia packages, OSCAR *(Updated: 2025-06-25, Labels: None)*
- **Issue #1286**: GH Actions disk space exceeded *(Updated: 2025-07-21, Labels: None)*
- **Issue #1000**: Replace pty-based interfaces by library interfaces *(Updated: 2025-07-23, Labels: None)*
- **Issue #1324**: Graver basis functionality *(Updated: 2025-07-26, Labels: None)*
- **Issue #1394**: Ship Jupyter kernels for all interpreters *(Updated: 2025-08-20, Labels: None)*
- **Issue #1549**: `sage-spkg-info`: Indicate top level package that should be installed *(Updated: 2025-09-09, Labels: None)*
- **Issue #1577**: passagemath-gap: AGT test failures *(Updated: 2025-09-21, Labels: None)*
- **Issue #420**: passagemath-ecl: Expose the shipped ecl using common-lisp-jupyter *(Updated: 2025-09-22, Labels: None)*
- **Issue #1603**: Refactor passagemath-conf through passagemath-bootstrap *(Updated: 2025-09-24, Labels: None)*
- **Issue #1604**: Import failures due to import cycles *(Updated: 2025-09-24, Labels: None)*
- **Issue #609**: Use primesieve-python for next_prime, previous_prime *(Updated: 2025-10-13, Labels: None)*
- **Issue #1426**: passagemath-gap: Ship a full set of GAP packages *(Updated: 2025-10-21, Labels: None)*
- **Issue #1106**: Consider forking sagemath-giac *(Updated: 2025-10-29, Labels: None)*
- **Issue #1695**: Consider forking cysignals *(Updated: 2025-11-15, Labels: None)*
- **Issue #1508**: Continued vandalism in the SageMath project *(Updated: 2026-03-05, Labels: help wanted)*
- **PR #1203**: passagemath-flint: Remove dependency on passagemath-ntl *(Updated: 2026-02-15, Labels: help wanted)*


## D (Recent/Lower Priority) Tier (47 items)

- **Issue #1951**: `sage-run`, `sage-preparse`: Add option `--environment` *(Updated: 2026-01-08, Labels: None)*
- **Issue #1821**: build/pkgs/ntl: Should disable `NTL_GF2X_LIB` when on aarch64 *(Updated: 2026-01-13, Labels: None)*
- **Issue #1981**: Download from cpan.metacpan.org unreliable *(Updated: 2026-01-14, Labels: None)*
- **Issue #2006**: What's the relation between modularization and pip-installability? *(Updated: 2026-01-24, Labels: None)*
- **Issue #2011**: fedora-44-minimal: gfortran-14.2.0 FTBFS *(Updated: 2026-01-25, Labels: None)*
- **Issue #2053**: Replace `gsl_complex` in `ComplexDoubleElement` by `std::complex<double>` *(Updated: 2026-01-29, Labels: None)*
- **Issue #2094**: uv workspace *(Updated: 2026-02-03, Labels: None)*
- **Issue #2100**: build/pkgs/python3: Check for bz2 module in spkg-configure.m4 *(Updated: 2026-02-03, Labels: None)*
- **Issue #700**: Announce passagemath-* distributions in upstream forums *(Updated: 2026-02-17, Labels: None)*
- **Issue #2191**: pycvxset *(Updated: 2026-02-20, Labels: None)*
- **Issue #910**: Consider checking in files generated by `bootstrap` *(Updated: 2026-02-22, Labels: None)*
- **Issue #2152**: `<class 'object'> is a built-in class [autodoc]` *(Updated: 2026-03-02, Labels: bug)*
- **Issue #2108**: `weighted_adjacency_matrix(vertices=True)` broken for sparse graph *(Updated: 2026-03-02, Labels: bug)*
- **Issue #2201**: Bug with FLINT exposed by RKkit *(Updated: 2026-03-02, Labels: bug)*
- **Issue #2225**: Doctests fail because toplevel `sage` is referenced without importing *(Updated: 2026-03-02, Labels: bug)*
- **Issue #2236**: Jupyter: Plots only display when using the Sage kernel, not the Python kernel *(Updated: 2026-03-03, Labels: None)*
- **Issue #2244**: Sage formatter for Marimo *(Updated: 2026-03-05, Labels: None)*
- **Issue #2249**: Missing file `shortened_000_111_extended_binary_Golay_code_graph.pickle.xz` *(Updated: 2026-03-06, Labels: bug)*
- **Issue #2243**: Partitions(n).cardinality() raises NameError in modular install without passagemath-flint *(Updated: 2026-03-06, Labels: bug)*
- **Issue #1025**: Connections to Lean / mathlib *(Updated: 2026-03-06, Labels: None)*
- **PR #1954**: build/pkgs/maxima: Update to 5.49.0 *(Updated: 2026-02-15, Labels: None)*
- **PR #1952**: mingw.yml: Use mingw-w64-*-fc on clangarm64 *(Updated: 2026-02-15, Labels: None)*
- **PR #1949**: mingw.yml: Use `--without-system-zlib` *(Updated: 2026-02-15, Labels: None)*
- **PR #1903**: Don't use M_PI from libc.math by @tobiasdiez, backported *(Updated: 2026-02-15, Labels: None)*
- **PR #1901**: `Matrix.{restrict_domain,kernel,image,...}`: Add `side` keywords *(Updated: 2026-02-15, Labels: None)*
- **PR #1897**: Sets.MorphismMethods.restrict_domain: New *(Updated: 2026-02-15, Labels: None)*
- **PR #1813**: src/sage/matrix/matrix_cmr_sparse.pyx: Make documentation of Seymour decomposition parameters visible *(Updated: 2026-02-15, Labels: None)*
- **PR #1810**: CVXPYSDPBackend: New *(Updated: 2026-02-15, Labels: None)*
- **PR #1787**: Python 3.15 *(Updated: 2026-02-15, Labels: None)*
- **PR #1648**: build/pkgs/_sagemath: Make it a pip package for the upstream SageMath library *(Updated: 2026-02-15, Labels: None)*
- **PR #1643**: build/pkgs/mpsolve: Update to 3.2.3 *(Updated: 2026-02-15, Labels: None)*
- **PR #1581**: pkgs/sagemath-repl: Add sage.interacts *(Updated: 2026-02-15, Labels: None)*
- **PR #1429**: build/pkgs/jfricas: New *(Updated: 2026-02-15, Labels: None)*
- **PR #1149**: Replace C99 `double complex` by C++ `std::complex<double>` in src/sage/schemes/elliptic_curves/mod_sym_num.pyx *(Updated: 2026-02-15, Labels: None)*
- **PR #1815**: Added Refined GraverBasis class for advanced examples for integer mat… *(Updated: 2026-02-15, Labels: None)*
- **PR #667**: ⬆️ Bump dev-hanz-ops/install-gh-cli-action from 0.2.0 to 0.2.1 *(Updated: 2026-02-15, Labels: dependencies)*
- **PR #559**: Use https://github.com/passagemath/topcom/ for shared lib build *(Updated: 2026-02-15, Labels: None)*
- **PR #332**: build/pkgs/gfan: Update to 0.7 *(Updated: 2026-02-15, Labels: dependencies)*
- **PR #214**: build(deps): bump conda-incubator/setup-miniconda from 2 to 3 *(Updated: 2026-02-15, Labels: dependencies)*
- **PR #190**: Replace monolithic editable install by modularized editable installs *(Updated: 2026-02-15, Labels: None)*
- **PR #2**: build(deps): bump jakebailey/pyright-action from 1 to 2 *(Updated: 2026-02-15, Labels: dependencies)*
- **PR #2188**: build/pkgs/jupyterlite_sphinx: New *(Updated: 2026-02-21, Labels: None)*
- **PR #2178**: build/pkgs/mpmath: Update to 1.4.0 *(Updated: 2026-02-27, Labels: None)*
- **PR #2212**: Fix tests with giac 2.0.0.19 by @antonio-rojas, backported *(Updated: 2026-03-02, Labels: None)*
- **PR #2238**: gambit: Re-create as a pip package `pygambit` (help wanted!) *(Updated: 2026-03-04, Labels: None)*
- **PR #2250**: build/pkgs/fricas: Update to 1.3.13 *(Updated: 2026-03-06, Labels: None)*
- **PR #1694**: Implement GraverBasis class for integer matrices *(Updated: 2026-03-06, Labels: None)*


