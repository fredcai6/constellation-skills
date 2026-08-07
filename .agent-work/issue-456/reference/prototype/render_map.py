"""x13: full-repo derived map -- one page per entity, agent-lean.

Self-contained adaptation of evidence/x11/render_fn.py (which depended on
evidence/x11/render.py for loading). Changes for the full repo:

  - loads evidence/x13/statements.jsonl + evidence/x13/supplement.json
  - module list is DERIVED from the extraction, not hardcoded
  - the entity tree is driven by the supplement's structurally-correct keys,
    joined to the store's symbols on (file, line); see D2 below
  - the top INDEX groups modules by top-level package (src / scripts / tests)
    so it stays a routing surface at ~1,200 modules
  - scripts/ and tests/ ARE indexed now, so the "not indexed" caveats that
    x11's templates carried are gone

Defects carried / found:
  D1 (x11, kept): the store's q.line is 0-based and the schema does not say so,
     so every line read out of a statement gets +1.
  D2 (new here): the store's `contains` symbol truncates the enclosing chain
     for entities nested inside a function -- a class defined in a function is
     named as if module-level, and a function defined in a method is named
     against the class, dropping the method. Pages are therefore keyed by the
     supplement's qualified name, and the store's symbol is looked up through a
     (file, line) join.

Output layout:
  map/INDEX.md                       top index, grouped by package
  map/<dotted.module>/INDEX.md       module doc, deps, constants, contents
  map/<dotted.module>/<Entity>.md    one page per class/function/method
  map/ids.jsonl                      id -> symbol-path lookup (empty: f1Brainz
                                     carries no anchor comments yet)
"""
import collections
import json
import pathlib
import shutil
import sys
import time

HERE = pathlib.Path(__file__).parent
OUT = HERE / "map"
STDLIB = set(sys.stdlib_module_names)

HOLE = "HOLE: no docstring"

# ---------------------------------------------------------------- load stores

t0 = time.time()
supp = json.loads((HERE / "supplement.json").read_text(encoding="utf-8"))
ent_supp = supp["entities"]
mod_supp = supp["modules"]

docs = {}                                    # store symbol -> doc summary
params = collections.defaultdict(list)       # store symbol -> [(order, name)]
inherits = collections.defaultdict(list)     # store symbol -> [base symbol]
edges = collections.defaultdict(list)        # store symbol -> [(p, o, res, why)]
inbound = collections.defaultdict(collections.Counter)   # symbol -> {caller module: n}
imports_out = collections.defaultdict(list)  # "mod:" -> [(o, res)]
imported_by = collections.defaultdict(set)   # module -> {importing module}
cont_at = {}                                 # (file, line1) -> store symbol

intern = sys.intern


def modof(symbol):
    return symbol.split(":", 1)[0] if ":" in symbol else symbol


for line in open(HERE / "statements.jsonl", encoding="utf-8"):
    st = json.loads(line)
    p, s, o = st["p"], st["s"], st["o"]
    if p == "documents":
        docs[s] = o
        continue
    if p == "contains":
        q = st["q"]
        cont_at[(q["file"], q["line"] + 1)] = intern(o)   # D1: +1
        continue
    if p == "param-of":
        q = st["q"]
        params[o].append(((q["line"], q["col"]), s.rsplit(".", 1)[-1]))
        continue
    if p == "inherits":
        inherits[s].append(o)
        continue
    if p == "imports":
        imports_out[s].append((o, st.get("res")))
        if st.get("res") == "internal":
            imported_by[modof(o)].add(modof(s))
        continue
    res = st.get("res")
    if res == "local":
        continue
    edges[intern(s)].append((intern(p), intern(o), intern(res or "?"),
                             intern(st.get("why") or "")))
    if p in ("calls", "reads"):
        inbound[o][intern(modof(s))] += 1

t_load = time.time() - t0

# ------------------------------------------------- D2: supplement key -> store symbol

alias = {}          # supplement key -> store symbol
alias_missing = 0
for key, e in ent_supp.items():
    mod = modof(key)
    f = mod_supp[mod]["file"]
    sym = cont_at.get((f, e["line"]))
    if sym is None:
        alias_missing += 1
        alias[key] = key
    else:
        alias[key] = sym

# children, by supplement key: parent is the qualified name minus its last part
children = collections.defaultdict(list)     # parent supp key -> [(line, child key)]
for key, e in ent_supp.items():
    mod, name = key.split(":", 1)
    parent = mod + ":" + name.rsplit(".", 1)[0] if "." in name else mod + ":"
    children[parent].append((e["line"], key))
for v in children.values():
    v.sort()

MODULES = sorted(mod_supp)
BY_PKG = collections.defaultdict(list)
for m in MODULES:
    BY_PKG[m.split(".")[0]].append(m)
