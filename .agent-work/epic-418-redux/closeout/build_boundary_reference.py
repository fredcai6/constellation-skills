import copy
import json
import pathlib

ROOT = pathlib.Path(r"C:/Programs/constellation-skills/.agent-work/epic-418-redux/transitions")
SRC = ROOT / "w4-to-close"
DST = ROOT / "close-to-w5"
DST.mkdir(parents=True, exist_ok=True)

src_in = json.load(open(SRC / "REPLAN_INPUT.json", encoding="utf-8"))
src_res = json.load(open(SRC / "REPLAN_RESULT.json", encoding="utf-8"))

# ---------------------------------------------------------------- INPUT
inp = copy.deepcopy(src_in)

# current_wave stays wave 4 -- it is the last LAUNCHED wave, and the proven
# pattern (w3-to-w4) holds current_wave across the boundary. Wave 5 rides in
# the forecast, which is exactly what `forecast_is_provisional: true` means.

inp["wave_evidence"] = [
    {
        "claim": "Wave 4 landed and main is green.",
        "expected": "Suite green on the final merged main, not per-PR.",
        "observed": "1867 passed, 2 skipped, 829 subtests, real exit 0, re-run by the Admiral on the merged tree.",
        "source": "FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests, unpiped, exit code read directly.",
    },
    {
        "claim": "The epic scores 1 of 5 done-conditions met, 1 substantially, 1 partial, 2 untouched.",
        "expected": "A score derived from REVISED_SPEC.md's own five-condition table, not from the wave list.",
        "observed": (
            "DC3 met (#422 merged, #436 observed refusing a real new template). DC2 substantially met "
            "(echo fixed, `directives` renders, completeness test now fails by default on a new populated "
            "field -- but the per-field written rulings never shipped and _EXCLUDED_FIELDS carries 13 "
            "entries with no reasons). DC1 mechanism done, shipping not: every governor reading this epic "
            "took came from an untracked .claude/settings.local.json. DC4 and DC5 untouched -- E and F "
            "never ran."
        ),
        "source": (
            "REVISED_SPEC.md lines 804-824 read directly; gh issue view on each named issue; "
            "grep of _EXCLUDED_FIELDS in tests/test_checklist_engine.py."
        ),
    },
    {
        "claim": "The backlog grew during the epic, and E structurally cannot run while the epic runs.",
        "expected": "A count from the forge, not from a document.",
        "observed": (
            "156 open today against 117 when the spec was written; 24 closed since the redux began and "
            "more filed than closed. E (#423) is specified to run on 'what survives the redux', so its "
            "input is undefined until the redux stops."
        ),
        "source": "gh issue list --state open --limit 500 | length; gh issue list --state closed --search 'closed:>=2026-08-07'.",
    },
]

inp["discrepancies"] = [
    {
        "id": "D4",
        "signal": (
            "The w4-to-close boundary exited `stop` on the reading that no further wave was authorized. "
            "That reading was correct when made and is now false: the human, at the checkpoint, authorized "
            "one more wave and then widened it."
        ),
        "classification": "invalidates_forecast_or_decomposition",
        "affects": "The forecast, which said close; and the decomposition, which had no wave 5 in it.",
        "evidence": (
            "ADMIRAL_LOG 2026-08-08 CHECKPOINT entry. The `stop` exit itself stands and is not rewritten -- "
            "it is logged at ADMIRAL_LOG.md:3242 as `- TRANSITION | boundary=w4-to-close | decision=stop | "
            "verified`, and this is a NEW boundary rather than an edit to that one."
        ),
        "reason": (
            "The input changed, not the reasoning. Recording this as a fresh material_exception keeps the "
            "one-exit-per-boundary invariant intact; editing w4-to-close would have been a doctored verdict."
        ),
    },
    {
        "id": "D5",
        "signal": (
            "Three duplicate collapses were found in the open backlog that no prior sweep had caught, "
            "because all three are invisible from the titles and only show in the bodies."
        ),
        "classification": "later_only",
        "affects": "E (#423), whose whole job is consolidation, and the honest reading of the open count.",
        "evidence": (
            "#501 and #468 name the same function and line (_installed_skills_root, "
            "verify_iterative_role_artifacts.py:53). #439, #484 and #446 are all the same postcondition, "
            "archive.c2b. #507, #370 and #413 are one defect filed across three epics. Verified by reading "
            "each body, not each title."
        ),
        "reason": (
            "Wave 5 retires all eight as a side effect of fixing three defects, which is the "
            "retire-what-you-subsume obligation working. The general lesson -- that a title-level sweep "
            "cannot find a duplicate -- belongs to E, not to this wave."
        ),
    },
]

