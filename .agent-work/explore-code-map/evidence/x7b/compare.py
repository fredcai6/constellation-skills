"""Measure the AST resolver against x1's SCIP index, joined on source position.

Join key: (file, 0-based line, 0-based start column) of the referenced
identifier. SCIP marks exactly the identifier; the AST extractor emits the
same span (for `a.b`, the span of `b`).

Only *reference* statements are scored -- reads, writes, calls, inherits.
contains/documents/param-of/imports are structural and need no resolution.
"""
import collections
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REF_PREDS = {"reads", "writes", "calls", "inherits"}


def norm_file(p):
    return p.replace("\\", "/").lower()


def load():
    scip = {}
    for ln in open(os.path.join(HERE, "scip_occ.jsonl"), encoding="utf-8"):
        r = json.loads(ln)
        k = (norm_file(r["file"]), r["line"], r["c0"])
        # a definition occurrence and a reference can share a position only
        # for the def itself; prefer the non-definition entry
        if k in scip and (scip[k]["roles"] & 0x1) == 0:
            continue
        scip[k] = r
    ast_rows = []
    for ln in open(os.path.join(HERE, "statements_all.jsonl"), encoding="utf-8"):
        ast_rows.append(json.loads(ln))
    return scip, ast_rows


def classify_wrong(mine, scip_norm):
    """Name the disagreement. Some of these are SCIP's fault, not ours --
    labelled scip-* -- and the split is the point of the measurement."""
    mmod, mmem = (mine.split(":", 1) + [""])[:2]
    smod, smem = (scip_norm.split(":", 1) + [""])[:2]
    if smem == "" and mmod == smod and mmem:
        # SCIP pointed at the MODULE, we named a member of that module.
        return "scip-module-stub (star-import: SCIP could not resolve)"
    if mmod == smod and mmem and smem:
        if mmem.split(".")[-1] == smem.split(".")[-1]:
            return "same-name-different-owner (class/attr attribution)"
        return "wrong-member-same-module"
    if mmod != smod:
        if mmem.split(".")[-1] == smem.split(".")[-1]:
            return "wrong-module-right-name (re-export chase landed short)"
        return "wrong-module-and-name"
    return "other"


def main():
    scip, rows = load()
    wrong_class = collections.Counter()
    core_prefix = "src/utils/"
    buckets = collections.Counter()
    why = collections.Counter()
    wrong_samples = []
    miss_samples = []
    notscip_samples = collections.defaultdict(list)
    per_pred = collections.defaultdict(collections.Counter)
    core_buckets = collections.Counter()

    for r in rows:
        if r["p"] not in REF_PREDS:
            continue
        f = norm_file(r["q"]["file"])
        k = (f, r["q"]["line"], r["q"]["col"])
        g = scip.get(k)
        mine, res = r["s"], r["res"]
        # the AST extractor tags an element write `c[k] = v` as a write to the
        # container with a `[]` qualifier; SCIP has no element-level symbol, so
        # compare on the container.
        obj = r["o"][:-2] if r["o"].endswith("[]") else r["o"]
        incore = r["q"]["file"].startswith(core_prefix)

        if g is None:
            b = "no-scip-symbol/" + res
            buckets[b] += 1
            if res == "unresolved":
                why["NO-SCIP:" + r.get("why", "?")] += 1
            if len(notscip_samples[res]) < 6:
                notscip_samples[res].append(r)
        else:
            go, gn = g["origin"], g["norm"]
            if go == "local":
                b = "scip-local/" + ("agree" if res == "local" else res)
            elif go == "external":
                if res == "external":
                    b = "scip-external/agree"
                elif res == "unresolved":
                    b = "scip-external/unresolved"
                    why["EXT:" + r.get("why", "?")] += 1
                else:
                    b = "scip-external/" + res
            else:  # internal -- the scored population
                if res == "internal":
                    if obj == gn:
                        b = "scip-internal/CORRECT"
                    else:
                        b = "scip-internal/WRONG"
                        wrong_class[classify_wrong(obj, gn)] += 1
                        if len(wrong_samples) < 400:
                            wrong_samples.append({"mine": obj, "scip": gn,
                                                  "at": r["q"], "p": r["p"],
                                                  "class": classify_wrong(obj, gn)})
                elif res == "unresolved":
                    b = "scip-internal/UNRESOLVED"
                    why["INT:" + r.get("why", "?")] += 1
                    if len(miss_samples) < 400:
                        miss_samples.append({"scip": gn, "at": r["q"],
                                             "why": r.get("why"), "p": r["p"]})
                elif res == "local":
                    b = "scip-internal/said-local"
                    if len(miss_samples) < 400:
                        miss_samples.append({"scip": gn, "at": r["q"],
                                             "why": "said-local", "p": r["p"]})
                else:
                    b = "scip-internal/" + res
            buckets[b] += 1
        per_pred[r["p"]][b] += 1
        if incore:
            core_buckets[b] += 1

    tot_int = sum(v for k, v in buckets.items() if k.startswith("scip-internal/"))
    correct = buckets["scip-internal/CORRECT"]
    wrong = buckets["scip-internal/WRONG"]
    unres = buckets["scip-internal/UNRESOLVED"]
    saidlocal = buckets["scip-internal/said-local"]
    other = tot_int - correct - wrong - unres - saidlocal

    out = {
        "scored_population_scip_internal": tot_int,
        "correct": correct, "wrong": wrong, "unresolved": unres,
        "said_local": saidlocal, "other": other,
        "pct_correct": round(100.0 * correct / tot_int, 1) if tot_int else None,
        "pct_wrong": round(100.0 * wrong / tot_int, 1) if tot_int else None,
        "pct_unresolved": round(100.0 * unres / tot_int, 1) if tot_int else None,
        "pct_said_local": round(100.0 * saidlocal / tot_int, 1) if tot_int else None,
        "all_buckets": dict(buckets.most_common()),
        "core_only_buckets": dict(core_buckets.most_common()),
        "failure_classes": dict(why.most_common()),
        "wrong_classes": dict(wrong_class.most_common()),
        "by_predicate": {k: dict(v.most_common(8)) for k, v in per_pred.items()},
    }
    with open(os.path.join(HERE, "accuracy.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    with open(os.path.join(HERE, "wrong_samples.json"), "w", encoding="utf-8") as f:
        json.dump({"wrong": wrong_samples[:200], "missed": miss_samples[:200],
                   "no_scip": {k: v for k, v in notscip_samples.items()}},
                  f, indent=2)
    print(json.dumps({k: v for k, v in out.items()
                      if k not in ("by_predicate",)}, indent=2))


if __name__ == "__main__":
    main()