members_of = collections.defaultdict(list)
for key in ent_supp:
    members_of[modof(key)].append(key)

# ---------------------------------------------------------------- formatting


def ext_label(symbol):
    """stdlib vs third-party -- classified renderer-side; the store does not say."""
    top = symbol.split(":", 1)[0].split(".")[0]
    return "stdlib" if top in STDLIB or top == "builtins" else "third-party"


def tally(items):
    c = collections.Counter(items)
    return ", ".join(
        f"{k}" + (f" x{v}" if v > 1 else "")
        for k, v in sorted(c.items(), key=lambda kv: (-kv[1], kv[0]))
    )


def summary_of(key):
    """Store first (that is the map's source of truth); supplement fills gaps."""
    return docs.get(alias[key]) or ent_supp[key].get("doc_summary")


def mod_summary_of(mod):
    return docs.get(mod + ":") or mod_supp[mod].get("doc_summary")


def loc(key, e):
    """file:line, N lines. Supplement lines are 1-based already (D1 applied at load)."""
    head = f"{mod_supp[modof(key)]['file']}:{e['line']}"
    if e.get("end_line"):
        head += f", {e['end_line'] - e['line'] + 1} lines"
    return head


def doc_block(summary, body):
    L = []
    if summary:
        L.append(summary)
        if body:
            L.append("")
            L.extend(body.split("\n"))
    else:
        L.append(HOLE)
    L.append("")
    return L


def attr_lines(attrs):
    """Constants / fields as code-shaped lines: NAME: annotation = value"""
    L = ["```python"]
    for a in attrs:
        if a["name"].startswith("__"):
            continue
        s = a["name"]
        if a.get("annotation"):
            s += f": {a['annotation']}"
        v = a.get("value")
        if v is not None:
            v = " ".join(v.split())
            if len(v) > 90:
                v = v[:87] + "..."
            s += f" = {v}"
        L.append(s)
    L.append("```")
    L.append("")
    return L


def uses_lines(key, mod):
    sym = alias[key]
    buckets = collections.defaultdict(list)
    unresolved = collections.Counter()
    ownparams = {f"{sym}.{pn}" for _, pn in params.get(sym, [])}
    for p, o, res, why in edges.get(sym, []):
        if o in ownparams and p == "reads":
            continue
        if res == "unresolved":
            unresolved[(p, why or "?")] += 1
        elif res == "internal":
            tag = "internal" if modof(o) == mod else "cross-module"
            buckets[(p, tag)].append(
                o.split(":", 1)[1] if tag == "internal" and ":" in o else o)
        elif res == "external":
            lab = o[:-1] + " (module)" if o.endswith(":") else o.replace(":", ".")
            buckets[(p, ext_label(o))].append(lab)
    L = []
    for pred in ("calls", "reads", "writes"):
        for tag in ("internal", "cross-module", "stdlib", "third-party"):
            v = buckets.get((pred, tag))
            if v:
                L.append(f"{pred} {tag}: {tally(v)}")
    if unresolved:
        L.append("unresolved: " + ", ".join(
            f"{n} {p} ({why})" for (p, why), n in sorted(unresolved.items())))
    if L:
        L.append("")
    return L


def refs_line(key, mod):
    callers = inbound.get(alias[key])
    if not callers:
        return ["referenced by: none found", ""]
    n = sum(callers.values())
    ext = sorted(m for m in callers if m != mod)
    if ext:
        s = f"referenced by: {n} sites in {len(callers)} modules (" + ", ".join(ext) + ")"
    else:
        s = f"referenced by: {n} sites, this module only"
    return [s, ""]


def entity_page(key, mod):
    name = key.split(":", 1)[1]
    sym = alias[key]
    e = ent_supp[key]
    kind = e.get("kind", "?")
    L = [f"# {key}", f"{kind}, {loc(key, e)}", ""]

    sig = e.get("signature")
    decos = [d for d in e.get("decorators", [])
             if d not in ("property", "classmethod", "staticmethod")]
    if sig or kind == "class" or decos:
        L.append("```python")
        for d in decos:
            L.append(f"@{d}")
        if sig:
            L.append(f"{'async ' if kind.startswith('async') else ''}"
                     f"def {name.split('.')[-1]}{sig}")
        elif kind == "class":
            bases = ", ".join(b.split(":")[-1] for b in inherits.get(sym, []))
            L.append(f"class {name.split('.')[-1]}({bases})" if bases
                     else f"class {name.split('.')[-1]}")
        L.append("```")
        L.append("")

    L.extend(doc_block(summary_of(key), e.get("doc_body")))

    attrs = [a for a in (e.get("attrs") or []) if not a["name"].startswith("__")]
    if attrs:
        L.extend(attr_lines(attrs))

    kids = children.get(key, [])
    if kids:
        for _, k in kids:
            kn = k.split(":", 1)[1]
            ke = ent_supp[k]
            L.append(f"- [{kn.split('.')[-1]}]({kn}.md) {ke.get('kind', '')}: "
                     + (summary_of(k) or HOLE))
        L.append("")

    L.extend(uses_lines(key, mod))
    L.extend(refs_line(key, mod))
    return "\n".join(L).rstrip() + "\n"


