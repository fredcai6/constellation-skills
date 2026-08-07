"""Function-by-function renderer -- one markdown page per entity.

Ruling 2026-08-07 (human): the per-module pages are too long; the map should be
bite-sized so a reader loads exactly the entity they care about, not a whole
file's worth of syntax. This reuses render.py's loaded stores and its
entity_section verbatim -- only the pagination changes.

Output layout:
  articles-fn/INDEX.md                    top index, links to module indexes
  articles-fn/<module>/INDEX.md           module page: doc, deps, constants, contents
  articles-fn/<module>/<Entity>.md        one page per class/function/method
"""
import collections
import pathlib

import render as R

OUT = pathlib.Path(__file__).parent / "articles-fn"

FOOTER = (
    "\n---\n"
    "*Generated from the statement store by `evidence/x11/render_fn.py`. "
    "Unmarked facts = `x7b` statements; `[a]` = `x7a`; `[s]` = fetched from "
    "source (a logged vocabulary gap). Source-link lines are the store's "
    "`q.line` + 1 (defect D1: the store is 0-based and does not say so).*\n"
)


def crumbs(mod, parent=None):
    c = f"[map index](../INDEX.md) / [`{mod}`](INDEX.md)"
    if parent:
        c += f" / [`{parent}`]({parent}.md)"
    return c


def entity_page(key, mod, parent):
    body = R.entity_section(key, 1, mod)
    text = crumbs(mod, parent) + "\n\n" + "\n".join(body)
    # the Members list was written for a single-file page (in-page anchors);
    # on a per-entity page each member is its own file
    for _, kid in R.contains.get(key, []):
        kn = kid.split(":", 1)[1]
        text = text.replace(f"](#{R.anchor(kn)})", f"]({kn}.md)")
    return text + FOOTER


def contents_listing(mod):
    L = []

    def walk(key, depth):
        nm = key.split(":", 1)[1]
        kd = R.docs.get(key)
        kk = R.ent_supp.get(key, {}).get("kind", "")
        L.append("  " * depth + f"- [`{nm}`]({nm}.md) — *{kk}* [s] — "
                 + (kd or "**[HOLE] undocumented**"))
        for _, kid in sorted(R.contains.get(key, [])):
            walk(kid, depth + 1)

    for _, k in sorted(R.contains.get(mod + ":", [])):
        walk(k, 0)
    return L


