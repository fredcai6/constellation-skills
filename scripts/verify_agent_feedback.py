#!/usr/bin/env python
"""Verify the durable Constellation agent feedback log for a work id."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from agent_work_root import durable_root


class FeedbackVerificationError(Exception):
    """Raised when the durable feedback-log invariant is broken."""


_BARE_NONE_RE = re.compile(r"^[-*]?\s*`?none\.?`?\s*$", re.IGNORECASE)
_SIGNAL_SECTIONS = ("Friction / unclear", "Crew-reported friction", "Improvement signals")


def _entry_block(text: str, work_id: str) -> str | None:
    """Return the feedback entry block for work_id (its ## heading to the next ##)."""
    lines = text.splitlines()
    start = None
    for i, line in enumerate(lines):
        if line.startswith("## ") and work_id in line:
            start = i
            break
    if start is None:
        return None
    end = len(lines)
    for j in range(start + 1, len(lines)):
        if lines[j].startswith("## "):
            end = j
            break
    return "\n".join(lines[start:end])


def _boilerplate_errors(entry: str, work_id: str) -> list[str]:
    """Reject content-free entries: every signal bullet is a bare 'none'."""
    bullets: list[str] = []
    in_section = False
    for line in entry.splitlines():
        stripped = line.strip()
        if stripped.startswith("**") and stripped.rstrip(":*").lstrip("*") in (
            s for s in _SIGNAL_SECTIONS
        ):
            in_section = True
            continue
        if stripped.startswith("**"):
            in_section = False
            continue
        if in_section and stripped.startswith(("-", "*")):
            bullets.append(stripped.lstrip("-* ").strip())
    if not bullets:
        return [
            f"feedback entry for {work_id!r} has no bullets under its signal sections "
            f"({', '.join(_SIGNAL_SECTIONS)})"
        ]
    if all(_BARE_NONE_RE.match(b) for b in bullets):
        return [
            f"feedback entry for {work_id!r} is content-free: every signal bullet is a bare "
            "'none'. A 'none' requires a run-specific reason, e.g. "
            "'none — confirmed after review: <what you checked>'"
        ]
    return []


def _current_run_archive_dirs(agent_work: Path, work_id: str) -> list[Path]:
    archive_root = agent_work / "archive"
    if not archive_root.exists():
        return []
    return [
        path
        for path in archive_root.iterdir()
        if path.is_dir() and (path.name == work_id or path.name.endswith(f"-{work_id}"))
    ]


def verify_agent_feedback(
    root: Path, work_id: str, phase: str, durable: Path | None = None
) -> None:
    # The DURABLE feedback log resolves under `durable` (the shared main-checkout
    # root when run inside a linked worktree); the work-area and archive negative
    # checks stay `root`-local (worktree-local). `durable` defaults to `root`, so
    # an explicit --root wins for BOTH.
    if durable is None:
        durable = root
    agent_work = root / ".agent-work"
    durable_agent_work = durable / ".agent-work"
    feedback = durable_agent_work / "AGENT_FEEDBACK.md"
    errors: list[str] = []

    if not feedback.is_file():
        errors.append(f"missing durable feedback log: {feedback}")
    else:
        text = feedback.read_text(encoding="utf-8")
        if work_id not in text:
            errors.append(f"durable feedback log does not mention work id {work_id!r}: {feedback}")
        else:
            entry = _entry_block(text, work_id)
            if entry is None:
                errors.append(
                    f"work id {work_id!r} appears in {feedback} but not as a '## ' entry heading"
                )
            else:
                errors.extend(_boilerplate_errors(entry, work_id))

    work_feedback = agent_work / work_id / "AGENT_FEEDBACK.md"
    if work_feedback.exists():
        errors.append(f"feedback log must stay durable, not inside the work area: {work_feedback}")

    work_lessons = agent_work / work_id / "LESSONS.md"
    if work_lessons.exists():
        errors.append(f"lessons playbook must stay durable, not inside the work area: {work_lessons}")

    archive_dirs = _current_run_archive_dirs(agent_work, work_id)
    archived_feedback = [path for base in archive_dirs for path in base.rglob("AGENT_FEEDBACK.md")]
    for path in archived_feedback:
        errors.append(f"feedback log must not be archived with the run package: {path}")
    archived_lessons = [path for base in archive_dirs for path in base.rglob("LESSONS.md")]
    for path in archived_lessons:
        errors.append(f"lessons playbook must not be archived with the run package: {path}")

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
    parser.add_argument("--root", default=None, type=Path)
    parser.add_argument("--phase", choices=("feedback", "archive"), required=True)
    args = parser.parse_args(argv)

    # Explicit --root wins for BOTH the durable log and the work-area/archive
    # checks. When omitted, work-area/archive stay cwd-local while the durable log
    # resolves to the shared main-checkout root (durable across worktree removal).
    if args.root is not None:
        local_root, durable = args.root, args.root
    else:
        local_root, durable = Path("."), durable_root()

    try:
        verify_agent_feedback(local_root, args.work_id, args.phase, durable=durable)
    except FeedbackVerificationError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print(f"agent feedback invariant ok: {args.work_id} ({args.phase})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
