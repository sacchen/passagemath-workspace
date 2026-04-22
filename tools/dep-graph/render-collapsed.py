"""
Render a collapsed Mermaid dependency diagram for passagemath packages.

Packages with identical required-deps and required-rdeps are collapsed into
a single stacked node. Large groups (> STACK_THRESHOLD) are further split by
name prefix and rendered as summary nodes ("prefix-* (N)"). Packages with no
edges in either direction are omitted.

Usage:
    python3 extract-dep-graph.py | python3 render-collapsed.py
    python3 render-collapsed.py dep-graph.json
"""

import json
import sys
from collections import defaultdict

STACK_THRESHOLD = 6


def short(name):
    return name.removeprefix("passagemath-")


def prefix_key(name):
    s = short(name)
    if s.startswith("gap-pkg-"):
        return "gap-pkg"
    return s.split("-")[0]


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

        if len(pkgs) <= STACK_THRESHOLD:
            if rep not in connected_reps:
                continue
            if len(pkgs) == 1:
                lines.append(f'{nid}["{short(rep)}"]')
            else:
                label = "<br/>".join(short(p) for p in pkgs)
                lines.append(f'{nid}["{label}"]:::group')
        else:
            if rep not in connected_reps:
                continue
            # Split large groups by prefix; each sub-node gets the same edges
            by_prefix = defaultdict(list)
            for p in pkgs:
                by_prefix[prefix_key(p)].append(p)
            for pfx, members in sorted(by_prefix.items()):
                sub_nid = f"{node_id(members[0])}_grp"
                label = f"{pfx}-*<br/>({len(members)})"
                lines.append(f'{sub_nid}["{label}"]:::group')
                # Remap rep → sub_nid for edge emission below
                for p in members:
                    pkg_to_rep[p] = f"__sub__{sub_nid}"

    lines.append("")

    # Re-emit edges using updated pkg_to_rep (sub-nodes)
    edges2 = set()
    for pkg, info in graph.items():
        src_rep = pkg_to_rep[pkg]
        src_nid = src_rep.removeprefix("__sub__") if src_rep.startswith("__sub__") else node_id(src_rep)
        for dep in info["required"]:
            if dep not in pkg_to_rep:
                continue
            dst_rep = pkg_to_rep[dep]
            dst_nid = dst_rep.removeprefix("__sub__") if dst_rep.startswith("__sub__") else node_id(dst_rep)
            if src_nid != dst_nid:
                edges2.add((src_nid, dst_nid))

    # Filter out edges to/from omitted (disconnected singleton) nodes
    defined_nids = set()
    for line in lines:
        if line and line not in ("graph LR", "") and "[" in line:
            defined_nids.add(line.split("[")[0])

    for src_nid, dst_nid in sorted(edges2):
        if src_nid in defined_nids and dst_nid in defined_nids:
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
