#!/usr/bin/env python
"""Verify the durable Constellation agent feedback log for a work id."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


class FeedbackVerificationError(Exception):
    """Raised when the durable feedback-log invariant is broken."""


def _current_run_archive_dirs(agent_work: Path, work_id: str) -> list[Path]:
    archive_root = agent_work / "archive"
    if not archive_root.exists():
        return []
    return [
        path
        for path in archive_root.iterdir()
        if path.is_dir() and (path.name == work_id or path.name.endswith(f"-{work_id}"))
    ]


def verify_agent_feedback(root: Path, work_id: str, phase: str) -> None:
    agent_work = root / ".agent-work"
    feedback = agent_work / "AGENT_FEEDBACK.md"
    errors: list[str] = []

    if not feedback.is_file():
        errors.append(f"missing durable feedback log: {feedback}")
    else:
        text = feedback.read_text(encoding="utf-8")
        if work_id not in text:
            errors.append(f"durable feedback log does not mention work id {work_id!r}: {feedback}")

    work_feedback = agent_work / work_id / "AGENT_FEEDBACK.md"
    if work_feedback.exists():
        errors.append(f"feedback log must stay durable, not inside the work area: {work_feedback}")

    archive_dirs = _current_run_archive_dirs(agent_work, work_id)
    archived_feedback = [path for base in archive_dirs for path in base.rglob("AGENT_FEEDBACK.md")]
    for path in archived_feedback:
        errors.append(f"feedback log must not be archived with the run package: {path}")

    if phase == "archive":
        work_area = agent_work / work_id
        if work_area.exists():
            errors.append(f"work area still exists after archive phase: {work_area}")
        if not archive_dirs:
            errors.append(
                f"no archived run package found for work id {work_id!r} under {agent_work / 'archive'}"
            )

    if errors:
        raise FeedbackVerificationError("\n".join(errors))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("work_id")
    parser.add_argument("--root", default=".", type=Path)
    parser.add_argument("--phase", choices=("feedback", "archive"), required=True)
    args = parser.parse_args(argv)

    try:
        verify_agent_feedback(args.root, args.work_id, args.phase)
    except FeedbackVerificationError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print(f"agent feedback invariant ok: {args.work_id} ({args.phase})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
