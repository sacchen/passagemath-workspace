#!/usr/bin/env python3
"""
explore.py — generate an explorable Jupyter notebook from a passagemath source file.

Install once:
    uv tool install /path/to/passagemath-workspace/tools/

Then, from anywhere:
    pm-explore ../passagemath/src/sage/combinat/partition.py   # any cwd
    pm-explore partition.py                     # from the file's directory

Generates explore_<stem>.ipynb in a user-owned scratch directory and opens it.
"""
import ast
import argparse
import json
import os
import re
import subprocess
import sys
import uuid
import webbrowser
from pathlib import Path
from urllib.parse import quote

KERNEL_NAME = "passagemath-explore"
KERNEL_DISPLAY = "passagemath (explore)"

# Jupyter and ipykernel live alongside this Python interpreter (uv tool manages it).
_BIN_DIR = Path(sys.executable).parent


# ---------------------------------------------------------------------------
# Output directory
# ---------------------------------------------------------------------------

def default_scratch_dir() -> Path:
    """
    Return a stable user-owned directory for generated notebooks.

    The location is intentionally independent of the target file path and the
    current working directory, so running pm-explore inside a passagemath clone
    never writes into that repo by accident.
    """
    override = os.environ.get("PM_EXPLORE_SCRATCH_DIR")
    if override:
        return Path(override).expanduser()

    xdg_data_home = os.environ.get("XDG_DATA_HOME")
    if xdg_data_home:
        return Path(xdg_data_home).expanduser() / "pm-explore"

    return Path.home() / ".local" / "share" / "pm-explore"


# ---------------------------------------------------------------------------
# Environment setup
# ---------------------------------------------------------------------------

def _is_kernel_stale(kernel_json: Path) -> bool:
    if not kernel_json.exists():
        return True
    try:
        data = json.loads(kernel_json.read_text())
        spec_argv = data.get("argv", [])
        if not spec_argv or spec_argv[0] != sys.executable:
            return True
    except (json.JSONDecodeError, KeyError, IndexError, OSError):
        return True
    return False


def ensure_kernel():
    """Register the Jupyter kernel if not already present or if the path is stale."""
    kernel_dir = Path.home() / ".local" / "share" / "jupyter" / "kernels" / KERNEL_NAME
    kernel_json = kernel_dir / "kernel.json"

    if not _is_kernel_stale(kernel_json):
        return

    print(f"Kernel path is missing or stale (expected {sys.executable}).")
    
    kernel_dir.parent.mkdir(parents=True, exist_ok=True)
    lock_file = kernel_dir.parent / f"{KERNEL_NAME}.lock"

    import fcntl
    with open(lock_file, "w") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        try:
            if not _is_kernel_stale(kernel_json):
                return

            print(f"Registering kernel '{KERNEL_NAME}'...")
            subprocess.run(
                [
                    sys.executable, "-m", "ipykernel", "install",
                    "--user",
                    "--name", KERNEL_NAME,
                    "--display-name", KERNEL_DISPLAY,
                ],
                check=True,
            )
            print("Kernel registered.")
        finally:
            fcntl.flock(f, fcntl.LOCK_UN)


def _jupyter_cmd(*args: str) -> list[str]:
    """Run the bundled Jupyter executable from the tool environment."""
    return [str(_BIN_DIR / "jupyter"), *args]


