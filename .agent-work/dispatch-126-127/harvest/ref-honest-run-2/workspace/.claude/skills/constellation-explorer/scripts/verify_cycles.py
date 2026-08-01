#!/usr/bin/env python
"""Verify a work area's exploration cycles are consolidated before explore closes.

Wired as the explorer spine's `explore` step command check: `explore` cannot
close having run zero cycles, or with any cycle left unconsolidated — the
mechanical teeth behind "premature convergence is the failure mode this skill
exists to prevent" (see DESIGN_SPEC.md, spine table, "explore").
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


class CyclesVerificationError(Exception):
    """Raised when the exploration-cycles invariant is broken."""


def cycles_dir(root: Path, work_id: str) -> Path:
    return root / ".agent-work" / work_id


def verify_cycles(root: Path, work_id: str) -> None:
    base = cycles_dir(root, work_id)
    cycle_files = sorted(base.glob("cycle-*.json")) if base.is_dir() else []

    if not cycle_files:
        raise CyclesVerificationError(
            f"no cycle-*.json files found in {base}: explore cannot close having run zero cycles"
        )

    errors: list[str] = []
    for path in cycle_files:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            errors.append(f"{path}: unparseable JSON ({exc})")
            continue
        if not isinstance(data, dict):
            errors.append(f"{path}: not a JSON object")
            continue
        if data.get("type") != "survey":
            errors.append(f"{path}: not a survey checklist (type={data.get('type')!r})")
        if data.get("consolidation") is None:
            errors.append(f"{path}: unconsolidated (consolidation: null)")

    if errors:
        raise CyclesVerificationError("\n".join(errors))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("work_id")
    parser.add_argument("--root", default=".", type=Path)
    args = parser.parse_args(argv)

    try:
        verify_cycles(args.root, args.work_id)
    except CyclesVerificationError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print(f"cycles invariant ok: {args.work_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
