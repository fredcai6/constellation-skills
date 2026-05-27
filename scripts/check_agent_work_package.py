#!/usr/bin/env python
"""Validate an active or archived .agent-work/<work-id> package."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


PILOT_HEADINGS = [
    "Workflow State",
    "Ambiguity / Authority",
    "Gates",
    "Plan Consistency Criteria",
    "Implementation Gates",
    "Project Mechanics",
    "Semantic Closeout",
]

CREW_HANDOFF_HEADINGS = [
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
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="Repository root")
    parser.add_argument("--work-id", required=True, help="Work package id under .agent-work")
    parser.add_argument("--archive", action="store_true", help="Check .agent-work/archive/*-<work-id>")
    parser.add_argument("--verbose", action="store_true", help="Print checked files")
    return parser.parse_args()


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def has_heading(text: str, heading: str) -> bool:
    return f"## {heading}" in text or f"### {heading}" in text


def section(text: str, heading: str) -> str:
    match = re.search(rf"^##+ {re.escape(heading)}\s*$", text, re.MULTILINE)
    if not match:
        return ""
    next_match = re.search(r"^##+ .+$", text[match.end() :], re.MULTILINE)
    if not next_match:
        return text[match.end() :]
    return text[match.end() : match.end() + next_match.start()]


def error(errors: list[str], path: Path, message: str, root: Path) -> None:
    errors.append(f"{path.relative_to(root)}: {message}")


def check_headings(path: Path, headings: list[str], errors: list[str], root: Path) -> None:
    text = read(path)
    for heading in headings:
        if not has_heading(text, heading):
            error(errors, path, f"missing heading {heading!r}", root)


def check_status_reasons(path: Path, errors: list[str], root: Path) -> None:
    for line in read(path).lower().splitlines():
        if "<" in line:
            continue
        if "skipped" in line and "because" not in line:
            error(errors, path, "skipped status lacks because <reason>", root)
        if "blocked" in line and not any(word in line for word in ("because", "blocker", "next action", "authority")):
            error(errors, path, "blocked status lacks blocker/authority/next action", root)


def check_implementation_gates(path: Path, errors: list[str], root: Path) -> None:
    text = read(path)
    gates_section = section(text, "Implementation Gates")
    if not gates_section.strip():
        return
    gates = re.findall(r"^### Implementation Gate\s+\S+:", gates_section, flags=re.MULTILINE)
    if not gates:
        return
    for gate in re.split(r"^### Implementation Gate\s+\S+:", gates_section, flags=re.MULTILINE)[1:]:
        for label in ("Close criteria", "Required evidence", "Stop conditions"):
            if label.lower() not in gate.lower():
                error(errors, path, f"implementation gate missing {label}", root)


def required_field_has_placeholder(text: str, heading: str) -> bool:
    body = section(text, heading).strip()
    return not body or bool(re.fullmatch(r"`?<[^`>]+>`?", body.replace("\n", " ").strip()))


def check_handoff(path: Path, errors: list[str], root: Path) -> None:
    check_headings(path, CREW_HANDOFF_HEADINGS, errors, root)
    text = read(path)
    for heading in CREW_HANDOFF_HEADINGS:
        if required_field_has_placeholder(text, heading):
            error(errors, path, f"{heading!r} still contains only a placeholder", root)
    commands = section(text, "Required Verification Commands").lower()
    if "none because" not in commands and not re.search(r"```(?:bash)?\s*\S+", commands):
        error(errors, path, "verification commands must be exact commands or none because <reason>", root)


def check_archive(root: Path, work_id: str, work_dir: Path, errors: list[str]) -> None:
    active = root / ".agent-work" / work_id
    if active.exists():
        errors.append(f"{active.relative_to(root)}: loose active work package remains outside archive")
    if not work_dir.exists():
        errors.append(f".agent-work/archive/*-{work_id}: archive package not found")


def resolve_work_dir(root: Path, work_id: str, archive: bool) -> Path:
    if not archive:
        return root / ".agent-work" / work_id
    matches = sorted((root / ".agent-work" / "archive").glob(f"*-{work_id}"))
    return matches[-1] if matches else root / ".agent-work" / "archive" / f"*-{work_id}"


def main() -> int:
    args = parse_args()
    root = Path(args.root).resolve()
    work_dir = resolve_work_dir(root, args.work_id, args.archive)
    errors: list[str] = []

    if args.archive:
        check_archive(root, args.work_id, work_dir, errors)
    elif not work_dir.exists():
        errors.append(f"{work_dir.relative_to(root)}: work package does not exist")

    if work_dir.exists():
        default_checklist = work_dir / "DEFAULT_CHECKLIST.md"
        pilot = work_dir / "PILOT_CHECKLIST.md"

        if not default_checklist.exists() and not pilot.exists():
            error(errors, work_dir, "missing PILOT_CHECKLIST.md or DEFAULT_CHECKLIST.md", root)

        if pilot.exists():
            check_headings(pilot, PILOT_HEADINGS, errors, root)
            check_implementation_gates(pilot, errors, root)

        for handoff in sorted(work_dir.glob("crew-handoffs/*.md")):
            if args.verbose:
                print(f"checking {handoff.relative_to(root)}")
            check_handoff(handoff, errors, root)

        for md in work_dir.rglob("*.md"):
            check_status_reasons(md, errors, root)

    if errors:
        for item in errors:
            print(f"ERROR: {item}", file=sys.stderr)
        return 1
    if args.verbose:
        print("Agent work package checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
