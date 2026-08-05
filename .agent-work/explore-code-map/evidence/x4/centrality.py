"""Symbol-level centrality over the SCIP call graph produced by excursion x1.

Reads (read-only) evidence/x1/{call_edges,defs,module_deps}.jsonl, builds a
directed call graph restricted to f1Brainz's own src/ definitions, runs
PageRank + HITS, and joins the ranking against docstring presence.
"""
import json
import re
import ast
import os
import sys
from pathlib import Path
from collections import defaultdict

import networkx as nx

X1 = Path(r"C:\Programs\constellation-skills\.claude\worktrees\explore-code-map\.agent-work\explore-code-map\evidence\x1")
X4 = Path(r"C:\Programs\constellation-skills\.claude\worktrees\explore-code-map\.agent-work\explore-code-map\evidence\x4")
F1 = Path(r"C:\Programs\f1Brainz")

PKG_PREFIX = "scip-python python f1brainz excursion-x1 "


def parse_symbol(sym):
    """Return (module, qualname, kind) for an f1Brainz src symbol, else None.

    Symbol shape:
      scip-python python f1brainz excursion-x1 `src.pkg.mod`/Class#method().
      scip-python python f1brainz excursion-x1 `src.pkg.mod`/func().
    """
    if not sym.startswith(PKG_PREFIX):
        return None
    rest = sym[len(PKG_PREFIX):]
    m = re.match(r"^`([^`]+)`/(.*)$", rest)
    if not m:
        return None
    module, tail = m.group(1), m.group(2)
    if not module.startswith("src"):
        return None
    if tail in ("__init__:", ""):
        return None
    # strip trailing descriptor chars
    kind = "function" if tail.endswith("().") else ("class" if tail.endswith("#") else "term")
    qual = tail.rstrip(".")
    qual = qual.replace("().", ".").replace("()", "")
    qual = qual.replace("#", ".").strip(".")
    if not qual:
        return None
    return module, qual, kind


def load_defs():
    """symbol -> dict(module, qual, kind, file, has_docstring)"""
    out = {}
    with open(X1 / "defs.jsonl", encoding="utf-8") as fh:
        for line in fh:
            d = json.loads(line)
            p = parse_symbol(d["symbol"])
            if not p:
                continue
            module, qual, kind = p
            f = d.get("file") or ""
            if not f.startswith("src"):
                continue
            out[d["symbol"]] = dict(module=module, qual=qual, kind=d.get("kind") or kind,
                                    file=f.replace("\\", "/"), has_docstring=bool(d.get("has_docstring")))
    return out


def build_graph(defs):
    g = nx.DiGraph()
    for sym, d in defs.items():
        if d["kind"] in ("term",):
            continue
        g.add_node(sym, **d)
    n_edges = 0
    skipped_ext = 0
    with open(X1 / "call_edges.jsonl", encoding="utf-8") as fh:
        for line in fh:
            e = json.loads(line)
            a, b = e["caller"], e["callee"]
            if a in g and b in g:
                w = e.get("count", 1)
                if g.has_edge(a, b):
                    g[a][b]["weight"] += w
                else:
                    g.add_edge(a, b, weight=w)
                n_edges += 1
            else:
                skipped_ext += 1
    return g, n_edges, skipped_ext


def ast_lines():
    """(relpath, qualname) -> lineno, plus docstring flag, by walking f1Brainz src."""
    lines = {}
    for root, dirs, files in os.walk(F1 / "src"):
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        for fn in files:
            if not fn.endswith(".py"):
                continue
            p = Path(root) / fn
            rel = p.relative_to(F1).as_posix()
            try:
                tree = ast.parse(p.read_text(encoding="utf-8", errors="replace"))
            except SyntaxError:
                continue

            def walk(node, prefix):
                for ch in ast.iter_child_nodes(node):
                    if isinstance(ch, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                        q = f"{prefix}{ch.name}"
                        lines[(rel, q)] = (ch.lineno, ast.get_docstring(ch) is not None)
                        walk(ch, q + ".")
            walk(tree, "")
    return lines


def main():
    defs = load_defs()
    g, n_edges, skipped = build_graph(defs)
    print(f"nodes={g.number_of_nodes()} edges={g.number_of_edges()} raw_internal_edges={n_edges} external_or_unknown_edges_skipped={skipped}")

    pr = nx.pagerank(g, alpha=0.85, weight="weight")
    try:
        hubs, auth = nx.hits(g, max_iter=500)
    except Exception as exc:  # pragma: no cover
        print("HITS failed:", exc)
        hubs, auth = {}, {}

    lines = ast_lines()

    rows = []
    for sym, score in pr.items():
        d = g.nodes[sym]
        key = (d["file"], d["qual"])
        ln, ast_doc = lines.get(key, (None, None))
        rows.append(dict(
            symbol=sym, module=d["module"], qual=d["qual"], kind=d["kind"],
            file=d["file"], line=ln,
            has_docstring=d["has_docstring"] if ast_doc is None else ast_doc,
            scip_docstring=d["has_docstring"],
            pagerank=score, authority=auth.get(sym, 0.0), hub=hubs.get(sym, 0.0),
            in_degree=g.in_degree(sym), out_degree=g.out_degree(sym),
            in_weight=sum(g[u][sym]["weight"] for u in g.predecessors(sym)),
        ))
    rows.sort(key=lambda r: -r["pagerank"])
    for i, r in enumerate(rows, 1):
        r["pr_rank"] = i
    by_auth = sorted(rows, key=lambda r: -r["authority"])
    for i, r in enumerate(by_auth, 1):
        r["auth_rank"] = i

    (X4 / "centrality.json").write_text(json.dumps(rows, indent=1), encoding="utf-8")
    print("matched_lines:", sum(1 for r in rows if r["line"] is not None), "/", len(rows))
    print("\nTOP 30 BY PAGERANK")
    for r in rows[:30]:
        print(f"{r['pr_rank']:3d} {r['pagerank']:.5f} auth={r['authority']:.4f} in={r['in_degree']:3d} doc={'Y' if r['has_docstring'] else 'N'} {r['module']}.{r['qual']}")


if __name__ == "__main__":
    main()
