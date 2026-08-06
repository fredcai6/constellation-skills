"""x7a diagnostic — why writes are scarce and what fails to join."""
import os, json
from collections import Counter

OUT = os.path.dirname(os.path.abspath(__file__))
ROLE_DEF, ROLE_READ = 0x1, 0x8


def load(n):
    with open(os.path.join(OUT, n), encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


occ = load("scip_occ.jsonl")
ast_rows = load("ast_ctx.jsonl")
idx = {}
for r in ast_rows:
    idx.setdefault((r["file"], r["line"], r["bcol"]), []).append(r)

# --- A. do SCIP *Definition* occurrences land on AST store nodes?
defctx = Counter()
def_store_samples = []
for o in occ:
    if not (o["roles"] & ROLE_DEF):
        continue
    hits = idx.get((o["file"], o["line"] + 1, o["col"]), [])
    ctxs = {x["ctx"] for x in hits}
    key = "+".join(sorted(ctxs)) or "<no ast node>"
    defctx[(o["kind"], key)] += 1
    if "store" in ctxs and len(def_store_samples) < 8:
        def_store_samples.append({"file": o["file"], "line": o["line"] + 1,
                                  "sym": o["symbol"], "kind": o["kind"],
                                  "name": hits[0]["name"]})

# --- B. what are the unjoined ReadAccess refs?
unjoined = Counter()
unjoined_samples = []
for o in occ:
    if (o["roles"] & ROLE_DEF) or o["kind"] == "method":
        continue
    if not (o["roles"] & ROLE_READ):
        continue
    hits = idx.get((o["file"], o["line"] + 1, o["col"]), [])
    if any(x["ctx"] in ("store", "del", "augstore", "load") for x in hits):
        continue
    near = idx.get((o["file"], o["line"] + 1, o["col"]), [])
    unjoined[(o["kind"], "+".join(sorted({x["ctx"] for x in near})) or "<none>")] += 1
    if len(unjoined_samples) < 25:
        unjoined_samples.append({"file": o["file"], "line": o["line"] + 1,
                                 "col": o["col"], "kind": o["kind"],
                                 "sym": o["symbol"][-70:],
                                 "ast_here": [x["ctx"] + ":" + x["name"] for x in near]})

out = {
    "A_definition_occurrences_by_ast_ctx":
        {"%s | %s" % k: v for k, v in defctx.most_common()},
    "A_samples": def_store_samples,
    "B_unjoined_readaccess": {"%s | %s" % k: v for k, v in unjoined.most_common()},
    "B_samples": unjoined_samples,
}
json.dump(out, open(os.path.join(OUT, "diag.json"), "w", encoding="utf-8"),
          indent=2)
print(json.dumps(out, indent=2)[:6000])
