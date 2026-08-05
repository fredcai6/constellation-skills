"""Second pass over the SCIP index: things summary.json did not answer.

- Is Document.text emitted (can we resolve `local N` names without the source)?
- Do occurrences carry enclosing_range (field 7)?
- Can caller->callee call edges be reconstructed by bucketing occurrences into
  the line span of the enclosing function definition?
- Split `term` symbols into module-level state vs class fields.
- Which import edges exist (module -> module).
"""

import sys, json, os
from collections import Counter, defaultdict
from decode_scip import iter_fields, unpack_varints, s, classify_symbol, ROLE

path = sys.argv[1] if len(sys.argv) > 1 else "index.scip"
raw = open(path, "rb").read()

docs = [v for fn, wt, v in iter_fields(raw) if fn == 2 and wt == 2]

text_docs = 0
occ_total = 0
occ_with_enclosing = 0
def_occ_with_enclosing = 0
term_module = 0
term_field = 0
term_module_samples, term_field_samples = [], []
import_role = 0

# call-edge reconstruction
call_edges = Counter()          # (caller_sym, callee_sym)
callee_unattributed = 0
callee_total = 0
cross_module_calls = 0
file_dep = Counter()            # (from_file, to_module)

for dbuf in docs:
    relpath = None
    occs, syms, text = [], [], None
    for fn, wt, val in iter_fields(dbuf):
        if fn == 1 and wt == 2:
            relpath = s(val)
        elif fn == 2 and wt == 2:
            occs.append(val)
        elif fn == 3 and wt == 2:
            syms.append(val)
        elif fn == 5 and wt == 2:
            text = val
    if text:
        text_docs += 1

    # parse occurrences once
    parsed = []
    for obuf in occs:
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
        parsed.append((sym, roles, rng, encl))
        occ_total += 1
        if encl:
            occ_with_enclosing += 1
            if roles & ROLE["Definition"]:
                def_occ_with_enclosing += 1
        if roles & ROLE["Import"]:
            import_role += 1

    # term split, from the SymbolInformation table
    for sbuf in syms:
        sym = None
        for fn, wt, val in iter_fields(sbuf):
            if fn == 1 and wt == 2:
                sym = s(val)
                break
        if not sym:
            continue
        kind, desc = classify_symbol(sym)
        if kind == "term":
            # descriptor tail after the last '#' or '/' tells us the owner
            if "#" in desc:
                term_field += 1
                if len(term_field_samples) < 5:
                    term_field_samples.append((relpath, sym))
            else:
                term_module += 1
                if len(term_module_samples) < 5:
                    term_module_samples.append((relpath, sym))

    # ---- call-edge reconstruction ----------------------------------------
    # method definitions in THIS file, with their start line; the span of a
    # method is [start_line, next_method_start).  This is the only way to get
    # "which function is this occurrence inside", because enclosing_symbol and
    # enclosing_range are not emitted.
    method_defs = sorted(
        [(rng[0], sym) for sym, roles, rng, encl in parsed
         if (roles & ROLE["Definition"]) and classify_symbol(sym)[0] == "method" and rng]
    )
    def owner_of(line):
        lo, hi = 0, len(method_defs)
        while lo < hi:
            mid = (lo + hi) // 2
            if method_defs[mid][0] <= line:
                lo = mid + 1
            else:
                hi = mid
        return method_defs[lo - 1][1] if lo > 0 else None

    for sym, roles, rng, encl in parsed:
        if roles & ROLE["Definition"]:
            continue
        kind, _ = classify_symbol(sym)
        if kind != "method":
            continue
        callee_total += 1
        caller = owner_of(rng[0]) if rng else None
        if caller is None:
            callee_unattributed += 1
        else:
            call_edges[(caller, sym)] += 1
        # file-level dependency: module part of the callee symbol
        parts = sym.split(" ", 4)
        if len(parts) == 5:
            mod = parts[4].split("/")[0].strip("`")
            if relpath and mod:
                file_dep[(relpath, mod)] += 1

out = {
    "documents": len(docs),
    "documents_with_text_field": text_docs,
    "occurrences_total": occ_total,
    "occurrences_with_enclosing_range": occ_with_enclosing,
    "definition_occurrences_with_enclosing_range": def_occ_with_enclosing,
    "occurrences_with_Import_role": import_role,
    "term_module_level": term_module,
    "term_class_field": term_field,
    "term_module_samples": term_module_samples,
    "term_field_samples": term_field_samples,
    "method_reference_occurrences": callee_total,
    "method_refs_not_attributable_to_a_caller": callee_unattributed,
    "distinct_caller_callee_pairs": len(call_edges),
    "top_call_edges": [[a, b, n] for (a, b), n in call_edges.most_common(8)],
    "distinct_file_to_module_dep_pairs": len(file_dep),
}
outdir = os.path.dirname(os.path.abspath(path))
json.dump(out, open(os.path.join(outdir, "probe2.json"), "w", encoding="utf-8"), indent=2)
with open(os.path.join(outdir, "call_edges.jsonl"), "w", encoding="utf-8") as f:
    for (a, b), n in call_edges.items():
        f.write(json.dumps({"caller": a, "callee": b, "count": n}) + "\n")
print(json.dumps(out, indent=2)[:5000])
