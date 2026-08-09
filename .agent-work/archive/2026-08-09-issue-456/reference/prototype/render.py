"""Deterministic article renderer: statement store -> markdown pages.

NO prose is written by a model here. Every sentence in an output page is either
(a) a fixed template string, (b) a docstring copied verbatim from the source,
or (c) a symbol/number lifted from a statement.

Provenance markers used in the pages:
  (no marker)  fact came from evidence/x7b/statements.jsonl  (the ruled pipeline)
  [a]          fact came from evidence/x7a/statements.jsonl  (SCIP sidecar)
  [s]          fact had to be fetched from source by evidence/x11/supplement.py
               -- i.e. a measured statement-vocabulary gap
"""
import collections
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).parent
EV = HERE.parent
OUT = HERE / "articles"
OUT.mkdir(parents=True, exist_ok=True)

STDLIB = set(sys.stdlib_module_names)
REPO_URL_BASE = "C:/Programs/f1Brainz/"

MODULES = [
    "src.utils",
    "src.utils.config",
    "src.utils.console",
    "src.utils.constants",
    "src.utils.environment",
    "src.utils.f1_calendar",
    "src.utils.ids",
    "src.utils.simplification_limits",
    "src.utils.utilization",
]

# ---------------------------------------------------------------- load stores

def load(path):
    return [json.loads(l) for l in open(path, encoding="utf-8")]


core = load(EV / "x7b" / "statements.jsonl")
allst = load(EV / "x7b" / "statements_all.jsonl")
x7a = load(EV / "x7a" / "statements.jsonl")
supp = json.loads((HERE / "supplement.json").read_text(encoding="utf-8"))

docs = {}
params = collections.defaultdict(list)
contains = collections.defaultdict(list)
inherits = collections.defaultdict(list)
modwrites = collections.defaultdict(list)   # module-level `writes` = the store's only trace of a constant
written = collections.defaultdict(set)      # subject -> attribute names the store knows about
edges = collections.defaultdict(list)   # (subject) -> statement
qline = {}
for st in core:
    p, s, o = st["p"], st["s"], st["o"]
    q = st.get("q", {})
    if p == "documents":
        docs[s] = o
    elif p == "param-of":
        # declaration order = (line, col); col alone ties on multi-line signatures
        params[o].append(((q.get("line", 0), q.get("col", 0)), s.rsplit(".", 1)[-1]))
    elif p == "contains":
        contains[s].append((q.get("line", 0), o))
        qline[o] = (q.get("file"), q.get("line"))
    elif p == "inherits":
        inherits[s].append(o)
    else:
        if p == "writes" and st.get("res") == "internal":
            written[s].add(o.rsplit(".", 1)[-1].split(":")[-1])
            if s.endswith(":"):
                modwrites[s].append((q.get("line", 0), o.split(":", 1)[1]))
        edges[s].append(st)

# x7a: per-parameter prose, keyed back onto x7b symbol scheme
a_param_doc = {}
a_doc = {}
for st in x7a:
    if st["p"] != "documents":
        continue
    f = st.get("q", {}).get("file", "")
    if not f.startswith("src/utils"):
        continue
    s = st["s"]
    # `src.utils.config`/Config#load_config().(config_file)  ->  parts
    mod = s.split("`")[1] if "`" in s else None
    if mod is None:
        continue
    tail = s.split("/", 1)[1] if "/" in s else ""
    if tail.endswith(")") and "().(" in tail:
        ent, param = tail.split("().(")
        param = param.rstrip(").")
        key = (f"{mod}:{ent.replace('#', '.')}", param)
        a_param_doc[key] = st["o"]
    else:
        ent = tail.rstrip(".").rstrip("()").rstrip("#.")
        a_doc[f"{mod}:{ent.replace('#', '.').rstrip('.')}"] = st["o"]

# inbound edges over the whole 67-file extraction window
inbound = collections.defaultdict(list)
for st in allst:
    if st["p"] in ("calls", "reads", "imports"):
        inbound[st["o"]].append(st)

ent_supp = supp["entities"]
mod_supp = supp["modules"]

GAPLOG = collections.Counter()


def gap(gid, n=1):
    GAPLOG[gid] += n


# ---------------------------------------------------------------- formatting

def modof(symbol):
    return symbol.split(":", 1)[0] if ":" in symbol else symbol


def short(symbol):
    if symbol.startswith("local:"):
        return "`" + symbol[6:] + "`"
    if ":" in symbol:
        m, n = symbol.split(":", 1)
        return f"`{n}`" if n else f"`{m}`"
    return f"`{symbol}`"


def ext_label(symbol):
    """stdlib vs third-party -- classified renderer-side; the store does not say."""
    top = symbol.split(":", 1)[0].split(".")[0]
    return "stdlib" if top in STDLIB or top == "builtins" else "third-party"


