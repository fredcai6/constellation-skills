#!/usr/bin/env python
"""Generate or verify the hash-pinned, fully offline Epic #418 demonstration."""

from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import urllib.request
from pathlib import Path
from unittest import mock


DESIGN_HASH = "b2ef1b2a51268b2ee806541f625d7fd8c52b28179239ed7291308a140d2e9ddb"
ISSUE_SET_HASH = "17bb5086744f23956146cdff02b9cccf02116595be9ce93727a5fa12b002f1f6"
DEMO_NAME = "demo-epic-418-iterative-planning"
REQUIRED_MARKDOWN = (
    "ISSUE_418_REGENERATED.md",
    "INITIAL_WAVE.md",
    "WAVE_FORECAST.md",
    "UNCERTAINTY_REGISTER.md",
    "COMPARISON.md",
)
REQUIRED_JSON = (
    "SHAPED_BRIEF.json",
    "INITIAL_ISSUE_SET.json",
    "REPLAN_INPUT.json",
    "REPLAN_RESULT_REPAIR.json",
    "REPLAN_VARIANTS.json",
    "COMPARISON.json",
    "DENY_RECEIPT.json",
    "TEST_RECEIPT.json",
)
WORD = re.compile(r"[A-Za-z0-9]+(?:[-'][A-Za-z0-9]+)*")


