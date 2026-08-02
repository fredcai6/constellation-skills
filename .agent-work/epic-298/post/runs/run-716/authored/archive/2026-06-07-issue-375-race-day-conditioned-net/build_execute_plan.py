"""Author execute.json for issue-375 from the gate plan (commander)."""
import json

WID = "issue-375-race-day-conditioned-net"
TESTCMD = ('py -m pytest tests/unit/evo_predictor/ '
           '-k "fusion or replay or metalearner or record or sampled_runtime" -q')

def gate(gid, name, pre, implement_imp, review_imp, integrate_post, constraints):
    return {
        f"{gid}-implement": {
            "id": f"{gid}-implement", "title": f"{name}: implement",
            "imperative": implement_imp,
            "preconditions": [{"id": "p1", "statement": pre, "check": None, "satisfied": False}],
            "postconditions": [{"id": "c1", "statement": "IMPLEMENTER_RESULT returned with no unresolved blockers",
                                 "check": {"kind": "artifact", "evidence_type": "implementer-result"}, "satisfied": False}],
            "constraints": constraints, "directives": None, "child_checklist": None,
            "status": "pending", "status_detail": {}, "result": None, "finding": None, "evidence": [], "rework_count": 0,
        },
        f"{gid}-review": {
            "id": f"{gid}-review", "title": f"{name}: review",
            "imperative": review_imp,
            "preconditions": [{"id": "p1", "statement": "IMPLEMENTER_RESULT received for this gate", "check": None, "satisfied": False}],
            "postconditions": [{"id": "c1", "statement": "REVIEW_RESULT returned",
                                 "check": {"kind": "artifact", "evidence_type": "review-result"}, "satisfied": False}],
            "constraints": [], "directives": None, "child_checklist": None,
            "status": "pending", "status_detail": {}, "result": None, "finding": None, "evidence": [], "rework_count": 0,
        },
        f"{gid}-integrate": {
            "id": f"{gid}-integrate", "title": f"{name}: integrate",
            "imperative": ("Check the REVIEW_RESULT verdict. APPROVE: run the verification command, confirm postconditions "
                           "pass, advance this gate. BLOCK: send the implementer back for rework or raise a blocker if "
                           "unresolvable. Log out-of-scope finds as triage candidates."),
            "preconditions": [{"id": "p1", "statement": "REVIEW_RESULT received for this gate", "check": None, "satisfied": False}],
            "postconditions": integrate_post,
            "constraints": [], "directives": None, "child_checklist": None,
            "status": "pending", "status_detail": {}, "result": None, "finding": None, "evidence": [], "rework_count": 0,
        },
    }

PROJ_RULES = [
    "py not python; PYTHONIOENCODING=utf-8 in shells AND child envs of captured subprocesses",
    "DB read-only at C:/Programs/f1Brainz/data/ (absolute); no FastF1; DB is canonical",
    "Do NOT modify quali_pace_anchor.py, its config keys, §7.6.4, or prediction_ceiling_and_priorities.md",
    "Records are non-committed generated artifacts (gitignored)",
    "py -m src.utils.simplification_limits on touched src/ and tests/ paths",
]

tasks = {}

# e0-context
tasks["e0-context"] = {
    "id": "e0-context", "title": "Load execution context",
    "imperative": ("Read docs/agents/ORCHESTRATOR_CONTEXT.md, GLOSSARY.md, the evo_predictor arch packet, the brief, and "
                   "the distilled investigation findings. Confirm the frozen plan's intent and scope, then attest c1."),
    "preconditions": [],
    "postconditions": [{"id": "c1", "statement": "context + plan intent/scope confirmed", "check": None, "satisfied": False}],
    "constraints": [], "directives": None, "child_checklist": None,
    "status": "pending", "status_detail": {}, "result": None, "finding": None, "evidence": [], "rework_count": 0,
}