def anchor(name):
    return name.lower().replace(".", "").replace("_", "-").replace(" ", "-")


def tally(items):
    c = collections.Counter(items)
    return ", ".join(
        f"{k}" + (f" x{v}" if v > 1 else "") for k, v in sorted(c.items(), key=lambda kv: (-kv[1], kv[0]))
    )


def srclink(file, line):
    """D1: x7b's q.line is 0-based for all 87 entities (verified against ast).
    Nothing in the statement schema declares the base, so the renderer has to
    know it out of band. +1 here so the link lands on the def."""
    line = line + 1
    return f"[`{file}:{line}`]({REPO_URL_BASE}{file}#L{line})"


HOLE = "> **[HOLE] no docstring** — this entity's purpose is not recorded in the source. Nothing in the store can supply it."


def attr_table(attrs, owner, heading):
    """Attributes / constants / dataclass fields.

    The store's ONLY trace of these is a `writes` statement carrying the name --
    no value, no annotation, and for annotation-only declarations (dataclass
    fields) not even that. Everything except the name column is [s].
    """
    if not attrs:
        return []
    known = written.get(owner, set())
    L = [f"**{heading}**", ""]
    L.append("| name | annotation [s] | value [s] | line | in store? |")
    L.append("| --- | --- | --- | --- | --- |")
    for a in attrs:
        if a["name"].startswith("__"):
            continue
        val = a["value"]
        if val is not None:
            val = val.replace("|", "\\|").replace("\n", " ")
            if len(val) > 70:
                val = val[:67] + "..."
            val = f"`{val}`"
        else:
            val = "—"
        gap("G7-value")
        if a["name"] in known:
            instore = "name only"
        else:
            gap("G8-missing-attr")
            instore = "**absent — no statement of any kind**"
        L.append(f"| `{a['name']}` | {'`' + a['annotation'] + '`' if a['annotation'] else '—'} | {val} | {a['line']} | {instore} |")
    L.append("")
    return L


