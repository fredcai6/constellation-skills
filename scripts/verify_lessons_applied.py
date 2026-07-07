#!/usr/bin/env python
"""Feedback-step gate: refuse advance while any threshold-ripe lesson is unpaid.

A lesson is unpaid when its scope threshold is crossed and it has no terminal
disposition this cycle (neither applied/exported nor deferred at/above its current
count). Reuses the ripeness model from apply_lessons_delta. Exit 0 = clear, 1 = blocked.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from apply_lessons_delta import LessonsDeltaError, load_playbook, ripe_lessons


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--file", type=Path, default=Path(".agent-work/LESSONS.md"))
    args = parser.parse_args(argv)

    if not args.file.exists():
        print("lessons gate: no playbook — clear")
        return 0
    try:
        book = load_playbook(args.file)
    except LessonsDeltaError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    ripe = ripe_lessons(book)
    if not ripe:
        print("lessons gate: clear — no ripe lesson awaiting apply-or-defer")
        return 0

    print("lessons gate: BLOCKED — ripe lesson(s) need apply / export / defer:", file=sys.stderr)
    for lesson in ripe:
        target = lesson.target or "CONSTELLATION_FEEDBACK.md"
        print(f"  - {lesson.lesson_id} ({lesson.scope}) -> {target}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
