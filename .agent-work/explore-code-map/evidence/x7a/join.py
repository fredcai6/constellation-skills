"""x7a step 3 — join SCIP symbol identity to AST Store/Load context, emit
statement lines.

The join key is source position. SCIP Occurrence.range is 0-based
(line, char); CPython's ast col_offset is a 0-based UTF-8 *byte* offset, so
the sidecar carries both and this script measures which one agrees.

Output: statements.jsonl, join_report.json
"""
import os, json, hashlib, re
from collections import Counter, defaultdict

OUT = os.path.dirname(os.path.abspath(__file__))
ROLE_DEF, ROLE_READ = 0x1, 0x8


def load(name):
    with open(os.path.join(OUT, name), encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


def short(sym):
    """Readable symbol id: drop the scip scheme header, keep the descriptor."""
    if sym.startswith("local "):
        return sym
    parts = sym.split(" ", 4)
    if len(parts) < 5:
        return sym
    scheme, _, pkg, ver, desc = parts
    return desc if pkg == "f1brainz" else "ext:%s/%s" % (pkg, desc)


def parent_symbol(sym):
    """Strip the last descriptor: `m`/A#b(). -> `m`/A#  ;  `m`/A# -> `m`/"""
    parts = sym.split(" ", 4)
    if len(parts) < 5 or sym.startswith("local "):
        return None
    head, desc = " ".join(parts[:4]), parts[4]
    if desc.endswith(")") and "(" in desc:            # parameter
        return head + " " + desc[:desc.rfind("(")]
    for suf in ("().", "#", ".", "/", ":"):
        if desc.endswith(suf):
            body = desc[:-len(suf)]
            m = max(body.rfind("#"), body.rfind("/"), body.rfind("`"))
            if m < 0:
                return None
            cut = body[:m + 1]
            return (head + " " + cut) if cut else None
    return None


DOC_FENCE = re.compile(r"```.*?```", re.S)
# scip-python's documentation field carries hover text, not only docstrings:
# a rendered signature (fenced), and for untyped-in-source symbols a bare
# inferred-type line like "(module): yaml [unable to resolve module]".
HOVER_TYPE = re.compile(
    r"^\((module|variable|parameter|property|function|method|class|type"
    r"|type parameter|constant|field)\)")


def prose(doc_lines):
    joined = "\n".join(doc_lines)
    txt = DOC_FENCE.sub("", joined).strip()
    if not txt or HOVER_TYPE.match(txt):
        return None
    return txt


def h(*parts):
    return hashlib.sha1("\x1f".join(str(p) for p in parts)
                        .encode("utf-8")).hexdigest()[:12]


def main():
    occ = load("scip_occ.jsonl")
    defs = load("scip_defs.jsonl")
    ast_rows = load("ast_ctx.jsonl")
    mods = json.load(open(os.path.join(OUT, "ast_modules.json"), encoding="utf-8"))

    rpt = Counter()

    # ---------------------------------------------------------------- join keys
    by_bcol, by_ccol = {}, {}
    for r in ast_rows:
        by_bcol.setdefault((r["file"], r["line"], r["bcol"]), []).append(r)
        by_ccol.setdefault((r["file"], r["line"], r["ccol"]), []).append(r)

    # measure which column convention SCIP uses
    probe = [o for o in occ if not (o["roles"] & ROLE_DEF)]
    hit_b = sum(1 for o in probe
                if (o["file"], o["line"] + 1, o["col"]) in by_bcol)
    hit_c = sum(1 for o in probe
                if (o["file"], o["line"] + 1, o["col"]) in by_ccol)
    rpt["probe_refs"] = len(probe)
    rpt["hit_utf8_bytecol"] = hit_b
    rpt["hit_charcol"] = hit_c
    index = by_bcol if hit_b >= hit_c else by_ccol
    convention = "utf8-byte" if hit_b >= hit_c else "char"

    # ------------------------------------------------- enclosing-def attribution
    spans = defaultdict(list)
    for o in occ:
        if (o["roles"] & ROLE_DEF) and o["encl"] and len(o["encl"]) >= 3:
            e = o["encl"]
            sl, el = e[0], (e[2] if len(e) >= 4 else e[0])
            spans[o["file"]].append((sl, el, o["symbol"]))
    for f in spans:
        spans[f].sort(key=lambda t: (t[1] - t[0]))     # innermost first

    module_sym = {}
    for d in defs:
        if d["kind"] == "meta" and d["desc"].endswith("__init__:"):
            module_sym[d["file"]] = d["symbol"]

    def subject_at(file, line0):
        for sl, el, sym in spans.get(file, []):
            if sl <= line0 <= el:
                return sym
        return module_sym.get(file, "module:" + file.replace("\\", "/"))

    stmts = []

    def add(s, p, o, file, line, ref, extra=None):
        q = {"file": file.replace("\\", "/"), "line": line}
        if extra:
            q.update(extra)
        stmts.append({"s": short(s), "p": p, "o": o if isinstance(o, str) else o,
                      "q": q, "ref": ref, "hash": h(s, p, o, file, line)})
        rpt["p:" + p] += 1
        rpt["ref:" + ref] += 1

    # ---------------------------------------------------------------- contains
    known = {d["symbol"] for d in defs}
    def_line = {}
    for o in occ:
        if (o["roles"] & ROLE_DEF) and o["symbol"] not in def_line:
            def_line[o["symbol"]] = (o["file"], o["line"] + 1)
    for d in defs:
        if d["kind"] in ("local", "meta"):
            continue
        par = parent_symbol(d["symbol"])
        if not par:
            continue
        f, ln = def_line.get(d["symbol"], (d["file"], 0))
        if d["kind"] == "parameter":
            add(par, "param-of", short(d["symbol"]), f, ln, "scip",
                {"inverse": True})
        else:
            add(par, "contains", short(d["symbol"]), f, ln, "scip",
                {"kind": d["kind"]})

    # locals: SCIP knows the container exists but not its name; the AST join
    # supplies the name. Emit contains edges for named locals.
    for o in occ:
        if not (o["roles"] & ROLE_DEF) or not o["symbol"].startswith("local "):
            continue
        hits = index.get((o["file"], o["line"] + 1, o["col"]), [])
        nm = hits[0]["name"] if hits else None
        if nm is None:
            rpt["local_name_unrecovered"] += 1
            continue
        add(subject_at(o["file"], o["line"]), "contains", nm,
            o["file"], o["line"] + 1, "scip+ast",
            {"kind": "local", "scip_id": o["symbol"]})

    # ---------------------------------------------------------------- documents
    ast_doc = {}
    for r in ast_rows:
        if r["ctx"] == "def" and r.get("doc"):
            ast_doc[(r["file"], r["line"], r["name"])] = r["doc"]
    for d in defs:
        if d["kind"] == "local":
            continue           # locals carry an inferred type, never prose
        p = prose(d["doc"])
        if p:
            f, ln = def_line.get(d["symbol"], (d["file"], 0))
            add(d["symbol"], "documents", p.split("\n")[0].strip(),
                f, ln, "scip", {"chars": len(p)})
            rpt["doc_from_scip"] += 1
    for m in mods:
        if m["doc"] and m["file"].startswith("src\\utils"):
            add("module:" + m["file"].replace("\\", "/"), "documents",
                m["doc"].split("\n")[0].strip(), m["file"], 1, "ast",
                {"chars": len(m["doc"])})
            rpt["doc_module_from_ast"] += 1

    # ------------------------------------------------------------------- calls
    #
    # SCIP's "method" symbol kind covers callables, properties and imported
    # names alike; only the AST says whether this *position* is a call site.
    # An unconfirmed method reference is a read, not a call — @property access
    # (`rel.parts`) and `from m import f` both land here.
    for o in occ:
        if o["roles"] & ROLE_DEF or o["kind"] != "method":
            continue
        subj = subject_at(o["file"], o["line"])
        if subj == o["symbol"]:
            continue
        hits = index.get((o["file"], o["line"] + 1, o["col"]), [])
        ctxs = {x["ctx"] for x in hits}
        d = {"external": not o["project"],
             "direction": "in" if (not o["in_slice"]) else
                          ("out" if not o["utils_sym"] else "internal")}
        f, ln = o["file"], o["line"] + 1
        if "callee" in ctxs:
            add(subj, "calls", short(o["symbol"]), f, ln, "scip+ast", d)
        elif "import" in ctxs:
            add(subj, "reads", short(o["symbol"]), f, ln, "scip+ast",
                dict(d, via="import"))
            rpt["method_ref_is_import"] += 1
        elif ctxs & {"load", "store", "augstore"}:
            p = "writes" if (ctxs & {"store", "augstore"}) else "reads"
            add(subj, p, short(o["symbol"]), f, ln, "scip+ast",
                dict(d, via="attribute-not-call"))
            rpt["method_ref_is_" + p] += 1
        else:
            add(subj, "calls", short(o["symbol"]), f, ln, "scip",
                dict(d, ast_unconfirmed=True))
            rpt["call_unconfirmed"] += 1

    # -------------------------------------------------------- reads and writes
    #
    # The write signal is split across BOTH tools and BOTH SCIP roles:
    #   * a first binding (`X = 5`) is a SCIP *Definition*, never a write role
    #   * a re-binding or attribute store is SCIP *ReadAccess*
    # Only the AST says which is a store. So writes = (Definition | ReadAccess)
    # intersected with an ast.Store context.
    for o in occ:
        if not (o["roles"] & ROLE_DEF):
            continue
        if o["kind"] in ("method", "type", "parameter", "meta"):
            continue                     # transformers and params, not writes
        hits = index.get((o["file"], o["line"] + 1, o["col"]), [])
        if not any(x["ctx"] in ("store", "augstore") for x in hits):
            rpt["def_write_unjoined:" + o["kind"]] += 1
            continue
        nm = hits[0]["name"]
        add(subject_at(o["file"], o["line"]), "writes", short(o["symbol"]),
            o["file"], o["line"] + 1, "scip+ast",
            {"name": nm, "binding": "first", "scip_role": "Definition",
             "direction": "internal" if o["in_slice"] else "in"})
        rpt["write_from_definition"] += 1

    CTX2P = {"store": ["writes"], "del": ["writes"],
             "augstore": ["reads", "writes"], "load": ["reads"],
             "import": ["reads"], "kwarg": ["reads"],
             "param": None, "def": None, "callee": ["reads"]}
    for o in occ:
        if o["roles"] & ROLE_DEF:
            continue
        if o["kind"] == "method":
            continue                     # already emitted as calls
        if not (o["roles"] & ROLE_READ):
            continue
        hits = index.get((o["file"], o["line"] + 1, o["col"]), [])
        # prefer a context-bearing node over a bare callee marker
        ctx = None
        for want in ("store", "del", "augstore", "load", "import", "kwarg"):
            if any(x["ctx"] == want for x in hits):
                ctx = want
                break
        if ctx is None:
            rpt["rw_unjoined"] += 1
            preds, ref = ["reads"], "scip"     # SCIP's own (read-only) claim
        else:
            preds, ref = CTX2P[ctx], "scip+ast"
            rpt["rw_joined:" + ctx] += 1
            rpt["rw_joined"] += 1
        subj = subject_at(o["file"], o["line"])
        nm = hits[0]["name"] if hits else None
        for p in preds:
            add(subj, p, short(o["symbol"]), o["file"], o["line"] + 1, ref,
                {"name": nm, "external": not o["project"],
                 "direction": "in" if (not o["in_slice"]) else
                              ("out" if not o["utils_sym"] else "internal"),
                 "scip_role": "ReadAccess"})

    with open(os.path.join(OUT, "statements.jsonl"), "w", encoding="utf-8") as f:
        for st in stmts:
            f.write(json.dumps(st, ensure_ascii=False) + "\n")

    rpt["column_convention"] = convention
    rpt["statements"] = len(stmts)
    report = dict(rpt)
    with open(os.path.join(OUT, "join_report.json"), "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