inp["unlaunched_items"] = [
    {"id": "U-f-424", "kind": "forecast"},
    {"id": "U-c-421", "kind": "forecast"},
    {"id": "U-e-423", "kind": "forecast"},
    {"id": "U-w5-c1-bookend-gates", "kind": "forecast"},
    {"id": "U-w5-c2-readiness", "kind": "forecast"},
    {"id": "U-w5-c3-addressing", "kind": "forecast"},
    {"id": "U-w5-c4-engine", "kind": "forecast"},
    {"id": "U-w5-c5-docs", "kind": "forecast"},
]

inp["repo_state"] = {
    "anchors": [
        "scripts/verify_iterative_role_artifacts.py",
        "scripts/checklist_engine.py",
        "skills/commander/templates/COMMANDER_SPINE.template.json",
        "scripts/install_constellation.py",
        "docs/CHECKLIST_SCHEMA.md",
    ],
    "map_status": (
        "docs/architecture present; cartographer reconcile is a closeout substep and has not run for "
        "waves 4-5. Wave 5 touches the launch/archive gate surface and the engine's Task shape, both of "
        "which the map covers."
    ),
}

with open(DST / "REPLAN_INPUT.json", "w", encoding="utf-8", newline="\n") as fh:
    json.dump(inp, fh, indent=2)
    fh.write("\n")

# ---------------------------------------------------------------- RESULT
res = copy.deepcopy(src_res)
res["decision"] = "advance"
res["applicable"] = True
res["escalation"] = None

res["criteria_assessment"] = {
    "wave_exit": (
        "Wave 4 exited at w4-to-close and that exit stands: #467 merged (PR #505, c875ee23), #431 verified "
        "dissolved and closed, suite green on the merged tree. This boundary does not re-assess wave 4; it "
        "records a scope change that arrived after wave 4 had already exited."
    ),
    "epic_done": (
        "Not complete, and now scored rather than asserted: DC3 met, DC2 substantially met, DC1 mechanism "
        "done but shipping not, DC4 and DC5 untouched. Wave 5 targets DC1 (via #458) and DC2 (via #475) and "
        "clears the gate machinery that F will run on. F (#424), C (#421) and E (#423) remain unlaunched and "
        "are, by the human's decision at this checkpoint, a separate effort after this epic closes."
    ),
    "good_enough": (
        "Preserved. The three duplicate collapses that justify wave 5's issue count were verified against "
        "issue BODIES, not titles -- the titles do not show the collapse in any of the three cases. The "
        "done-condition score was read out of REVISED_SPEC.md's own table rather than inferred from the wave "
        "list, which would have flattered the run."
    ),
}

res["discrepancy_dispositions"] = [
    {
        "id": "D4",
        "action": "revise_plan",
        "reason": (
            "The plan gains a wave 5 it did not have. Five dispatches, 21 issues, ~8 real fixes. The "
            "epic's close moves behind it."
        ),
        "issue_created": False,
    },
    {
        "id": "D5",
        "action": "amend_forecast_or_parked",
        "reason": (
            "The eight duplicate-collapsed issues are retired inside wave 5's three fixes. The general "
            "finding -- a title-level sweep cannot detect a duplicate -- is parked for E."
        ),
        "issue_created": False,
    },
]

