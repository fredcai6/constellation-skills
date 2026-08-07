"""x13 follow-ups: the 28 store-only defs, and the function-local-import defect."""
import ast
import collections
import json
import pathlib

HERE = pathlib.Path(__file__).parent
ROOT = pathlib.Path(r"C:\Programs\f1Brainz")

supp = json.loads((HERE / "supplement.json").read_text(encoding="utf-8"))
ent, mods = supp["entities"], supp["modules"]
spos = {(mods[k.split(":", 1)[0]]["file"], e["line"]) for k, e in ent.items()}

# ---- what the store sees that the supplement's body-walk does not
store_only = []
for line in open(HERE / "statements.jsonl", encoding="utf-8"):
    st = json.loads(line)
    if st["p"] == "contains":
        p = (st["q"]["file"], st["q"]["line"] + 1)
        if p not in spos:
            store_only.append((p, st["o"]))
print("== store-only definition sites (%d) ==" % len(store_only))
for (f, ln), sym in sorted(store_only)[:6]:
    src = (ROOT / f).read_text(encoding="utf-8").splitlines()
    ctx = "".join(x.strip() + " | " for x in src[max(0, ln - 3):ln])
    print(f"  {f}:{ln}  {sym}\n     ...{ctx[:110]}")

# ---- function-local imports: names bound inside a function body
local_imported = collections.defaultdict(set)   # file -> {name}
nfiles = 0
manifest = json.loads((HERE / "slice_manifest.json").read_text(encoding="utf-8"))
for rel in manifest["core"]:
    f = rel.replace("\\", "/")
    try:
        tree = ast.parse((ROOT / f).read_text(encoding="utf-8"))
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
for line in open(HERE / "statements.jsonl", encoding="utf-8"):
    st = json.loads(line)
    if st.get("res") != "local" or st["p"] not in ("calls", "reads"):
        continue
    total_local += 1
    f = st["q"]["file"]
    name = st["o"].split(":", 1)[1] if ":" in st["o"] else st["o"]
    if name in local_imported.get(f, ()):
        lost[st["p"]] += 1

print()
print("== function-local imports (defect D4) ==")
print("files with at least one function-scoped import:", nfiles, "of", len(manifest["core"]))
print("distinct names bound by function-scoped imports:",
      sum(len(v) for v in local_imported.values()))
print("local-resolved calls/reads whose name is one of them:", dict(lost),
      "total", sum(lost.values()))
print("as a share of all local calls/reads:",
      round(100.0 * sum(lost.values()) / total_local, 2), "%")
