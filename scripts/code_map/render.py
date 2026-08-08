"""Full-repo derived map -- one page per entity, agent-lean.

The module list is DERIVED from the extraction, not hardcoded. The entity tree
is driven by the supplement's structurally-correct keys, joined to the store's
symbols on (file, line). The top INDEX groups modules by top-level package so it
stays a routing surface as the module count grows.

Importing this module has no side effects: the prototype loaded both stores at
import time, which made the module unimportable without a built store and
impossible to run twice against different roots. `load_stores()` now owns that.

Defects carried, each owned by a later gate:
  D1 the store's q.line is 0-based and the schema does not say so, so every
     line read out of a statement gets +1. Gate g3.
D2 is FIXED (gate g2): `extract.py` now names every definition as its enclosing
scope's symbol plus its own name, so the store's symbol equals the supplement's
qualified key. Pages are still keyed by the supplement's key and the store symbol
is still reached through the (file, line) join, but that join is now a redundancy
check between two agreeing passes rather than a translation between two spellings
-- `checks.entity_symbol_join` compares the WHOLE symbol because of it.

Output layout:
  map/INDEX.md                       top index, grouped by package
  map/<dotted.module>/INDEX.md       module doc, deps, constants, contents
  map/<dotted.module>/<Entity>.md    one page per class/function/method
  map/ids.jsonl                      id -> symbol-path lookup
"""
import collections
import hashlib
import json
import os
import pathlib
import shutil
import subprocess
import sys

from .extract import STATEMENTS_NAME
from .supplement import SUPPLEMENT_NAME

STDLIB = set(sys.stdlib_module_names)
REPORT_NAME = "render_report.json"

HOLE = "HOLE: no docstring"

# ---------------------------------------------------------------- store state
# Populated by load_stores(); module-level so the page builders below read them
# the way the prototype did, rather than threading one context object through
# every formatter.

ent_supp = {}                                # supplement key -> entity record
mod_supp = {}                                # module name -> module record
docs = {}                                    # store symbol -> doc summary
params = collections.defaultdict(list)       # store symbol -> [(order, name)]
inherits = collections.defaultdict(list)     # store symbol -> [base symbol]
edges = collections.defaultdict(list)        # store symbol -> [(p, o, res, why)]
inbound = collections.defaultdict(collections.Counter)   # symbol -> {caller module: n}
imports_out = collections.defaultdict(list)  # "mod:" -> [(o, res)]
imported_by = collections.defaultdict(set)   # module -> {importing module}
cont_at = {}                                 # (file, line1) -> store symbol
alias = {}                                   # supplement key -> store symbol
alias_missing = 0
children = collections.defaultdict(list)     # parent supp key -> [(line, child key)]
members_of = collections.defaultdict(list)   # module -> [supplement key]
page_file = {}                               # supplement key -> page filename
MODULES = []
BY_PKG = collections.defaultdict(list)

intern = sys.intern


def modof(symbol):
    return symbol.split(":", 1)[0] if ":" in symbol else symbol


def _case_tag(name):
    """A short, stable tag that tells two case-only spellings apart.

    `hashlib`, never the builtin `hash()`: `PYTHONHASHSEED` varies per process,
    so a `hash()`-derived filename would differ between two builds of the same
    source and the determinism check would -- correctly -- go red on it."""
    return hashlib.sha1(name.encode("utf-8")).hexdigest()[:8]


def assign_page_filenames(keys):
    """supplement key -> page filename, for the keys of ONE module.

    A page used to be named after its entity alone, so two entities in one
    module whose names differ only by case resolved to one file: on a
    case-insensitive filesystem the second write destroyed the first, and the
    map advertised a page a reader could not open.

    Names are grouped by their FOLDED spelling, and only a group with more than
    one member is disambiguated -- so the common case keeps the readable
    `<Entity>.md` and nothing else in the tree moves. `~` cannot occur in a
    Python qualified name, so a disambiguated filename can never collide with an
    undisambiguated one.

    Deliberately NOT handled: an entity literally named `INDEX`, which still
    lands on its module's own index page. Reserving that stem would make
    `page_accounting`'s only cross-platform falsifier unable to fail, and a
    check that cannot fail is the thing this gate exists to stamp out. Filed as
    a triage candidate instead."""
    groups = collections.defaultdict(list)
    for key in keys:
        groups[key.split(":", 1)[1].lower()].append(key)
    out = {}
    for group in groups.values():
        for key in group:
            name = key.split(":", 1)[1]
            out[key] = (f"{name}~{_case_tag(name)}.md" if len(group) > 1
                        else f"{name}.md")
    return out


