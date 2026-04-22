"""
Render a collapsed Mermaid dependency diagram for passagemath packages.

Packages with identical required-deps and required-rdeps are collapsed into
a single stacked node. Packages with no edges in either direction are omitted.

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

    return {k: sorted(v) for k, v in groups.items()}


def node_id(name):
    return short(name).replace("-", "_").replace(".", "_")


def render(graph):
    classes = equivalence_classes(graph)

    pkg_to_rep = {}
    for pkgs in classes.values():
        rep = pkgs[0]
        for p in pkgs:
            pkg_to_rep[p] = rep

    # Collapsed edges between representatives
    edges = set()
    for pkg, info in graph.items():
        src = pkg_to_rep[pkg]
        for dep in info["required"]:
            if dep in pkg_to_rep:
                dst = pkg_to_rep[dep]
                if src != dst:
                    edges.add((src, dst))

    # Nodes that participate in at least one edge
    connected_reps = set()
    for src, dst in edges:
        connected_reps.add(src)
        connected_reps.add(dst)

    lines = ["graph LR", ""]

    for key, pkgs in sorted(classes.items(), key=lambda x: x[1][0]):
        rep = pkgs[0]
        nid = node_id(rep)

        if rep not in connected_reps:
            continue
        if len(pkgs) == 1:
            lines.append(f'{nid}["{short(rep)}"]')
        else:
            label = "<br/>".join(short(p) for p in pkgs)
            lines.append(f'{nid}["{label}"]:::group')

    lines.append("")

    for src, dst in sorted(edges):
        src_nid = node_id(src)
        dst_nid = node_id(dst)
        lines.append(f"{src_nid} --> {dst_nid}")

    lines.append("")
    lines.append("classDef group fill:#eee,stroke:#999,color:#333")

    return "\n".join(lines)


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else None
    graph = load_graph(path)
    print(render(graph))


if __name__ == "__main__":
    main()
