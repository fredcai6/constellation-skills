#!/usr/bin/env python
"""Verify and render the strict v1 initial-cut contract.

The shaped brief is the direct Explorer-to-cutter input.  The resulting
manifest makes only ``current_wave.issues`` runnable; forecasts remain
structurally non-actionable.
"""

from __future__ import annotations

import argparse
import copy
import json
import re
import sys
from datetime import date as calendar_date
from pathlib import Path


VALID_TYPES = ("AFK", "HITL")
ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


class IssueSetError(Exception):
    """Raised when a shaped brief or initial issue-set contract is invalid."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise IssueSetError(message)


def _object(value: object, path: str, required: set[str], optional: set[str] = set()) -> dict:
    _require(isinstance(value, dict), f"{path} must be an object")
    assert isinstance(value, dict)
    missing = required - value.keys()
    unknown = value.keys() - required - optional
    _require(not missing, f"{path} missing required field(s): {', '.join(sorted(missing))}")
    _require(not unknown, f"{path} has unknown field(s): {', '.join(sorted(unknown))}")
    return value


def _string(value: object, path: str) -> str:
    _require(isinstance(value, str) and bool(value.strip()), f"{path} must be a nonempty string")
    assert isinstance(value, str)
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


def _forecast(value: object, path: str) -> list[dict]:
    _require(isinstance(value, list), f"{path} must be an array")
    assert isinstance(value, list)
    for index, entry in enumerate(value):
        item_path = f"{path}[{index}]"
        item = _object(entry, item_path, {"outcome", "why_likely", "entry_conditions"})
        _string(item["outcome"], f"{item_path}.outcome")
        _string(item["why_likely"], f"{item_path}.why_likely")
        _strings(item["entry_conditions"], f"{item_path}.entry_conditions")
    return value


def _uncertainties(value: object, path: str) -> list[dict]:
    _require(isinstance(value, list), f"{path} must be an array")
    assert isinstance(value, list)
    fields = {"unknown", "affects", "settle_by", "current_evidence", "next_probe"}
    for index, entry in enumerate(value):
        item_path = f"{path}[{index}]"
        item = _object(entry, item_path, fields)
        for field in fields:
            _string(item[field], f"{item_path}.{field}")
    return value


def _good_enough(value: object, path: str) -> dict:
    fields = {"mandatory_quality", "sufficient_evidence", "appetite"}
    item = _object(value, path, fields)
    for field in fields:
        _string(item[field], f"{path}.{field}")
    return item


def verify_shaped_brief(brief: object) -> dict:
    """Fail fast unless ``brief`` is exactly the confirmed v1 input contract."""
    fields = {
        "schema_version", "title", "source_path", "confirmation", "intent_and_why",
        "definition_of_done", "good_enough", "hard_constraints", "fixed_decisions",
        "initial_wave", "wave_forecast", "uncertainty_register", "parked_possibilities",
        "evidence_digest",
    }
    brief = _object(brief, "brief", fields)
    _version(brief["schema_version"], "brief.schema_version")
    _string(brief["title"], "brief.title")
    _string(brief["source_path"], "brief.source_path")
    confirmation = _object(
        brief["confirmation"], "brief.confirmation", {"status", "confirmed_by", "date"}
    )
    _require(confirmation["status"] == "CONFIRMED", "brief.confirmation.status must be CONFIRMED")
    _string(confirmation["confirmed_by"], "brief.confirmation.confirmed_by")
    date = _string(confirmation["date"], "brief.confirmation.date")
    _require(bool(ISO_DATE.fullmatch(date)), "brief.confirmation.date must be an ISO date (YYYY-MM-DD)")
    try:
        calendar_date.fromisoformat(date)
    except ValueError as exc:
        raise IssueSetError("brief.confirmation.date must be a valid ISO calendar date") from exc
    _string(brief["intent_and_why"], "brief.intent_and_why")
    _strings(brief["definition_of_done"], "brief.definition_of_done", nonempty=True)
    _good_enough(brief["good_enough"], "brief.good_enough")
    _strings(brief["hard_constraints"], "brief.hard_constraints")
    _strings(brief["fixed_decisions"], "brief.fixed_decisions")
    wave = _object(brief["initial_wave"], "brief.initial_wave", {"objective", "exit_criteria"})
    _string(wave["objective"], "brief.initial_wave.objective")
    _strings(wave["exit_criteria"], "brief.initial_wave.exit_criteria", nonempty=True)
    _forecast(brief["wave_forecast"], "brief.wave_forecast")
    _uncertainties(brief["uncertainty_register"], "brief.uncertainty_register")
    _strings(brief["parked_possibilities"], "brief.parked_possibilities")
    digest = brief["evidence_digest"]
    _require(isinstance(digest, list), "brief.evidence_digest must be an array")
    for index, entry in enumerate(digest):
        item_path = f"brief.evidence_digest[{index}]"
        item = _object(entry, item_path, {"claim", "source", "conclusion"})
        for field in ("claim", "source", "conclusion"):
            _string(item[field], f"{item_path}.{field}")
    return brief


ISSUE_FIELDS = {
    "id", "title", "desired_outcome", "useful_now", "appetite",
    "acceptance_or_falsification_evidence", "implementation_latitude",
    "hard_constraints_no_gos", "local_unknowns", "anchors", "type", "blocks",
}


def _issue(value: object, path: str) -> dict:
    issue = _object(value, path, ISSUE_FIELDS, {"hitl_reason"})
    for field in (
        "id", "title", "desired_outcome", "useful_now", "appetite",
        "acceptance_or_falsification_evidence", "implementation_latitude",
    ):
        _string(issue[field], f"{path}.{field}")
    _strings(issue["hard_constraints_no_gos"], f"{path}.hard_constraints_no_gos")
    _strings(issue["local_unknowns"], f"{path}.local_unknowns")
    _strings(issue["anchors"], f"{path}.anchors", nonempty=True)
    _require(issue["type"] in VALID_TYPES, f"{path}.type must be AFK or HITL")
    _strings(issue["blocks"], f"{path}.blocks")
    if issue["type"] == "HITL":
        _require("hitl_reason" in issue, f"{path}.hitl_reason is required for HITL")
        _string(issue["hitl_reason"], f"{path}.hitl_reason")
    else:
        _require("hitl_reason" not in issue, f"{path}.hitl_reason is only allowed for HITL")
    return issue


def verify_edges(issues: list[dict]) -> None:
    ids = [issue["id"] for issue in issues]
    _require(len(ids) == len(set(ids)), "current_wave.issues contains duplicate ids")
    known = set(ids)
    dependencies = {iid: set() for iid in ids}
    for issue in issues:
        for target in issue["blocks"]:
            _require(target in known, f"issue {issue['id']!r}: blocks target {target!r} names no known issue")
            dependencies[target].add(issue["id"])
    placed: set[str] = set()
    while len(placed) < len(ids):
        ready = [iid for iid in ids if iid not in placed and dependencies[iid] <= placed]
        _require(bool(ready), "dependency cycle in current_wave.issues blocks edges")
        placed.update(ready)


def verify_manifest_shape(manifest: object) -> dict:
    fields = {
        "schema_version", "epic", "definition_of_done", "good_enough",
        "hard_constraints", "fixed_decisions", "current_wave", "wave_forecast",
        "uncertainty_register", "parked_possibilities",
    }
    manifest = _object(manifest, "manifest", fields)
    _version(manifest["schema_version"], "manifest.schema_version")
    epic = _object(manifest["epic"], "manifest.epic", {"title", "spec_path", "intent_and_why"})
    for field in ("title", "spec_path", "intent_and_why"):
        _string(epic[field], f"manifest.epic.{field}")
    _strings(manifest["definition_of_done"], "manifest.definition_of_done", nonempty=True)
    _good_enough(manifest["good_enough"], "manifest.good_enough")
    _strings(manifest["hard_constraints"], "manifest.hard_constraints")
    _strings(manifest["fixed_decisions"], "manifest.fixed_decisions")
    wave = _object(manifest["current_wave"], "manifest.current_wave", {"objective", "exit_criteria", "issues"})
    _string(wave["objective"], "manifest.current_wave.objective")
    _strings(wave["exit_criteria"], "manifest.current_wave.exit_criteria", nonempty=True)
    _require(isinstance(wave["issues"], list) and bool(wave["issues"]), "manifest.current_wave.issues must be a nonempty array")
    for index, issue in enumerate(wave["issues"]):
        _issue(issue, f"manifest.current_wave.issues[{index}]")
    _forecast(manifest["wave_forecast"], "manifest.wave_forecast")
    _uncertainties(manifest["uncertainty_register"], "manifest.uncertainty_register")
    _strings(manifest["parked_possibilities"], "manifest.parked_possibilities")
    verify_edges(wave["issues"])
    return manifest


def build_initial_manifest(brief: object, issues: object) -> dict:
    """Add current-wave issue drafts to a confirmed brief without prose translation."""
    brief = verify_shaped_brief(brief)
    _require(isinstance(issues, list) and bool(issues), "issues must be a nonempty array")
    manifest = {
        "schema_version": 1,
        "epic": {
            "title": brief["title"],
            "spec_path": brief["source_path"],
            "intent_and_why": brief["intent_and_why"],
        },
        "definition_of_done": copy.deepcopy(brief["definition_of_done"]),
        "good_enough": copy.deepcopy(brief["good_enough"]),
        "hard_constraints": copy.deepcopy(brief["hard_constraints"]),
        "fixed_decisions": copy.deepcopy(brief["fixed_decisions"]),
        "current_wave": {
            "objective": brief["initial_wave"]["objective"],
            "exit_criteria": copy.deepcopy(brief["initial_wave"]["exit_criteria"]),
            "issues": copy.deepcopy(issues),
        },
        "wave_forecast": copy.deepcopy(brief["wave_forecast"]),
        "uncertainty_register": copy.deepcopy(brief["uncertainty_register"]),
        "parked_possibilities": copy.deepcopy(brief["parked_possibilities"]),
    }
    return verify_manifest_shape(manifest)


def verify_issue_set(manifest: object, brief: object) -> None:
    brief = verify_shaped_brief(brief)
    manifest = verify_manifest_shape(manifest)
    _require(manifest["epic"]["title"] == brief["title"], "manifest.epic.title must copy brief.title exactly")
    _require(manifest["epic"]["spec_path"] == brief["source_path"], "manifest.epic.spec_path must copy brief.source_path exactly")
    mappings = {
        "intent_and_why": manifest["epic"]["intent_and_why"],
        "definition_of_done": manifest["definition_of_done"],
        "good_enough": manifest["good_enough"],
        "hard_constraints": manifest["hard_constraints"],
        "fixed_decisions": manifest["fixed_decisions"],
        "wave_forecast": manifest["wave_forecast"],
        "uncertainty_register": manifest["uncertainty_register"],
        "parked_possibilities": manifest["parked_possibilities"],
    }
    for field, actual in mappings.items():
        _require(actual == brief[field], f"manifest.{field} must preserve brief.{field} exactly")
    _require(manifest["current_wave"]["objective"] == brief["initial_wave"]["objective"], "current_wave.objective must copy brief.initial_wave.objective")
    _require(manifest["current_wave"]["exit_criteria"] == brief["initial_wave"]["exit_criteria"], "current_wave.exit_criteria must copy brief.initial_wave.exit_criteria")


def _bullets(values: list[str], empty: str = "None.") -> list[str]:
    return [f"- {value}" for value in values] or [empty]


def render_epic_body(manifest: dict) -> str:
    """Render current truth with exactly the eight required level-two headings."""
    verify_manifest_shape(manifest)
    good = manifest["good_enough"]
    lines = [
        "## Intent and why", manifest["epic"]["intent_and_why"], "",
        "## Definition of done", *_bullets(manifest["definition_of_done"]), "",
        "## Good-enough boundary and appetite",
        f"- Mandatory quality: {good['mandatory_quality']}",
        f"- Sufficient evidence: {good['sufficient_evidence']}",
        f"- Appetite: {good['appetite']}", "",
        "## Hard constraints and fixed decisions",
        "### Hard constraints", *_bullets(manifest["hard_constraints"]),
        "### Fixed decisions", *_bullets(manifest["fixed_decisions"]), "",
        "## Current wave", f"Objective: {manifest['current_wave']['objective']}",
        "### Exit criteria", *_bullets(manifest["current_wave"]["exit_criteria"]),
        "### Runnable issues",
    ]
    for issue in manifest["current_wave"]["issues"]:
        reason = f" — {issue['hitl_reason']}" if issue["type"] == "HITL" else ""
        lines.append(f"- [ ] **[{issue['type']}]** {issue['id']}: {issue['title']}{reason}")
    lines.extend(["", "## Wave forecast (nonbinding)"])
    for item in manifest["wave_forecast"]:
        lines.append(f"- **{item['outcome']}** — {item['why_likely']}")
    if not manifest["wave_forecast"]:
        lines.append("None.")
    lines.extend(["", "## Active uncertainty register"])
    for item in manifest["uncertainty_register"]:
        lines.append(f"- **{item['unknown']}** — affects {item['affects']}; next probe: {item['next_probe']}")
    if not manifest["uncertainty_register"]:
        lines.append("None.")
    lines.extend(["", "## Parked possibilities", *_bullets(manifest["parked_possibilities"]), ""])
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", help="path to the initial issue-set manifest JSON")
    parser.add_argument("--brief", required=True, help="path to the confirmed shaped brief JSON")
    args = parser.parse_args(argv)
    try:
        manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
        brief = json.loads(Path(args.brief).read_text(encoding="utf-8"))
        verify_issue_set(manifest, brief)
    except (OSError, json.JSONDecodeError, IssueSetError) as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return 1
    print(f"initial issue set ok: {args.manifest} ({len(manifest['current_wave']['issues'])} current issue(s))")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
