"""x7a — draw a spread of statements for hand-verification, each with the
literal source line it claims."""
import os, json, random
from collections import Counter, defaultdict

OUT = os.path.dirname(os.path.abspath(__file__))
REPO = r"C:\Programs\f1Brainz"
src = {}


def line_of(f, n):
    f = f.replace("/", "\\")
    if f not in src:
        src[f] = open(os.path.join(REPO, f), encoding="utf-8").read().split("\n")
    return src[f][n - 1].strip() if 0 < n <= len(src[f]) else "<n/a>"


st = [json.loads(l) for l in
      open(os.path.join(OUT, "statements.jsonl"), encoding="utf-8") if l.strip()]

by_p = defaultdict(list)
for s in st:
    by_p[s["p"]].append(s)

print(json.dumps({k: len(v) for k, v in sorted(by_p.items())}, indent=2))
print("direction:", json.dumps(dict(Counter(
    s["q"].get("direction") for s in st).most_common()), indent=2))
print("ref:", json.dumps(dict(Counter(s["ref"] for s in st).most_common())))

random.seed(7)
picks = []
# deliberate spread: every predicate, plus the cross-package and write cases
buckets = {
    "contains(local, name recovered by join)":
        [s for s in by_p["contains"] if s["q"].get("kind") == "local"],
    "contains(method in class)":
        [s for s in by_p["contains"] if s["q"].get("kind") == "method"],
    "param-of": by_p["param-of"],
    "documents": by_p["documents"],
    "calls(internal)":
        [s for s in by_p["calls"] if s["q"].get("direction") == "internal"],
    "calls(inbound cross-package)":
        [s for s in by_p["calls"] if s["q"].get("direction") == "in"],
    "calls(outbound to another package/lib)":
        [s for s in by_p["calls"] if s["q"].get("direction") == "out"],
    "writes(first binding, was SCIP Definition)":
        [s for s in by_p["writes"] if s["q"].get("binding") == "first"],
    "writes(re-binding, was SCIP ReadAccess)":
        [s for s in by_p["writes"] if s["q"].get("binding") != "first"],
    "reads(internal)":
        [s for s in by_p["reads"] if s["q"].get("direction") == "internal"],
    "reads(inbound cross-package)":
        [s for s in by_p["reads"] if s["q"].get("direction") == "in"],
    "reads(outbound)":
        [s for s in by_p["reads"] if s["q"].get("direction") == "out"],
}
for label, rows in buckets.items():
    for s in random.sample(rows, min(2, len(rows))):
        picks.append({"bucket": label, "n_in_bucket": len(rows), "stmt": s,
                      "source": line_of(s["q"]["file"], s["q"]["line"])})

json.dump(picks, open(os.path.join(OUT, "verify_sample.json"), "w",
                      encoding="utf-8"), indent=2, ensure_ascii=False)
for p in picks:
    s = p["stmt"]
    print("\n--- %s  [%d in bucket]" % (p["bucket"], p["n_in_bucket"]))
    print("  (%s) --%s--> (%s)" % (s["s"], s["p"], s["o"]))
    print("  @ %s:%d   ref=%s" % (s["q"]["file"], s["q"]["line"], s["ref"]))
    print("  SRC: %s" % p["source"])