def running_jupyter_servers() -> list[dict]:
    """
    Return metadata for currently running Jupyter servers.

    If detection fails, return an empty list and let the normal launch path run.
    """
    try:
        proc = subprocess.run(
            _jupyter_cmd("server", "list", "--jsonlist"),
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError:
        return []

    if proc.returncode != 0:
        return []

    text = proc.stdout.strip()
    if not text:
        return []

    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        parsed = []
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                parsed.append(json.loads(line))
            except json.JSONDecodeError:
                continue

    if isinstance(parsed, dict):
        return [parsed]
    if isinstance(parsed, list):
        return [item for item in parsed if isinstance(item, dict)]
    return []


def reusable_lab_url(notebook_path: Path, server: dict) -> str | None:
    """Return a JupyterLab URL if the server can already see notebook_path."""
    url = server.get("url")
    root_dir = server.get("root_dir") or server.get("notebook_dir")
    if not url or not root_dir:
        return None

    try:
        rel_path = notebook_path.resolve().relative_to(Path(root_dir).resolve())
    except ValueError:
        return None

    lab_url = f"{url.rstrip('/')}/lab/tree/{quote(rel_path.as_posix())}"
    token = server.get("token")
    if token and "token=" not in lab_url and "token=" not in url:
        lab_url += f"?token={quote(token)}"
    return lab_url


# ---------------------------------------------------------------------------
# Module name detection
# ---------------------------------------------------------------------------

def module_from_path(file_path: Path) -> tuple[str, Path | None]:
    """
    Derive the Python module name and source root from a file path.

    src/sage/combinat/partition.py  ->  (sage.combinat.partition, /.../src)
    /any/prefix/sage/graphs/graph.py  ->  (sage.graphs.graph, /any/prefix/sage/..)
    """
    parts = file_path.parts
    module_parts = []
    src_root = None

    # Walk back to find 'sage' after 'src', or just 'sage' if no 'src'
    if "src" in parts:
        idx = list(parts).index("src")
        module_parts = parts[idx + 1 :]
        src_root = Path(*parts[: idx + 1])
    elif "sage" in parts:
        idx = list(parts).index("sage")
        module_parts = parts[idx:]
        src_root = Path(*parts[:idx])
    else:
        print(
            f"Warning: could not find 'sage' or 'src' in path {file_path}. "
            f"Module name may be wrong — the import cell may fail."
        )
        module_parts = parts[-2:]  # best guess: parent/file

    stem = ".".join(module_parts)
    for suffix in (".py", ".pyx"):
        stem = stem.removesuffix(suffix)
    return stem, src_root


# ---------------------------------------------------------------------------
# Doctest extraction
# ---------------------------------------------------------------------------

# Section headers in SageMath docstrings, e.g. "EXAMPLES::", "TESTS::", "NOTE::"
_SECTION_RE = re.compile(r"^[A-Z][A-Z\s\-]+::?\s*$")


def extract_example_blocks(docstring: str) -> list[str]:
    """
    Extract EXAMPLES:: blocks from a docstring.

    Returns a list of code strings, one per sage: statement.
    Multi-line statements (sage: + ....: continuations) stay in one string.
    Expected output lines and prose are dropped.
    """
    if not docstring:
        return []

    statements: list[str] = []
    current: list[str] | None = None  # lines of the in-progress statement
    in_examples = False

    for raw_line in docstring.splitlines():
        stripped = raw_line.strip()

        if re.match(r"^EXAMPLES?::?\s*$", stripped):
            in_examples = True
            continue

        if _SECTION_RE.match(stripped) and in_examples:
            # New section — flush and stop collecting
            if current is not None:
                statements.append("\n".join(current))
                current = None
            in_examples = False
            continue

        if not in_examples:
            continue

        if stripped.startswith("sage: "):
            # Each sage: line starts a new statement — flush previous
            if current is not None:
                statements.append("\n".join(current))
            current = [stripped[6:]]
        elif stripped.startswith("....: ") and current is not None:
            # Continuation — append to the last line of the current statement
            current[-1] = current[-1] + "\n" + stripped[6:]
        # else: expected output, blank line, or prose — skip

    if current is not None:
        statements.append("\n".join(current))

    return statements


# ---------------------------------------------------------------------------
# File parsing
# ---------------------------------------------------------------------------

def _is_internal_class(name: str) -> bool:
    """
    Return True for classes that look like internal implementation variants.

    The pattern: a CamelCase base name followed by _lowercase_suffix, e.g.
    Partitions_all, Partitions_n, RegularPartitions_bounded.
    Snake_case functions (number_of_partitions) are never filtered.
    """
    return bool(re.search(r"[A-Z].*_[a-z]", name))


_NEEDS_RE = re.compile(r'\s*#\s*(?:needs|optional\s*-)\s+\S.*')


def _strip_annotations(s: str) -> str:
    """
    Strip trailing '# needs ...' / '# optional - ...' from each line.
    These are optional-package markers in SageMath doctests; passagemath-standard
    covers all of them so they're meaningless noise in the notebook.
    """
    return "\n".join(_NEEDS_RE.sub("", line) for line in s.splitlines())


def _filter_examples(statements: list[str]) -> list[str]:
    """
    Remove statements that are noisy rather than educational:
    - Lines that are only a comment (e.g. "# needs sage.libs.gap")
    - Calls to TestSuite (internal test scaffolding, not useful for exploration)
    Also strips trailing optional-package annotations from each line.
    """
    out = []
    for s in statements:
        s = _strip_annotations(s)
        stripped = s.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if "TestSuite(" in s:
            continue
        out.append(s)
    return out


def _dedup(statements: list[str]) -> list[str]:
    """Remove duplicate statements while preserving order."""
    seen: set[str] = set()
    out = []
    for s in statements:
        if s not in seen:
            seen.add(s)
            out.append(s)
    return out


def _literal_string_list(node: ast.AST) -> list[str] | None:
    """Return a list of strings for a literal list/tuple/set expression."""
    if not isinstance(node, (ast.List, ast.Tuple, ast.Set)):
        return None

    values: list[str] = []
    for elt in node.elts:
        if not isinstance(elt, ast.Constant) or not isinstance(elt.value, str):
            return None
        values.append(elt.value)
    return values


def _module_exports(tree: ast.Module) -> list[str] | None:
    """
    Return statically-declared ``__all__`` exports, if they can be determined.

    Only simple literal assignments are supported; dynamic construction falls
    back to the existing heuristic-based filtering.
    """
    exports: list[str] | None = None

    for node in tree.body:
        if isinstance(node, ast.Assign):
            if not any(isinstance(target, ast.Name) and target.id == "__all__" for target in node.targets):
                continue
            exports = _literal_string_list(node.value)
        elif isinstance(node, ast.AnnAssign):
            if not isinstance(node.target, ast.Name) or node.target.id != "__all__":
                continue
            if node.value is None:
                continue
            exports = _literal_string_list(node.value)
        elif isinstance(node, ast.AugAssign):
            if not isinstance(node.target, ast.Name) or node.target.id != "__all__":
                continue
            if exports is None:
                return None
            extra = _literal_string_list(node.value)
            if extra is None:
                return None
            exports.extend(extra)

    return exports


def parse_python_file(file_path: Path) -> dict | None:
    """Parse a .py file with AST and return structured data."""
    source = file_path.read_text(encoding="utf-8", errors="replace")
    try:
        tree = ast.parse(source)
    except SyntaxError as exc:
        print(f"Warning: could not parse {file_path}: {exc}")
        return None

    module_doc = ast.get_docstring(tree) or ""
    exports = _module_exports(tree)
    export_names = set(exports) if exports is not None else None
    items: list[dict] = []

    for node in ast.iter_child_nodes(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            continue
        if node.name.startswith("_"):
            continue
        if export_names is not None and node.name not in export_names:
            continue
        if export_names is None and isinstance(node, ast.ClassDef) and _is_internal_class(node.name):
            continue

        doc = ast.get_docstring(node) or ""
        first_para = doc.split("\n\n")[0].strip()
        examples = _dedup(_filter_examples(extract_example_blocks(doc)))

        methods: list[dict] = []
        if isinstance(node, ast.ClassDef):
            seen = set(examples)  # skip method examples already shown at class level
            for child in ast.iter_child_nodes(node):
                if not isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    continue
                if child.name.startswith("_"):  # skip __init__ and all private methods
                    continue
                child_doc = ast.get_docstring(child) or ""
                child_examples = [
                    ex for ex in _filter_examples(extract_example_blocks(child_doc))
                    if ex not in seen
                ]
                if not child_examples:
                    continue
                methods.append({
                    "name": child.name,
                    "doc": child_doc.split("\n\n")[0].strip(),
                    "examples": child_examples[:3],
                })

        items.append({
            "name": node.name,
            "type": "class" if isinstance(node, ast.ClassDef) else "function",
            "doc": first_para,
            "examples": examples[:6],
            "methods": methods[:3],
        })

    return {"module_doc": module_doc, "items": items}


def parse_pyx_file(file_path: Path) -> dict:
    """
    Parse a Cython .pyx file with regex (AST doesn't handle Cython syntax).
    Extracts top-level class/function docstrings the same way.
    """
    source = file_path.read_text(encoding="utf-8", errors="replace")

    # Module docstring: first triple-quoted string at file start
    module_doc = ""
    m = re.match(r'\s*r?"""(.*?)"""', source, re.DOTALL)
    if m:
        module_doc = m.group(1).strip()

    items: list[dict] = []
    pattern = re.compile(
        r'^(?:cdef\s+|cpdef\s+)?(?:class|def)\s+(\w+)\s*(?:\([^)]*\))?\s*:\s*\n'
        r'\s+r?"""(.*?)"""',
        re.MULTILINE | re.DOTALL,
    )
    for match in pattern.finditer(source):
        name = match.group(1)
        if name.startswith("_"):
            continue
        doc = match.group(2).strip()
        first_para = doc.split("\n\n")[0].strip()
        examples = extract_example_blocks(doc)
        items.append({
            "name": name,
            "type": "function",
            "doc": first_para,
            "examples": examples[:2],
            "methods": [],
        })

    return {"module_doc": module_doc, "items": items}


# ---------------------------------------------------------------------------
# Notebook generation
# ---------------------------------------------------------------------------

def _cell_id() -> str:
    return str(uuid.uuid4())[:8]


def _md(source: str) -> dict:
    return {"cell_type": "markdown", "id": _cell_id(), "metadata": {}, "source": source}


def _code(source: str) -> dict:
    return {
        "cell_type": "code",
        "id": _cell_id(),
        "metadata": {},
        "source": source,
        "outputs": [],
        "execution_count": None,
    }


def _import_cell(module_name: str, src_root: Path | None) -> str:
    """Build the notebook import cell."""
    if src_root is None:
        return f"from {module_name} import *"

    src_root_str = repr(str(src_root.resolve()))
    module_name_str = repr(module_name)
    root_package_str = repr(module_name.split(".", 1)[0])
    return (
        "import os, sys\n"
        f"_pm_explore_src_root = os.path.abspath({src_root_str})\n"
        f"_pm_explore_module = {module_name_str}\n"
        f"_pm_explore_root_package = {root_package_str}\n"
        "if _pm_explore_root_package == 'sage':\n"
        "    exec('from sage.all import *', globals())\n"
        "    for key in list(sys.modules):\n"
        "        if key == _pm_explore_module or key.startswith(_pm_explore_module + '.'):\n"
        "            del sys.modules[key]\n"
        "_pm_explore_modules_before = {\n"
        "    name: module\n"
        "    for name, module in sys.modules.items()\n"
        "    if name == _pm_explore_root_package or name.startswith(_pm_explore_root_package + '.')\n"
        "}\n"
        "sys.path.insert(0, _pm_explore_src_root)\n"
        "try:\n"
        "    exec(f'from {_pm_explore_module} import *', globals())\n"
        "    print(f'Imported {_pm_explore_module} from local checkout: {_pm_explore_src_root}')\n"
        "except Exception as exc:\n"
        "    if sys.path and sys.path[0] == _pm_explore_src_root:\n"
        "        sys.path.pop(0)\n"
        "    for name in list(sys.modules):\n"
        "        if name != _pm_explore_root_package and not name.startswith(_pm_explore_root_package + '.'):\n"
        "            continue\n"
        "        previous = _pm_explore_modules_before.get(name)\n"
        "        current = sys.modules.get(name)\n"
        "        if previous is None or current is not previous:\n"
        "            sys.modules.pop(name, None)\n"
        "    print(\n"
        "        f'Local checkout import failed for {_pm_explore_module} '\n"
        "        f'({exc.__class__.__name__}: {exc}). Falling back to installed package.'\n"
        "    )\n"
        "    try:\n"
        "        if _pm_explore_root_package == 'sage':\n"
        "            exec('from sage.all import *', globals())\n"
        "        exec(f'from {_pm_explore_module} import *', globals())\n"
        "    except Exception as fallback_exc:\n"
        "        raise RuntimeError(\n"
        "            f'pm-explore could not import {_pm_explore_module} from either the local checkout '\n"
        "            f'or the installed package environment. '\n"
        "            f'Local import error: {exc.__class__.__name__}: {exc}. '\n"
        "            f'Installed import error: {fallback_exc.__class__.__name__}: {fallback_exc}. '\n"
        "            'This usually means the underlying passagemath environment cannot import this module cleanly.'\n"
        "        ) from None\n"
    )


def build_notebook(file_path: Path, module_name: str, src_root: Path | None, parsed: dict) -> dict:
    cells: list[dict] = []

    # Header
    module_doc_short = parsed["module_doc"].split("\n\n")[0].strip()
    header = f"# `{module_name}`"
    if module_doc_short:
        header += f"\n\n{module_doc_short}"
    header += f"\n\n*Generated from `{file_path.name}` by `tools/explore.py`.*"
    cells.append(_md(header))

    # Table of contents
    toc_lines = []
    for item in parsed["items"]:
        desc = f" — {item['doc'].split(chr(10))[0]}" if item["doc"] else ""
        toc_lines.append(f"- `{item['name']}`{desc}")
    if toc_lines:
        cells.append(_md("\n".join(toc_lines)))

    # Import cell — wildcard import so all examples run as-is
    cells.append(_code(_import_cell(module_name, src_root)))

    for item in parsed["items"]:
        kind = "Class" if item["type"] == "class" else "Function"
        section = f"## `{item['name']}` ({kind})"
        if item["doc"]:
            section += f"\n\n{item['doc']}"
        cells.append(_md(section))

        for ex in item["examples"]:
            cells.append(_code(ex))

        for method in item["methods"]:
            if not method["examples"]:
                continue
            method_md = f"### `{item['name']}.{method['name']}`"
            if method["doc"]:
                method_md += f"\n\n{method['doc']}"
            cells.append(_md(method_md))
            for ex in method["examples"]:
                cells.append(_code(ex))

    return {
        "nbformat": 4,
        "nbformat_minor": 5,
        "metadata": {
            "kernelspec": {
                "display_name": KERNEL_DISPLAY,
                "language": "python",
                "name": KERNEL_NAME,
            },
            "language_info": {"name": "python"},
        },
        "cells": cells,
    }


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Generate an explorable Jupyter notebook from a passagemath source "
            "file."
        )
    )
    parser.add_argument("file", help="Path to a passagemath .py or .pyx source file")
    parser.add_argument(
        "--no-open",
        action="store_true",
        help="Generate the notebook but do not launch JupyterLab",
    )
    parser.add_argument(
        "--new-lab",
        action="store_true",
        help="Always start a new JupyterLab server instead of reusing an existing one",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite the existing notebook if it exists, instead of appending a suffix",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    file_path = Path(args.file).resolve()
    if not file_path.exists():
        print(f"File not found: {file_path}")
        sys.exit(1)

    ensure_kernel()

    suffix = file_path.suffix
    if suffix == ".py":
        parsed = parse_python_file(file_path)
    elif suffix == ".pyx":
        parsed = parse_pyx_file(file_path)
    else:
        print(f"Unsupported file type: {suffix!r} (expected .py or .pyx)")
        sys.exit(1)

    if parsed is None:
        sys.exit(1)

    if not parsed["items"]:
        print(f"Warning: no public functions or classes found in {file_path.name}")

    module_name, src_root = module_from_path(file_path)
    if suffix == ".pyx":
        src_root = None  # Do not inject local source path for Cython extensions

    notebook = build_notebook(file_path, module_name, src_root, parsed)

    scratch_dir = default_scratch_dir()
    scratch_dir.mkdir(parents=True, exist_ok=True)

    out_path = scratch_dir / f"explore_{file_path.stem}.ipynb"
    if not args.overwrite:
        counter = 1
        while out_path.exists():
            out_path = scratch_dir / f"explore_{file_path.stem}_{counter}.ipynb"
            counter += 1

    out_path.write_text(json.dumps(notebook, indent=1))
    print(f"Generated: {out_path}")

    if args.no_open:
        print("Skipped opening JupyterLab (--no-open).")
        return

    servers = [] if args.new_lab else running_jupyter_servers()

    for server in servers:
        lab_url = reusable_lab_url(out_path, server)
        if lab_url is None:
            continue
        print("Reusing existing JupyterLab server...")
        print(f"Opening: {lab_url}")
        webbrowser.open(lab_url)
        return

    if servers:
        print(
            "Detected a running Jupyter server, but it cannot see the notebook "
            "directory. Starting a dedicated JupyterLab server instead."
        )

    print("Opening in JupyterLab...")
    subprocess.Popen(
        _jupyter_cmd("lab", f"--ServerApp.root_dir={scratch_dir}", str(out_path))
    )


if __name__ == "__main__":
    main()