def module_index(mod):
    ms = mod_supp[mod]
    members = members_of.get(mod, [])
    holes = sum(1 for k in members if not summary_of(k))
    L = [f"# {mod}",
         f"{ms['file']}, {ms['loc']} lines" + (f", {holes} holes" if holes else ""), ""]
    L.extend(doc_block(mod_summary_of(mod), ms.get("doc_body")))

    if ms.get("all"):
        L.append("__all__: " + ", ".join(str(x) for x in ms["all"]))
        L.append("")

    imps = imports_out.get(mod + ":", [])
    ext = sorted({o.rstrip(":").replace(":", ".") for o, res in imps if res == "external"})
    inte = sorted({o for o, res in imps if res == "internal"})
    std = [x for x in ext if ext_label(x) == "stdlib"]
    thi = [x for x in ext if ext_label(x) != "stdlib"]
    if std:
        L.append("imports stdlib: " + ", ".join(std))
    if thi:
        L.append("imports third-party: " + ", ".join(thi))
    if inte:
        L.append("imports internal: " + ", ".join(inte))
    importers = sorted(imported_by.get(mod, ()))
    if importers:
        L.append("imported by: " + ", ".join(importers))
    else:
        L.append("imported by: none found")
    L.append("")

    mattrs = [a for a in (ms.get("attrs") or []) if not a["name"].startswith("__")]
    if mattrs:
        L.extend(attr_lines(mattrs))

    def walk(key, depth):
        nm = key.split(":", 1)[1]
        e = ent_supp[key]
        L.append("  " * depth + f"- [{nm}]({nm}.md) {e.get('kind', '')}: "
                 + (summary_of(key) or HOLE))
        for _, kid in children.get(key, []):
            walk(kid, depth + 1)

    for _, k in children.get(mod + ":", []):
        walk(k, 0)
    return "\n".join(L).rstrip() + "\n"


def top_index():
    L = ["# f1Brainz map", ""]
    for pkg in sorted(BY_PKG):
        mods = BY_PKG[pkg]
        nent = sum(len(members_of.get(m, [])) for m in mods)
        L.append(f"## {pkg} ({len(mods)} modules, {nent} entities)")
        L.append("")
        for mod in mods:
            members = members_of.get(mod, [])
            h = sum(1 for k in members if not summary_of(k))
            d = mod_summary_of(mod)
            L.append(f"- [{mod}]({mod}/INDEX.md) ({len(members)} entities"
                     + (f", {h} holes" if h else "") + "): " + (d or HOLE))
        L.append("")
    return "\n".join(L).rstrip() + "\n"


def main():
    t1 = time.time()
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    npages = 0
    sizes = []
    for mod in MODULES:
        d = OUT / mod
        d.mkdir(exist_ok=True)
        (d / "INDEX.md").write_text(module_index(mod), encoding="utf-8", newline="\n")
        npages += 1

        def emit(key):
            nonlocal npages
            page = entity_page(key, mod)
            (d / (key.split(":", 1)[1] + ".md")).write_text(
                page, encoding="utf-8", newline="\n")
            sizes.append((page.count("\n"), key))
            npages += 1
            for _, kid in children.get(key, []):
                emit(kid)

        for _, k in children.get(mod + ":", []):
            emit(k)
    (OUT / "INDEX.md").write_text(top_index(), encoding="utf-8", newline="\n")
    npages += 1
    # ids.jsonl: id -> symbol path. f1Brainz carries no anchor comments yet, so
    # this is empty by construction; the file establishes the well-known location.
    (OUT / "ids.jsonl").write_text("", encoding="utf-8", newline="\n")

    t2 = time.time()
    holes = sum(1 for k in ent_supp if not summary_of(k))
    sizes.sort(reverse=True)
    report = {
        "modules": len(MODULES),
        "entities": len(ent_supp),
        "pages": npages,
        "entity_pages": len(sizes),
        "holes": holes,
        "alias_missing": alias_missing,
        "median_entity_page_lines": sizes[len(sizes) // 2][0] if sizes else 0,
        "largest_5": [[n, k] for n, k in sizes[:5]],
        "load_sec": round(t_load, 1),
        "render_sec": round(t2 - t1, 1),
    }
    print(json.dumps(report, indent=1))
    (HERE / "render_report.json").write_text(json.dumps(report, indent=1),
                                             encoding="utf-8")


if __name__ == "__main__":
    main()
