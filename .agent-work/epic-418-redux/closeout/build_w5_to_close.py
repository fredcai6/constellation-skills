"""Build the w5-to-close boundary packet.

COPIED from .agent-work/epic-418-redux/closeout/build_boundary_reference.py (which built
close-to-w5 and passed G2) and re-pointed. NOT authored fresh: the last pre-staged boundary
skeleton in this epic reproduced the exact shape error it was built to prevent (census 12).

Contract gotchas already paid for and preserved here:
  * entry_conditions must be an ARRAY
  * a stop/later_only disposition maps to amend_forecast_or_parked
  * record_evidence_only requires issue_created=false
  * a fixed-boundary change requires applicable=false  (we do not change one, so applicable=true)
"""
import copy
import json
import pathlib

ROOT = pathlib.Path(r"C:/Programs/constellation-skills/.agent-work/epic-418-redux/transitions")
SRC = ROOT / "close-to-w5"
DST = ROOT / "w5-to-close"
DST.mkdir(parents=True, exist_ok=True)

src_in = json.load(open(SRC / "REPLAN_INPUT.json", encoding="utf-8"))
src_res = json.load(open(SRC / "REPLAN_RESULT.json", encoding="utf-8"))

# ------------------------------------------------------------------ INPUT
inp = copy.deepcopy(src_in)

inp["completed_outcomes"] = [
    {
        "item": "wave-5",
        "outcome": "delivered",
        "evidence": (
            "Five PRs merged and verified MERGED on the forge, never by ancestry: "
            "#511 39fb542a (#507, #370); #509 4bde569e (#496, #411); #513 c045ed2f (#458); "
            "#516 f9945286 (#439, #446, #468, #484, #501, #506); #514 b2f33603 (#474, #475, "
            "#476, #427, #479, #480, #493); #517 c9f894f4 (#477). Main c9f894f4 green: "
            "1943 passed, 2 skipped, 884 subtests, real exit 0."
        ),
    }
]

inp["wave_evidence"] = [
    {
        "claim": "Wave 5 landed in full and main is green.",
        "expected": "Suite green on the final merged main, not per-PR, with the delta attributed.",
        "observed": (
            "1943 passed, 2 skipped, 884 subtests, real exit 0 at c9f894f4. Collected 1922 -> 1945 "
            "(+23) and subtests 872 -> 884 (+12), attributed from the squash commits rather than the "
            "PR bodies: #514 +10 tests / 0 subTest loops, #517 +13 tests / 2 subTest loops. Zero "
            "unexplained; nothing silently stopped being collected."
        ),
        "source": "FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests, redirected not piped, exit read directly.",
    },
    {
        "claim": "The post-merge count was predicted before the merge and matched exactly.",
        "expected": "A prediction derived from a measured fork point, not from remembered per-PR deltas.",
        "observed": (
            "Fork point ea854471 measured at 1869 collected in a throwaway detached worktree created "
            "and removed in one command; main 1898; crew-1 branch 1893. Predicted 1898 + 24 = 1922. "
            "Measured after merging #516: 1922 collected, 1920 passed + 2 skipped. Exact."
        ),
        "source": "pytest --collect-only at three revisions; git worktree add --detach / remove.",
    },
    {
        "claim": "#506 is fixed and the close gate it blocked can now be exercised honestly.",
        "expected": "The installed verifier carries the fix, checked against the repo blob rather than the installer's own report.",
        "observed": (
            "All three installed copies of scripts/verify_iterative_role_artifacts.py transitioned "
            "dabb48ff -> fc1b50f9 (constellation-admiral, -commander, -explorer) after a --force "
            "reinstall. A transition, not an equality: the originally-planned step hashed "
            "verify_replan.py, which is byte-identical in all three places and untouched by this wave."
        ),
        "source": "git hash-object on each installed copy vs git rev-parse HEAD:<path>, before and after reinstall.",
    },
    {
        "claim": "The engine was changed twice underneath this live run and the run survived both.",
        "expected": "The Admiral's own spine still resolves on the merged engine, with no hand-repair.",
        "observed": (
            "current against .agent-work/epic-418-redux/spine.json exited 0 after each of #514 and "
            "#517, lease active, ACTIVE execute unchanged, git status on the spine directory 0 before "
            "and after. #517 was additionally smoke-tested from its branch BEFORE merging, producing "
            "byte-identical output to the then-current main engine."
        ),
        "source": "python scripts/checklist_engine.py --file .agent-work/epic-418-redux/spine.json current.",
    },
]