def entity_section(key, level, mod):
    """Render one entity. Returns markdown lines."""
    L = []
    name = key.split(":", 1)[1]
    e = ent_supp.get(key, {})
    kind = e.get("kind", "?")
    gap("G1-kind")
    sig = e.get("signature")
    head = f"{'#' * level} `{name}`"
    L.append(head)
    file, line = qline.get(key, (mod_supp[mod]["file"], e.get("line", 0)))
    span = ""
    if e.get("end_line"):
        span = f" · {e['end_line'] - e.get('line', e['end_line']) + 1} lines [s]"
        gap("G5-span")
    L.append(f"*{kind}* [s] · {srclink(file, line)}{span}")
    L.append("")
    if sig:
        L.append("**Signature** [s]")
        L.append("")
        L.append(f"```python\n{'async ' if kind.startswith('async') else ''}def {name.split('.')[-1]}{sig}\n```")
        gap("G2-signature")
    elif kind == "class":
        bases = inherits.get(key) or []
        basetxt = ", ".join(b.split(":")[-1] for b in bases)
        L.append(f"```python\nclass {name}({basetxt})\n```" if basetxt else f"```python\nclass {name}\n```")
    decos = [d for d in e.get("decorators", []) if d not in ("property", "classmethod", "staticmethod")]
    if decos:
        L.append(f"**Decorators** [s]: " + ", ".join(f"`@{d}`" for d in decos))
        gap("G3-decorators")
    L.append("")

    d = docs.get(key)
    if d:
        L.append("> " + d)
        body = e.get("doc_body")
        if body:
            gap("G4-docbody")
            L.append(">")
            for bl in body.split("\n"):
                L.append("> " + bl if bl.strip() else ">")
            L.append("")
            L.append("*(everything after the first line above is [s] — the store keeps only the summary line.)*")
    else:
        L.append(HOLE)
    L.append("")

    # parameters
    ps = sorted(params.get(key, []))
    if [p for _, p in ps if p not in ("self", "cls")]:
        L.append("**Parameters**")
        L.append("")
        for _, pname in ps:
            if pname in ("self", "cls"):
                continue
            prose = a_param_doc.get((key, pname))
            if prose:
                L.append(f"- `{pname}` — {prose} [a]")
            else:
                L.append(f"- `{pname}` — *[HOLE] undocumented parameter*")
        L.append("")

    # attributes / dataclass fields
    L.extend(attr_table(e.get("attrs") or [], key, "Fields"))

    # members
    kids = sorted(contains.get(key, []))
    if kids:
        L.append("**Members**")
        L.append("")
        for _, k in kids:
            kd = docs.get(k)
            kk = ent_supp.get(k, {}).get("kind", "")
            L.append(f"- [`{k.split(':',1)[1]}`](#{anchor(k.split(':',1)[1])}) — *{kk}* — " + (kd or "**[HOLE] undocumented**"))
        L.append("")

    # edges out
    out = edges.get(key, [])
    buckets = collections.defaultdict(list)
    unresolved = collections.Counter()
    localn = collections.Counter()
    ownparams = {f"{key}.{pn}" for _, pn in params.get(key, [])}
    paramreads = 0
    for st in out:
        res = st.get("res")
        if st["o"] in ownparams and st["p"] == "reads":
            paramreads += 1
            continue
        if res == "unresolved":
            unresolved[(st["p"], st.get("why", "?"))] += 1
            continue
        if res == "local":
            localn[st["p"]] += 1
            continue
        elif res == "internal":
            tag = "internal" if modof(st["o"]) == mod else "cross-module"
            buckets[(st["p"], tag)].append(
                f"`{st['o'].split(':',1)[1] or st['o']}`" if tag == "internal" else f"`{st['o']}`"
            )
        elif res == "external":
            lab = st["o"]
            lab = lab[:-1] + " (module)" if lab.endswith(":") else lab.replace(":", ".")
            buckets[(st["p"], ext_label(st["o"]))].append(f"`{lab}`")
    order = ["calls", "reads", "writes"]
    rows = []
    for pred in order:
        for tag in ["internal", "cross-module", "stdlib", "third-party"]:
            v = buckets.get((pred, tag))
            if v:
                rows.append((pred, tag, v))
    if rows:
        L.append("**Uses**")
        L.append("")
        L.append("| relation | scope | targets |")
        L.append("| --- | --- | --- |")
        for pred, tag, v in rows:
            L.append(f"| {pred} | {tag} | {tally(v)} |")
        L.append("")
    noise = []
    if localn:
        noise.append(", ".join(f"{n} local-variable {p}" for p, n in sorted(localn.items())))
    if paramreads:
        noise.append(f"{paramreads} reads of its own parameters")
    if noise:
        L.append("*Not shown: " + "; ".join(noise) + ".*")
        L.append("")
    if unresolved:
        L.append("**Unresolved by the extractor**: "
                 + ", ".join(f"{n} {p} ({why})" for (p, why), n in sorted(unresolved.items())))
        L.append("")

    # callers in
    inb = [st for st in inbound.get(key, []) if st["p"] in ("calls", "reads")]
    callers = collections.Counter(modof(st["s"]) for st in inb)
    ext_callers = {m: n for m, n in callers.items() if m != mod}
    if inb:
        L.append(f"**Referenced by**: {len(inb)} site(s) across {len(callers)} module(s)"
                 + (" — " + tally([m for m in ext_callers for _ in range(ext_callers[m])]) if ext_callers else " (all within this module)"))
    else:
        L.append("**Referenced by**: no reference recorded inside the extraction window "
                 "(9 `src/utils` files + 58 direct importers under `src/`; `scripts/` and `tests/` were not extracted).")
    L.append("")
    L.append("")
    return L


# ---------------------------------------------------------------- module page

