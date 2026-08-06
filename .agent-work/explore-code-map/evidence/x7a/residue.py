"""x7a — enumerate every remaining join failure, with the source line."""
import os, json

OUT = os.path.dirname(os.path.abspath(__file__))
REPO = r"C:\Programs\f1Brainz"
ROLE_DEF, ROLE_READ = 0x1, 0x8
CTXS = ("store", "del", "augstore", "load", "import", "kwarg")


def load(n):
    with open(os.path.join(OUT, n), encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


occ = load("scip_occ.jsonl")
idx = {}
for r in load("ast_ctx.jsonl"):
    idx.setdefault((r["file"], r["line"], r["bcol"]), []).append(r)

src = {}


def line_of(f, n):
    if f not in src:
        src[f] = open(os.path.join(REPO, f), encoding="utf-8").read().split("\n")
    return src[f][n - 1].rstrip() if n <= len(src[f]) else "<eof>"


out = {"unjoined_readaccess": [], "unjoined_local_definition": []}
for o in occ:
    hits = idx.get((o["file"], o["line"] + 1, o["col"]), [])
    ctxs = [x["ctx"] for x in hits]
    if o["roles"] & ROLE_DEF:
        if o["kind"] == "local" and not any(c in ("store", "augstore") for c in ctxs):
            out["unjoined_local_definition"].append(
                {"file": o["file"], "line": o["line"] + 1, "col": o["col"],
                 "sym": o["symbol"], "ast": ctxs,
                 "src": line_of(o["file"], o["line"] + 1)})
    else:
        if o["kind"] == "method" or not (o["roles"] & ROLE_READ):
            continue
        if not any(c in CTXS for c in ctxs):
            out["unjoined_readaccess"].append(
                {"file": o["file"], "line": o["line"] + 1, "col": o["col"],
                 "kind": o["kind"], "sym": o["symbol"].split(" ", 4)[-1],
                 "ast": ctxs, "src": line_of(o["file"], o["line"] + 1)})

json.dump(out, open(os.path.join(OUT, "residue.json"), "w", encoding="utf-8"),
          indent=2)
print(json.dumps(out, indent=2, ensure_ascii=False))
