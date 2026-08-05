"""Third pass: exact call attribution using Occurrence.enclosing_range,
internal-vs-external callee split, module dependency graph, and a check that
`local N` variable names are recoverable from the source at the given range.
"""

import sys, json, os, io
from collections import Counter, defaultdict
from decode_scip import iter_fields, unpack_varints, s, classify_symbol, ROLE

path = sys.argv[1] if len(sys.argv) > 1 else "index.scip"
SRC_ROOT = r"C:\Programs\f1Brainz"
raw = open(path, "rb").read()
docs = [v for fn, wt, v in iter_fields(raw) if fn == 2 and wt == 2]

encl_by_kind = Counter()
call_edges = Counter()
call_internal = 0
call_external = 0
unattributed = 0
mod_dep = Counter()             # (from_module, to_module) internal only
methods_with_span = 0
methods_total = 0
local_name_checks = []
container_reads_in_fn = 0       # field/module-var reads attributed to a function
container_edges = Counter()     # (function, container_symbol, "read")


def norm_range(r):
    # SCIP range is [startLine, startChar, endLine, endChar] or 3-elem
    # [startLine, startChar, endChar] when single-line.
    if len(r) == 3:
        return r[0], r[0]
    if len(r) >= 4:
        return r[0], r[2]
    return r[0], r[0]


for dbuf in docs:
    relpath, occs, syms = None, [], []
    for fn, wt, val in iter_fields(dbuf):
        if fn == 1 and wt == 2:
            relpath = s(val)
        elif fn == 2 and wt == 2:
            occs.append(val)
        elif fn == 3 and wt == 2:
            syms.append(val)

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
        if sym:
            parsed.append((sym, roles, rng, encl))

    # exact spans of function bodies, innermost-wins
    spans = []
    for sym, roles, rng, encl in parsed:
        if roles & ROLE["Definition"]:
            k = classify_symbol(sym)[0]
            if k == "method":
                methods_total += 1
            if encl:
                encl_by_kind[k] += 1
                if k == "method":
                    methods_with_span += 1
                    a, b = norm_range(encl)
                    spans.append((a, b, sym))
    spans.sort(key=lambda t: (t[0], -(t[1] - t[0])))

    def owner_of(line):
        best = None
        for a, b, sym in spans:
            if a <= line <= b:
                if best is None or (b - a) < (best[1] - best[0]):
                    best = (a, b, sym)
        return best[2] if best else None

    this_mod = relpath.replace("\\", "/").replace(".py", "").replace("/", ".") if relpath else "?"

    for sym, roles, rng, encl in parsed:
        if roles & ROLE["Definition"]:
            continue
        kind = classify_symbol(sym)[0]
        line = rng[0] if rng else 0
        internal = " f1brainz " in sym
        if kind == "method":
            caller = owner_of(line)
            if caller is None:
                unattributed += 1
            else:
                call_edges[(caller, sym)] += 1
            if internal:
                call_internal += 1
                parts = sym.split(" ", 4)
                tomod = parts[4].split("/")[0].strip("`") if len(parts) == 5 else "?"
                mod_dep[(this_mod, tomod)] += 1
            else:
                call_external += 1
        elif kind == "term" and internal:
            owner = owner_of(line)
            if owner:
                container_reads_in_fn += 1
                container_edges[(owner, sym)] += 1

    # sample: can we recover `local N` names from source?
    if relpath and len(local_name_checks) < 12:
        full = os.path.join(SRC_ROOT, relpath)
        try:
            lines = io.open(full, encoding="utf-8", errors="replace").read().splitlines()
        except OSError:
            lines = None
        if lines:
            for sym, roles, rng, encl in parsed:
                if len(local_name_checks) >= 12:
                    break
                if sym.startswith("local ") and (roles & ROLE["Definition"]) and rng and len(rng) >= 3:
                    ln = rng[0]
                    if ln < len(lines):
                        c0 = rng[1]
                        c1 = rng[2] if len(rng) == 3 else rng[3]
                        local_name_checks.append({
                            "file": relpath, "symbol": sym,
                            "recovered_name": lines[ln][c0:c1],
                            "source_line": lines[ln].strip()[:90],
                        })

out = {
    "definition_occurrences_with_enclosing_range_by_kind": dict(encl_by_kind),
    "methods_total": methods_total,
    "methods_with_body_span": methods_with_span,
    "call_site_occurrences_internal": call_internal,
    "call_site_occurrences_external": call_external,
    "call_sites_not_inside_any_function": unattributed,
    "distinct_caller_callee_pairs": len(call_edges),
    "distinct_internal_module_dep_pairs": len(mod_dep),
    "top_module_deps": [[a, b, n] for (a, b), n in mod_dep.most_common(10)],
    "function_reads_container_occurrences": container_reads_in_fn,
    "distinct_function_container_read_pairs": len(container_edges),
    "local_name_recovery_samples": local_name_checks,
}
outdir = os.path.dirname(os.path.abspath(path))
json.dump(out, open(os.path.join(outdir, "probe3.json"), "w", encoding="utf-8"), indent=2)
with open(os.path.join(outdir, "module_deps.jsonl"), "w", encoding="utf-8") as f:
    for (a, b), n in mod_dep.items():
        f.write(json.dumps({"from": a, "to": b, "count": n}) + "\n")
print(json.dumps(out, indent=2)[:6000])
