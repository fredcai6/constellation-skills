"""Emit execute.json for issue-456 from a compact gate spec.

Ten gates x (implement, review, integrate) + e0-context = 31 items. Hand-writing
31 blocks invites drift between them; this generates them from one spec so the
shape is uniform and only the per-gate content varies.

Shape follows skills/commander/templates/EXECUTE_PLAN.template.json exactly.
Reasoning gates (crew waived) emit a single item instead of the triple.
"""
import json
import sys

WORK_ID = "issue-456"


def implement(g):
    return {
        "id": "%s-implement" % g["id"],
        "title": "%s: implement" % g["title"],
        "imperative": (
            "Fill templates/IMPLEMENTER_HANDOFF.template.md for this gate: task, protected "
            "intent, test mode, close criteria, allowed scope, specific exclusions, "
            "constraints, required evidence, verification commands, authority, and the "
            "inbound map anchors from this gate's anchors block -- including the Map entry "
            "point. Dispatch a subagent invoking constellation-implementer with the "
            "completed handoff. Wait for and integrate the returned IMPLEMENTER_RESULT as "
            "evidence.\n\nGATE TASK: %s" % g["task"]
        ),
        "preconditions": [{"id": "p1", "statement": g["depends"], "check": None, "satisfied": False}],
        "postconditions": [{
            "id": "c1",
            "statement": "IMPLEMENTER_RESULT returned with no unresolved blockers",
            "check": {"kind": "artifact", "evidence_type": "implementer-result"},
            "satisfied": False,
        }],
        "constraints": g["constraints"],
        "anchors": g["anchors"],
        "directives": None, "child_checklist": None,
        "status": "pending", "status_detail": {}, "result": None,
        "finding": None, "evidence": [], "rework_count": 0,
    }


def review(g):
    return {
        "id": "%s-review" % g["id"],
        "title": "%s: review" % g["title"],
        "imperative": (
            "Fill templates/REVIEWER_HANDOFF.template.md: what was implemented, how to "
            "inspect the diff, task statement, close criteria, allowed scope, specific "
            "exclusions, constraints, the inbound map anchors from this gate's anchors "
            "block, and the evidence from IMPLEMENTER_RESULT. Dispatch a subagent invoking "
            "constellation-reviewer with the completed handoff. Wait for and integrate the "
            "returned REVIEW_RESULT as evidence."
        ),
        "preconditions": [{"id": "p1", "statement": "IMPLEMENTER_RESULT received for this gate",
                           "check": None, "satisfied": False}],
        "postconditions": [{"id": "c1", "statement": "REVIEW_RESULT returned",
                            "check": {"kind": "artifact", "evidence_type": "review-result"},
                            "satisfied": False}],
        "constraints": [],
        "anchors": {"inherits": "%s-implement anchors -- review verifies the change against "
                                "the same structural/capability/constraint/decision/evidence "
                                "anchors" % g["id"]},
        "directives": None, "child_checklist": None,
        "status": "pending", "status_detail": {}, "result": None,
        "finding": None, "evidence": [], "rework_count": 0,
    }


def integrate(g):
    post = [{
        "id": "c1",
        "statement": g["close"],
        "check": {"kind": "command", "command": g["command"]},
        "override_policy": {"allowed": True, "authority": "human", "reason_required": True},
        "satisfied": False,
    }, {
        "id": "c2",
        "statement": "reviewer verdict is APPROVE",
        "check": {"kind": "artifact", "evidence_type": "review-result",
                  "match": {"verdict": "APPROVE"}},
        "satisfied": False,
    }]
    return {
        "id": "%s-integrate" % g["id"],
        "title": "%s: integrate" % g["title"],
        "imperative": (
            "Check the REVIEW_RESULT verdict. APPROVE: run the verification command "
            "yourself, then advance this gate -- a command-kind postcondition is satisfied "
            "by `advance`, which re-runs the check, NOT by `attest`. BLOCK: send the "
            "implementer back for rework or raise a blocker if the gate is unresolvable. "
            "Log any out-of-scope finds as triage candidates."
        ),
        "preconditions": [{"id": "p1", "statement": "REVIEW_RESULT received for this gate",
                           "check": None, "satisfied": False}],
        "postconditions": post,
        "constraints": [],
        "directives": None, "child_checklist": None,
        "status": "pending", "status_detail": {}, "result": None,
        "finding": None, "evidence": [], "rework_count": 0,
    }


def reasoning(g):
    """A gate run in the Commander's own context, with a stated crew-waiver reason."""
    return {
        "id": g["id"],
        "title": g["title"],
        "imperative": "%s\n\nCREW WAIVED: %s" % (g["task"], g["waiver"]),
        "preconditions": [{"id": "p1", "statement": g["depends"], "check": None, "satisfied": False}],
        "postconditions": [{
            "id": "c1", "statement": g["close"],
            "check": {"kind": "command", "command": g["command"]},
            "override_policy": {"allowed": True, "authority": "human", "reason_required": True},
            "satisfied": False,
        }],
        "constraints": g["constraints"],
        "anchors": g["anchors"],
        "directives": None, "child_checklist": None,
        "status": "pending", "status_detail": {}, "result": None,
        "finding": None, "evidence": [], "rework_count": 0,
    }


E0 = {
    "id": "e0-context",
    "title": "Load execution context",
    "imperative": (
        "Read the inherited global doctrine (skills/_shared/global-orchestrator.md and "
        "skills/_shared/global-everyone.md), then docs/agents/ORCHESTRATOR_CONTEXT.md and "
        "docs/agents/GLOSSARY.md. This repo has NO docs/architecture packets -- orientation "
        "was DEGRADED-NO-MAP and the hash-pinned substitute is "
        ".agent-work/issue-456/reference/DESIGN_SPEC.md. Read that plus "
        ".agent-work/issue-456/MISSION_FRAME.md and "
        ".agent-work/issue-456/ownership-scope.md. Confirm the frozen plan's intent and "
        "scope, then attest c1."
    ),
    "preconditions": [],
    "postconditions": [{"id": "c1",
                        "statement": "orchestrator context + glossary + confirmed spec + mission frame loaded; plan intent and scope confirmed",
                        "check": None, "satisfied": False}],
    "constraints": [], "directives": None, "child_checklist": None,
    "status": "pending", "status_detail": {}, "result": None,
    "finding": None, "evidence": [], "rework_count": 0,
}


def build(gates):
    items = ["e0-context"]
    tasks = {"e0-context": E0}
    for g in gates:
        if g.get("mode") == "reasoning":
            items.append(g["id"])
            tasks[g["id"]] = reasoning(g)
        else:
            for suffix, fn in (("implement", implement), ("review", review), ("integrate", integrate)):
                key = "%s-%s" % (g["id"], suffix)
                items.append(key)
                tasks[key] = fn(g)
    return {
        "work_id": WORK_ID,
        "type": "gated",
        "config_ref": "docs/agents/engine-config.json",
        "items": items,
        "tasks": tasks,
        "consolidation": None,
        "triage_candidates": [],
        "blockers": [],
    }


if __name__ == "__main__":
    spec = json.load(open(sys.argv[1], encoding="utf-8"))
    plan = build(spec["gates"])
    with open(sys.argv[2], "w", encoding="utf-8") as fh:
        json.dump(plan, fh, indent=2)
        fh.write("\n")
    print("wrote %s: %d items across %d gates" % (sys.argv[2], len(plan["items"]), len(spec["gates"])))
