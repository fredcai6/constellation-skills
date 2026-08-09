"""Function-by-function renderer, agent-lean -- one page per entity.

Rulings applied (human, 2026-08-07):
  - one page per class/function/method, not per module
  - these pages are FOR AGENTS first: aggressively minimize every excess
    character -- no provenance markers, no footers, no stats lines, no
    decoration, ASCII-only template text (docstrings stay verbatim)

Reuses render.py's loaded stores; rendering is independent.

Output layout:
  articles-fn/INDEX.md                    top index, links to module indexes
  articles-fn/<module>/INDEX.md           module doc, deps, constants, contents
  articles-fn/<module>/<Entity>.md        one page per class/function/method
"""
import collections
import pathlib

import render as R

OUT = pathlib.Path(__file__).parent / "articles-fn"

HOLE = "HOLE: no docstring"


def loc(key, e):
    file, line = R.qline.get(key, (None, e.get("line", 0)))
    if file is None:
        file = "?"
    # x7b q.line is 0-based and the schema does not say so (defect D1): +1
    head = f"{file}:{line + 1}"
    if e.get("end_line") and e.get("line") is not None:
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
    buckets = collections.defaultdict(list)
    unresolved = collections.Counter()
    ownparams = {f"{key}.{pn}" for _, pn in R.params.get(key, [])}
    for st in R.edges.get(key, []):
        res = st.get("res")
        if st["o"] in ownparams and st["p"] == "reads":
            continue
        if res == "unresolved":
            unresolved[(st["p"], st.get("why", "?"))] += 1
        elif res == "local":
            continue
        elif res == "internal":
            tag = "internal" if R.modof(st["o"]) == mod else "cross-module"
            buckets[(st["p"], tag)].append(
                st["o"].split(":", 1)[1] if tag == "internal" and ":" in st["o"] else st["o"])
        elif res == "external":
            lab = st["o"]
            lab = lab[:-1] + " (module)" if lab.endswith(":") else lab.replace(":", ".")
            buckets[(st["p"], R.ext_label(st["o"]))].append(lab)
    L = []
    for pred in ("calls", "reads", "writes"):
        for tag in ("internal", "cross-module", "stdlib", "third-party"):
            v = buckets.get((pred, tag))
            if v:
                L.append(f"{pred} {tag}: {R.tally(v)}")
    if unresolved:
        L.append("unresolved: " + ", ".join(
            f"{n} {p} ({why})" for (p, why), n in sorted(unresolved.items())))
    if L:
        L.append("")
    return L


def refs_line(key, mod):
    inb = [st for st in R.inbound.get(key, []) if st["p"] in ("calls", "reads")]
    if not inb:
        return ["referenced by: none found (scripts/ and tests/ not indexed)", ""]
    callers = collections.Counter(R.modof(st["s"]) for st in inb)
    ext = sorted(m for m in callers if m != mod)
    s = f"referenced by: {len(inb)} sites in {len(callers)} modules"
    if ext:
        s += " (" + ", ".join(ext) + ")"
    elif len(callers) == 1:
        s = f"referenced by: {len(inb)} sites, this module only"
    return [s, ""]


def entity_page(key, mod):
    name = key.split(":", 1)[1]
    e = R.ent_supp.get(key, {})
    kind = e.get("kind", "?")
    L = [f"# {key}", f"{kind}, {loc(key, e)}", ""]

    sig = e.get("signature")
    decos = [d for d in e.get("decorators", []) if d not in ("property", "classmethod", "staticmethod")]
    if sig or kind == "class" or decos:
        L.append("```python")
        for d in decos:
            L.append(f"@{d}")
        if sig:
            L.append(f"{'async ' if kind.startswith('async') else ''}def {name.split('.')[-1]}{sig}")
        elif kind == "class":
            bases = ", ".join(b.split(":")[-1] for b in R.inherits.get(key, []))
            L.append(f"class {name.split('.')[-1]}({bases})" if bases else f"class {name.split('.')[-1]}")
        L.append("```")
        L.append("")

    L.extend(doc_block(R.docs.get(key), e.get("doc_body")))

    attrs = [a for a in (e.get("attrs") or []) if not a["name"].startswith("__")]
    if attrs:
        L.extend(attr_lines(attrs))

    kids = sorted(R.contains.get(key, []))
    if kids:
        for _, k in kids:
            kn = k.split(":", 1)[1]
            kd = R.docs.get(k)
            kk = R.ent_supp.get(k, {}).get("kind", "")
            L.append(f"- [{kn.split('.')[-1]}]({kn}.md) {kk}: " + (kd or HOLE))
        L.append("")

    L.extend(uses_lines(key, mod))
    L.extend(refs_line(key, mod))
    return "\n".join(L).rstrip() + "\n"


