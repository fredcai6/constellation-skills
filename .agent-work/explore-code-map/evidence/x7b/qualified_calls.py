"""The number directly comparable to x6's MATLAB finding.

x6 measured that 56% of MATLAB *qualified* call sites (obj.method(...),
pkg.fn(...)) resolve to no target under a pure-parse extractor. This computes
the same rate for the Python AST extractor: of every call whose callee is an
attribute expression, what fraction is UNRESOLVED -- and, separately, what
fraction SCIP (with pyright's inference) did resolve, i.e. the true hole.
"""
import ast
import collections
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = r"C:\Programs\f1Brainz"


def main():
    manifest = json.load(open(os.path.join(HERE, "slice_manifest.json"),
                              encoding="utf-8"))
    files = manifest["core"] + manifest["importers"]
    core = set(manifest["core"])

    # positions of qualified (attribute) vs bare (name) call sites
    qual, bare = set(), set()
    for rel in files:
        tree = ast.parse(open(os.path.join(ROOT, rel), encoding="utf-8").read())
        for n in ast.walk(tree):
            if isinstance(n, ast.Call):
                f = n.func
                if isinstance(f, ast.Attribute):
                    qual.add((rel.replace("\\", "/"), f.end_lineno - 1,
                              f.end_col_offset - len(f.attr)))
                elif isinstance(f, ast.Name):
                    bare.add((rel.replace("\\", "/"), f.lineno - 1, f.col_offset))

    scip = {}
    for l in open(os.path.join(HERE, "scip_occ.jsonl"), encoding="utf-8"):
        r = json.loads(l)
        k = (r["file"].replace("\\", "/"), r["line"], r["c0"])
        if k in scip and (scip[k]["roles"] & 1) == 0:
            continue
        scip[k] = r

    stats = collections.defaultdict(collections.Counter)
    core_stats = collections.defaultdict(collections.Counter)
    for l in open(os.path.join(HERE, "statements_all.jsonl"), encoding="utf-8"):
        r = json.loads(l)
        if r["p"] != "calls":
            continue
        k = (r["q"]["file"], r["q"]["line"], r["q"]["col"])
        form = "qualified" if k in qual else ("bare" if k in bare else "other")
        g = scip.get(k)
        gorig = g["origin"] if g else "none"
        stats[form][r["res"]] += 1
        stats[form]["TOTAL"] += 1
        if r["res"] == "unresolved":
            stats[form]["unresolved__scip_" + gorig] += 1
        rel = r["q"]["file"]
        if rel in core or rel.replace("/", "\\") in core:
            core_stats[form][r["res"]] += 1
            core_stats[form]["TOTAL"] += 1

    out = {}
    for form in ("qualified", "bare", "other"):
        c = stats[form]
        t = c["TOTAL"] or 1
        out[form] = {
            "total": c["TOTAL"],
            "unresolved": c["unresolved"],
            "pct_unresolved": round(100.0 * c["unresolved"] / t, 1),
            "resolved_internal": c["internal"],
            "resolved_external": c["external"],
            "unresolved_but_scip_knew_internal": c["unresolved__scip_internal"],
            "unresolved_but_scip_knew_external": c["unresolved__scip_external"],
            "unresolved_and_scip_also_blind": (c["unresolved__scip_local"]
                                               + c["unresolved__scip_none"]),
        }
    out["core_src_utils_only"] = {
        f: {"total": core_stats[f]["TOTAL"],
            "unresolved": core_stats[f]["unresolved"],
            "pct_unresolved": round(100.0 * core_stats[f]["unresolved"]
                                    / (core_stats[f]["TOTAL"] or 1), 1)}
        for f in ("qualified", "bare")}
    with open(os.path.join(HERE, "qualified_calls.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