res["unlaunched_dispositions"] = [
    {"id": "U-f-424", "action": "defer", "reason": "Its own effort after this epic closes, by the human's decision at this checkpoint. A2 has settled the verb contract it needs."},
    {"id": "U-c-421", "action": "defer", "reason": "Follows F, unchanged. Wave 5 does not touch it."},
    {"id": "U-e-423", "action": "defer", "reason": "Its input is 'what survives the redux', which is undefined until the redux stops. Wave 5 is the last thing that changes that input."},
    {"id": "U-w5-c1-bookend-gates", "action": "keep", "reason": "Launching now as crew 1. #506, #501+#468, #439+#484+#446 -- six issues, three fixes, all in the gates that open and close a run."},
    {"id": "U-w5-c2-readiness", "action": "keep", "reason": "Launching now as crew 2. #458, workstream R -- the one issue that moves a done-condition."},
    {"id": "U-w5-c3-addressing", "action": "keep", "reason": "Launching now as crew 3. #507+#370+#413 -- one defect, three filings, three epics."},
    {"id": "U-w5-c4-engine", "action": "keep", "reason": "Launching now as crew 4. Nine issues inside checklist_engine.py, kept as ONE crew because two writers in one file in one wave is against standing doctrine."},
    {"id": "U-w5-c5-docs", "action": "keep", "reason": "Launching now as crew 5. #496+#411, docs only, deliberately carved out so it cannot collide with crew 4."},
]

res["material_changes"] = [
    {
        "surface": "wave_forecast",
        "before": "The forecast after w4-to-close was: close the epic, then cut F, C and E as separate efforts.",
        "after": "A wave 5 is inserted before the close -- five dispatches, 21 issues -- and F, C and E stay deferred to separate efforts after it.",
        "reason": (
            "Human scope decision at the wave-4 checkpoint, given the done-condition score. The epic buys "
            "DC1 and DC2 outright and hands F a launch/archive gate surface that works, rather than handing "
            "it three broken gates and a waiver."
        ),
    },
    {
        "surface": "current_wave.exit_criteria",
        "before": "Wave 4's exit criteria, all met.",
        "after": (
            "Wave 5's exit criteria: 21 named issues closed against verified fixes; #506 fixed so this "
            "epic's own execute gate closes without a waiver; #458 landed so DC1's shipping clause is "
            "answerable; and every duplicate collapse confirmed against the issue body before its issue "
            "is closed."
        ),
        "reason": "The wave changed; the epic's fixed boundaries did not. No entry here touches a fixed boundary, so applicable stays true.",
    },
]

res["revised_forecast"] = [
    {
        "outcome": (
            "Crew 1 -- the bookend gates. #506 (execute.c3 demands a launch authorization at a boundary "
            "that exits stop), #501+#468 (the launch verifier cannot run as its own spine instructs), "
            "#439+#484+#446 (archive.c2b ships an unsubstituted <branch> placeholder AND accepts only an "
            "open PR, so the success case forces --force). Six issues, three fixes."
        ),
        "entry_conditions": "Main green at c875ee23; a provisioned worktree; no other crew writing verify_iterative_role_artifacts.py or COMMANDER_SPINE.template.json.",
        "why_likely": (
            "All three are small and all three are proven by construction rather than inferred -- #506 was "
            "walked down three refusals to the one that cannot be fixed, and #484 shows the same command "
            "returning false and true one substitution apart."
        ),
    },
    {
        "outcome": (
            "Crew 2 -- #458, workstream R. A command that answers 'is this project constellation ready' "
            "and refuses with a named reason. First job is a discrepancy, not code: workstream R and "
            "#458's body specify DIFFERENT deliverables."
        ),
        "entry_conditions": "The Admiral's standing ruling on which done-condition governs, overridable by the Commander with a stated reason.",
        "why_likely": (
            "install_constellation.py already reports hook-wiring state, so most of the check exists. The "
            "risk is scope, not difficulty: 'what else belongs on the list' is open by the issue's own text."
        ),
    },
    {
        "outcome": (
            "Crew 3 -- crew addressing. #507+#370+#413: a handoff names an ephemeral agent instance, so "
            "every delivery after a Commander relaunch misroutes, bidirectionally and unrecoverably. Fix "
            "is address-the-job-not-the-agent."
        ),
        "entry_conditions": "None beyond a worktree; it touches handoff templates, which no other crew in this wave writes.",
        "why_likely": (
            "The mechanism is understood and the fix is a template change. The acceptance test is the hard "
            "part -- it needs a Commander relaunched mid-gate, which is exactly what this wave will be doing "
            "anyway."
        ),
    },
    {
        "outcome": (
            "Crew 4 -- checklist_engine.py internals, nine issues: #474 #475 #476 (the Task shape is written "
            "in three places and reconciled nowhere), #479 #480 (render/record branches), #427 #503 "
            "(validation blind spots), #493 #495 (line endings). #475 is the one that moves DC2 to met."
        ),
        "entry_conditions": "Sole writer on scripts/checklist_engine.py and tests/test_checklist_engine.py for the wave.",
        "why_likely": "Each is small and independently testable. The risk is nine changes in one file, which is why they are one crew and not two.",
    },
    {
        "outcome": "Crew 5 -- docs only. #496 (CREW_CONTEXT's newline rule doesn't name save()'s byte-faithful exception) and #411 (_shared listed as a 20th role).",
        "entry_conditions": "None; deliberately carved out to be collision-free with crew 4.",
        "why_likely": "Both are single-sentence corrections with a named authority to check against.",
    },
    {
        "outcome": (
            "After wave 5: closeout, then F (#424) as its own effort with its own spec and latitude "
            "contract, then C (#421), then E (#423) against a settled input."
        ),
        "entry_conditions": "Wave 5 merged and this epic closed.",
        "why_likely": "F's measurement design is contested by its own critic findings and needs a spec, not a launch order.",
    },
]