def module_index(mod):
    ms = R.mod_supp[mod]
    L = ["[map index](../INDEX.md)", "", f"# `{mod}`", ""]
    d = R.docs.get(mod + ":")
    L.append("> " + d if d else R.HOLE)
    body = ms.get("doc_body")
    if body:
        L.append(">")
        for bl in body.split("\n"):
            L.append("> " + bl if bl.strip() else ">")
        L.append("")
        L.append("*(everything after the first line above is [s].)*")
    L.append("")
    members = [k for k in R.ent_supp if R.modof(k) == mod]
    documented = sum(1 for k in members if k in R.docs)
    L.append(f"`{ms['file']}` · {ms['loc']} lines [s] · {len(members)} entities "
             f"· {documented} documented, {len(members) - documented} **holes**")
    if ms.get("all"):
        L.append("")
        L.append("**Re-exports (`__all__`) [s]**: " + ", ".join(f"`{x}`" for x in ms["all"]))
    L.append("")

    # dependencies (same derivation as render.module_page)
    imps = [st for st in R.core if st["p"] == "imports" and st["s"] == mod + ":"]
    ext = sorted({st["o"].rstrip(":").replace(":", ".") for st in imps if st.get("res") == "external"})
    inte = sorted({st["o"] for st in imps if st.get("res") == "internal"})
    L.append("## Dependencies")
    L.append("")
    if ext:
        std = [x for x in ext if R.ext_label(x) == "stdlib"]
        thi = [x for x in ext if R.ext_label(x) != "stdlib"]
        if std:
            L.append("**Imports (stdlib)**: " + ", ".join(f"`{x}`" for x in std))
        if thi:
            L.append("**Imports (third-party)**: " + ", ".join(f"`{x}`" for x in thi))
    if inte:
        L.append("")
        L.append("**Imports (internal)**: "
                 + ", ".join(f"`{x}`" for x in sorted({R.modof(x) + ':' + x.split(':', 1)[1] for x in inte})))
    importers = collections.Counter()
    for st in R.allst:
        if st["p"] == "imports" and R.modof(st["o"]) == mod:
            importers[R.modof(st["s"])] += 1
    L.append("")
    if importers:
        L.append(f"**Imported by** ({len(importers)} modules in the extraction window): "
                 + ", ".join(f"`{m}`" for m in sorted(importers)))
    else:
        L.append("**Imported by**: no importer inside the extraction window "
                 "(9 `src/utils` files + 58 direct importers under `src/`; "
                 "`scripts/` and `tests/` were not extracted, so this is *not* "
                 "evidence the module is unused).")
    L.append("")

    mattrs = [a for a in (ms.get("attrs") or []) if not a["name"].startswith("__")]
    if mattrs:
        L.append("## Module-level constants")
        L.append("")
        L.extend(R.attr_table(mattrs, mod + ":", "Declared at module level")[2:])

    L.append("## Contents")
    L.append("")
    listing = contents_listing(mod)
    if listing:
        L.extend(listing)
    else:
        L.append("*No classes or functions — module-level definitions only.*")
    return "\n".join(L) + FOOTER


def top_index():
    L = ["# `src/utils` — map index (one page per entity)", "",
         "Generated from the statement store by `evidence/x11/render_fn.py`. "
         "Each class, function, and method has its own page; module pages hold "
         "only the module doc, dependencies, constants, and a linked contents "
         "list. Entities with no docstring carry an explicit **[HOLE]** marker.", "",
         "| module | purpose | entities | holes | source lines |",
         "| --- | --- | --- | --- | --- |"]
    tot = holes = 0
    for mod in R.MODULES:
        ms = R.mod_supp[mod]
        members = [k for k in R.ent_supp if R.modof(k) == mod]
        h = sum(1 for k in members if k not in R.docs)
        tot += len(members)
        holes += h
        L.append(f"| [`{mod}`]({mod}/INDEX.md) | {R.docs.get(mod + ':', '**[HOLE]**')} "
                 f"| {len(members)} | {h if h else '—'} | {ms['loc']} |")
    L.append("")
    L.append(f"**Totals**: 9 modules, {tot} entities, {holes} undocumented "
             f"({holes * 100 // tot}% holes), "
             f"{sum(R.mod_supp[m]['loc'] for m in R.MODULES)} source lines.")
    return "\n".join(L) + FOOTER


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    npages = 0
    sizes = []
    for mod in R.MODULES:
        d = OUT / mod
        d.mkdir(exist_ok=True)
        (d / "INDEX.md").write_text(module_index(mod), encoding="utf-8")
        npages += 1

        def emit(key, parent):
            nonlocal npages
            page = entity_page(key, mod, parent)
            (d / (key.split(":", 1)[1] + ".md")).write_text(page, encoding="utf-8")
            sizes.append((page.count("\n"), key))
            npages += 1
            for _, kid in sorted(R.contains.get(key, [])):
                emit(kid, key.split(":", 1)[1])

        for _, k in sorted(R.contains.get(mod + ":", [])):
            emit(k, None)
    (OUT / "INDEX.md").write_text(top_index(), encoding="utf-8")
    npages += 1
    sizes.sort(reverse=True)
    print("pages:", npages)
    print("entity pages:", len(sizes))
    print("median entity page lines:", sizes[len(sizes) // 2][0])
    print("largest 5:", sizes[:5])


if __name__ == "__main__":
    main()
