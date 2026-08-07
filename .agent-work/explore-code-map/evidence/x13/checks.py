"""x13 self-checks: non-ASCII provenance, entity reconciliation, spot checks."""
import ast
import collections
import json
import pathlib

HERE = pathlib.Path(__file__).parent
MAP = HERE / "map"
ROOT = pathlib.Path(r"C:\Programs\f1Brainz")

supp = json.loads((HERE / "supplement.json").read_text(encoding="utf-8"))
ent = supp["entities"]
mods = supp["modules"]

# ---- (b) non-ASCII scan: every non-ASCII line must be traceable to a docstring
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
for f in sorted(MAP.rglob("*.md")):
    npages += 1
    for i, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
        if any(ord(c) > 127 for c in line):
            nonascii.append((str(f.relative_to(MAP)), i, line))
            probe = " ".join(line.strip().lstrip("- ").split())
            if not any(probe in c or c in probe for c in collapsed):
                unexplained.append((str(f.relative_to(MAP)), i, line[:90]))

print("== (b) non-ASCII ==")
print("pages scanned:", npages)
print("non-ascii lines:", len(nonascii))
print("not traceable to a docstring/source value:", len(unexplained))
for t in unexplained[:15]:
    print("   ", ascii(t))

# ---- (c) entity count reconciliation: statements `contains` vs supplement AST
# Reconcile on SOURCE POSITION, not symbol: the store's symbols are not unique
# (D2 flattens nested names), so a symbol-keyed dict silently loses sites.
cont_at = {}
nstmt = 0
for line in open(HERE / "statements.jsonl", encoding="utf-8"):
    st = json.loads(line)
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
    tree = ast.parse((ROOT / f).read_text(encoding="utf-8"))
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

# ---- (d) spot checks
print()
print("== (d) spot checks ==")
target_file = "scripts/validate_segment_map_662.py"
tmod = "scripts.validate_segment_map_662"
src = (ROOT / target_file).read_text(encoding="utf-8")
tree = ast.parse(src)
top = [n.name for n in tree.body
       if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))]
print(target_file, "top-level defs in source:", top)
d = MAP / tmod
have = sorted(p.stem for p in d.glob("*.md") if p.name != "INDEX.md")
print("pages present:", have)
print("every source def has a page:", all(n in have for n in top))

page = d / "split_half_boundary_drift.md"
print()
print("--- split_half_boundary_drift.md ---")
print(page.read_text(encoding="utf-8"))

# who really calls it, straight from source (independent of the store)
callers = collections.Counter()
manifest = json.loads((HERE / "slice_manifest.json").read_text(encoding="utf-8"))
for rel in manifest["core"]:
    rp = rel.replace("\\", "/")
    try:
        t = ast.parse((ROOT / rp).read_text(encoding="utf-8"))
    except Exception:
        continue
    for n in ast.walk(t):
        if isinstance(n, ast.Name) and n.id == "split_half_boundary_drift":
            callers[rp] += 1
        elif isinstance(n, ast.Attribute) and n.attr == "split_half_boundary_drift":
            callers[rp] += 1
print("independent source scan, files mentioning the name:", dict(callers))
