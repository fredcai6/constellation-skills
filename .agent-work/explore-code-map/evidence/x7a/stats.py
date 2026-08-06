"""x7a — final statement census for the result write-up."""
import os, json
from collections import Counter

OUT = os.path.dirname(os.path.abspath(__file__))
st = [json.loads(l) for l in
      open(os.path.join(OUT, "statements.jsonl"), encoding="utf-8") if l.strip()]
defs = [json.loads(l) for l in
        open(os.path.join(OUT, "scip_defs.jsonl"), encoding="utf-8") if l.strip()]

pred = Counter(s["p"] for s in st)
ref = Counter(s["ref"] for s in st)
pr = Counter((s["p"], s["ref"]) for s in st)
direction = Counter((s["p"], s["q"].get("direction")) for s in st
                    if s["q"].get("direction"))

TRANSFORMER = {"method", "type"}
CONTAINER = {"parameter", "term", "local"}
kinds = Counter(d["kind"] for d in defs)

out = {
    "statements_total": len(st),
    "by_predicate": dict(pred.most_common()),
    "by_ref": dict(ref.most_common()),
    "by_predicate_and_ref": {"%s/%s" % k: v for k, v in pr.most_common()},
    "cross_package": {"%s/%s" % k: v for k, v in direction.most_common()},
    "slice_defs_by_kind": dict(kinds.most_common()),
    "slice_transformers": sum(v for k, v in kinds.items() if k in TRANSFORMER),
    "slice_containers": sum(v for k, v in kinds.items() if k in CONTAINER),
    "distinct_subjects": len({s["s"] for s in st}),
    "distinct_objects": len({s["o"] for s in st}),
    "hash_collisions": len(st) - len({s["hash"] for s in st}),
    "writes_split": dict(Counter(
        s["q"].get("binding", "re-binding") for s in st if s["p"] == "writes")),
    "reads_via": dict(Counter(
        s["q"].get("via", "direct") for s in st if s["p"] == "reads")),
}
json.dump(out, open(os.path.join(OUT, "stats.json"), "w", encoding="utf-8"),
          indent=2)
print(json.dumps(out, indent=2))
