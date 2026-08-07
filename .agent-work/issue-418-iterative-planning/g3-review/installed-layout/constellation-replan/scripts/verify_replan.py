#!/usr/bin/env python
"""Verify and render strict offline v1 wave-replanning packets."""

from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
SOURCE_SCRIPTS = Path(__file__).resolve().parents[3] / "scripts"
for candidate in (SCRIPT_DIR, SOURCE_SCRIPTS):
    if candidate.is_dir():
        sys.path.insert(0, str(candidate))

from verify_issue_set import IssueSetError, verify_manifest_shape  # noqa: E402


DECISIONS = {"advance", "repair", "replan", "stop"}
CLASSIFICATION_ACTIONS = {
    "blocks_current_wave_exit": "repair_current_wave",
    "invalidates_forecast_or_decomposition": "revise_plan",
    "later_only": "amend_forecast_or_parked",
    "evidence_only": "record_evidence_only",
    "drop": "drop",
}
UNLAUNCHED_KINDS = {"issue", "forecast", "uncertainty", "parked"}
UNLAUNCHED_ACTIONS = {"keep", "rewrite", "reorder", "defer", "delete"}
FIXED_BOUNDARIES = {
    "intent_and_why", "definition_of_done", "good_enough",
    "hard_constraints", "fixed_decisions",
}


