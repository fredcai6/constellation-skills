#!/usr/bin/env python
"""Validate Constellation bundled/project templates and path consistency."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


EXPECTED_TEMPLATE_HEADINGS = {
    "skills/pilot/templates/CREW_HANDOFF.template.md": [
        "Role",
        "Assigned Gate",
        "Task",
        "Intent Protected",
        "Close Criteria",
        "Authority",
        "Allowed Scope",
        "Specific Exclusions",
        "Required Evidence",
        "Required Verification Commands",
        "Stop Conditions",
        "Return Format",
    ],
    "skills/pilot/templates/PILOT_CHECKLIST.template.md": [
        "Workflow State",
        "Ambiguity / Authority",
        "Gates",
        "Plan Consistency Criteria",
        "Implementation Gates",
        "Project Mechanics",
        "Triage Candidates",
        "Semantic Closeout",
    ],
}

EXPECTED_TEMPLATES = sorted(
    set(EXPECTED_TEMPLATE_HEADINGS)
    | {
        "skills/workbench/templates/WORKFLOW_CLOSEOUT.template.md",
        "skills/workbench/templates/DEFAULT_CHECKLIST.template.md",
        "skills/crew/templates/IMPLEMENTER_RESULT.template.md",
        "skills/crew/templates/REVIEW_RESULT.template.md",
    }
)

STATUS_MODEL = "skills/workbench/references/status-model.md"
STATUS_REFERENCE = "Status values follow `skills/workbench/references/status-model.md`."
STATUS_TEMPLATES = [
    "skills/pilot/templates/PILOT_CHECKLIST.template.md",
    "skills/crew/templates/IMPLEMENTER_RESULT.template.md",
    "skills/crew/templates/REVIEW_RESULT.template.md",
    "skills/workbench/templates/DEFAULT_CHECKLIST.template.md",
]
AGENT_WORK_TYPO = ".agent" + "_work"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="Repository root")
    parser.add_argument(
        "--check-project-templates",
        action="store_true",
        help="Also check .agent-work/templates when present",
    )
    parser.add_argument("--verbose", action="store_true", help="Print checked files")
    return parser.parse_args()


def tracked_files(root: Path) -> list[Path]:
    try:
        result = subprocess.run(
            ["git", "ls-files"],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return [path for path in root.rglob("*") if path.is_file() and ".git" not in path.parts]
    return [root / line for line in result.stdout.splitlines() if line]


def read_text(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return None
    except UnicodeDecodeError:
        return None


def has_heading(text: str, heading: str) -> bool:
    needles = (f"## {heading}", f"### {heading}")
    return any(needle in text for needle in needles)


def check_no_agent_work_typo(root: Path, errors: list[str]) -> None:
    for path in tracked_files(root):
        text = read_text(path)
        if text is not None and AGENT_WORK_TYPO in text:
            errors.append(f"{path.relative_to(root)}: contains stale underscore agent-work path")


def check_expected_templates(root: Path, errors: list[str], verbose: bool) -> None:
    for rel in EXPECTED_TEMPLATES:
        path = root / rel
        if verbose:
            print(f"checking {rel}")
        if not path.exists():
            errors.append(f"{rel}: missing expected template")
            continue
        text = path.read_text(encoding="utf-8")
        if AGENT_WORK_TYPO in text:
            errors.append(f"{rel}: uses underscore agent-work path")
        for heading in EXPECTED_TEMPLATE_HEADINGS.get(rel, []):
            if not has_heading(text, heading):
                errors.append(f"{rel}: missing heading {heading!r}")


def check_status_model(root: Path, errors: list[str]) -> None:
    if not (root / STATUS_MODEL).exists():
        errors.append(f"{STATUS_MODEL}: missing status model")
    for rel in STATUS_TEMPLATES:
        path = root / rel
        if path.exists() and STATUS_REFERENCE not in path.read_text(encoding="utf-8"):
            errors.append(f"{rel}: missing shared status model reference")


def check_pilot_consistency(root: Path, errors: list[str]) -> None:
    checklist = root / "skills/pilot/templates/PILOT_CHECKLIST.template.md"
    if not checklist.exists():
        errors.append(f"{checklist.relative_to(root)}: missing pilot checklist template")
        return
    text = checklist.read_text(encoding="utf-8")
    if "Plan Consistency Criteria" not in text:
        errors.append(f"{checklist.relative_to(root)}: missing Plan Consistency Criteria section")
    if "recorded override reason" not in text:
        errors.append(f"{checklist.relative_to(root)}: dispatch does not require override reason for skipped criteria")


def check_closeout(root: Path, errors: list[str]) -> None:
    closeout = root / "skills/workbench/templates/WORKFLOW_CLOSEOUT.template.md"
    if not closeout.exists():
        errors.append(f"{closeout.relative_to(root)}: missing closeout template")
        return
    text = closeout.read_text(encoding="utf-8")
    if "## Template Update Candidates" not in text:
        errors.append(f"{closeout.relative_to(root)}: missing Template Update Candidates section")


def check_project_templates(root: Path, errors: list[str]) -> None:
    project_dir = root / ".agent-work" / "templates"
    if not project_dir.exists():
        return
    for path in project_dir.rglob("*.md"):
        text = path.read_text(encoding="utf-8")
        if AGENT_WORK_TYPO in text:
            errors.append(f"{path.relative_to(root)}: uses underscore agent-work path")


def main() -> int:
    args = parse_args()
    root = Path(args.root).resolve()
    errors: list[str] = []

    check_no_agent_work_typo(root, errors)
    check_expected_templates(root, errors, args.verbose)
    check_status_model(root, errors)
    check_pilot_consistency(root, errors)
    check_closeout(root, errors)
    if args.check_project_templates:
        check_project_templates(root, errors)

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    if args.verbose:
        print("Constellation template checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