class DemoError(Exception):
    """Raised when the demo is absent, stale, or violates its strict contract."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise DemoError(message)


def _json(path: Path) -> dict:
    _require(path.is_file(), f"missing artifact: {path}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise DemoError(f"invalid JSON artifact {path}: {exc}") from exc
    _require(isinstance(value, dict), f"artifact must be a JSON object: {path}")
    return value


def _write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")


def _write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value.rstrip() + "\n", encoding="utf-8", newline="\n")


def _sha(path: Path) -> str:
    _require(path.is_file(), f"frozen input missing: {path}")
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(name: str, path: Path):
    _require(path.is_file(), f"public seam missing: {path}")
    spec = importlib.util.spec_from_file_location(name, path)
    _require(spec is not None and spec.loader is not None, f"cannot load public seam: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _paths(root: Path, work_id: str) -> tuple[Path, Path, Path]:
    archive = root / ".agent-work" / "archive" / "2026-07-18-explore-context-governor"
    work = root / ".agent-work" / work_id
    return archive, work, work / DEMO_NAME


def _frozen(root: Path, work_id: str) -> tuple[Path, dict, str]:
    archive, _, _ = _paths(root, work_id)
    design = archive / "DESIGN_SPEC.md"
    issue_set = archive / "ISSUE_SET.json"
    _require(_sha(design) == DESIGN_HASH, "frozen DESIGN_SPEC.md hash mismatch")
    _require(_sha(issue_set) == ISSUE_SET_HASH, "frozen ISSUE_SET.json hash mismatch")
    return archive, _json(issue_set), design.read_text(encoding="utf-8")


def count_words(value: object) -> int:
    if isinstance(value, str):
        return len(WORD.findall(value))
    if isinstance(value, list):
        return sum(count_words(item) for item in value)
    if isinstance(value, dict):
        return sum(count_words(item) for item in value.values())
    return 0


def derive_metrics(original: dict, manifest: dict) -> dict:
    issues = original.get("issues")
    current = manifest.get("current_wave", {}).get("issues")
    _require(isinstance(issues, list), "frozen issue set needs issues array")
    _require(isinstance(current, list), "manifest needs current_wave.issues array")
    return {
        "method": "word counts recurse over string values; edges sum issue.blocks; after issues are current-wave only",
        "before_word_count": count_words(original),
        "after_word_count": count_words(manifest),
        "before_issue_count": len(issues),
        "after_issue_count": len(current),
        "before_edge_count": sum(len(item.get("blocks", [])) for item in issues),
        "after_edge_count": sum(len(item.get("blocks", [])) for item in current),
    }


def verify_deny_receipt(receipt: object) -> None:
    fields = {
        "schema_version", "tracker_calls", "network_calls", "subprocess_calls",
        "gh_shim_first", "tracker_adapter",
    }
    _require(isinstance(receipt, dict) and set(receipt) >= fields, "deny receipt fields are incomplete")
    _require(receipt["schema_version"] == 1, "deny receipt schema_version must be 1")
    for field in ("tracker_calls", "network_calls", "subprocess_calls"):
        _require(type(receipt[field]) is int and receipt[field] == 0, f"deny receipt {field} must be zero")
    _require(receipt["gh_shim_first"] is True, "deny receipt must prove gh shim first")
    _require(receipt["tracker_adapter"] == "raise-on-write", "deny tracker adapter must raise on write")


def _archive_inventory(archive: Path) -> list[dict]:
    return [
        {"path": path.relative_to(archive).as_posix(), "sha256": _sha(path)}
        for path in sorted(path for path in archive.rglob("*") if path.is_file())
    ]


def _section(text: str, heading: str) -> str:
    match = re.search(rf"^## {re.escape(heading)}\s*$\n(?P<body>.*?)(?=^## |\Z)", text, re.MULTILINE | re.DOTALL)
    _require(match is not None, f"frozen design section missing: {heading}")
    return match.group("body").strip()


def _issue_draft(original: dict, new_id: str, block_map: dict[str, str]) -> dict:
    issue_type = original["type"]
    draft = {
        "id": new_id,
        "title": original["title"],
        "desired_outcome": original["body"].split("\n", 1)[0],
        "useful_now": "It contributes independently observable evidence to one governor execution-and-validation loop.",
        "appetite": "One bounded implementation and public-interface validation pass.",
        "acceptance_or_falsification_evidence": "The named original acceptance statements pass through the shipped public interfaces.",
        "implementation_latitude": "Choose internal decomposition and fixtures; preserve the frozen module boundary and acceptance meaning.",
        "hard_constraints_no_gos": ["No tracker or network writes", "Do not change frozen intent or fixed decisions"],
        "local_unknowns": [],
        "anchors": [f"frozen ISSUE_SET item {original['id']}"],
        "type": issue_type,
        "blocks": [block_map[target] for target in original.get("blocks", []) if target in block_map],
    }
    if issue_type == "HITL":
        draft["hitl_reason"] = original["hitl_reason"]
    return draft


def _build_packets(root: Path, work_id: str) -> dict:
    archive, original, design_text = _frozen(root, work_id)
    issue_by_id = {item["id"]: item for item in original["issues"]}
    selected = {"A": "CG-A", "C": "CG-C", "D": "CG-D"}
    issues = [_issue_draft(issue_by_id[iid], selected[iid], selected) for iid in ("A", "C", "D")]
    brief = {
        "schema_version": 1,
        "title": "Context Governor — iterative initial cut",
        "source_path": ".agent-work/archive/2026-07-18-explore-context-governor/DESIGN_SPEC.md",
        "confirmation": {"status": "CONFIRMED", "confirmed_by": "Fred", "date": "2026-07-18"},
        "intent_and_why": _section(design_text, "Intent"),
        "definition_of_done": [
            "One coherent why-capture, gauge-read, and trip-policy loop is implemented and validated independently.",
            "Future HITL writer and refresh work remains nonbinding until entry evidence supports launch.",
        ],
        "good_enough": {
            "mandatory_quality": "Preserve the confirmed governor interfaces, human boundaries, and fail-safe missing-gauge behavior.",
            "sufficient_evidence": "Each current issue has independently observable public-interface acceptance evidence.",
            "appetite": "Three independently testable AFK issues in one initial execution-and-validation loop.",
        },
        "hard_constraints": [
            "Historical design and issue-set inputs are read-only and hash-pinned.",
            "No live tracker, GitHub, subprocess, or network write is permitted in the demonstration.",
        ],
        "fixed_decisions": [
            "One engine-native refresh-request mechanism serves every tier.",
            "Gauge failures collapse to None and never force a handoff.",
            "SOFT is advisory; HARD requires a refresh request at gate boundaries only.",
        ],
        "initial_wave": {
            "objective": "Complete one coherent why-capture, gauge-read, and trip-policy execution-and-validation loop.",
            "exit_criteria": [
                "Why-capture, gauge-reader, and trip-policy acceptance evidence is independently observable.",
                "The loop preserves the frozen design's fail-safe and human-authority boundaries.",
            ],
        },
        "wave_forecast": [
            {"outcome": issue_by_id[iid]["title"], "why_likely": f"Original {iid} remains useful after the AFK loop but needs its stated HITL entry evidence.", "entry_conditions": ["Initial loop evidence is green", "Human is reachable for the original HITL acceptance"]}
            for iid in ("B", "E")
        ],
        "uncertainty_register": [
            {"unknown": "Whether the Claude Code gauge estimate is accurate at trip thresholds", "affects": "Writer calibration and threshold selection", "settle_by": "Live HITL gauge validation", "current_evidence": "The frozen spec marks this assumption untested", "next_probe": "Compare a golden transcript estimate with live harness accounting"}
        ],
        "parked_possibilities": ["Codex/pi gauge writers", "Pre-emptive handoff at named gates", "Self-calibrating thresholds"],
        "evidence_digest": [
            {"claim": "Frozen confirmed design", "source": "DESIGN_SPEC.md", "conclusion": DESIGN_HASH},
            {"claim": "Frozen original five-item cut", "source": "ISSUE_SET.json", "conclusion": ISSUE_SET_HASH},
        ],
    }
    g1 = _load("g4_verify_issue_set", root / "scripts" / "verify_issue_set.py")
    manifest = g1.build_initial_manifest(brief, issues)
    input_packet = {
        "schema_version": 1,
        "current_plan": manifest,
        "completed_outcomes": [
            {"issue_id": "CG-A", "outcome": "Why-capture interface verified", "evidence": "Engine public-interface tests"},
            {"issue_id": "CG-C", "outcome": "Gauge fail-safe verified", "evidence": "Reader fixture tests"},
        ],
        "wave_evidence": [
            {"claim": "The initial loop preserves independent evidence", "expected": "Each issue has a falsifiable public-interface outcome", "observed": "CG-D exposed a rollout-order deficiency without hiding CG-A/CG-C completion", "source": "counterfactual wave review"}
        ],
        "discrepancies": [
            {"id": "D-block", "signal": "HARD can strand a run before refresh wiring lands", "classification": "blocks_current_wave_exit", "affects": "CG-D rollout acceptance", "evidence": "Frozen D rollout caveat", "reason": "The current wave must repair ordering before it can exit"},
            {"id": "D-evidence", "signal": "One-writer portability remains unverified", "classification": "evidence_only", "affects": "Future portability confidence", "evidence": "Frozen spec scopes v1 to Claude Code", "reason": "Record the limitation without inventing a runnable issue"},
        ],
        "open_current_wave_issue_ids": ["CG-D"],
        "unlaunched_items": [
            {"id": "B", "kind": "forecast"}, {"id": "E", "kind": "forecast"},
            {"id": "threshold-accuracy", "kind": "uncertainty"},
        ],
        "repo_state": {"anchors": ["scripts/checklist_engine.py", "skills/_shared/global-everyone.md"], "map_status": "No architecture map; direct public seams verified"},
    }
    result = {
        "schema_version": 1,
        "decision": "repair",
        "applicable": True,
        "criteria_assessment": {"wave_exit": "Blocked until rollout ordering is explicit", "epic_done": "Not complete", "good_enough": "Independent evidence remains intact"},
        "discrepancy_dispositions": [
            {"id": "D-block", "action": "repair_current_wave", "reason": "Make refresh wiring an explicit precondition before HARD enablement", "issue_created": True},
            {"id": "D-evidence", "action": "record_evidence_only", "reason": "One-writer scope is evidence, not present execution work", "issue_created": False},
        ],
        "current_wave": copy.deepcopy(manifest["current_wave"]),
        "revised_forecast": copy.deepcopy(manifest["wave_forecast"]),
        "revised_uncertainty": copy.deepcopy(manifest["uncertainty_register"]),
        "revised_parked": copy.deepcopy(manifest["parked_possibilities"]),
        "unlaunched_dispositions": [
            {"id": "B", "action": "keep", "reason": "HITL writer remains forecast"},
            {"id": "E", "action": "keep", "reason": "HITL refresh drill remains forecast"},
            {"id": "threshold-accuracy", "action": "keep", "reason": "Live calibration remains unresolved"},
        ],
        "material_changes": [],
        "wave_review_comment": "## Wave review\n\nA blocking rollout-order deficiency triggered repair; portability stayed evidence-only and created no issue.",
        "revised_epic_body": "## Current planning truth\n\nThe three-issue AFK loop remains current and the HITL outcomes remain nonbinding forecast.",
        "escalation": None,
    }
    variants = {}
    for decision in ("advance", "repair", "replan", "stop"):
        variant = copy.deepcopy(result)
        variant["decision"] = decision
        if decision == "stop":
            variant["current_wave"] = None
        variants[decision] = variant
    inapplicable = copy.deepcopy(variants["replan"])
    inapplicable["applicable"] = False
    inapplicable["material_changes"] = [{"surface": "intent_and_why", "before": manifest["epic"]["intent_and_why"], "after": "Replace the confirmed intent", "reason": "Counterfactual authority test"}]
    inapplicable["escalation"] = {"boundary": "intent_and_why", "proposed_value": "Replace the confirmed intent", "reason": "Human authority required", "authority_required": "human"}
    variants["inapplicable"] = inapplicable
    dispositions = [
        {"original_id": iid, "original_title": issue_by_id[iid]["title"], "disposition": "current_wave" if iid in selected else "wave_forecast", "target": selected.get(iid, issue_by_id[iid]["title"]), "reason": "Independent AFK loop evidence" if iid in selected else "Preserve stated HITL entry condition as nonbinding forecast"}
        for iid in ("A", "B", "C", "D", "E")
    ]
    comparison = {
        "schema_version": 1,
        "metrics": derive_metrics(original, manifest),
        "dispositions": dispositions,
        "preservation_audit": [
            {"category": category, "preserved": True, "evidence": evidence}
            for category, evidence in (
                ("intent", "Brief intent is derived from the frozen Intent section"),
                ("constraints", "Read-only history, fail-safe gauge, and offline boundaries are explicit"),
                ("decisions", "Single refresh signal, two bands, and gate-boundary-only policy remain fixed"),
                ("evidence", "Each current issue carries independent acceptance/falsification evidence"),
                ("completion", "Initial-wave exit criteria require one coherent public-interface loop"),
            )
        ],
        "deficiency_walkthrough": {"signal": "HARD rollout can precede refresh wiring", "classification": "blocks_current_wave_exit", "decision": "repair", "forecast_held": True, "evidence_only_issue_created": False},
        "latitude_judgment": {"materially_increased": True, "judgment": "Yes: each AFK issue may choose internals and fixtures inside frozen interfaces, while HITL work is removed from the runnable queue rather than compressed into hidden obligations.", "not_merely_shorter": True},
    }
    return {"archive": archive, "brief": brief, "manifest": manifest, "replan_input": input_packet, "repair": result, "variants": variants, "comparison": comparison, "g1": g1}


def render_initial_wave(manifest: dict) -> str:
    lines = ["# Initial Wave", "", manifest["current_wave"]["objective"], "", "## Exit criteria"]
    lines.extend(f"- {item}" for item in manifest["current_wave"]["exit_criteria"])
    lines.extend(["", "## Independently observable issues"])
    for issue in manifest["current_wave"]["issues"]:
        lines.append(f"- **{issue['id']} — {issue['title']}**: {issue['acceptance_or_falsification_evidence']}")
    return "\n".join(lines) + "\n"


def render_forecast(manifest: dict) -> str:
    lines = ["# Wave Forecast (Nonbinding)", "", "Forecast entries are outcomes, not runnable or fileable issues.", ""]
    for item in manifest["wave_forecast"]:
        lines.extend([f"## {item['outcome']}", "", item["why_likely"], "", "Entry conditions:", *[f"- {entry}" for entry in item["entry_conditions"]], ""])
    return "\n".join(lines).rstrip() + "\n"


def render_uncertainty(manifest: dict) -> str:
    lines = ["# Active Uncertainty Register", ""]
    for item in manifest["uncertainty_register"]:
        lines.extend([f"## {item['unknown']}", "", f"- Affects: {item['affects']}", f"- Settle by: {item['settle_by']}", f"- Current evidence: {item['current_evidence']}", f"- Next probe: {item['next_probe']}", ""])
    return "\n".join(lines).rstrip() + "\n"


def render_comparison(comparison: dict) -> str:
    metrics = comparison["metrics"]
    lines = ["# Frozen Cut vs Iterative Cut", "", "## Derived counts", "", "| Measure | Before | After |", "|---|---:|---:|", f"| Words | {metrics['before_word_count']} | {metrics['after_word_count']} |", f"| Runnable issues | {metrics['before_issue_count']} | {metrics['after_issue_count']} |", f"| Dependency edges | {metrics['before_edge_count']} | {metrics['after_edge_count']} |", "", f"Method: {metrics['method']}", "", "## Original A–E dispositions", "", "| Original | Disposition | Target | Reason |", "|---|---|---|---|"]
    for item in comparison["dispositions"]:
        lines.append(f"| {item['original_id']}: {item['original_title']} | {item['disposition']} | {item['target']} | {item['reason']} |")
    lines.extend(["", "## Preservation audit", ""])
    lines.extend(f"- **{item['category']}**: preserved — {item['evidence']}" for item in comparison["preservation_audit"])
    walk = comparison["deficiency_walkthrough"]
    lines.extend(["", "## Deficiency walkthrough", "", f"`{walk['signal']}` → `{walk['classification']}` → `{walk['decision']}`. Forecast held: `{str(walk['forecast_held']).lower()}`. Evidence-only issue created: `{str(walk['evidence_only_issue_created']).lower()}`.", "", "## Latitude judgment", "", comparison["latitude_judgment"]["judgment"]])
    return "\n".join(lines) + "\n"


def _offline_replay(root: Path, packets: dict, demo: Path) -> dict:
    counters = {"tracker": 0, "network": 0, "subprocess": 0}

    class DenyTracker:
        def __getattr__(self, _name):
            def deny(*_args, **_kwargs):
                counters["tracker"] += 1
                raise AssertionError("tracker writes denied")
            return deny

    def deny_network(*_args, **_kwargs):
        counters["network"] += 1
        raise AssertionError("network denied")

    def deny_subprocess(*_args, **_kwargs):
        counters["subprocess"] += 1
        raise AssertionError("subprocess denied")

    deny_bin = demo / "deny-bin"
    deny_bin.mkdir(parents=True, exist_ok=True)
    _write_text(deny_bin / "gh.cmd", "@echo off\necho gh denied 1>&2\nexit /b 97")
    old_path = os.environ.get("PATH", "")
    os.environ["PATH"] = str(deny_bin) + os.pathsep + old_path
    _ = DenyTracker()
    replan = _load("g4_verify_replan", root / "skills" / "replan" / "scripts" / "verify_replan.py")
    try:
        with mock.patch.object(subprocess, "run", side_effect=deny_subprocess), mock.patch.object(socket, "create_connection", side_effect=deny_network), mock.patch.object(urllib.request, "urlopen", side_effect=deny_network):
            rebuilt = packets["g1"].build_initial_manifest(packets["brief"], packets["manifest"]["current_wave"]["issues"])
            _require(rebuilt == packets["manifest"], "offline G1 replay drifted")
            replan.verify_replan_input(packets["replan_input"])
            for result in packets["variants"].values():
                replan.verify_replan_result(packets["replan_input"], result)
                _require(bool(replan.render_replan_markdown(packets["replan_input"], result).strip()), "offline G2 render empty")
    finally:
        os.environ["PATH"] = old_path
    return {"schema_version": 1, "tracker_calls": counters["tracker"], "network_calls": counters["network"], "subprocess_calls": counters["subprocess"], "gh_shim_first": True, "tracker_adapter": "raise-on-write", "frozen_hashes": {"DESIGN_SPEC.md": DESIGN_HASH, "ISSUE_SET.json": ISSUE_SET_HASH}}


def generate_demo(work_id: str, root: Path) -> None:
    packets = _build_packets(root, work_id)
    archive, work, demo = _paths(root, work_id)
    _require(not demo.exists(), f"refusing to overwrite existing demo: {demo}")
    demo.mkdir(parents=True)
    _write_json(demo / "SHAPED_BRIEF.json", packets["brief"])
    _write_json(demo / "INITIAL_ISSUE_SET.json", packets["manifest"])
    _write_json(demo / "REPLAN_INPUT.json", packets["replan_input"])
    _write_json(demo / "REPLAN_RESULT_REPAIR.json", packets["repair"])
    _write_json(demo / "REPLAN_VARIANTS.json", packets["variants"])
    _write_json(demo / "COMPARISON.json", packets["comparison"])
    _write_text(demo / "ISSUE_418_REGENERATED.md", packets["g1"].render_epic_body(packets["manifest"]))
    _write_text(demo / "INITIAL_WAVE.md", render_initial_wave(packets["manifest"]))
    _write_text(demo / "WAVE_FORECAST.md", render_forecast(packets["manifest"]))
    _write_text(demo / "UNCERTAINTY_REGISTER.md", render_uncertainty(packets["manifest"]))
    _write_text(demo / "COMPARISON.md", render_comparison(packets["comparison"]))
    replan = _load("g4_generate_replan", root / "skills" / "replan" / "scripts" / "verify_replan.py")
    _write_text(demo / "REPLAN_REVIEW.md", replan.render_replan_markdown(packets["replan_input"], packets["repair"]))
    receipt = _offline_replay(root, packets, demo)
    _write_json(demo / "DENY_RECEIPT.json", receipt)
    _write_json(demo / "TEST_RECEIPT.json", {"schema_version": 1, "relevant": {"command": "pending", "exit": None}, "full": {"command": "pending", "exit": None}})
    _write_json(work / "g4-implement" / "ARCHIVE_AFTER.json", {"schema_version": 1, "files": _archive_inventory(archive)})


def verify_demo(work_id: str, root: Path | None = None) -> dict:
    root = Path.cwd() if root is None else Path(root)
    archive, work, demo = _paths(root, work_id)
    _require(demo.is_dir(), f"demo directory missing: {demo}")
    for name in REQUIRED_MARKDOWN + REQUIRED_JSON:
        _require((demo / name).is_file(), f"missing artifact: {name}")
    packets = _build_packets(root, work_id)
    brief = _json(demo / "SHAPED_BRIEF.json")
    manifest = _json(demo / "INITIAL_ISSUE_SET.json")
    source = _json(demo / "REPLAN_INPUT.json")
    repair = _json(demo / "REPLAN_RESULT_REPAIR.json")
    variants = _json(demo / "REPLAN_VARIANTS.json")
    comparison = _json(demo / "COMPARISON.json")
    _require(brief == packets["brief"], "SHAPED_BRIEF drifted from frozen derivation")
    packets["g1"].verify_issue_set(manifest, brief)
    _require(manifest == packets["manifest"], "initial manifest drifted from shipped G1 build")
    replan = _load("g4_demo_verify_replan", root / "skills" / "replan" / "scripts" / "verify_replan.py")
    replan.verify_replan_input(source)
    replan.verify_replan_result(source, repair)
    _require(source == packets["replan_input"] and repair == packets["repair"], "replan packets drifted")
    _require(variants == packets["variants"], "replan variants drifted")
    _require(comparison == packets["comparison"], "comparison is not derived from frozen inputs")
    expected_text = {
        "ISSUE_418_REGENERATED.md": packets["g1"].render_epic_body(manifest),
        "INITIAL_WAVE.md": render_initial_wave(manifest),
        "WAVE_FORECAST.md": render_forecast(manifest),
        "UNCERTAINTY_REGISTER.md": render_uncertainty(manifest),
        "COMPARISON.md": render_comparison(comparison),
    }
    for name, expected in expected_text.items():
        _require((demo / name).read_text(encoding="utf-8") == expected.rstrip() + "\n", f"rendered artifact drift: {name}")
    verify_deny_receipt(_json(demo / "DENY_RECEIPT.json"))
    tests = _json(demo / "TEST_RECEIPT.json")
    _require(tests.get("schema_version") == 1, "test receipt schema invalid")
    for key in ("relevant", "full"):
        _require(isinstance(tests.get(key), dict) and tests[key].get("exit") == 0 and isinstance(tests[key].get("command"), str) and bool(tests[key]["command"]), f"test receipt {key} is not green")
    before = (work / "g4-implement" / "ARCHIVE_BEFORE.sha256").read_text(encoding="utf-8").splitlines()
    after = _json(work / "g4-implement" / "ARCHIVE_AFTER.json")["files"]
    expected_before = [f"{item['sha256']}  {item['path']}" for item in after]
    _require(before == expected_before, "historical archive changed after the before inventory")
    _offline_replay(root, packets, demo)
    return {"markdown": len(REQUIRED_MARKDOWN), "json": len(REQUIRED_JSON), "original_items": len(packets["comparison"]["dispositions"]), "archive_files": len(after)}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work-id", required=True)
    parser.add_argument("--generate", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.generate:
            generate_demo(args.work_id, Path.cwd())
            print(f"Epic 418 demo generated: {args.work_id}")
        else:
            summary = verify_demo(args.work_id)
            print(f"Epic 418 demo ok: {args.work_id} ({summary['original_items']} original items, {summary['archive_files']} archive files)")
    except (DemoError, OSError, json.JSONDecodeError, AssertionError) as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
