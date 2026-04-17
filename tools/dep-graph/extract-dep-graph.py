"""
Extract the install_requires dependency graph from all passagemath pkgs/*/pyproject.toml files.

Usage:
    python3 extract-dep-graph.py

Outputs JSON: { "package-name": { "required": [...], "optional": { "extra": [...] } } }

Notes:
- Package directories are named sagemath-* but the published names are passagemath-*
- passagemath-ppl and passagemath-primesieve-primecount appear as required deps
  but have no pkgs/ directory in this repo (published separately)
- Key: parse [project] section, not the whole file, to avoid false matches
"""

import os
import re
import json
from collections import defaultdict

PKGS_DIR = "/home/dev/sandbox/passagemath/pkgs"


def extract_deps(pkg_dir):
    toml_path = os.path.join(PKGS_DIR, pkg_dir, "pyproject.toml")
    if not os.path.exists(toml_path):
        return None, None

    content = open(toml_path).read()

    name_m = re.search(r'^name\s*=\s*"([^"]+)"', content, re.MULTILINE)
    if not name_m:
        return None, None
    name = name_m.group(1)

    # Extract [project] section only (stops at next section header)
    proj_m = re.search(r'^\[project\](.*?)(?=^\[)', content, re.DOTALL | re.MULTILINE)
    required = []
    if proj_m:
        dep_m = re.search(r'^dependencies\s*=\s*\[(.*?)\]', proj_m.group(1), re.DOTALL | re.MULTILINE)
        if dep_m:
            required = re.findall(r"'(passagemath-[^'\s=<>!;]+)", dep_m.group(1))

    # Extract [project.optional-dependencies] section
    opt_m = re.search(r'^\[project\.optional-dependencies\](.*?)(?=^\[|\Z)', content, re.DOTALL | re.MULTILINE)
    optional = defaultdict(list)
    if opt_m:
        current_extra = None
        for line in opt_m.group(1).split('\n'):
            extra_m = re.match(r'^(\S[\w-]*)\s*=\s*\[', line)
            if extra_m:
                current_extra = extra_m.group(1)
            if current_extra:
                for dep in re.findall(r'"(passagemath-[^"=<>!\s\[]+)', line):
                    optional[current_extra].append(dep)

    return name, {"required": required, "optional": dict(optional)}


def main():
    graph = {}
    for pkg_dir in sorted(os.listdir(PKGS_DIR)):
        name, deps = extract_deps(pkg_dir)
        if name:
            graph[name] = deps
    print(json.dumps(graph, indent=2))


if __name__ == "__main__":
    main()