def module_index(mod):
    ms = R.mod_supp[mod]
    members = [k for k in R.ent_supp if R.modof(k) == mod]
    holes = sum(1 for k in members if k not in R.docs)
    L = [f"# {mod}",
         f"{ms['file']}, {ms['loc']} lines" + (f", {holes} holes" if holes else ""), ""]
    L.extend(doc_block(R.docs.get(mod + ":"), ms.get("doc_body")))

    if ms.get("all"):
        L.append("__all__: " + ", ".join(ms["all"]))
        L.append("")

    imps = [st for st in R.core if st["p"] == "imports" and st["s"] == mod + ":"]
    ext = sorted({st["o"].rstrip(":").replace(":", ".") for st in imps if st.get("res") == "external"})
    inte = sorted({st["o"] for st in imps if st.get("res") == "internal"})
    std = [x for x in ext if R.ext_label(x) == "stdlib"]
    thi = [x for x in ext if R.ext_label(x) != "stdlib"]
    if std:
        L.append("imports stdlib: " + ", ".join(std))
    if thi:
        L.append("imports third-party: " + ", ".join(thi))
    if inte:
        L.append("imports internal: " + ", ".join(sorted({x for x in inte})))
    importers = sorted({R.modof(st["s"]) for st in R.allst
                        if st["p"] == "imports" and R.modof(st["o"]) == mod})
    if importers:
        L.append("imported by: " + ", ".join(importers))
    else:
        L.append("imported by: none found (scripts/ and tests/ not indexed)")
    L.append("")

    mattrs = [a for a in (ms.get("attrs") or []) if not a["name"].startswith("__")]
    if mattrs:
        L.extend(attr_lines(mattrs))

    def walk(key, depth):
        nm = key.split(":", 1)[1]
        kd = R.docs.get(key)
        kk = R.ent_supp.get(key, {}).get("kind", "")
        L.append("  " * depth + f"- [{nm}]({nm}.md) {kk}: " + (kd or HOLE))
        for _, kid in sorted(R.contains.get(key, [])):
            walk(kid, depth + 1)

    for _, k in sorted(R.contains.get(mod + ":", [])):
        walk(k, 0)
    return "\n".join(L).rstrip() + "\n"


def top_index():
    L = ["# src/utils map", ""]
    for mod in R.MODULES:
        members = [k for k in R.ent_supp if R.modof(k) == mod]
        h = sum(1 for k in members if k not in R.docs)
        d = R.docs.get(mod + ":")
        L.append(f"- [{mod}]({mod}/INDEX.md) ({len(members)} entities"
                 + (f", {h} holes" if h else "") + "): " + (d or HOLE))
    return "\n".join(L) + "\n"


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for old in OUT.rglob("*.md"):
        old.unlink()
    npages = 0
    sizes = []
    nonascii = []
    for mod in R.MODULES:
        d = OUT / mod
        d.mkdir(exist_ok=True)
        (d / "INDEX.md").write_text(module_index(mod), encoding="utf-8")
        npages += 1

        def emit(key):
            nonlocal npages
            page = entity_page(key, mod)
            (d / (key.split(":", 1)[1] + ".md")).write_text(page, encoding="utf-8")
            sizes.append((page.count("\n"), key))
            npages += 1
            for _, kid in sorted(R.contains.get(key, [])):
                emit(kid)

        for _, k in sorted(R.contains.get(mod + ":", [])):
            emit(k)
    (OUT / "INDEX.md").write_text(top_index(), encoding="utf-8")
    npages += 1
    for f in OUT.rglob("*.md"):
        for i, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            if any(ord(c) > 127 for c in line):
                nonascii.append((str(f.relative_to(OUT)), i, line[:60]))
    sizes.sort(reverse=True)
    print("pages:", npages)
    print("median entity page lines:", sizes[len(sizes) // 2][0])
    print("largest 5:", sizes[:5])
    print("non-ascii lines (should be docstring-verbatim only):", len(nonascii))
    for t in nonascii[:10]:
        print("  ", ascii(t))


if __name__ == "__main__":
    main()
