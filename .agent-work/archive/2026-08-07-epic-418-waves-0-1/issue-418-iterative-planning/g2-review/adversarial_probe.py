from __future__ import annotations

import copy
import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


fixtures = load("g2_test_fixtures", ROOT / "tests" / "test_replan.py")
rail = fixtures.load_verifier()


def expect_refused(label: str, fn) -> bool:
    try:
        fn()
    except rail.ReplanError as exc:
        print(f"REFUSED {label}: {exc}")
        return True
    print(f"ACCEPTED {label}")
    return False


source = fixtures.replan_input()
multi = fixtures.replan_result("replan", source=source)
multi["applicable"] = False
multi["material_changes"] = [
    {"surface": "intent_and_why", "before": "old", "after": "new", "reason": "evidence"},
    {"surface": "fixed_decisions", "before": "old", "after": "new", "reason": "evidence"},
]
multi["escalation"] = {
    "boundary": "intent_and_why",
    "proposed_value": "new intent",
    "reason": "human decision required",
    "authority_required": "human",
}
multi_refused = expect_refused(
    "two fixed deltas with only one escalation",
    lambda: rail.verify_replan_result(source, multi),
)


collision = fixtures.replan_input()
collision["unlaunched_items"][0]["id"] = "A"
collision_accepted = not expect_refused(
    "launched/unlaunched identity collision",
    lambda: rail.verify_replan_input(collision),
)


duplicate = fixtures.replan_input()
duplicate["current_plan"]["parked_possibilities"] = ["same", "same"]
duplicate_result = fixtures.replan_result("advance", source=duplicate)
duplicate_result["revised_parked"] = ["same", "same"]
duplicate_refused = expect_refused(
    "exact G1 parked shape with duplicate nonempty values",
    lambda: rail.verify_replan_result(duplicate, duplicate_result),
)


dependency_source = fixtures.replan_input(open_ids=["A", "B"])
dependency_source["current_plan"]["current_wave"]["issues"].append(fixtures.issue("B"))
dependency_result = fixtures.replan_result("replan", source=dependency_source)
replacement = fixtures.issue("U-issue")
replacement["blocks"] = ["B"]
dependency_result["unlaunched_dispositions"][0].update(
    {"action": "rewrite", "replacement": replacement}
)
replacement_refused = expect_refused(
    "G1 issue replacement whose dependency exists in the result wave",
    lambda: rail.verify_replan_result(dependency_source, dependency_result),
)


print(
    {
        "multi_fixed_missing_escalation_accepted": not multi_refused,
        "launched_unlaunched_collision_accepted": collision_accepted,
        "exact_g1_duplicate_parked_refused": duplicate_refused,
        "valid_contextual_issue_dependency_refused": replacement_refused,
    }
)