res["revised_uncertainty"] = [
    {
        "unknown": "Whether crew 1 actually lands #506, which is what lets this epic close without a waiver against the human's name.",
        "affects": "The epic's own close. This is a single point of failure and it is accepted knowingly.",
        "settle_by": "Crew 1's return.",
        "current_evidence": "The defect is proven by construction and the cheapest of three named fixes is a conditional on decision == stop.",
        "next_probe": "If crew 1 misses, fall back to the waiver -- and do NOT let crew 1 report it done because the fallback exists.",
    },
    {
        "unknown": "Whether #458 should deliver a readiness CHECK or an actually-shipped gauge reading on a fresh clone.",
        "affects": "Whether DC1's shipping clause closes or merely becomes visible.",
        "settle_by": "Crew 2's first gate, against the Admiral's standing ruling.",
        "current_evidence": "#458's own Fixed section says the check reports and never silently repairs, and wiring stays opt-in behind --wire-hooks. Workstream R's line says a fresh clone produces a reading.",
        "next_probe": "Build the check; treat wiring as a separate decision and say so in the return.",
    },
    {
        "unknown": "Whether nine changes in one file by one crew is the right call versus two crews and a merge conflict.",
        "affects": "Crew 4's cycle time and its review quality.",
        "settle_by": "Crew 4's return.",
        "current_evidence": "Standing doctrine is one writer per shared document per wave; #493 and #495 were moved INTO crew 4 for exactly this reason after they read as repo-wide hygiene.",
        "next_probe": "If crew 4 stalls, split by theme at its own gate boundary rather than mid-file.",
    },
]

with open(DST / "REPLAN_RESULT.json", "w", encoding="utf-8", newline="\n") as fh:
    json.dump(res, fh, indent=2)
    fh.write("\n")

# ---------------------------------------------------------------- NEXT_WAVE
nw = pathlib.Path(r"C:/Programs/constellation-skills/.agent-work/epic-418-redux/NEXT_WAVE.json")
with open(nw, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(
        {
            "boundary_id": "close-to-w5",
            "launch_id": "w5-gates-readiness-and-cheap-fixes",
            "trigger": "material_exception",
        },
        fh,
        indent=2,
    )
    fh.write("\n")

print("wrote", DST)
print("decision:", res["decision"], "applicable:", res["applicable"], "escalation:", res["escalation"])
print("discrepancies:", [d["id"] for d in inp["discrepancies"]])
print("unlaunched:", [u["id"] for u in inp["unlaunched_items"]])
