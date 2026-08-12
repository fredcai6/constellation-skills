#!/usr/bin/env python
"""Verify a crash-resume state note exists and is filled, before detached work.

Wired as a `command` precondition on the spine `execute` step: an agent cannot
enter the detach-heavy execute phase without a well-formed
`.agent-work/<work-id>/STATE_NOTE.md`. The note is the one artifact that turns a
dead detached session into a clean resume instead of hours of forensics — see
`skills/admiral/references/fleet-doctrine.md`, "State-note-before-detach".

It checks the five resume fields are present and actually filled (not left as
`<placeholder>` text and not empty). It does NOT judge whether the values are
correct — that is the agent's job; the engine only guarantees the note exists
and is filled in before the first detach.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# The crash-resume fields, in the order a recovering agent reads them.
REQUIRED_FIELDS = ("step", "slug", "next command", "pid", "expected artifact")
FIELD_RE = re.compile(r"^- \*\*(.+?):\*\*\s*(.*?)\s*$")


def _utf8_stdio() -> None:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, OSError):
            pass


_utf8_stdio()


def parse_fields(text: str) -> dict[str, str]:
    """Pull `- **key:** value` lines into a lowercased key -> value map."""
    fields: dict[str, str] = {}
    for line in text.splitlines():
        match = FIELD_RE.match(line.strip())
        if match:
            fields[match.group(1).strip().lower()] = match.group(2).strip()
    return fields


def _is_placeholder(value: str) -> bool:
    """True for an empty value or an unfilled `<...>` template placeholder."""
    v = value.strip()
    if not v:
        return True
    return v.startswith("<") and v.endswith(">")


def validate(text: str) -> list[str]:
    """Return a list of problems; empty means the note is well-formed."""
    fields = parse_fields(text)
    problems = []
    for key in REQUIRED_FIELDS:
        if key not in fields:
            problems.append(f"missing field: {key}")
        elif _is_placeholder(fields[key]):
            problems.append(f"unfilled field: {key} (still a placeholder or empty)")
    return problems


def note_path(work_id: str, root: Path) -> Path:
    return root / ".agent-work" / work_id / "STATE_NOTE.md"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("work_id", help="the spine work-id / epic-id")
    parser.add_argument("--root", type=Path, default=Path("."), help="project root (default cwd)")
    parser.add_argument(
        "--file", type=Path, help="explicit note path (overrides work_id resolution)"
    )
    args = parser.parse_args(argv)

    path = args.file or note_path(args.work_id, args.root)
    if not path.is_file():
        print(f"state note missing: {path}", file=sys.stderr)
        print(
            "write the crash-resume note (step, slug, next command, pid, expected "
            "artifact) before detaching any work",
            file=sys.stderr,
        )
        return 1

    problems = validate(path.read_text(encoding="utf-8"))
    if problems:
        print(f"state note incomplete: {path}", file=sys.stderr)
        for problem in problems:
            print(f"  - {problem}", file=sys.stderr)
        return 1

    print(f"state note OK: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
