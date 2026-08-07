"""Print-only diagnostics over the built map: non-ASCII provenance, entity
reconciliation, store-only definition sites, and the function-local-import
measurement.

These PRINT. They assert nothing and they never set an exit code, so a broken
map does not fail a run today. Gate g1 rewrites them into real checks; this
port exists only to keep the `check` subcommand wired and the numbers readable
in the meantime.

The prototype's fourth section is DROPPED. It spot-checked one hardcoded file
of another repository (`scripts/validate_segment_map_662.py`) and printed one
named page from it, so there is nothing here for it to look at. What it
demonstrated -- that every top-level def in a source file gets a page -- is a
real check, and it belongs in g1's rewrite as a rule over the whole corpus
rather than as one file's spot check.

Both prototype halves (`checks.py` and `checks2.py`) are folded into this one
module; they read the same two stores and split only because they were written
on different days.
"""
import ast
import collections
import json
import os
import pathlib

from .discovery import discover_corpus
from .extract import STATEMENTS_NAME
from .supplement import SUPPLEMENT_NAME


def _statements(artifacts):
    with open(pathlib.Path(artifacts) / STATEMENTS_NAME, encoding="utf-8") as f:
        for line in f:
            yield json.loads(line)


def non_ascii_provenance(supp, out):
    """(b) every non-ASCII line in the page tree should trace to a docstring or
    a source value the renderer copied through."""
    ent, mods = supp["entities"], supp["modules"]
    docstring_text = set()
    for m, ms in mods.items():
        for fld in ("doc_summary", "doc_body"):
            if ms.get(fld):
                docstring_text.update(ms[fld].split("\n"))
    for k, e in ent.items():
        for fld in ("doc_summary", "doc_body"):
            if e.get(fld):
                docstring_text.update(e[fld].split("\n"))
        for a in (e.get("attrs") or []):
            if a.get("value"):
                docstring_text.add(a["value"])
            if a.get("annotation"):
                docstring_text.add(a["annotation"])
    for m, ms in mods.items():
        for a in (ms.get("attrs") or []):
            if a.get("value"):
                docstring_text.add(a["value"])
            if a.get("annotation"):
                docstring_text.add(a["annotation"])
    # attr/doc text gets whitespace-collapsed or truncated in the renderer
    collapsed = {" ".join(t.split()) for t in docstring_text}

    nonascii = []
    unexplained = []
    npages = 0
    for f in sorted(pathlib.Path(out).rglob("*.md")):
        npages += 1
        for i, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            if any(ord(c) > 127 for c in line):
                nonascii.append((str(f), i, line))
                probe = " ".join(line.strip().lstrip("- ").split())
                if not any(probe in c or c in probe for c in collapsed):
                    unexplained.append((str(f), i, line[:90]))

    print("== (b) non-ASCII ==")
    print("pages scanned:", npages)
    print("non-ascii lines:", len(nonascii))
    print("not traceable to a docstring/source value:", len(unexplained))
    for t in unexplained[:15]:
        print("   ", ascii(t))


def reconciliation(root, supp, artifacts):
    """(c) statements `contains` vs the supplement's AST walk.

    Reconcile on SOURCE POSITION, not symbol: the store's symbols are not
    unique (D2 flattens nested names), so a symbol-keyed dict silently loses
    sites."""
    ent, mods = supp["entities"], supp["modules"]
    root = pathlib.Path(root)
    cont_at = {}
    nstmt = 0
    for st in _statements(artifacts):
        if st["p"] == "contains":
            nstmt += 1
            cont_at[(st["q"]["file"], st["q"]["line"] + 1)] = st["o"]   # D1: +1
    supp_at = {(mods[k.split(":", 1)[0]]["file"], e["line"]): k for k, e in ent.items()}
    print()
    print("== (c) reconciliation ==")
    print("store `contains` statements:", nstmt, "at", len(cont_at), "distinct positions")
    print("distinct store symbols:",
          len({v for v in cont_at.values()}), "(fewer than positions = D2 collisions)")
    print("supplement entities:", len(ent), "at", len(supp_at), "distinct positions")
    print("supplement positions with no store contains:", len(set(supp_at) - set(cont_at)))
    store_only = sorted(set(cont_at) - set(supp_at))
    print("store positions with no supplement entity:", len(store_only))
    parent_kind = collections.Counter()
    for f, ln in store_only:
        try:
            tree = ast.parse((root / f).read_text(encoding="utf-8"))
        except Exception:
            continue
        for n in ast.walk(tree):
            for c in ast.iter_child_nodes(n):
                if isinstance(c, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) \
                        and c.lineno == ln:
                    parent_kind[type(n).__name__] += 1
    print("   their enclosing node:", dict(parent_kind),
          "-- control-flow bodies the supplement's walk skips;",
          "Module/ClassDef ones are same-name redefinitions the supplement dict shadows")
    namediff = [(cont_at[p], supp_at[p]) for p in set(cont_at) & set(supp_at)
                if cont_at[p] != supp_at[p]]
    print("same position, different symbol (D2):", len(namediff))
    for a, b in sorted(namediff)[:5]:
        print("    store:", a, "\n    supp :", b)


