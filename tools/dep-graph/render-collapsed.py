"""
Render a collapsed Mermaid dependency diagram for passagemath packages.

Packages with identical required-deps and required-rdeps are collapsed into
a single stacked node. Reads JSON from extract-dep-graph.py on stdin or as
the first argument.

Usage:
    python3 extract-dep-graph.py | python3 render-collapsed.py
    python3 render-collapsed.py dep-graph.json
"""

import json
import sys
from collections import defaultdict


def short(name):
    return name.removeprefix("passagemath-")


def load_graph(path=None):
    if path:
        return json.load(open(path))
    return json.load(sys.stdin)


def equivalence_classes(graph):
    rdeps = defaultdict(set)
    for pkg, info in graph.items():
        for dep in info["required"]:
            rdeps[dep].add(pkg)

    groups = defaultdict(list)
    for pkg, info in graph.items():
        key = (frozenset(info["required"]), frozenset(rdeps[pkg]))
        groups[key].append(pkg)

    # Sort members within each group for stable output
    return {k: sorted(v) for k, v in groups.items()}


def render(graph):
    classes = equivalence_classes(graph)

    # Map each package to its group representative (first member)
    pkg_to_rep = {}
    for pkgs in classes.values():
        rep = pkgs[0]
        for p in pkgs:
            pkg_to_rep[p] = rep

    # Collect collapsed edges (between representatives)
    edges = set()
    for pkg, info in graph.items():
        src = pkg_to_rep[pkg]
        for dep in info["required"]:
            if dep in pkg_to_rep:
                dst = pkg_to_rep[dep]
                if src != dst:
                    edges.add((src, dst))

    lines = ["graph LR", ""]

    # Emit node definitions
    for key, pkgs in sorted(classes.items(), key=lambda x: x[1][0]):
        rep = pkgs[0]
        node_id = short(rep).replace("-", "_").replace(".", "_")
        if len(pkgs) == 1:
            label = short(rep)
            lines.append(f'{node_id}["{label}"]')
        else:
            label = "<br/>".join(short(p) for p in pkgs)
            lines.append(f'{node_id}["{label}"]:::group')

    lines.append("")

    # Emit edges
    for src, dst in sorted(edges):
        src_id = short(src).replace("-", "_").replace(".", "_")
        dst_id = short(dst).replace("-", "_").replace(".", "_")
        lines.append(f"{src_id} --> {dst_id}")

    lines.append("")
    lines.append("classDef group fill:#eee,stroke:#999,color:#333")

    return "\n".join(lines)


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else None
    graph = load_graph(path)
    print(render(graph))


if __name__ == "__main__":
    main()
