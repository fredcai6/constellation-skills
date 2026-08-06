"""Sanity-check the position join: print every SCIP occurrence on one source
line next to the exact substring its column range covers."""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = r"C:\Programs\f1Brainz"


def main(relfile, lineno):
    ln0 = int(lineno) - 1
    key = relfile.replace("/", "\\").lower()
    src = open(os.path.join(ROOT, relfile.replace("/", os.sep)),
               encoding="utf-8").read().splitlines()
    print("SRC | %s" % src[ln0])
    print()
    for l in open(os.path.join(HERE, "scip_occ.jsonl"), encoding="utf-8"):
        r = json.loads(l)
        if r["file"].lower() != key or r["line"] != ln0:
            continue
        text = src[ln0][r["c0"]:r["c1"]]
        print("SCIP c%-3d-%-3d %-22r roles=%-3d %s"
              % (r["c0"], r["c1"], text, r["roles"], r["symbol"][:100]))
    print()
    for l in open(os.path.join(HERE, "statements_all.jsonl"), encoding="utf-8"):
        r = json.loads(l)
        if r["q"]["file"].lower() != relfile.lower() or r["q"]["line"] != ln0:
            continue
        print("AST  c%-3d      %-8s %-40s [%s]"
              % (r["q"]["col"], r["p"], r["o"][:40], r["res"]))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