def module_page(mod):
    ms = mod_supp[mod]
    L = []
    L.append(f"# `{mod}`")
    L.append("")
    d = docs.get(mod + ":")
    L.append("> " + d if d else HOLE)
    body = ms.get("doc_body")
    if body:
        gap("G4-docbody")
        L.append(">")
        for bl in body.split("\n"):
            L.append("> " + bl if bl.strip() else ">")
        L.append("")
        L.append("*(everything after the first line above is [s].)*")
    L.append("")
    tops = sorted(contains.get(mod + ":", []))
    members = [k for k in ent_supp if modof(k) == mod]
    documented = sum(1 for k in members if k in docs)
    L.append(f"`{ms['file']}` · {ms['loc']} lines [s] · {len(tops)} top-level, {len(members)} entities total "
             f"· {documented} documented, {len(members) - documented} **holes**")
    gap("G5-span")
    if ms.get("all"):
        gap("G6-dunder")
        L.append("")
        L.append("**Re-exports (`__all__`) [s]**: " + ", ".join(f"`{x}`" for x in ms["all"]))
    L.append("")

    # module dependency edges
    imps = [st for st in core if st["p"] == "imports" and st["s"] == mod + ":"]
    ext = sorted({st["o"].rstrip(":").replace(":", ".") for st in imps if st.get("res") == "external"})
    inte = sorted({st["o"] for st in imps if st.get("res") == "internal"})
    L.append("## Dependencies")
    L.append("")
    if ext:
        std = [x for x in ext if ext_label(x) == "stdlib"]
        thi = [x for x in ext if ext_label(x) != "stdlib"]
        if std:
            L.append(f"**Imports (stdlib)**: " + ", ".join(f"`{x}`" for x in std))
        if thi:
            L.append(f"**Imports (third-party)**: " + ", ".join(f"`{x}`" for x in thi))
    if inte:
        L.append("")
        L.append("**Imports (internal)**: " + ", ".join(f"`{x}`" for x in sorted({modof(x) + ':' + x.split(':',1)[1] for x in inte})))
    # who imports this module
    importers = collections.Counter()
    for st in allst:
        if st["p"] == "imports" and modof(st["o"]) == mod:
            importers[modof(st["s"])] += 1
    for k in ent_supp:
        if modof(k) != mod:
            continue
        for st in inbound.get(k, []):
            if modof(st["s"]) != mod:
                importers[modof(st["s"])] += 0
    L.append("")
    if importers:
        L.append(f"**Imported by** ({len(importers)} modules in the extraction window): "
                 + ", ".join(f"`{m}`" for m in sorted(importers)))
    else:
        L.append("**Imported by**: no importer inside the extraction window "
                 "(9 `src/utils` files + 58 direct importers under `src/`; `scripts/` and `tests/` were not extracted, "
                 "so this is *not* evidence the module is unused).")
    L.append("")

    mattrs = [a for a in (ms.get("attrs") or []) if not a["name"].startswith("__")]
    if mattrs:
        L.append("## Module-level constants")
        L.append("")
        L.extend(attr_table(mattrs, mod + ":", "Declared at module level")[2:])
    L.append("## Contents")
    L.append("")
    if not tops:
        L.append("*No classes or functions — module-level definitions only.*")
    for _, k in tops:
        nm = k.split(":", 1)[1]
        kd = docs.get(k)
        kk = ent_supp.get(k, {}).get("kind", "")
        L.append(f"- [`{nm}`](#{anchor(nm)}) — *{kk}* — " + (kd or "**[HOLE] undocumented**"))
    L.append("")
    L.append("---")
    L.append("")

    # entities: top-level in source order, each followed by its members
    def emit(key, level):
        L.extend(entity_section(key, level, mod))
        for _, kid in sorted(contains.get(key, [])):
            emit(kid, level + 1)

    for _, k in tops:
        emit(k, 2)

    L.append("---")
    L.append("")
    L.append("**Provenance**: unmarked facts come from `evidence/x7b/statements.jsonl`; "
             "`[a]` from `evidence/x7a/statements.jsonl`; `[s]` had to be fetched from source "
             "by `evidence/x11/supplement.py` and is a logged statement-vocabulary gap. "
             "No sentence on this page was written by a model.\n\n"
             "Line numbers in source links are the store's `q.line` **+ 1**: x7b records 0-based "
             "lines for all 87 entities and the schema does not say so (defect D1).")
    return "\n".join(L) + "\n"


def index_page():
    L = ["# `src/utils` — module index", "",
         "Generated from the statement store by `evidence/x11/render.py`. "
         "One page per module; every entity gets an article; entities with no docstring "
         "carry an explicit **[HOLE]** marker.", "",
         "| module | purpose | entities | holes | lines |",
         "| --- | --- | --- | --- | --- |"]
    tot = holes = 0
    for mod in MODULES:
        ms = mod_supp[mod]
        members = [k for k in ent_supp if modof(k) == mod]
        h = sum(1 for k in members if k not in docs)
        tot += len(members)
        holes += h
        page = ("__init__" if mod == "src.utils" else mod.split(".")[-1]) + ".md"
        L.append(f"| [`{mod}`]({page}) | {docs.get(mod + ':', '**[HOLE]**')} | {len(members)} | "
                 f"{h if h else '—'} | {ms['loc']} |")
    L.append("")
    L.append(f"**Totals**: 9 modules, {tot} entities, {holes} undocumented "
             f"({holes * 100 // tot}% holes), {sum(mod_supp[m]['loc'] for m in MODULES)} source lines.")
    L.append("")
    L.append("**Provenance**: unmarked = `x7b` statements · `[a]` = `x7a` statements · "
             "`[s]` = fetched from source (a logged gap in the statement vocabulary).")
    return "\n".join(L) + "\n"


def main():
    for mod in MODULES:
        page = ("__init__" if mod == "src.utils" else mod.split(".")[-1]) + ".md"
        (OUT / page).write_text(module_page(mod), encoding="utf-8")
    (OUT / "INDEX.md").write_text(index_page(), encoding="utf-8")
    (HERE / "gaplog.json").write_text(json.dumps(dict(GAPLOG), indent=1), encoding="utf-8")
    print("pages:", len(MODULES) + 1)
    print("gap hits:", dict(GAPLOG))


if __name__ == "__main__":
    main()
