"""Scope statements_all.jsonl down to the x7b slice and count by predicate.

Slice = every statement in src/utils/*.py, PLUS every statement in an importer
file whose object symbol lands in src.utils.* (the inbound cross-package edges).
"""
import collections
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
CORE = "src/utils/"


def main():
    rows = [json.loads(l) for l in
            open(os.path.join(HERE, "statements_all.jsonl"), encoding="utf-8")]
    out = []
    for r in rows:
        f = r["q"]["file"]
        if f.startswith(CORE):
            r["q"]["slice"] = "core"
            out.append(r)
        elif isinstance(r["o"], str) and r["o"].startswith("src.utils."):
            r["q"]["slice"] = "inbound"
            out.append(r)
    with open(os.path.join(HERE, "statements.jsonl"), "w", encoding="utf-8") as f:
        for r in out:
            f.write(json.dumps(r) + "\n")

    def tally(rs):
        pred = collections.Counter(r["p"] for r in rs)
        res = collections.Counter(r["res"] for r in rs)
        cross = collections.Counter()
        for r in rs:
            if r["p"] in ("reads", "writes", "calls") and r["res"] == "internal":
                mod = r["o"].split(":")[0]
                fmod = r["q"]["file"][:-3].replace("/", ".")
                cross["same-module" if mod == fmod or fmod.endswith(mod)
                      else "cross-module"] += 1
        return {"n": len(rs), "by_predicate": dict(pred.most_common()),
                "by_resolution": dict(res.most_common()),
                "internal_edge_locality": dict(cross)}

    summary = {
        "slice_total": tally(out),
        "core_only": tally([r for r in out if r["q"]["slice"] == "core"]),
        "inbound_only": tally([r for r in out if r["q"]["slice"] == "inbound"]),
        "all_67_files": tally(rows),
    }
    with open(os.path.join(HERE, "statement_counts.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