class ReplanError(Exception):
    """Raised when a replan input/result violates its strict public contract."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ReplanError(message)


def _object(value: object, path: str, required: set[str], optional: set[str] | None = None) -> dict:
    optional = optional or set()
    _require(isinstance(value, dict), f"{path} must be an object")
    assert isinstance(value, dict)
    missing = required - value.keys()
    unknown = value.keys() - required - optional
    _require(not missing, f"{path} missing required field(s): {', '.join(sorted(missing))}")
    _require(not unknown, f"{path} has unknown field(s): {', '.join(sorted(unknown))}")
    return value


def _string(value: object, path: str, *, nonempty: bool = True) -> str:
    _require(isinstance(value, str), f"{path} must be a string")
    assert isinstance(value, str)
    _require(not nonempty or bool(value.strip()), f"{path} must be nonempty")
    return value


def _strings(value: object, path: str, *, nonempty: bool = False) -> list[str]:
    _require(isinstance(value, list), f"{path} must be an array")
    assert isinstance(value, list)
    _require(not nonempty or bool(value), f"{path} must be nonempty")
    for index, entry in enumerate(value):
        _string(entry, f"{path}[{index}]")
    return value


def _version(value: object, path: str) -> None:
    _require(type(value) is int and value == 1, f"{path} must be integer 1")


def _validate_plan(plan: object, path: str) -> dict:
    try:
        return verify_manifest_shape(plan)
    except IssueSetError as exc:
        raise ReplanError(f"{path} is not an exact G1 plan: {exc}") from exc


def _validate_wave(value: object, plan: dict, path: str) -> dict:
    candidate = copy.deepcopy(plan)
    candidate["current_wave"] = value
    _validate_plan(candidate, path)
    assert isinstance(value, dict)
    return value


def _validate_forecast(value: object, plan: dict, path: str) -> list[dict]:
    candidate = copy.deepcopy(plan)
    candidate["wave_forecast"] = value
    _validate_plan(candidate, path)
    assert isinstance(value, list)
    return value


def _validate_uncertainty(value: object, plan: dict, path: str) -> list[dict]:
    candidate = copy.deepcopy(plan)
    candidate["uncertainty_register"] = value
    _validate_plan(candidate, path)
    assert isinstance(value, list)
    return value


def _validate_parked(value: object, path: str) -> list[str]:
    return _strings(value, path)


def verify_replan_input(packet: object) -> dict:
    """Fail fast unless ``packet`` is the exact v1 replanning input."""
    fields = {
        "schema_version", "current_plan", "completed_outcomes", "wave_evidence",
        "discrepancies", "open_current_wave_issue_ids", "unlaunched_items", "repo_state",
    }
    packet = _object(packet, "input", fields)
    _version(packet["schema_version"], "input.schema_version")
    plan = _validate_plan(packet["current_plan"], "input.current_plan")
    current_ids = {issue["id"] for issue in plan["current_wave"]["issues"]}

    outcomes = packet["completed_outcomes"]
    _require(isinstance(outcomes, list), "input.completed_outcomes must be an array")
    completed_ids: list[str] = []
    for index, entry in enumerate(outcomes):
        path = f"input.completed_outcomes[{index}]"
        item = _object(entry, path, {"issue_id", "outcome", "evidence"})
        completed_ids.append(_string(item["issue_id"], f"{path}.issue_id"))
        _string(item["outcome"], f"{path}.outcome")
        _string(item["evidence"], f"{path}.evidence")
    _require(len(completed_ids) == len(set(completed_ids)), "completed outcome issue ids must be unique")

    evidence = packet["wave_evidence"]
    _require(isinstance(evidence, list) and bool(evidence), "input.wave_evidence must be a nonempty array")
    for index, entry in enumerate(evidence):
        path = f"input.wave_evidence[{index}]"
        item = _object(entry, path, {"claim", "expected", "observed", "source"})
        for field in ("claim", "expected", "observed", "source"):
            _string(item[field], f"{path}.{field}")

    discrepancies = packet["discrepancies"]
    _require(isinstance(discrepancies, list), "input.discrepancies must be an array")
    discrepancy_ids: list[str] = []
    fields = {"id", "signal", "classification", "affects", "evidence", "reason"}
    for index, entry in enumerate(discrepancies):
        path = f"input.discrepancies[{index}]"
        item = _object(entry, path, fields)
        discrepancy_ids.append(_string(item["id"], f"{path}.id"))
        for field in ("signal", "affects", "evidence"):
            _string(item[field], f"{path}.{field}")
        _require(item["classification"] in CLASSIFICATION_ACTIONS, f"{path}.classification is invalid")
        _string(item["reason"], f"{path}.reason", nonempty=item["classification"] == "drop")
    _require(len(discrepancy_ids) == len(set(discrepancy_ids)), "input.discrepancy ids must be unique")

    open_ids = _strings(packet["open_current_wave_issue_ids"], "input.open_current_wave_issue_ids")
    _require(len(open_ids) == len(set(open_ids)), "open current-wave issue ids must be unique")
    launched = set(completed_ids) | set(open_ids)
    _require(set(completed_ids).isdisjoint(open_ids), "completed and open current-wave issue ids must be disjoint")
    _require(launched == current_ids, "completed and open ids must exactly partition current-wave issue ids")

    unlaunched = packet["unlaunched_items"]
    _require(isinstance(unlaunched, list), "input.unlaunched_items must be an array")
    unlaunched_ids: list[str] = []
    for index, entry in enumerate(unlaunched):
        path = f"input.unlaunched_items[{index}]"
        item = _object(entry, path, {"id", "kind"})
        unlaunched_ids.append(_string(item["id"], f"{path}.id"))
        _require(item["kind"] in UNLAUNCHED_KINDS, f"{path}.kind is invalid")
    _require(len(unlaunched_ids) == len(set(unlaunched_ids)), "input.unlaunched item ids must be unique")
    unlaunched_issue_ids = {item["id"] for item in unlaunched if item["kind"] == "issue"}
    _require(
        current_ids.isdisjoint(unlaunched_issue_ids),
        "unlaunched issue ids must be disjoint from launched current-wave issue ids",
    )

    repo = _object(packet["repo_state"], "input.repo_state", {"anchors", "map_status"})
    _strings(repo["anchors"], "input.repo_state.anchors")
    _string(repo["map_status"], "input.repo_state.map_status")
    return packet


def _validate_discrepancy_dispositions(source: dict, result: dict) -> None:
    dispositions = result["discrepancy_dispositions"]
    _require(isinstance(dispositions, list), "result.discrepancy_dispositions must be an array")
    expected = {item["id"]: item for item in source["discrepancies"]}
    seen: set[str] = set()
    for index, entry in enumerate(dispositions):
        path = f"result.discrepancy_dispositions[{index}]"
        item = _object(entry, path, {"id", "action", "reason", "issue_created"})
        item_id = _string(item["id"], f"{path}.id")
        _require(item_id in expected and item_id not in seen, f"{path}.id must name one undispositioned input discrepancy")
        seen.add(item_id)
        action = item["action"]
        expected_action = CLASSIFICATION_ACTIONS[expected[item_id]["classification"]]
        _require(action == expected_action, f"{path}.action must be {expected_action!r} for its classification")
        _string(item["reason"], f"{path}.reason")
        _require(type(item["issue_created"]) is bool, f"{path}.issue_created must be boolean")
        if action in {"record_evidence_only", "drop"}:
            _require(item["issue_created"] is False, f"{path}.issue_created must be false for {action}")
    _require(seen == set(expected), "every input discrepancy must receive exactly one disposition")


def _validate_unlaunched_dispositions(source: dict, result: dict, plan: dict) -> None:
    dispositions = result["unlaunched_dispositions"]
    _require(isinstance(dispositions, list), "result.unlaunched_dispositions must be an array")
    expected = {item["id"]: item for item in source["unlaunched_items"]}
    seen: set[str] = set()
    rewritten_issues: list[dict] = []
    for index, entry in enumerate(dispositions):
        path = f"result.unlaunched_dispositions[{index}]"
        item = _object(entry, path, {"id", "action", "reason"}, {"replacement"})
        item_id = _string(item["id"], f"{path}.id")
        _require(item_id in expected and item_id not in seen, f"{path}.id must name one undispositioned input item")
        seen.add(item_id)
        _require(item["action"] in UNLAUNCHED_ACTIONS, f"{path}.action is invalid")
        _string(item["reason"], f"{path}.reason")
        if item["action"] != "rewrite":
            _require("replacement" not in item, f"{path}.replacement is allowed only for rewrite")
            continue
        _require("replacement" in item, f"{path}.replacement is required for rewrite")
        kind = expected[item_id]["kind"]
        replacement = item["replacement"]
        if kind == "issue":
            _require(isinstance(replacement, dict), f"{path}.replacement must be a G1 issue object")
            assert isinstance(replacement, dict)
            _require(
                replacement.get("id") == item_id,
                f"{path}.replacement.id must preserve unlaunched item id {item_id!r}",
            )
            rewritten_issues.append(replacement)
        elif kind == "forecast":
            _validate_forecast([replacement], plan, f"{path}.replacement")
        elif kind == "uncertainty":
            _validate_uncertainty([replacement], plan, f"{path}.replacement")
        else:
            _string(replacement, f"{path}.replacement")
    _require(seen == set(expected), "every input unlaunched item must receive exactly one disposition")
    if rewritten_issues:
        candidate = copy.deepcopy(plan)
        result_wave = result["current_wave"]
        candidate["current_wave"] = copy.deepcopy(
            plan["current_wave"] if result_wave is None else result_wave
        )
        candidate["current_wave"]["issues"].extend(copy.deepcopy(rewritten_issues))
        _validate_plan(candidate, "result assembled issue graph")


def _validate_escalation(source: dict, result: dict) -> None:
    changes = result["material_changes"]
    _require(isinstance(changes, list), "result.material_changes must be an array")
    fixed_changes: list[dict] = []
    for index, entry in enumerate(changes):
        path = f"result.material_changes[{index}]"
        item = _object(entry, path, {"surface", "before", "after", "reason"})
        for field in ("surface", "before", "after", "reason"):
            _string(item[field], f"{path}.{field}")
        if item["surface"] in FIXED_BOUNDARIES:
            fixed_changes.append(item)

    escalation = result["escalation"]
    if not fixed_changes:
        _require(escalation is None, "result.escalation is allowed only for a fixed-boundary material change")
        return
    fixed_surfaces = {change["surface"] for change in fixed_changes}
    _require(
        len(fixed_surfaces) == 1,
        "a singular escalation packet may propose material changes to only one fixed boundary",
    )
    _require(result["applicable"] is False, "a fixed-boundary change requires applicable=false")
    escalation = _object(
        escalation, "result.escalation", {"boundary", "proposed_value", "reason", "authority_required"}
    )
    boundary = escalation["boundary"]
    _require(boundary in FIXED_BOUNDARIES, "result.escalation.boundary is invalid")
    _require(boundary == next(iter(fixed_surfaces)), "escalation boundary must match the fixed material change")
    _string(escalation["reason"], "result.escalation.reason")
    _string(escalation["authority_required"], "result.escalation.authority_required")
    proposed = escalation["proposed_value"]
    if boundary == "intent_and_why":
        _string(proposed, "result.escalation.proposed_value")
    elif boundary == "definition_of_done":
        _strings(proposed, "result.escalation.proposed_value", nonempty=True)
    elif boundary == "good_enough":
        plan = copy.deepcopy(source["current_plan"])
        plan["good_enough"] = proposed
        _validate_plan(plan, "result.escalation.proposed_value")
    else:
        _strings(proposed, "result.escalation.proposed_value")


def verify_replan_result(source: object, result: object) -> None:
    """Verify a result against its exact input identities and fixed boundaries."""
    source = verify_replan_input(source)
    fields = {
        "schema_version", "decision", "applicable", "criteria_assessment",
        "discrepancy_dispositions", "current_wave", "revised_forecast",
        "revised_uncertainty", "revised_parked", "unlaunched_dispositions",
        "material_changes", "wave_review_comment", "revised_epic_body", "escalation",
    }
    result = _object(result, "result", fields)
    _version(result["schema_version"], "result.schema_version")
    _require(result["decision"] in DECISIONS, "result.decision is invalid")
    _require(type(result["applicable"]) is bool, "result.applicable must be boolean")
    criteria = _object(result["criteria_assessment"], "result.criteria_assessment", {"wave_exit", "epic_done", "good_enough"})
    for field in ("wave_exit", "epic_done", "good_enough"):
        _string(criteria[field], f"result.criteria_assessment.{field}")

    plan = source["current_plan"]
    wave = result["current_wave"]
    if wave is None:
        _require(result["decision"] == "stop", "only stop may set result.current_wave to null")
    else:
        _validate_wave(wave, plan, "result.current_wave")
    _validate_forecast(result["revised_forecast"], plan, "result.revised_forecast")
    _validate_uncertainty(result["revised_uncertainty"], plan, "result.revised_uncertainty")
    _validate_parked(result["revised_parked"], "result.revised_parked")

    if result["decision"] == "repair":
        _require(wave == plan["current_wave"], "repair must hold the current wave exactly")
        _require(result["revised_forecast"] == plan["wave_forecast"], "repair must hold the forecast exactly")
    if result["applicable"] and wave is not None:
        before = {issue["id"]: issue for issue in plan["current_wave"]["issues"]}
        after = {issue["id"]: issue for issue in wave["issues"]}
        for issue_id in source["open_current_wave_issue_ids"]:
            _require(after.get(issue_id) == before[issue_id], f"applicable result must preserve launched open issue {issue_id!r}")

    _validate_discrepancy_dispositions(source, result)
    _validate_unlaunched_dispositions(source, result, plan)
    _validate_escalation(source, result)
    _string(result["wave_review_comment"], "result.wave_review_comment")
    _string(result["revised_epic_body"], "result.revised_epic_body")


def render_replan_markdown(source: object, result: object) -> str:
    """Render one validated transition record without side effects."""
    verify_replan_result(source, result)
    assert isinstance(result, dict)
    criteria = result["criteria_assessment"]
    lines = [
        "## Wave decision", f"**{result['decision']}** (applicable: {str(result['applicable']).lower()})", "",
        "## Criteria assessment",
        f"- Wave exit: {criteria['wave_exit']}",
        f"- Epic done: {criteria['epic_done']}",
        f"- Good enough: {criteria['good_enough']}", "",
        "## Discrepancy dispositions",
    ]
    for item in result["discrepancy_dispositions"]:
        lines.append(f"- {item['id']}: **{item['action']}** — {item['reason']}")
    lines.extend(["", "## Unlaunched dispositions"])
    for item in result["unlaunched_dispositions"]:
        lines.append(f"- {item['id']}: **{item['action']}** — {item['reason']}")
    lines.extend(["", result["wave_review_comment"].strip(), "", result["revised_epic_body"].strip(), ""])
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", help="path to REPLAN_INPUT JSON")
    parser.add_argument("result", help="path to REPLAN_RESULT JSON")
    args = parser.parse_args(argv)
    try:
        source = json.loads(Path(args.input).read_text(encoding="utf-8"))
        result = json.loads(Path(args.result).read_text(encoding="utf-8"))
        rendered = render_replan_markdown(source, result)
    except (OSError, json.JSONDecodeError, ReplanError) as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return 1
    print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
