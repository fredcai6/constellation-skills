"""Amendment 3 — append the doctrine-version gate after Tommy's ruling.

Appends one gate rather than reopening g1, so no reviewed work is cascade-reset.
"""
import json

P = r"C:/Programs/constellation-skills-wt/298-300/.agent-work/300/execute.json"
OUT = r"C:/Programs/constellation-skills-wt/298-300/.agent-work/300/amend-3.json"
PYT = "python -m pytest"

gate = {
    "op": "add",
    "id": "g5-doctrine-version",
    "title": "Doctrine version: repo revision in the manifest content (Tommy's ruling)",
    "imperative": (
        "SINGLE bounded gate, appended after Tommy's 2026-08-01 ruling: \"we should also give "
        "doctrine a version so there's a little traceability... practically, it's just the repo rev "
        "number of the last doctrine edit that is sufficient for a versioning system (heck it could "
        "just be the current repo version in totality for ease).\" Fill the implementer handoff and "
        "dispatch, crew plan file under .agent-work/300/g5-implement/. SCOPE, and nothing beyond it: "
        "(1) add the repo revision to the manifest as a CONTENT field, admitted into CONTENT_KEYS -- "
        "it is a fact about canon, not about the run environment, so it must not hide in the "
        "excluded /run subtree; (2) add a dirty marker beside it, because a bare commit SHA lies "
        "about a dirty tree and this design exists precisely because commit SHAs lie about dirty "
        "trees -- shipping the stamp without the marker would be incoherent with the per-file blob "
        "OID it sits next to; (3) keep the per-file blob OID EXACTLY as it is (Tommy's ruling adds a "
        "traceability stamp, it does not replace content identity); (4) one line in "
        "docs/CHECKLIST_ENGINE_DESIGN.md explaining the two-level scheme. The determinism test must "
        "still pass unchanged: both children are worktrees at the SAME commit and are equally dirty, "
        "so the field is identical across environments -- if it is not, that is a finding, report it."
    ),
    "preconditions": [{"id": "p1", "statement": "g1 and g3 integrated; PR #324 green",
                       "check": None, "satisfied": False}],
    "postconditions": [
        {"id": "c1", "statement": "IMPLEMENTER_RESULT returned",
         "check": {"kind": "artifact", "evidence_type": "implementer-result"}, "satisfied": False},
        {"id": "c2", "statement": "the repo revision is CONTENT, not run -- admitted into "
                                  "CONTENT_KEYS and asserted present in the content projection",
         "check": {"kind": "command",
                   "command": f"{PYT} tests/test_context_manifest.py -q -k 'repo_rev or doctrine_version' --no-header"},
         "satisfied": False},
        {"id": "c3", "statement": "the cross-environment determinism acceptance test STILL passes "
                                  "unchanged -- the new field must be identical across two checkouts "
                                  "at the same commit, or it does not belong in content",
         "check": {"kind": "command", "command": f"{PYT} tests/test_context_determinism.py -q"},
         "satisfied": False},
        {"id": "c4", "statement": "full suite green and no new skip introduced (CI's skip guard uses "
                                  "an exact-triple allow-list)",
         "check": {"kind": "command",
                   "command": f"{PYT} tests/ -q --junitxml=junit-report.xml && python scripts/verify_skip_guard.py junit-report.xml && rm -f junit-report.xml"},
         "satisfied": False},
        {"id": "c5", "statement": "REVIEW_RESULT verdict is APPROVE",
         "check": {"kind": "artifact", "evidence_type": "review-result",
                   "match": {"verdict": "APPROVE"}}, "satisfied": False},
    ],
    "constraints": [
        "Do NOT replace or weaken the per-file blob OID. Tommy asked for a traceability stamp "
        "alongside it, not instead of it -- a commit SHA cannot answer 'which bytes did this agent "
        "get' for a dirty, untracked or out-of-repo file, which is the whole reason the OID exists.",
        "Do NOT reopen the design. One field plus a dirty marker plus one doc line is the whole "
        "budget; the Admiral said explicitly that anything larger goes back to Tommy rather than "
        "inflating this issue.",
        "python -m pytest, never py -m pytest. CI pins Python 3.12 (host is 3.14.3) -- no "
        "Path.read_text(newline=)/write_text(newline=). No skipTest. cwd = worktree root.",
        "Every file write pins newline='\\n'.",
    ],
    "anchors": {
        "structural": ["scripts/context_manifest.py - CONTENT_KEYS and the manifest builder",
                       "docs/CHECKLIST_ENGINE_DESIGN.md - the manifest section added by g3"],
        "capability": ["capability:doctrine-traceability - NEW, per Tommy's ruling"],
        "constraint": ["constraint:determinism-is-the-acceptance-test - the new field must not break "
                       "cross-environment byte-identity of content"],
        "decision": [
            "decision:repo-rev-is-content-not-run - the repo revision is a property of canon, not of "
            "the run environment, so it is admitted into CONTENT_KEYS rather than quarantined in "
            "/run @grade: guess - leans g5-doctrine-version - settle: the determinism test decides "
            "it; if two checkouts at the same commit disagree on the field, it belongs in /run",
            "decision:keep-blob-oid-alongside-repo-rev - the two answer different questions (which "
            "bytes vs which doctrine version) and Tommy's ruling adds the second without removing "
            "the first @grade: settled/human - leans g5-doctrine-version",
        ],
        "evidence": ["claim:deterministic-across-environments must survive the addition unchanged"],
        "confidence_flags": [
            "Tommy is separately un-gitignoring .agent-work/ in this repo. That changes the storage "
            "location's properties, NOT the row shape or the identity function -- which is itself "
            "evidence the no-case-analysis design was right, since it survives the change untouched.",
        ],
    },
    "directives": None, "child_checklist": None, "status": "pending", "status_detail": {},
    "result": None, "finding": None, "evidence": [], "rework_count": 0,
}

with open(OUT, "w", encoding="utf-8", newline="\n") as f:
    json.dump({"ops": [gate]}, f, indent=1)
    f.write("\n")
print("amend-3 written: append g5-doctrine-version")
