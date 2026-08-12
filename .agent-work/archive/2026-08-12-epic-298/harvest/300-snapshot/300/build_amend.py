import json

P = r"C:/Programs/constellation-skills-wt/298-300/.agent-work/300/execute.json"
OUT = r"C:/Programs/constellation-skills-wt/298-300/.agent-work/300/amend-1.json"

d = json.load(open(P, encoding="utf-8"))
g = d["tasks"]["g1-implement"]

cons = list(g["constraints"]) + [
    "INTERPRETER: CI pins python-version 3.12 (.github/workflows/ci.yml:34) while this host runs "
    "3.14.3. Every test and script here must run green on 3.12. Do NOT use "
    "Path.read_text(newline=) or Path.write_text(newline=) - the newline kwarg on those is 3.13+. "
    "Use open(..., newline=...) instead. A sibling issue in this same epic shipped a red CI on "
    "exactly this defect, so this is a live trap, not a hypothetical.",
    "GITATTRIBUTES: the in-process identity function equals git's blob OID only because "
    ".gitattributes is `* text=auto` with no exemption. If any path is ever marked -text or "
    "binary, git stops LF-normalising it and the in-process hash silently diverges from "
    "git hash-object for that path. c7 pins the invariant; do not remove it.",
]

post = list(g["postconditions"])
for c in post:
    if c["id"] == "c6":
        c["statement"] = (
            "no filesystem enumeration, no unpinned text write, and no 3.13+-only API in the new "
            "producer - the three constraints the mission frame and CI call load-bearing are "
            "mechanically checked, not merely asserted in a constraints array"
        )
        c["check"]["command"] = (
            "python -m pytest tests/test_context_manifest.py -q "
            "-k 'no_globs or newline_pinned or py312_compatible' --no-header"
        )

post.append({
    "id": "c7",
    "statement": (
        "INVARIANT - no path is exempted from git LF normalisation. The identity function equals "
        "git hash-object ONLY while .gitattributes carries no -text/binary rule; a future "
        "exemption would make the two silently diverge for that path. This check passes today and "
        "fails the moment an exemption is added - both directions verified before freezing."
    ),
    "check": {
        "kind": "command",
        "command": (
            "test -f .gitattributes && "
            "! grep -nE '(^|[[:space:]])(-text|binary)([[:space:]]|$)' .gitattributes"
        ),
    },
    "satisfied": False,
})

delta = {"ops": [{
    "op": "rescope",
    "id": "g1-implement",
    "constraints": cons,
    "postconditions": post,
}]}

with open(OUT, "w", encoding="utf-8", newline="\n") as f:
    json.dump(delta, f, indent=1)
    f.write("\n")
print(f"delta written: rescope g1-implement -> {len(cons)} constraints, {len(post)} postconditions")
