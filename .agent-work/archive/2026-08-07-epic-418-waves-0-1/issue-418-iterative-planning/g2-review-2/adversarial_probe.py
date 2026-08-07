from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]


def load_verifier():
    path = ROOT / "skills" / "replan" / "scripts" / "verify_replan.py"
    spec = importlib.util.spec_from_file_location("g2_review_2_verifier", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def load_packets():
    base = ROOT / "skills" / "replan" / "templates"
    source = json.loads((base / "REPLAN_INPUT.template.json").read_text(encoding="utf-8"))
    result = json.loads((base / "REPLAN_RESULT.template.json").read_text(encoding="utf-8"))
    return source, result


rail = load_verifier()


def refused(label: str, action) -> None:
    try:
        action()
    except rail.ReplanError as exc:
        print(f"PASS refused {label}: {exc}")
        return
    raise AssertionError(f"expected refusal: {label}")


def accepted(label: str, action) -> None:
    try:
        action()
    except rail.ReplanError as exc:
        raise AssertionError(f"expected acceptance: {label}: {exc}") from exc
    print(f"PASS accepted {label}")


source, result = load_packets()
multi = copy.deepcopy(result)
multi["decision"] = "replan"
multi["applicable"] = False
multi["material_changes"] = [
    {"surface": "intent_and_why", "before": "old", "after": "new", "reason": "wave evidence"},
    {"surface": "fixed_decisions", "before": "old", "after": "new", "reason": "wave evidence"},
]
multi["escalation"] = {
    "boundary": "intent_and_why",
    "proposed_value": "new intent",
    "reason": "human authority required",
    "authority_required": "human",
}
refused("multi-fixed packet under singular escalation schema", lambda: rail.verify_replan_result(source, multi))


collision_source, _ = load_packets()
collision_source["unlaunched_items"][0]["id"] = "A"
refused("launched/unlaunched issue identity collision", lambda: rail.verify_replan_input(collision_source))


duplicate_source, duplicate_result = load_packets()
duplicate_source["current_plan"]["parked_possibilities"] = ["same", "same"]
duplicate_result["revised_parked"] = ["same", "same"]
accepted("duplicate exact-G1 parked strings", lambda: rail.verify_replan_result(duplicate_source, duplicate_result))


graph_source, graph_result = load_packets()
issue_b = copy.deepcopy(graph_source["current_plan"]["current_wave"]["issues"][0])
issue_b["id"] = "B"
issue_b["title"] = "Issue B"
graph_source["current_plan"]["current_wave"]["issues"].append(issue_b)
graph_source["open_current_wave_issue_ids"] = ["A", "B"]
graph_result["current_wave"] = copy.deepcopy(graph_source["current_plan"]["current_wave"])
replacement = copy.deepcopy(issue_b)
replacement["id"] = "U-issue"
replacement["title"] = "Replacement U-issue"
replacement["blocks"] = ["B"]
graph_result["unlaunched_dispositions"][0].update({"action": "rewrite", "replacement": replacement})
accepted("rewritten issue dependency on result-wave issue", lambda: rail.verify_replan_result(graph_source, graph_result))


dangling = copy.deepcopy(graph_result)
dangling["unlaunched_dispositions"][0]["replacement"]["blocks"] = ["missing"]
refused("genuinely dangling assembled graph", lambda: rail.verify_replan_result(graph_source, dangling))


cycle_source = copy.deepcopy(graph_source)
cycle_source["unlaunched_items"].append({"id": "U-other", "kind": "issue"})
cycle = copy.deepcopy(graph_result)
first = copy.deepcopy(replacement)
first["blocks"] = ["U-other"]
second = copy.deepcopy(replacement)
second["id"] = "U-other"
second["title"] = "Replacement U-other"
second["blocks"] = ["U-issue"]
cycle["unlaunched_dispositions"][0]["replacement"] = first
cycle["unlaunched_dispositions"].append(
    {"id": "U-other", "action": "rewrite", "reason": "test assembled cycle", "replacement": second}
)
refused("cyclic assembled graph", lambda: rail.verify_replan_result(cycle_source, cycle))

print("ALL G2 ADVERSARIAL EXPECTATIONS PASSED")
