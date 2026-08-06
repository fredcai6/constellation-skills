"""Print a deliberately diverse sample of statements with their source lines,
for manual verification. Selection is by predicate + resolution class so the
sample covers the easy and the hard cases, not just the easy ones."""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = r"C:\Programs\f1Brainz"
_src = {}


def line_at(f, ln):
    p = os.path.join(ROOT, f.replace("/", os.sep))
    if p not in _src:
        _src[p] = open(p, encoding="utf-8").read().splitlines()
    return _src[p][ln] if 0 <= ln < len(_src[p]) else ""


WANT = [
    ("contains", "internal", None),
    ("documents", "literal", None),
    ("param-of", "internal", None),
    ("calls", "internal", "cross"),      # cross-module call
    ("calls", "external", None),
    ("calls", "unresolved", None),
    ("reads", "internal", "cross"),
    ("writes", "internal", None),
    ("reads", "local", None),
    ("imports", "internal", None),
    ("inherits", None, None),
    ("writes", "unresolved", None),
]


def main():
    rows = [json.loads(l) for l in
            open(os.path.join(HERE, "statements.jsonl"), encoding="utf-8")]
    picked = []
    used = set()
    for p, res, flag in WANT:
        for r in rows:
            if r["p"] != p:
                continue
            if res and r["res"] != res:
                continue
            if flag == "cross":
                mod = r["o"].split(":")[0]
                fmod = r["q"]["file"][:-3].replace("/", ".")
                if mod == fmod or not mod.startswith("src."):
                    continue
            k = (r["q"]["file"], r["q"]["line"], r["p"])
            if k in used:
                continue
            used.add(k)
            picked.append(r)
            break
    for i, r in enumerate(picked, 1):
        q = r["q"]
        print("%2d. %s  --%s-->  %s" % (i, r["s"], r["p"], r["o"]))
        print("    res=%-11s %s  %s:%d" % (r["res"],
                                           "why=" + r.get("why", "-"),
                                           q["file"], q["line"] + 1))
        print("    src | %s" % line_at(q["file"], q["line"]).strip()[:120])
        print("    hash=%s" % r["hash"])
    print("\ntotal hand-check sample: %d" % len(picked))


if __name__ == "__main__":
    main()
