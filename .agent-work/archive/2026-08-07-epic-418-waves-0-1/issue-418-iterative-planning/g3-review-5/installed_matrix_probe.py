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


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def require(label: str, condition: bool, detail: str = "") -> None:
    if not condition:
        raise AssertionError(f"{label}: {detail}")
    print(f"PASS {label}")


installer = load("g3_review_5_installer", ROOT / "scripts" / "install_constellation.py")
with tempfile.TemporaryDirectory() as raw:
    temp = Path(raw)
    skills = temp / "skills"
    project = temp / "project"
    project.mkdir()
    selected = installer.select_skills(
        ["explorer", "commander", "admiral", "to-initial-issues", "replan"],
        installer.discover_skills(),
    )
    installer.install_skills(
        selected,
        skills,
        dry_run=False,
        force=False,
        full_set=False,
        restart_message="",
        out=lambda _line: None,
        interpreter=installer.InterpreterResolution(
            sys.executable, (sys.executable,), "g3-review-5"
        ),
    )

    roles = {
        name: skills / f"constellation-{name}"
        for name in ("explorer", "commander", "admiral")
    }
    spines = {
        name: json.loads(
            (root / "templates" / f"{name.upper()}_SPINE.template.json").read_text(
                encoding="utf-8"
            )
        )
        for name, root in roles.items()
    }
    refs = [
        (
            roles["explorer"],
            spines["explorer"]["tasks"]["confirm"]["directives"]["shaped_brief"]["template"],
        ),
        (
            roles["commander"],
            spines["commander"]["tasks"]["execute"]["directives"]["replan_input"]["template"],
        ),
        (
            roles["admiral"],
            spines["admiral"]["tasks"]["execute"]["directives"]["wave_transition"]["input_template"],
        ),
        (
            roles["admiral"],
            spines["admiral"]["tasks"]["execute"]["directives"]["wave_transition"]["result_template"],
        ),
    ]
    require(
        "4/4 installed sibling paths resolve",
        len(refs) == 4 and all((root / rel).resolve().is_file() for root, rel in refs),
    )
    for role, task, cond in (
        ("explorer", "confirm", "c3"),
        ("commander", "execute", "c2"),
        ("admiral", "execute", "c3"),
    ):
        post = next(
            item
            for item in spines[role]["tasks"][task]["postconditions"]
            if item["id"] == cond
        )
        command = post["check"]["command"]
        require(
            f"{role} command installed and Windows-JSON-safe",
            post["check"]["kind"] == "command"
            and "\\" not in command.split(" ", 1)[0],
        )

    shaped = skills / "constellation-to-initial-issues" / "templates" / "SHAPED_BRIEF.template.json"
    input_path = skills / "constellation-replan" / "templates" / "REPLAN_INPUT.template.json"
    result_path = skills / "constellation-replan" / "templates" / "REPLAN_RESULT.template.json"
    source = json.loads(input_path.read_text(encoding="utf-8"))
    base_result = json.loads(result_path.read_text(encoding="utf-8"))
    replan = load(
        "g3_review_5_replan",
        skills / "constellation-replan" / "scripts" / "verify_replan.py",
    )

    def invoke(role: str, mode: str, work_id: str) -> subprocess.CompletedProcess[str]:
        helper = roles[role] / "scripts" / "verify_iterative_role_artifacts.py"
        return subprocess.run(
            [sys.executable, str(helper), mode, "--work-id", work_id],
            cwd=project,
            text=True,
            capture_output=True,
        )

    for role, mode, filename, fixture in (
        ("explorer", "explorer", "SHAPED_BRIEF.json", shaped),
        ("commander", "commander", "REPLAN_INPUT.json", input_path),
    ):
        work_id = f"{role}-g3-review-5"
        area = project / ".agent-work" / work_id
        area.mkdir(parents=True)
        require(f"{role} missing artifact refuses", invoke(role, mode, work_id).returncode != 0)
        (area / filename).write_text(
            '{"schema_version":1}', encoding="utf-8", newline="\n"
        )
        require(f"{role} malformed artifact refuses", invoke(role, mode, work_id).returncode != 0)
        shutil.copy2(fixture, area / filename)
        require(f"{role} exact artifact accepts", invoke(role, mode, work_id).returncode == 0)

    variants: dict[str, dict] = {}
    for decision in ("repair", "advance", "replan"):
        item = copy.deepcopy(base_result)
        item["decision"] = decision
        variants[decision] = item
    inapplicable = copy.deepcopy(base_result)
    inapplicable["decision"] = "replan"
    inapplicable["applicable"] = False
    inapplicable["material_changes"] = [
        {
            "surface": "intent_and_why",
            "before": "old",
            "after": "new",
            "reason": "evidence",
        }
    ]
    inapplicable["escalation"] = {
        "boundary": "intent_and_why",
        "proposed_value": "new intent",
        "reason": "human decision required",
        "authority_required": "human",
    }
    variants["inapplicable"] = inapplicable
    stopped = copy.deepcopy(base_result)
    stopped["decision"] = "stop"
    stopped["current_wave"] = None
    variants["stop"] = stopped
    for name, item in variants.items():
        replan.verify_replan_result(source, item)
        require(
            f"generic G2 validates and renders {name}",
            bool(replan.render_replan_markdown(source, item).strip()),
        )

    work_id = "admiral-g3-review-5"
    area = project / ".agent-work" / work_id
    area.mkdir(parents=True)
    require(
        "admiral missing NEXT_WAVE refuses",
        invoke("admiral", "admiral-prelaunch", work_id).returncode != 0,
    )
    (area / "NEXT_WAVE.json").write_text(
        json.dumps(
            {
                "boundary_id": "wave-1",
                "launch_id": "wave-2",
                "trigger": "wave_boundary",
            }
        ),
        encoding="utf-8",
        newline="\n",
    )
    transition = area / "transitions" / "wave-1"
    transition.mkdir(parents=True)
    shutil.copy2(input_path, transition / "REPLAN_INPUT.json")
    result_file = transition / "REPLAN_RESULT.json"
    log = area / "ADMIRAL_LOG.md"

    def set_case(item: dict, audit_lines: list[str]) -> None:
        result_file.write_text(json.dumps(item), encoding="utf-8", newline="\n")
        log.write_text(
            "\n".join(audit_lines) + ("\n" if audit_lines else ""),
            encoding="utf-8",
            newline="\n",
        )

    set_case({"schema_version": 1}, [])
    require(
        "admiral malformed result refuses",
        invoke("admiral", "admiral-prelaunch", work_id).returncode != 0,
    )

    audit_advance = "- TRANSITION | boundary=wave-1 | decision=advance | verified"
    set_case(variants["advance"], [])
    require(
        "authorized advance with zero audits causally refuses",
        invoke("admiral", "admiral-prelaunch", work_id).returncode != 0,
    )
    set_case(variants["advance"], [audit_advance, audit_advance])
    require(
        "authorized advance with duplicate audits causally refuses",
        invoke("admiral", "admiral-prelaunch", work_id).returncode != 0,
    )
    mismatch = "- TRANSITION | boundary=wave-1 | decision=replan | verified"
    set_case(variants["advance"], [mismatch])
    require(
        "authorized advance with mismatched audit causally refuses",
        invoke("admiral", "admiral-prelaunch", work_id).returncode != 0,
    )

    drift = copy.deepcopy(variants["repair"])
    drift["revised_forecast"] = []
    audit_repair = "- TRANSITION | boundary=wave-1 | decision=repair | verified"
    set_case(drift, [audit_repair])
    require(
        "repair forecast drift refuses",
        invoke("admiral", "admiral-prelaunch", work_id).returncode != 0,
    )
    drift = copy.deepcopy(variants["repair"])
    drift["current_wave"]["objective"] = "drifted"
    set_case(drift, [audit_repair])
    require(
        "repair current-wave drift refuses",
        invoke("admiral", "admiral-prelaunch", work_id).returncode != 0,
    )

    for decision in ("advance", "replan"):
        audit = f"- TRANSITION | boundary=wave-1 | decision={decision} | verified"
        set_case(variants[decision], [audit])
        run = invoke("admiral", "admiral-prelaunch", work_id)
        require(f"applicable {decision} authorizes", run.returncode == 0, run.stderr)
        require(
            f"{decision} renders dual retained Markdown",
            (transition / "CURRENT_TRUTH.md").read_text(encoding="utf-8")
            == variants[decision]["revised_epic_body"].strip() + "\n"
            and (transition / "WAVE_REVIEW.md").read_text(encoding="utf-8")
            == variants[decision]["wave_review_comment"].strip() + "\n",
        )

    for name, audit_decision in (
        ("repair", "repair"),
        ("stop", "stop"),
        ("inapplicable", "replan"),
    ):
        audit = f"- TRANSITION | boundary=wave-1 | decision={audit_decision} | verified"
        set_case(variants[name], [audit])
        require(
            f"{name} refuses next launch",
            invoke("admiral", "admiral-prelaunch", work_id).returncode != 0,
        )

    helper_path = roles["admiral"] / "scripts" / "verify_iterative_role_artifacts.py"
    helper_text = helper_path.read_text(encoding="utf-8")
    needle = "    _verify_transition_audit(work_area / \"ADMIRAL_LOG.md\", boundary_id, result[\"decision\"])\n"
    require("mutation target occurs exactly once", helper_text.count(needle) == 1)
    helper_path.write_text(
        helper_text.replace(needle, "    pass  # reviewer mutation: bypass transition audit\n"),
        encoding="utf-8",
        newline="\n",
    )
    set_case(variants["advance"], [])
    require(
        "bypassed audit makes shipped zero-audit assertion fail",
        invoke("admiral", "admiral-prelaunch", work_id).returncode == 0,
    )
    set_case(variants["advance"], [audit_advance, audit_advance])
    require(
        "bypassed audit makes shipped duplicate-audit assertion fail",
        invoke("admiral", "admiral-prelaunch", work_id).returncode == 0,
    )

print("FRESH G3 REVIEW-5 INSTALLED MATRIX COMPLETE")
