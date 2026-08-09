#!/usr/bin/env python
"""Verify all ten frozen iterative-planning acceptance items offline."""

from __future__ import annotations

import argparse
import copy
import importlib.util
import json
import sys
from pathlib import Path


ACCEPTANCE_ITEMS = (
    "canonical_renamed_install",
    "zero_edge_validity",
    "forecast_non_filing",
    "eight_required_headings",
    "all_four_exits",
    "blocking_repair_holds_forecast",
    "evidence_only_creates_no_issue",
    "fixed_boundaries_preserve_or_escalate",
    "deny_harness_zero_calls",
    "relevant_and_full_tests_green",
)


class AcceptanceError(Exception):
    """Raised when any frozen acceptance item lacks executable evidence."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise AcceptanceError(message)


def _load(name: str, path: Path):
    _require(path.is_file(), f"acceptance seam missing: {path}")
    spec = importlib.util.spec_from_file_location(name, path)
    _require(spec is not None and spec.loader is not None, f"cannot load acceptance seam: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _json(path: Path) -> dict:
    _require(path.is_file(), f"acceptance artifact missing: {path}")
    value = json.loads(path.read_text(encoding="utf-8"))
    _require(isinstance(value, dict), f"acceptance artifact must be an object: {path}")
    return value


def verify_acceptance(work_id: str, root: Path | None = None) -> dict[str, str]:
    root = Path.cwd() if root is None else Path(root)
    demo_verifier = _load("acceptance_demo_verifier", root / "scripts" / "verify_epic_418_demo.py")
    try:
        demo_verifier.verify_demo(work_id, root=root)
    except demo_verifier.DemoError as exc:
        raise AcceptanceError(str(exc)) from exc
    demo = root / ".agent-work" / work_id / demo_verifier.DEMO_NAME
    brief = _json(demo / "SHAPED_BRIEF.json")
    manifest = _json(demo / "INITIAL_ISSUE_SET.json")
    source = _json(demo / "REPLAN_INPUT.json")
    repair = _json(demo / "REPLAN_RESULT_REPAIR.json")
    variants = _json(demo / "REPLAN_VARIANTS.json")
    deny = _json(demo / "DENY_RECEIPT.json")
    tests = _json(demo / "TEST_RECEIPT.json")
    g1 = _load("acceptance_g1", root / "scripts" / "verify_issue_set.py")
    replan = _load("acceptance_g2", root / "skills" / "replan" / "scripts" / "verify_replan.py")
    results: dict[str, str] = {}

    _require((root / "skills" / "to-initial-issues" / "SKILL.md").is_file(), "canonical initial skill missing")
    _require(not (root / "skills" / "to-issues").exists(), "legacy initial skill still live")
    results[ACCEPTANCE_ITEMS[0]] = "canonical source and installed naming contract present; legacy source absent"

    zero_edges = copy.deepcopy(manifest)
    for issue in zero_edges["current_wave"]["issues"]:
        issue["blocks"] = []
    g1.verify_issue_set(zero_edges, brief)
    results[ACCEPTANCE_ITEMS[1]] = "public G1 verifier accepts zero dependency edges"

    forbidden = {"id", "type", "blocks", "body", "hitl_reason"}
    _require(all(not (set(item) & forbidden) for item in manifest["wave_forecast"]), "forecast contains fileable issue fields")
    results[ACCEPTANCE_ITEMS[2]] = "forecast entries are structurally non-fileable outcomes"

    rendered = (demo / "ISSUE_418_REGENERATED.md").read_text(encoding="utf-8")
    headings = [line for line in rendered.splitlines() if line.startswith("## ")]
    _require(len(headings) == 8, "initial rendering must contain exactly eight level-two headings")
    results[ACCEPTANCE_ITEMS[3]] = "exact eight-heading public G1 rendering"

    _require(set(variants) == {"advance", "repair", "replan", "stop", "inapplicable"}, "replan variant set incomplete")
    for decision in ("advance", "repair", "replan", "stop"):
        replan.verify_replan_result(source, variants[decision])
        _require(bool(replan.render_replan_markdown(source, variants[decision]).strip()), f"{decision} did not render")
    results[ACCEPTANCE_ITEMS[4]] = "all four generic G2 exits validate and render"

    _require(repair["decision"] == "repair" and repair["current_wave"] == source["current_plan"]["current_wave"] and repair["revised_forecast"] == source["current_plan"]["wave_forecast"], "blocking repair did not hold current wave and forecast")
    results[ACCEPTANCE_ITEMS[5]] = "blocking repair holds current wave and forecast exactly"

    evidence = next(item for item in repair["discrepancy_dispositions"] if item["id"] == "D-evidence")
    _require(evidence["action"] == "record_evidence_only" and evidence["issue_created"] is False, "evidence-only discrepancy created an issue")
    results[ACCEPTANCE_ITEMS[6]] = "evidence-only disposition explicitly creates no issue"

    fixed = ("intent_and_why", "definition_of_done", "good_enough", "hard_constraints", "fixed_decisions")
    for field in fixed:
        before = source["current_plan"]["epic"][field] if field == "intent_and_why" else source["current_plan"][field]
        after = repair["current_wave"] and (source["current_plan"]["epic"][field] if field == "intent_and_why" else source["current_plan"][field])
        _require(before == after, f"applicable repair changed fixed boundary {field}")
    replan.verify_replan_result(source, variants["inapplicable"])
    _require(variants["inapplicable"]["applicable"] is False and variants["inapplicable"]["escalation"]["authority_required"] == "human", "fixed-boundary proposal did not escalate")
    results[ACCEPTANCE_ITEMS[7]] = "applicable packet preserves fixed fields; changed intent is inapplicable and escalates to human"

    demo_verifier.verify_deny_receipt(deny)
    results[ACCEPTANCE_ITEMS[8]] = "raise-on-write tracker, failing gh shim, and network/subprocess spies recorded zero calls"

    _require(tests["relevant"]["exit"] == 0 and tests["full"]["exit"] == 0, "relevant/full tests are not both green")
    results[ACCEPTANCE_ITEMS[9]] = "stamped relevant and full test commands both exited zero"
    _require(tuple(results) == ACCEPTANCE_ITEMS, "acceptance result ordering drifted")
    return results


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work-id", required=True)
    args = parser.parse_args(argv)
    try:
        results = verify_acceptance(args.work_id)
    except (AcceptanceError, OSError, json.JSONDecodeError, AssertionError, StopIteration) as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return 1
    for index, name in enumerate(ACCEPTANCE_ITEMS, start=1):
        print(f"PASS {index:02d} {name}: {results[name]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
