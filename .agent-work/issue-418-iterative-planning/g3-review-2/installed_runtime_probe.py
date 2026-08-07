from __future__ import annotations

import copy
import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def run(helper: Path, mode: str, work_id: str, project: Path):
    return subprocess.run(
        [sys.executable, str(helper), mode, "--work-id", work_id],
        cwd=project,
        capture_output=True,
        text=True,
    )


def require(label: str, condition: bool, detail: str = "") -> None:
    if not condition:
        raise AssertionError(f"{label}: {detail}")
    print(f"PASS {label}")


installer = load_module("g3_review_2_installer", ROOT / "scripts" / "install_constellation.py")

with tempfile.TemporaryDirectory() as tmp:
    base = Path(tmp)
    skills_root = base / "skills"
    project = base / "project"
    project.mkdir()
    selected = installer.select_skills(
        ["explorer", "commander", "admiral", "to-initial-issues", "replan"],
        installer.discover_skills(),
    )
    installer.install_skills(
        selected,
        skills_root,
        dry_run=False,
        force=False,
        full_set=False,
        restart_message="",
        out=lambda _line: None,
        interpreter=installer.InterpreterResolution(sys.executable, (sys.executable,), "probe"),
    )

    roles = {
        name: skills_root / f"constellation-{name}"
        for name in ("explorer", "commander", "admiral")
    }
    spines = {
        "explorer": json.loads((roles["explorer"] / "templates" / "EXPLORER_SPINE.template.json").read_text(encoding="utf-8")),
        "commander": json.loads((roles["commander"] / "templates" / "COMMANDER_SPINE.template.json").read_text(encoding="utf-8")),
        "admiral": json.loads((roles["admiral"] / "templates" / "ADMIRAL_SPINE.template.json").read_text(encoding="utf-8")),
    }
    refs = [
        (roles["explorer"], spines["explorer"]["tasks"]["confirm"]["directives"]["shaped_brief"]["template"]),
        (roles["commander"], spines["commander"]["tasks"]["execute"]["directives"]["replan_input"]["template"]),
        (roles["admiral"], spines["admiral"]["tasks"]["execute"]["directives"]["wave_transition"]["input_template"]),
        (roles["admiral"], spines["admiral"]["tasks"]["execute"]["directives"]["wave_transition"]["result_template"]),
    ]
    require("all four canonical installed sibling paths resolve", all((root / ref).resolve().is_file() for root, ref in refs))

    for role, task, cond in (
        ("explorer", "confirm", "c3"),
        ("commander", "execute", "c2"),
        ("admiral", "execute", "c3"),
    ):
        post = next(item for item in spines[role]["tasks"][task]["postconditions"] if item["id"] == cond)
        command = post["check"]["command"]
        require(f"{role} operative command postcondition", post["check"]["kind"] == "command" and "verify_iterative_role_artifacts.py" in command)
        require(f"{role} installed command uses JSON-safe interpreter", "\\" not in command.split(" ", 1)[0])

    shaped = skills_root / "constellation-to-initial-issues" / "templates" / "SHAPED_BRIEF.template.json"
    replan_input = skills_root / "constellation-replan" / "templates" / "REPLAN_INPUT.template.json"
    replan_result = skills_root / "constellation-replan" / "templates" / "REPLAN_RESULT.template.json"

    # Explorer missing / malformed / exact.
    wid = "explorer-probe"
    area = project / ".agent-work" / wid
    area.mkdir(parents=True)
    helper = roles["explorer"] / "scripts" / "verify_iterative_role_artifacts.py"
    require("Explorer missing brief refuses", run(helper, "explorer", wid, project).returncode != 0)
    (area / "SHAPED_BRIEF.json").write_text('{"schema_version": 1}', encoding="utf-8", newline="\n")
    require("Explorer malformed brief refuses", run(helper, "explorer", wid, project).returncode != 0)
    shutil.copy2(shaped, area / "SHAPED_BRIEF.json")
    require("Explorer exact brief accepts", run(helper, "explorer", wid, project).returncode == 0)

    # Commander missing / malformed / exact.
    wid = "commander-probe"
    area = project / ".agent-work" / wid
    area.mkdir(parents=True)
    helper = roles["commander"] / "scripts" / "verify_iterative_role_artifacts.py"
    require("Commander missing packet refuses", run(helper, "commander", wid, project).returncode != 0)
    (area / "REPLAN_INPUT.json").write_text('{"schema_version": 1}', encoding="utf-8", newline="\n")
    require("Commander malformed packet refuses", run(helper, "commander", wid, project).returncode != 0)
    shutil.copy2(replan_input, area / "REPLAN_INPUT.json")
    require("Commander exact packet accepts", run(helper, "commander", wid, project).returncode == 0)

    # Admiral specified refusal/success matrix.
    wid = "admiral-probe"
    area = project / ".agent-work" / wid
    area.mkdir(parents=True)
    helper = roles["admiral"] / "scripts" / "verify_iterative_role_artifacts.py"
    require("Admiral missing NEXT_WAVE refuses", run(helper, "admiral-prelaunch", wid, project).returncode != 0)
    next_wave = {"boundary_id": "wave-1", "launch_id": "wave-2", "trigger": "wave_boundary"}
    (area / "NEXT_WAVE.json").write_text(json.dumps(next_wave), encoding="utf-8", newline="\n")
    transition = area / "transitions" / "wave-1"
    transition.mkdir(parents=True)
    shutil.copy2(replan_input, transition / "REPLAN_INPUT.json")
    (transition / "REPLAN_RESULT.json").write_text('{"schema_version": 1}', encoding="utf-8", newline="\n")
    (area / "ADMIRAL_LOG.md").write_text("", encoding="utf-8", newline="\n")
    require("Admiral malformed result refuses", run(helper, "admiral-prelaunch", wid, project).returncode != 0)
    shutil.copy2(replan_result, transition / "REPLAN_RESULT.json")
    require("Admiral zero audit transition refuses", run(helper, "admiral-prelaunch", wid, project).returncode != 0)
    audit = "- TRANSITION | boundary=wave-1 | decision=repair | verified"
    (area / "ADMIRAL_LOG.md").write_text(audit + "\n" + audit + "\n", encoding="utf-8", newline="\n")
    require("Admiral multiple audit transitions refuse", run(helper, "admiral-prelaunch", wid, project).returncode != 0)
    broken = json.loads(replan_result.read_text(encoding="utf-8"))
    broken["revised_forecast"] = []
    (transition / "REPLAN_RESULT.json").write_text(json.dumps(broken), encoding="utf-8", newline="\n")
    (area / "ADMIRAL_LOG.md").write_text(audit + "\n", encoding="utf-8", newline="\n")
    require("Admiral repair drift refuses", run(helper, "admiral-prelaunch", wid, project).returncode != 0)
    shutil.copy2(replan_result, transition / "REPLAN_RESULT.json")
    passed = run(helper, "admiral-prelaunch", wid, project)
    require("Admiral one valid transition accepts", passed.returncode == 0, passed.stderr)
    result = json.loads(replan_result.read_text(encoding="utf-8"))
    require("Admiral renders current truth", (transition / "CURRENT_TRUTH.md").read_text(encoding="utf-8") == result["revised_epic_body"].strip() + "\n")
    require("Admiral renders wave review", (transition / "WAVE_REVIEW.md").read_text(encoding="utf-8") == result["wave_review_comment"].strip() + "\n")

    # Authority/terminal semantics not covered by the supplied runtime test.
    inapplicable = copy.deepcopy(result)
    inapplicable["decision"] = "replan"
    inapplicable["applicable"] = False
    inapplicable["material_changes"] = [
        {"surface": "intent_and_why", "before": "old", "after": "new", "reason": "evidence"}
    ]
    inapplicable["escalation"] = {
        "boundary": "intent_and_why",
        "proposed_value": "new intent",
        "reason": "human decision required",
        "authority_required": "human",
    }
    (transition / "REPLAN_RESULT.json").write_text(json.dumps(inapplicable), encoding="utf-8", newline="\n")
    (area / "ADMIRAL_LOG.md").write_text(
        "- TRANSITION | boundary=wave-1 | decision=replan | verified\n", encoding="utf-8", newline="\n"
    )
    inapplicable_run = run(helper, "admiral-prelaunch", wid, project)
    print(f"OBSERVED inapplicable fixed-boundary proposal prelaunch returncode={inapplicable_run.returncode}")

    stopped = copy.deepcopy(result)
    stopped["decision"] = "stop"
    stopped["current_wave"] = None
    (transition / "REPLAN_RESULT.json").write_text(json.dumps(stopped), encoding="utf-8", newline="\n")
    (area / "ADMIRAL_LOG.md").write_text(
        "- TRANSITION | boundary=wave-1 | decision=stop | verified\n", encoding="utf-8", newline="\n"
    )
    stop_run = run(helper, "admiral-prelaunch", wid, project)
    print(f"OBSERVED stop decision prelaunch returncode={stop_run.returncode}")

print("G3 INSTALLED RUNTIME PROBE COMPLETE")