def load_stores(artifacts):
    """Read the statement store and the supplement, and build every index the
    page builders read. Safe to call repeatedly: it resets state first."""
    global alias_missing
    artifacts = pathlib.Path(artifacts)
    for d in (docs, params, inherits, edges, inbound, imports_out, imported_by,
              cont_at, alias, children, members_of, page_file, BY_PKG,
              ent_supp, mod_supp):
        d.clear()
    MODULES.clear()
    alias_missing = 0

    supp = json.loads((artifacts / SUPPLEMENT_NAME).read_text(encoding="utf-8"))
    ent_supp.update(supp["entities"])
    mod_supp.update(supp["modules"])

    with open(artifacts / STATEMENTS_NAME, encoding="utf-8") as f:
        for line in f:
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

    # D2: supplement key -> store symbol, joined on (file, line).
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
    for key, e in ent_supp.items():
        mod, name = key.split(":", 1)
        parent = mod + ":" + name.rsplit(".", 1)[0] if "." in name else mod + ":"
        children[parent].append((e["line"], key))
    for v in children.values():
        v.sort()

    MODULES.extend(sorted(mod_supp))
    for m in MODULES:
        BY_PKG[m.split(".")[0]].append(m)
    for key in ent_supp:
        members_of[modof(key)].append(key)
    for keys in members_of.values():
        page_file.update(assign_page_filenames(keys))


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
    """file, N lines -- a page header carries no source position.

    The line number is deliberately absent. It churned: a 3-line edit near the
    top of a file shifts every entity below it, rewriting hundreds of unrelated
    pages. The file path stays because it is not a position -- it changes only
    when the file moves -- and the entity's own size stays because it changes
    only that entity's own page, which is a page changing when its own subject
    changed. `.code-map/statements.jsonl` already carries per-statement
    {file, line, col} and is gitignored, so the positions remain available to
    anything that needs them; they are simply not committed.

    Supplement lines are 1-based already (D1 applied at load)."""
    head = mod_supp[modof(key)]["file"]
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


#: What the inbound count counted, said on the page itself.
#:
#: A count without a definition is the defect: the page said 5, a reader's grep
#: said 7, and neither number told him which one was answering his question.
#: The wording tracks `load_stores`, which counts `calls` and `reads` and
#: nothing else -- `checks.py` declares this same sentence independently and
#: `RefsAccountingTests` pins it to that predicate test, so widening one
#: without the other goes red.
REFS_LEGEND = ("counted: calls and reads that resolved to this symbol. "
               "not counted: its own definition, imports, inheritance, "
               "attribute writes, docstring mentions, unresolved references.")


def refs_line(key, mod):
    """The page's inbound line, plus the legend that says what it counted.

    The site total and the module total have always included the page's own
    module while the parenthesized list named only the others, so a reader could
    not attribute the difference. The `+ N in this module` clause closes that
    without naming the own module in the list -- the list stays the OTHER
    modules, which is the convention `refs_line_self_consistent` holds every
    page to."""
    callers = inbound.get(alias[key])
    if not callers:
        return ["referenced by: none found", REFS_LEGEND, ""]
    n = sum(callers.values())
    ext = sorted(m for m in callers if m != mod)
    if ext:
        s = f"referenced by: {n} sites in {len(callers)} modules (" + ", ".join(ext) + ")"
        own = callers.get(mod, 0)
        if own:
            s += f" + {own} in this module"
    else:
        s = f"referenced by: {n} sites, this module only"
    return [s, REFS_LEGEND, ""]


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
            L.append(f"- [{kn.split('.')[-1]}]({page_file[k]}) {ke.get('kind', '')}: "
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
        L.append("  " * depth + f"- [{nm}]({page_file[key]}) {e.get('kind', '')}: "
                 + (summary_of(key) or HOLE))
        for _, kid in children.get(key, []):
            walk(kid, depth + 1)

    for _, k in children.get(mod + ":", []):
        walk(k, 0)
    return "\n".join(L).rstrip() + "\n"


def repo_name(root):
    """Name the map after the repository, not the directory it was built in: a
    git worktree's directory is named for the branch, so `<root>.name` would
    title the map after whatever scratch checkout happened to build it."""
    root = pathlib.Path(root).resolve()
    try:
        common = subprocess.run(["git", "rev-parse", "--git-common-dir"],
                                cwd=str(root), check=True,
                                capture_output=True, text=True).stdout.strip()
    except Exception:
        return root.name
    if not common:
        return root.name
    common = pathlib.Path(common)
    if not common.is_absolute():
        common = root / common
    parent = common.resolve().parent
    return parent.name or root.name


def top_index(title):
    L = [f"# {title} map", ""]
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


# ---------------------------------------------------------------- stage

def run(root, artifacts, out):
    """Render the page tree for `root` from `artifacts` into `out`. Returns an
    exit code."""
    load_stores(artifacts)
    out = pathlib.Path(out)
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    sizes = []
    for mod in MODULES:
        d = out / mod
        d.mkdir(exist_ok=True)
        (d / "INDEX.md").write_text(module_index(mod), encoding="utf-8", newline="\n")

        def emit(key):
            page = entity_page(key, mod)
            (d / page_file[key]).write_text(
                page, encoding="utf-8", newline="\n")
            sizes.append((page.count("\n"), key))
            for _, kid in children.get(key, []):
                emit(kid)

        for _, k in children.get(mod + ":", []):
            emit(k)
    (out / "INDEX.md").write_text(top_index(repo_name(root)),
                                  encoding="utf-8", newline="\n")
    # ids.jsonl: id -> symbol path. This repo carries no anchor comments yet, so
    # the file is empty by construction; it establishes the well-known location.
    (out / "ids.jsonl").write_text("", encoding="utf-8", newline="\n")

    # Count the tree, not the writes. A per-write counter reports what the
    # renderer TRIED to do, so two pages resolving to one path -- a name
    # colliding with the module's own INDEX.md, or two names differing only by
    # case on a case-insensitive filesystem -- reads as two pages while one
    # file exists. Counting the files makes the number incapable of disagreeing
    # with the tree it describes. Deduplicating resolved path strings would NOT
    # do: two strings differing only by case are distinct strings and the same
    # file.
    npages = sum(1 for _ in out.rglob("*.md"))

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
    }
    print(json.dumps(report, indent=1))
    artifacts = os.fspath(artifacts)
    os.makedirs(artifacts, exist_ok=True)
    with open(os.path.join(artifacts, REPORT_NAME), "w", encoding="utf-8") as f:
        json.dump(report, f, indent=1)
    return 0
