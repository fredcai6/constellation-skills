#!/usr/bin/env python
"""Mechanize the fenced staged-feedback trio for a delegated Commander/Admiral run.

A delegated run fenced off the main checkout's durable `.agent-work/` cannot
write the durable `AGENT_FEEDBACK.md` (see "Fenced feedback/archive closeout
- stage, do not waive" in the commander doctrine). It instead stages a
worktree-local trio -- AGENT_FEEDBACK.md, lessons-delta.json,
CONSTELLATION_FEEDBACK.md, plus a FENCE.md citing the launch order -- at
`.agent-work/staged-feedback/<work-id>/`, in the shapes
`verify_agent_feedback.py --phase feedback` and `--phase archive` accept
(see `_staged_feedback_errors` there). Several commanders this epic hand-rolled
this exact four-file layout (#140, #143, #145); this script mechanizes it so a
fenced commander does not have to hand-roll it again (#154, issue-143 follow-on).

This script writes the FOUR FILES; it does not itself distill the retrospective
content or the lesson candidates -- those still require the calling agent's own
reflection (see `AGENT_FEEDBACK.template.md`). Pass the already-authored body
text/files for the parts that need genuine content (--feedback-body); the two
parts that are frequently a confirmed negative (lessons-delta, constellation
export) get a sane tick-only / no-export default when omitted, and can be
overridden with real content via --lessons-delta / --constellation-feedback.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

TRIO_FILES = ("AGENT_FEEDBACK.md", "lessons-delta.json", "CONSTELLATION_FEEDBACK.md", "FENCE.md")


def _utf8_stdio() -> None:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, OSError):
            pass


_utf8_stdio()


def _default_lessons_delta(work_id: str) -> str:
    return json.dumps(
        {
            "tick": True,
            "work_id": work_id,
            "ops": [],
            "note": "Tick-only. No lesson candidates distilled this run.",
        },
        indent=2,
    ) + "\n"


def _default_constellation_feedback(work_id: str) -> str:
    return (
        f"# Constellation Feedback (staged export -- {work_id})\n\n"
        "Cross-project (constellation-wide) lessons exported upstream. Staged for "
        "Admiral harvest.\n\n"
        "## This run: no constellation-wide exports.\n\n"
        "No threshold-ripe constellation lesson surfaced this run. Recorded here "
        "explicitly so the empty export is a confirmed negative, not a silent drop.\n"
    )


def _agent_feedback_text(work_id: str, entry_date: str, body: str) -> str:
    body = body.strip("\n")
    return (
        f"# Agent Feedback Log (staged -- {work_id})\n\n"
        "Staged for Admiral harvest into the durable `.agent-work/AGENT_FEEDBACK.md` "
        "(this run is fenced off the main checkout per the launch order). Newest on top.\n\n"
        "---\n\n"
        f"## `{entry_date}` -- `{work_id}`\n\n"
        f"{body}\n"
    )


def _fence_text(work_id: str, launch_order: str, ownership: str, return_shape: str) -> str:
    return (
        f"# Fence citation -- {work_id}\n\n"
        "This delegated run is fenced off the main checkout's durable `.agent-work/` "
        "per its Admiral launch order:\n\n"
        f"- **Launch order:** `{launch_order}`\n"
        f"- **Fence (File Ownership):** {ownership}\n"
        f"- **Return Shape:** {return_shape}\n\n"
        "Per the delegated-commander \"Fenced feedback/archive closeout -- stage, do "
        "not waive\" doctrine, the durable-root write is impossible from this worktree, "
        "so the feedback trio is staged here instead of waived:\n\n"
        "- `AGENT_FEEDBACK.md` -- this run's retrospective entry\n"
        "- `lessons-delta.json` -- tick + lesson ops\n"
        "- `CONSTELLATION_FEEDBACK.md` -- constellation export (or confirmed-empty)\n\n"
        "The Admiral harvests this trio into the shared durable `.agent-work/` root "
        "before sweeping this worktree.\n"
    )


def stage_feedback(
    root: Path,
    work_id: str,
    *,
    feedback_body: str,
    launch_order: str,
    ownership: str,
    return_shape: str,
    lessons_delta: str | None = None,
    constellation_feedback: str | None = None,
    fence_text: str | None = None,
    entry_date: str | None = None,
    force: bool = False,
) -> Path:
    """Write the four staged-feedback files at
    `<root>/.agent-work/staged-feedback/<work-id>/`. Returns that directory.

    Refuses (like `instantiate_spine`) to overwrite an existing staged run
    directory unless `force` is passed, so a re-run never silently clobbers a
    prior staging.
    """
    staged = root / ".agent-work" / "staged-feedback" / work_id
    if staged.exists() and not force:
        existing = [name for name in TRIO_FILES if (staged / name).exists()]
        if existing:
            raise SystemExit(
                f"staged feedback already exists (in-progress run state); pass --force to "
                f"overwrite: {staged} (carries {', '.join(existing)})"
            )
    staged.mkdir(parents=True, exist_ok=True)

    if entry_date is None:
        entry_date = date.today().isoformat()

    resolved_lessons_delta = lessons_delta if lessons_delta is not None else _default_lessons_delta(work_id)
    # Fail visibly rather than staging an invalid lessons delta the engine will
    # reject later at verify_agent_feedback.
    json.loads(resolved_lessons_delta)

    resolved_constellation = (
        constellation_feedback if constellation_feedback is not None else _default_constellation_feedback(work_id)
    )
    resolved_fence = (
        fence_text if fence_text is not None else _fence_text(work_id, launch_order, ownership, return_shape)
    )
    if not resolved_fence.strip():
        raise SystemExit("fence citation text must not be empty -- learning cannot be silently dropped")

    (staged / "AGENT_FEEDBACK.md").write_text(
        _agent_feedback_text(work_id, entry_date, feedback_body), encoding="utf-8"
    )
    (staged / "lessons-delta.json").write_text(resolved_lessons_delta, encoding="utf-8")
    (staged / "CONSTELLATION_FEEDBACK.md").write_text(resolved_constellation, encoding="utf-8")
    (staged / "FENCE.md").write_text(resolved_fence, encoding="utf-8")
    return staged


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("work_id")
    parser.add_argument("--root", default=".", type=Path)
    parser.add_argument(
        "--feedback-body-file",
        required=True,
        type=Path,
        help="path to markdown for the retrospective entry body (Run shape / Instruction "
        "adherence / Friction / Crew-reported friction / What worked / Improvement signals "
        "sections) -- this script adds the entry heading, not this content",
    )
    parser.add_argument("--launch-order", help="path/citation to the governing launch order")
    parser.add_argument("--ownership", help="this run's File Ownership fence, as prose")
    parser.add_argument("--return-shape", help="this run's Return Shape instruction, as prose")
    parser.add_argument("--fence-file", type=Path, help="full FENCE.md content override (skips the three fields above)")
    parser.add_argument("--lessons-delta-file", type=Path, help="pre-authored lessons-delta.json (default: tick-only stub)")
    parser.add_argument(
        "--constellation-feedback-file",
        type=Path,
        help="pre-authored CONSTELLATION_FEEDBACK.md content (default: confirmed-empty stub)",
    )
    parser.add_argument("--date", help="entry date, YYYY-MM-DD (default: today)")
    parser.add_argument("--force", action="store_true", help="overwrite an existing staged run directory")
    args = parser.parse_args(argv)

    if args.fence_file is None and not (args.launch_order and args.ownership and args.return_shape):
        parser.error("pass --fence-file, or all three of --launch-order/--ownership/--return-shape")

    feedback_body = args.feedback_body_file.read_text(encoding="utf-8")
    lessons_delta = args.lessons_delta_file.read_text(encoding="utf-8") if args.lessons_delta_file else None
    constellation_feedback = (
        args.constellation_feedback_file.read_text(encoding="utf-8") if args.constellation_feedback_file else None
    )
    fence_text = args.fence_file.read_text(encoding="utf-8") if args.fence_file else None

    staged = stage_feedback(
        args.root,
        args.work_id,
        feedback_body=feedback_body,
        launch_order=args.launch_order or "",
        ownership=args.ownership or "",
        return_shape=args.return_shape or "",
        lessons_delta=lessons_delta,
        constellation_feedback=constellation_feedback,
        fence_text=fence_text,
        entry_date=args.date,
        force=args.force,
    )
    print(f"staged feedback ready: {staged}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
