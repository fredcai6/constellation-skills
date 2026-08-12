"""Amendment 2 — apply Tommy's ruling: manifest lives under .agent-work/, no committed artifact.

Drops the contingent g2 triple and repairs the three places that referenced it. Also fixes a
correctness defect the ruling CREATES: with the committed artifact gone, the determinism acceptance
test now targets the RUN manifest, which carries a `run` subtree of legitimately-varying fields --
so "byte-identical output" is false as written and must become "byte-identical CONTENT, with /run
excluded". That exclusion is now load-bearing on the issue's single acceptance test.
"""
import json

P = r"C:/Programs/constellation-skills-wt/298-300/.agent-work/300/execute.json"
OUT = r"C:/Programs/constellation-skills-wt/298-300/.agent-work/300/amend-2.json"
PYT = "python -m pytest"

d = json.load(open(P, encoding="utf-8"))
ops = [{"op": "drop", "id": t} for t in ("g2-implement", "g2-review", "g2-integrate")]

# ---- g1-implement: single envelope, and the exclusion set is now load-bearing on acceptance
g1 = d["tasks"]["g1-implement"]
imp = g1["imperative"].replace(
    "(4) the run-local manifest, with every varying fact quarantined under a "
    "single `run` key that is the entire exclusion set;",
    "(4) the manifest, written under `.agent-work/` per Tommy's ruling, with every varying fact "
    "quarantined under a single `run` key that is the entire exclusion set. There is ONE envelope, "
    "not two - the committed per-role artifact was ruled out of #300's scope, so `rev` always "
    "resolves from the BYTES ACTUALLY DELIVERED (the working tree), never from the git object DB. "
    "The two-truth-source split is gone with the artifact that needed it;",
)
post = [dict(c) for c in g1["postconditions"]]
for c in post:
    if c["id"] == "c3":
        c["statement"] = (
            "cross-environment determinism - THE issue's acceptance test now that the committed "
            "artifact is out of scope. A clean second checkout (git worktree add at the same "
            "commit, different path, mutated LC_ALL/LANG/PYTHONHASHSEED) yields byte-identical "
            "CONTENT. Byte-identical *output* is FALSE and must not be asserted: the manifest "
            "carries a `run` subtree of legitimately-varying fields. The comparison excludes "
            "exactly one JSON pointer, `/run`, and excludes nothing else - if any other field has "
            "to be masked to make the test pass, that field is in the wrong subtree and the design "
            "is wrong, not the test. Honest limit: same OS and filesystem, so this exercises "
            "path/locale/hash ordering, not a cross-OS rebuild."
        )
    if c["id"] == "c4":
        c["statement"] = (
            "the first and only real declaration exists on the Commander spine template - with no "
            "committed artifact, this is what stops the declaration field shipping with zero users "
            "(check FAILS at HEAD today, verified)"
        )
ops.append({"op": "rescope", "id": "g1-implement", "imperative": imp, "postconditions": post,
            "constraints": g1["constraints"] + [
                "RULING (Tommy, 2026-08-01): the manifest goes under `.agent-work/`. There is NO "
                "committed per-role CONTEXT_PROJECTION.json in this issue. Its standing is a "
                "nice-to-have record - 'we shouldn't need to keep it but if it's available it's "
                "good to have' - not a load-bearing diff surface. Do not build one back in.",
            ]})

# ---- g1-integrate: g2 carried the only full-suite run before g3; restore it here
gi = d["tasks"]["g1-integrate"]
gpost = [dict(c) for c in gi["postconditions"]]
for c in gpost:
    if c["id"] == "c1":
        c["statement"] = ("the FULL suite re-runs green in the Commander's own hands - full, not a "
                          "filter, because dropped g2 carried the only full-suite check before g3")
        c["check"] = {"kind": "command", "command": f"{PYT} tests/ -q"}
ops.append({"op": "rescope", "id": "g1-integrate", "postconditions": gpost})

# ---- g3-implement: precondition no longer mentions the dropped gate
g3 = d["tasks"]["g3-implement"]
ops.append({"op": "rescope", "id": "g3-implement",
            "preconditions": [{"id": "p1",
                               "statement": "g1 integrated: identity function, context_refs "
                                            "declaration, producer, the first real declaration and "
                                            "the determinism evidence all exist and are reviewed",
                               "check": None, "satisfied": False}]})

# ---- g3-integrate: drop the committed-artifact freshness check; nothing to be fresh
g3i = d["tasks"]["g3-integrate"]
ops.append({"op": "rescope", "id": "g3-integrate",
            "postconditions": [dict(c) for c in g3i["postconditions"] if c["id"] != "c3"],
            "imperative": g3i["imperative"].replace(
                " This is the LAST gate that mutates doctrine, so the committed artifact's "
                "freshness is re-established here rather than left at the state g2 found it in.",
                " This is the LAST gate that mutates doctrine. The committed-artifact freshness "
                "check that used to close here is gone with g2 - there is no committed artifact to "
                "be stale.")})

with open(OUT, "w", encoding="utf-8", newline="\n") as f:
    json.dump({"ops": ops}, f, indent=1)
    f.write("\n")
print(f"amend-2: {len(ops)} ops -> 3 drops + 4 rescopes")
