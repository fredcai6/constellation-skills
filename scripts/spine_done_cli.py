#!/usr/bin/env python
"""Thin CLI wrapping `spine_lifecycle.finish_work` -- the reachable-today "one
door verb" (#574 g3): "I'm done" as one call, usable today without waiting on
`mcp_spine_server.py`'s rewrite (lane A, this wave) to land.

Argument parsing plus one call into `finish_work`, nothing else -- no
business logic lives here. Prints the returned dict as JSON to stdout; exits
1 when `result["ok"]` is `False`, else 0.

NEVER run this against a live spine file. Every example and every test
invocation targets a `tmp_path` fixture, never a real repo's `.agent-work/`.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import spine_lifecycle  # noqa: E402


def _auto_tree_clean(root: str) -> bool:
    """`git status --porcelain` against `root`: clean iff its output is empty
    AND the command itself succeeded -- a git failure (not a repo, etc.) is
    read as NOT clean, never silently treated as clean."""
    proc = subprocess.run(
        ["git", "status", "--porcelain"], cwd=root, capture_output=True, text=True,
    )
    return proc.returncode == 0 and proc.stdout.strip() == ""


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description='Close out a Constellation work area in one call: "I\'m done."',
    )
    parser.add_argument("--file", required=True, help="path to the spine.json to close")
    parser.add_argument("--root", required=True, help="the repo root")
    parser.add_argument("--session-id", required=True, dest="session_id")
    parser.add_argument("--today", required=True, help="YYYY-MM-DD")
    parser.add_argument("--why", default=None)
    parser.add_argument(
        "--tree-clean", dest="tree_clean", action="store_true", default=None,
        help="assert the working tree is clean (omit both flags to auto-detect via git status --porcelain)",
    )
    parser.add_argument(
        "--tree-dirty", dest="tree_clean", action="store_false",
        help="assert the working tree is dirty",
    )
    parser.add_argument(
        "--episodes-captured", dest="episodes_captured", action="store_true", default=False,
    )
    parser.add_argument("--no-push", dest="push", action="store_false", default=True)
    parser.add_argument("--open-pr", dest="open_pr", action="store_true", default=False)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    tree_clean = args.tree_clean
    if tree_clean is None:
        tree_clean = _auto_tree_clean(args.root)

    result = spine_lifecycle.finish_work(
        args.file, root=args.root, session_id=args.session_id, today=args.today,
        tree_clean=tree_clean, episodes_captured=args.episodes_captured,
        why=args.why, push=args.push, open_pr=args.open_pr,
    )
    print(json.dumps(result, indent=2))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