# G1 — STOP-GATE
tasks.update(gate(
    "g1", "G1 STOP-GATE: race_start ordering reconciliation",
    "context loaded; records for race_start+race generatable; metalearner methodology available",
    implement_imp=(
        "STOP-GATE, NO production net code. Deliverables: (1) Add a --tasks filter to "
        "scripts/fusion_replay/generate_records.py so record generation can be scoped to {race_start, race} "
        "(8 modules), keeping all-tasks default; regenerate race_start+race records into the worktree work area "
        "(.agent-work/issue-375-race-day-conditioned-net/records). (2) Extend scripts/fusion_replay/metalearner.py "
        "(or a sibling in scripts/fusion_replay/) to: (a) build a GRID/LAP-3 PERSISTENCE ordering baseline "
        "(prior-stage order from the DB via the scorecard's existing per-event DB access: grid/quali order for "
        "race_start, lap-3/race_start-target order for race) as an ordering comparator; (b) translate Model2b's "
        "race_start AND race gains into ORDERING metrics: pairwise SIGN-ACCURACY, rank MAE, spearman — vs (a) the "
        "best linear pool Model1 and (b) the persistence baseline, under LOSO with event-cluster bootstrap CIs and "
        "seed-stability. Reuse existing metalearner machinery; do not reinvent LOSO/bootstrap. (3) Run it; capture "
        "JSON + table to the work area evidence dir. (4) Write the G1 VERDICT into a NEW section of "
        "docs/evo/fusion_rework_findings.md: does race_start show real ordering improvement BEYOND grid persistence, "
        "or is the gain confidence-shaped (ordering ~flat)? State the resulting scope decision (full {race_start,race} "
        "/ race-only / ambiguous->race-only). All three outcomes are acceptable; report mechanically. Fill "
        "templates/IMPLEMENTER_HANDOFF for this and dispatch constellation-implementer."),
    review_imp=(
        "Dispatch constellation-reviewer. RE-DERIVE key numbers independently (per brief: independent reviewer per "
        "implementation gate re-derives). Verify: (a) Model1 LOSO loss reproduces the #374 baselines (race_start "
        "~0.3370, race ~0.4780 pairwise-LL) — fair-ceiling sanity; (b) the persistence baseline is correctly built "
        "from prior-stage order (grid for race_start, lap-3 for race) and is a legitimate ordering comparator; "
        "(c) the ordering-metric translation (sign-accuracy/rank MAE/spearman) is sound and antisymmetry-safe; "
        "(d) the G1 verdict's scope decision follows mechanically from the numbers; (e) tests pass. Confirm NO "
        "production net code was written and the quali anchor / ceiling doc are untouched."),
    integrate_post=[
        {"id": "c1", "statement": "G1 verdict written to fusion_rework_findings.md; scope decision recorded; tests pass",
         "check": {"kind": "command", "command": TESTCMD}, "satisfied": False},
        {"id": "c2", "statement": "reviewer verdict is APPROVE",
         "check": {"kind": "artifact", "evidence_type": "review-result", "match": {"verdict": "APPROVE"}}, "satisfied": False},
    ],
    constraints=PROJ_RULES + [
        "STOP-GATE: if race_start ordering gain dissolves vs persistence, scope drops to race-only for the ordering case",
        "Frozen #374 methodology: LOSO over seasons, event-cluster bootstrap (B=1000), seed-stability",
    ],
))

# G2 — the net + offline training/eval (the win/null determinant)
tasks.update(gate(
    "g2", "G2 BUILD: conditioned net + offline measurement",
    "G1 complete; in-scope tasks fixed by G1 scope decision",
    implement_imp=(
        "Build src/evo_predictor/fusion_conditioned_net.py: a context-conditioned fusion net for the IN-SCOPE "
        "race-day task(s) from G1. TWO DISTINCT HEADS: (1) ORDERING head — antisymmetric BY CONSTRUCTION "
        "logit(x)=g(x)-g(-x), flexible (small MLP) capacity, NOT fixed product terms; inputs per pair = the 4 module "
        "Delta-pi PLUS the derivable #377 conditioning (prior-stage-order position encoding foremost; pace-deviation "
        "is post-hoc/unavailable as an inference feature — document this and use only derivable features). (2) "
        "UNCERTAINTY head — the #408 magnitude/s_e component against the production spread-target convention "
        "(params/spread_target/<year>/<round>/<phase>.json; exchange-rate semantics); ZERO ordering leverage, kept "
        "DISTINCT from the ordering head. Wire offline training+eval in scripts/fusion_replay/ (extend, reuse the "
        "metalearner LOSO+bootstrap+seed machinery and the scorecard harness). Train/eval per in-scope task: LOSO "
        "over seasons, event-cluster bootstrap CIs, seed-stability. Apply the FROZEN SUCCESS BAR mechanically: "
        "ordering head must beat the fair linear pool (Model1) by >= the #374 gap's LOWER CI bound (race_start "
        ">=+0.00810, race >=+0.00364 pairwise-LL) WITHOUT degrading calibration vs the correlated-fusion (#373) "
        "option (compare coverage/calibration). Capture all numbers (JSON + table) to evidence. Produce the WIN/NULL "
        "call per task. Unit tests for the net (antisymmetry invariant: logit(-x)=-logit(x) exactly; head separation; "
        "shape/contract). Fill IMPLEMENTER_HANDOFF; dispatch constellation-implementer. Suggested model tier: stronger."),
    review_imp=(
        "Dispatch constellation-reviewer (stronger tier). RE-DERIVE the headline net-vs-ceiling numbers independently. "
        "Verify: (a) ordering head antisymmetry holds EXACTLY by construction (test logit(-x)==-logit(x)); (b) the net "
        "is measured against the FAIR linear pool (Model1), not a strawman, under the same LOSO/bootstrap as #374; "
        "(c) the success bar is applied mechanically and the WIN/NULL call follows from the CIs; (d) calibration is "
        "not degraded vs the correlated-fusion option; (e) the uncertainty head is distinct and consistent with the "
        "spread-target convention; (f) seed-stability is demonstrated; (g) tests pass; (h) no quali-anchor/ceiling-doc "
        "edits. Flag if any number cannot be reproduced."),
    integrate_post=[
        {"id": "c1", "statement": "net built; offline per-task net-vs-ceiling numbers + WIN/NULL call captured; tests pass",
         "check": {"kind": "command", "command": TESTCMD}, "satisfied": False},
        {"id": "c2", "statement": "reviewer verdict is APPROVE",
         "check": {"kind": "artifact", "evidence_type": "review-result", "match": {"verdict": "APPROVE"}}, "satisfied": False},
    ],
    constraints=PROJ_RULES + [
        "Antisymmetry-by-construction is a HARD constraint (logit(x)=g(x)-g(-x))",
        "Ordering head and uncertainty head MUST be distinct; uncertainty head has zero ordering leverage",
        "Success bar frozen BEFORE training; apply mechanically; honest-null is a valid successful outcome",
        "prefer torch (2.10 CPU installed); sklearn ABSENT; py -m pip install only if genuinely needed, LOG it",
    ],
))