def store_only_sites(root, supp, artifacts):
    """What the store sees that the supplement's body-walk does not."""
    ent, mods = supp["entities"], supp["modules"]
    root = pathlib.Path(root)
    spos = {(mods[k.split(":", 1)[0]]["file"], e["line"]) for k, e in ent.items()}
    store_only = []
    for st in _statements(artifacts):
        if st["p"] == "contains":
            p = (st["q"]["file"], st["q"]["line"] + 1)
            if p not in spos:
                store_only.append((p, st["o"]))
    print()
    print("== store-only definition sites (%d) ==" % len(store_only))
    for (f, ln), sym in sorted(store_only)[:6]:
        try:
            src = (root / f).read_text(encoding="utf-8").splitlines()
        except Exception:
            continue
        ctx = "".join(x.strip() + " | " for x in src[max(0, ln - 3):ln])
        print(f"  {f}:{ln}  {sym}\n     ...{ctx[:110]}")


def function_local_imports(root, artifacts, files):
    """Defect D4: names bound by a function-scoped import, and how many
    local-resolved calls/reads are one of them."""
    root = pathlib.Path(root)
    local_imported = collections.defaultdict(set)   # file -> {name}
    nfiles = 0
    for rel in files:
        f = rel.replace("\\", "/")
        try:
            tree = ast.parse((root / f).read_text(encoding="utf-8"))
        except Exception:
            continue
        for fn in ast.walk(tree):
            if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            for n in ast.walk(fn):
                if isinstance(n, (ast.Import, ast.ImportFrom)):
                    for a in n.names:
                        if a.name != "*":
                            local_imported[f].add(a.asname or a.name.split(".")[0])
        if local_imported.get(f):
            nfiles += 1

    lost = collections.Counter()
    total_local = 0
    for st in _statements(artifacts):
        if st.get("res") != "local" or st["p"] not in ("calls", "reads"):
            continue
        total_local += 1
        f = st["q"]["file"]
        name = st["o"].split(":", 1)[1] if ":" in st["o"] else st["o"]
        if name in local_imported.get(f, ()):
            lost[st["p"]] += 1

    print()
    print("== function-local imports (defect D4) ==")
    print("files with at least one function-scoped import:", nfiles, "of", len(files))
    print("distinct names bound by function-scoped imports:",
          sum(len(v) for v in local_imported.values()))
    print("local-resolved calls/reads whose name is one of them:", dict(lost),
          "total", sum(lost.values()))
    if total_local:
        print("as a share of all local calls/reads:",
              round(100.0 * sum(lost.values()) / total_local, 2), "%")


def run(root, artifacts, out):
    """Print every diagnostic. Always returns 0 -- these do not gate anything
    until g1 rewrites them."""
    artifacts = pathlib.Path(artifacts)
    supp = json.loads((artifacts / SUPPLEMENT_NAME).read_text(encoding="utf-8"))
    if os.path.isdir(out):
        non_ascii_provenance(supp, out)
    else:
        print("== (b) non-ASCII ==")
        print("no page tree at", out, "-- run `build` first")
    reconciliation(root, supp, artifacts)
    store_only_sites(root, supp, artifacts)
    function_local_imports(root, artifacts, discover_corpus(root))
    return 0
