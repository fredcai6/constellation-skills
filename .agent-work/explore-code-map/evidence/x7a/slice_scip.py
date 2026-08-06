"""x7a step 1 — pull the src/utils slice out of x1's SCIP index.

Reuses evidence/x1/decode_scip.py for the wire format. Emits, for the slice:
  scip_defs.jsonl  one line per SymbolInformation defined in a slice file
  scip_occ.jsonl   one line per Occurrence with a full range, in a slice file
                   OR in any file that references a src.utils symbol
  scip_slice.json  counts

Slice = documents under src\\utils\\  +  cross-package: every document that
mentions a `src.utils.*` symbol (inbound edges), and every non-utils symbol
mentioned inside src\\utils\\ (outbound edges).
"""
import sys, os, json
from collections import Counter, defaultdict

X1 = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "x1")
sys.path.insert(0, os.path.abspath(X1))
from decode_scip import iter_fields, unpack_varints, s, classify_symbol, ROLE  # noqa

OUT = os.path.dirname(os.path.abspath(__file__))
INDEX = os.path.join(os.path.abspath(X1), "index.scip")

SLICE_PREFIX = "src\\utils\\"
UTILS_MOD = "`src.utils"          # symbol module prefix for the slice package


def sym_module(sym):
    """Module path out of a scip-python symbol, or None."""
    parts = sym.split(" ", 4)
    if len(parts) < 5:
        return None
    desc = parts[4]
    if desc.startswith("`"):
        end = desc.find("`", 1)
        return desc[1:end] if end > 0 else None
    # non-backticked top package form: "src/foo." -> module "src"
    if "/" in desc:
        return desc.split("/", 1)[0]
    return None


def is_utils(sym):
    m = sym_module(sym)
    return m is not None and (m == "src.utils" or m.startswith("src.utils."))


def is_project(sym):
    return " f1brainz " in sym[:80]


def main():
    raw = open(INDEX, "rb").read()
    docs = []
    for fn, wt, val in iter_fields(raw):
        if fn == 2 and wt == 2:
            docs.append(val)

    defs, occs = [], []
    counts = Counter()
    inbound_files = set()

    for dbuf in docs:
        relpath = None
        occ_bufs, sym_bufs = [], []
        for fn, wt, val in iter_fields(dbuf):
            if fn == 1 and wt == 2:
                relpath = s(val)
            elif fn == 2 and wt == 2:
                occ_bufs.append(val)
            elif fn == 3 and wt == 2:
                sym_bufs.append(val)

        in_slice = relpath.startswith(SLICE_PREFIX)

        # decode occurrences once; decide relevance after
        decoded = []
        touches_utils = False
        for obuf in occ_bufs:
            sym, roles, rng, encl = None, 0, None, None
            for fn, wt, val in iter_fields(obuf):
                if fn == 1:
                    rng = unpack_varints(val) if wt == 2 else [val]
                elif fn == 2 and wt == 2:
                    sym = s(val)
                elif fn == 3 and wt == 0:
                    roles = val
                elif fn == 7:
                    encl = unpack_varints(val) if wt == 2 else [val]
            if sym is None:
                continue
            u = is_utils(sym)
            touches_utils = touches_utils or u
            decoded.append((sym, roles, rng, encl, u))

        if not (in_slice or touches_utils):
            continue
        if not in_slice:
            inbound_files.add(relpath)

        for sym, roles, rng, encl, u in decoded:
            # in-slice: keep everything. out-of-slice: keep utils refs plus
            # every def-with-body-span, needed to attribute a subject to the
            # inbound edge.
            if not in_slice and not u and not (
                    (roles & ROLE["Definition"]) and encl):
                continue
            kind, _ = classify_symbol(sym)
            # normalise range to (line, col, endline, endcol), 0-based
            if rng is None:
                continue
            if len(rng) == 3:
                r = (rng[0], rng[1], rng[0], rng[2])
            elif len(rng) == 4:
                r = (rng[0], rng[1], rng[2], rng[3])
            else:
                continue
            occs.append({
                "file": relpath, "symbol": sym, "kind": kind, "roles": roles,
                "line": r[0], "col": r[1], "end_line": r[2], "end_col": r[3],
                "encl": encl, "in_slice": in_slice, "utils_sym": u,
                "project": is_project(sym),
            })
            counts["occ"] += 1
            for name, bit in ROLE.items():
                if roles & bit:
                    counts["role:" + name] += 1

        if in_slice:
            for sbuf in sym_bufs:
                sym, doc_lines, kind_enum = None, [], None
                for fn, wt, val in iter_fields(sbuf):
                    if fn == 1 and wt == 2:
                        sym = s(val)
                    elif fn == 3 and wt == 2:
                        doc_lines.append(s(val))
                    elif fn == 5 and wt == 0:
                        kind_enum = val
                if sym is None:
                    continue
                kind, desc = classify_symbol(sym)
                defs.append({"symbol": sym, "file": relpath, "kind": kind,
                             "desc": desc, "kind_enum": kind_enum,
                             "doc": doc_lines})
                counts["def:" + kind] += 1

    with open(os.path.join(OUT, "scip_defs.jsonl"), "w", encoding="utf-8") as f:
        for d in defs:
            f.write(json.dumps(d) + "\n")
    with open(os.path.join(OUT, "scip_occ.jsonl"), "w", encoding="utf-8") as f:
        for o in occs:
            f.write(json.dumps(o) + "\n")

    summary = {"defs": len(defs), "occs": len(occs),
               "inbound_files": sorted(inbound_files),
               "n_inbound_files": len(inbound_files),
               "counts": dict(counts.most_common())}
    with open(os.path.join(OUT, "scip_slice.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(json.dumps({k: v for k, v in summary.items()
                      if k != "inbound_files"}, indent=2))


if __name__ == "__main__":
    main()
