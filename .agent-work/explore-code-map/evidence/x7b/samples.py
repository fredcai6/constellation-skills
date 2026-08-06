"""Print source-level samples of each agreement/disagreement bucket."""
import collections
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = r"C:\Programs\f1Brainz"
REF = {"reads", "writes", "calls", "inherits"}
_src = {}


def line_at(f, ln):
    p = os.path.join(ROOT, f.replace("/", os.sep))
    if p not in _src:
        _src[p] = open(p, encoding="utf-8").read().splitlines()
    return _src[p][ln] if ln < len(_src[p]) else ""


def build():
    scip = {}
    for ln in open(os.path.join(HERE, "scip_occ.jsonl"), encoding="utf-8"):
        r = json.loads(ln)
        k = (r["file"].replace("\\", "/").lower(), r["line"], r["c0"])
        if k in scip and (scip[k]["roles"] & 1) == 0:
            continue
        scip[k] = r
    rows = [json.loads(l) for l in
            open(os.path.join(HERE, "statements_all.jsonl"), encoding="utf-8")]
    buck = collections.defaultdict(list)
    for r in rows:
        if r["p"] not in REF:
            continue
        k = (r["q"]["file"].lower(), r["q"]["line"], r["q"]["col"])
        g = scip.get(k)
        if g is None:
            b = "noscip/" + r["res"]
        elif g["origin"] == "local":
            b = "local/" + ("agree" if r["res"] == "local" else r["res"])
        elif g["origin"] == "external":
            b = "ext/" + r["res"]
        else:
            _o = r["o"][:-2] if r["o"].endswith("[]") else r["o"]
            ok = r["res"] == "internal" and _o == g["norm"]
            b = "int/" + ("CORRECT" if ok else r["res"].upper())
        buck[b].append((r, g))
    return buck


def main():
    buck = build()
    which = sys.argv[1:] or sorted(buck, key=lambda k: -len(buck[k]))
    for b in which:
        rs = buck.get(b, [])
        print("=== %s  (n=%d) ===" % (b, len(rs)))
        for r, g in rs[:8]:
            print("  %s:%d  p=%s" % (r["q"]["file"], r["q"]["line"] + 1, r["p"]))
            print("     mine = %s   [%s%s]" % (r["o"][:80], r["res"],
                                               "/" + r.get("why", "") if r.get("why") else ""))
            print("     scip = %s" % (g["norm"][:80] if g else "(none)"))
            print("     src  | %s" % line_at(r["q"]["file"], r["q"]["line"]).strip()[:110])
        print()


if __name__ == "__main__":
    main()
