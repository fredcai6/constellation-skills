#!/usr/bin/env python
"""Scaffold a Constellation work area: .agent-work/<work-id>/ and its subdirs."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

SUBDIRS = ["crew-handoffs", "evidence", "triage-candidates"]


def init_work_area(root: Path, work_id: str) -> Path:
    base = root / ".agent-work" / work_id
    for sub in [""] + SUBDIRS:
        (base / sub).mkdir(parents=True, exist_ok=True)
    return base


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("work_id")
    parser.add_argument("--root", default=".")
    args = parser.parse_args(argv)
    base = init_work_area(Path(args.root), args.work_id)
    print(f"work area ready: {base}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