# G3 — verdict + conditional production wiring
tasks.update(gate(
    "g3", "G3 VERDICT + conditional opt-in wiring (default OFF)",
    "G2 complete; WIN/NULL call available per in-scope task",
    implement_imp=(
        "Finalize the findings + integration per the G2 WIN/NULL call. ALWAYS: write the complete #375 section in "
        "docs/evo/fusion_rework_findings.md (G1 reconciliation + per-task net-vs-ceiling numbers with CIs + WIN/NULL "
        "call + scope notes + reproduce block + the #408 magnitude-component disposition + the activation-plan "
        "composition with the #420 anchor retrain). IF WIN on an in-scope task: wire OPT-IN, DEFAULT-OFF production "
        "integration — add the conditioned-net intercept into sampled_runtime._run_stage for the IN-SCOPE race-day "
        "task(s) ONLY, behind a frozen config dataclass on RuntimeStageConfig MIRRORING QualiPaceAnchorConfig "
        "(enabled:bool default False; parsed from manifest; absent key => disabled; old manifests compatible), parsed "
        "in pipeline_manifest_v4.py. Do NOT alter the quali anchor attach. Document the activation plan (what retrain/"
        "validation flips it on; how it composes with the anchor's pending activation retrain). IF NULL on all "
        "in-scope tasks: write NO production wiring (verdict-only); leave #375 OPEN (no Closes). Ensure the full test "
        "command passes. Fill IMPLEMENTER_HANDOFF; dispatch constellation-implementer."),
    review_imp=(
        "Dispatch constellation-reviewer. Verify: (a) the findings section is complete, traceable, and the WIN/NULL "
        "call matches G2 evidence; (b) IF WIN: the production wiring is opt-in DEFAULT-OFF, mirrors the "
        "QualiPaceAnchorConfig pattern, touches sampled_runtime ONLY for the race-day intercept, does NOT alter the "
        "anchor attach, and old manifests stay compatible; (c) IF NULL: NO production net code was added and #375 is "
        "left open; (d) the activation plan composes with the #420 anchor retrain without conflict; (e) the #408 "
        "magnitude disposition is recorded; (f) full test command green; (g) quali anchor / ceiling doc untouched; "
        "(h) simplification limits pass on touched paths."),
    integrate_post=[
        {"id": "c1", "statement": "findings complete + (win: opt-in default-OFF wiring | null: verdict-only); full test suite green",
         "check": {"kind": "command", "command": TESTCMD}, "satisfied": False},
        {"id": "c2", "statement": "reviewer verdict is APPROVE",
         "check": {"kind": "artifact", "evidence_type": "review-result", "match": {"verdict": "APPROVE"}}, "satisfied": False},
    ],
    constraints=PROJ_RULES + [
        "Opt-in DEFAULT OFF; default-ON is NOT this issue",
        "Honest-null: losing net => NO production wiring, do NOT close #375",
        "Win => PR includes 'Closes #375'; verdict comment on #375; pointers on #374 + #408",
    ],
))

doc = {
    "work_id": WID,
    "type": "gated",
    "config_ref": "docs/agents/engine-config.json",
    "items": ["e0-context",
              "g1-implement", "g1-review", "g1-integrate",
              "g2-implement", "g2-review", "g2-integrate",
              "g3-implement", "g3-review", "g3-integrate"],
    "tasks": tasks,
    "consolidation": None,
    "triage_candidates": [],
    "blockers": [],
}
out = f".agent-work/{WID}/execute.json"
json.dump(doc, open(out, "w", encoding="utf-8"), indent=2)
print("wrote", out, "with", len(tasks), "tasks")