inp["discrepancies"] = [
    {
        "id": "d1",
        "observed": (
            "Two issues from the range the user asked wave 5 to cover, #477 and #478, were never "
            "written into any launch order and so were never worked. Found by auditing issue states "
            "before the close, not by any gate. #477 was dispatched late and merged (#517); #478 was "
            "carried deliberately, with the disposition posted on the issue."
        ),
        "classification": "evidence_only",
        "issue_created": False,
    },
    {
        "id": "d2",
        "observed": (
            "Three of PR #516's test failures were green in the worktree and red only on the CI "
            "runner: two prescriptive-episode guard rejections and one assertion comparing Windows "
            "paths as strings across an 8.3 short-name boundary (RUNNER~1 vs runneradmin). Every "
            "verification discipline this wave built runs in the worktree and none of it can see a "
            "second environment. The runner also reports a different pass/skip split (1918/1) from "
            "this box (1896/2) on the same tree."
        ),
        "classification": "evidence_only",
        "issue_created": False,
    },
    {
        "id": "d3",
        "observed": (
            "Crew 1's own spine carried the pre-fix archive.c2b and could not close its final gate: "
            "the crew that repaired the always-red reachability check was blocked by the copy of it "
            "instantiated before its own fix. Resolved by an Admiral waiver granted pre-emptively, "
            "with the PR opened first so the substance was real, and recorded as evidence-only."
        ),
        "classification": "evidence_only",
        "issue_created": False,
    },
]

inp["open_current_wave_issue_ids"] = []
inp["unlaunched_items"] = []
inp["repo_state"] = {
    "branch": "main",
    "head": "c9f894f4",
}

# ----------------------------------------------------------------- RESULT
res = copy.deepcopy(src_res)

res["decision"] = "stop"
res["applicable"] = True
res["escalation"] = None

res["discrepancy_dispositions"] = [
    {"id": "d1", "action": "record_evidence_only", "issue_created": False,
     "rationale": "#477 shipped, #478 carried with its disposition on the issue; both recorded in the run log. No new issue."},
    {"id": "d2", "action": "record_evidence_only", "issue_created": False,
     "rationale": "Carried to the lessons audit as a verification-coverage observation; the CI/worktree environment gap is not a code defect to file."},
    {"id": "d3", "action": "record_evidence_only", "issue_created": False,
     "rationale": "The underlying defect is #439/#484/#446, all merged and closed by #516. The waiver records a defective instantiated copy, not an open defect."},
]

res["current_wave"] = {
    "id": "wave-5",
    "status": "complete",
    "exit_criteria_met": (
        "All five wave-5 PRs merged and verified MERGED on the forge; main green at c9f894f4 with "
        "1943 passed / 2 skipped / 884 subtests, real exit 0; the +23 test and +12 subtest delta "
        "attributed to #514 (+10) and #517 (+13/+12) from the squash commits."
    ),
}

res["revised_forecast"] = []
res["unlaunched_dispositions"] = []

res["material_changes"] = [
    {"change": "Wave 5 is the final wave; the epic proceeds to closeout and does not launch again.",
     "why": "The user authorised one last wave and it is complete. F (#424) becomes its own effort."},
    {"change": "#478 is carried out of this epic unworked, with its disposition recorded on the issue.",
     "why": "It relocates directories this run's own closeout tooling and five live work areas sit in, with no forcing function."},
]

res["wave_review_comment"] = (
    "Wave 5 closed. Five PRs merged (#511, #509, #513, #516, #514, #517), main green at c9f894f4: "
    "1943 passed, 2 skipped, 884 subtests, real exit 0, with the whole +23 delta attributed. "
    "The post-merge count was predicted from a measured fork point before the merge and matched "
    "exactly (1922). Two gates blocked and were repaired rather than waived (#506's stop-transition "
    "test, and the gh stub's falsified refusal promise), and the one gate that genuinely could not be "
    "closed -- crew 1's own pre-fix archive.c2b -- was waived on Admiral authority with the PR opened "
    "first, never by editing the verdict. Exit: stop. Next step is closeout, not another wave."
)

res["revised_epic_body"] = (
    "Epic #418 -- post-phase-1 consolidation. Wave 5, the final wave, is complete: 21 issues "
    "dispatched across five crews plus one late bounded dispatch, six PRs merged, main green at "
    "c9f894f4 (1943 passed / 2 skipped / 884 subtests). The epic now proceeds to closeout: lessons "
    "audit, cartographer reconcile, harvest-before-sweep, repo hygiene, epic summary and user "
    "acceptance. F (#424) is explicitly out of scope and becomes its own effort, to be built from the "
    ".proto-exc9-mcp-front-door prototype. Carried out unworked and recorded on the issue: #478."
)

json.dump(inp, open(DST / "REPLAN_INPUT.json", "w", encoding="utf-8"), indent=2)
json.dump(res, open(DST / "REPLAN_RESULT.json", "w", encoding="utf-8"), indent=2)
print("wrote", DST)
print("decision:", res["decision"], "applicable:", res["applicable"])
