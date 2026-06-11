#!/usr/bin/env python
"""Deterministically apply structured lesson delta operations to a LESSONS.md playbook.

The LLM proposes operations (add/confirm/disconfirm/mention/retire) in a JSON delta
file; this script validates and applies them mechanically. The LLM never writes the
playbook directly. All-or-nothing: any invalid op rejects the whole delta.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

def _utf8_stdio() -> None:
    """Per field feedback: don't make every call site set PYTHONIOENCODING."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, OSError):
            pass


_utf8_stdio()


SCOPES = ("handoff", "commander", "admiral", "project", "constellation")
DEFAULT_CAP = 20
DEFAULT_DORMANCY_RUNS = 10

STATE_RE = re.compile(
    r"<!--\s*playbook-state:\s*run-tick=(\d+)\s+cap=(\d+)\s+dormancy-runs=(\d+)\s*-->"
)
LESSON_HEADING_RE = re.compile(r"^### lesson:([a-z0-9][a-z0-9-]*)$")
FIELD_RE = re.compile(r"^- ([a-z-]+): (.*)$")


class LessonsDeltaError(Exception):
    """Raised when a delta cannot be applied; nothing is written."""


@dataclass
class Lesson:
    lesson_id: str
    scope: str
    task_class: str
    statement: str
    grounding: str
    mentions: int = 1
    confirmed: int = 0
    disconfirmed: int = 0
    status: str = "active"
    added: str = ""
    last_confirmed: str = "none"
    runs_since_confirmed: int = 0
    retired: str = ""
    history: list[str] = field(default_factory=list)

    def render(self) -> str:
        lines = [
            f"### lesson:{self.lesson_id}",
            f"- scope: {self.scope}",
            f"- task-class: {self.task_class}",
            f"- statement: {self.statement}",
            f"- grounding: {self.grounding}",
            f"- mentions: {self.mentions}",
            f"- confirmed: {self.confirmed}",
            f"- disconfirmed: {self.disconfirmed}",
            f"- status: {self.status}",
            f"- added: {self.added}",
            f"- last-confirmed: {self.last_confirmed}",
            f"- runs-since-confirmed: {self.runs_since_confirmed}",
        ]
        if self.retired:
            lines.append(f"- retired: {self.retired}")
        for entry in self.history:
            lines.append(f"- history: {entry}")
        return "\n".join(lines)


@dataclass
class Playbook:
    run_tick: int
    cap: int
    dormancy_runs: int
    preamble: str
    active: list[Lesson]
    dormant: list[Lesson]

    def find(self, lesson_id: str) -> tuple[Lesson, str] | None:
        for lesson in self.active:
            if lesson.lesson_id == lesson_id:
                return lesson, "active"
        for lesson in self.dormant:
            if lesson.lesson_id == lesson_id:
                return lesson, "dormant"
        return None


def _default_preamble() -> str:
    return (
        "# Lessons Playbook\n\n"
        "<!-- playbook-state: run-tick=0 cap=20 dormancy-runs=10 -->\n\n"
        "Curated, bounded workflow lessons. Read the Active section at the Commander\n"
        "context step. Never edit by hand or by LLM: apply structured deltas via\n"
        "apply_lessons_delta.py, which enforces cap, grounding, and counter rules.\n"
    )


def parse_lessons(block: str) -> list[Lesson]:
    lessons: list[Lesson] = []
    current: dict[str, str] | None = None
    history: list[str] = []

    def flush() -> None:
        nonlocal current, history
        if current is None:
            return
        required = ("id", "scope", "task-class", "statement", "grounding")
        missing = [key for key in required if not current.get(key)]
        if missing:
            raise LessonsDeltaError(
                f"corrupt playbook: lesson {current.get('id', '?')!r} missing {missing}"
            )
        lessons.append(
            Lesson(
                lesson_id=current["id"],
                scope=current["scope"],
                task_class=current["task-class"],
                statement=current["statement"],
                grounding=current["grounding"],
                mentions=int(current.get("mentions", "1")),
                confirmed=int(current.get("confirmed", "0")),
                disconfirmed=int(current.get("disconfirmed", "0")),
                status=current.get("status", "active"),
                added=current.get("added", ""),
                last_confirmed=current.get("last-confirmed", "none"),
                runs_since_confirmed=int(current.get("runs-since-confirmed", "0")),
                retired=current.get("retired", ""),
                history=list(history),
            )
        )
        current = None
        history = []

    for line in block.splitlines():
        heading = LESSON_HEADING_RE.match(line.strip())
        if heading:
            flush()
            current = {"id": heading.group(1)}
            continue
        if current is None:
            continue
        match = FIELD_RE.match(line.strip())
        if not match:
            continue
        key, value = match.group(1), match.group(2).strip()
        if key == "history":
            history.append(value)
        else:
            current[key] = value
    flush()
    return lessons


def load_playbook(path: Path) -> Playbook:
    if not path.exists():
        text = _default_preamble() + "\n## Active\n\n## Dormant\n"
    else:
        text = path.read_text(encoding="utf-8")

    state = STATE_RE.search(text)
    if not state:
        raise LessonsDeltaError(f"playbook missing playbook-state marker: {path}")
    run_tick, cap, dormancy = (int(state.group(i)) for i in (1, 2, 3))

    active_idx = text.find("\n## Active")
    dormant_idx = text.find("\n## Dormant")
    if active_idx == -1 or dormant_idx == -1 or dormant_idx < active_idx:
        raise LessonsDeltaError(f"playbook missing '## Active'/'## Dormant' sections: {path}")

    preamble = text[:active_idx].rstrip("\n")
    active_block = text[active_idx + len("\n## Active") : dormant_idx]
    dormant_block = text[dormant_idx + len("\n## Dormant") :]

    return Playbook(
        run_tick=run_tick,
        cap=cap,
        dormancy_runs=dormancy,
        preamble=preamble,
        active=parse_lessons(active_block),
        dormant=parse_lessons(dormant_block),
    )


def render_playbook(book: Playbook) -> str:
    preamble = STATE_RE.sub(
        f"<!-- playbook-state: run-tick={book.run_tick} cap={book.cap} "
        f"dormancy-runs={book.dormancy_runs} -->",
        book.preamble,
    )
    parts = [preamble, "", "## Active", ""]
    for lesson in book.active:
        parts.append(lesson.render())
        parts.append("")
    parts.extend(["## Dormant", ""])
    for lesson in book.dormant:
        parts.append(lesson.render())
        parts.append("")
    return "\n".join(parts).rstrip("\n") + "\n"


def _stamp(work_id: str) -> str:
    return f"{date.today().isoformat()} ({work_id})"


def validate_delta(delta: dict) -> tuple[str, bool, list[dict]]:
    work_id = delta.get("work_id")
    if not work_id or not isinstance(work_id, str):
        raise LessonsDeltaError("delta requires a non-empty string work_id")
    tick = delta.get("tick", False)
    ops = delta.get("ops", [])
    if not isinstance(ops, list):
        raise LessonsDeltaError("delta ops must be a list")
    if not tick and not ops:
        raise LessonsDeltaError("delta is a no-op: provide ops or tick=true")

    for op in ops:
        kind = op.get("op")
        lesson_id = op.get("id", "")
        if kind not in ("add", "confirm", "disconfirm", "mention", "retire"):
            raise LessonsDeltaError(f"unknown op {kind!r}")
        if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", lesson_id or ""):
            raise LessonsDeltaError(f"op {kind}: invalid lesson id {lesson_id!r} (kebab-case)")
        if kind == "add":
            if op.get("scope") not in SCOPES:
                raise LessonsDeltaError(
                    f"add {lesson_id}: scope must be one of {', '.join(SCOPES)}"
                )
            for required in ("statement", "grounding", "task_class"):
                if not str(op.get(required, "")).strip():
                    raise LessonsDeltaError(f"add {lesson_id}: {required} is required")
        if kind in ("confirm", "disconfirm") and not str(op.get("grounding", "")).strip():
            raise LessonsDeltaError(
                f"{kind} {lesson_id}: grounding citation is required (no citation, no count)"
            )
        if kind == "retire" and not str(op.get("reason", "")).strip():
            raise LessonsDeltaError(f"retire {lesson_id}: reason is required")
    return work_id, bool(tick), ops


def apply_delta(book: Playbook, delta: dict) -> list[str]:
    work_id, tick, ops = validate_delta(delta)
    log: list[str] = []
    stamp = _stamp(work_id)

    # Retires first so retire-before-add can satisfy the cap within one delta.
    ordered = sorted(ops, key=lambda op: 0 if op["op"] == "retire" else 1)

    for op in ordered:
        kind, lesson_id = op["op"], op["id"]
        found = book.find(lesson_id)

        if kind == "add":
            if found:
                raise LessonsDeltaError(f"add {lesson_id}: id already exists ({found[1]})")
            if len(book.active) >= book.cap:
                raise LessonsDeltaError(
                    f"add {lesson_id}: active cap {book.cap} reached — retire before adding"
                )
            book.active.append(
                Lesson(
                    lesson_id=lesson_id,
                    scope=op["scope"],
                    task_class=str(op["task_class"]).strip(),
                    statement=str(op["statement"]).strip(),
                    grounding=str(op["grounding"]).strip(),
                    added=stamp,
                )
            )
            log.append(f"added lesson:{lesson_id}")
            continue

        if not found:
            raise LessonsDeltaError(f"{kind} {lesson_id}: no such lesson")
        lesson, section = found

        if kind == "confirm":
            if section == "dormant":
                if len(book.active) >= book.cap:
                    raise LessonsDeltaError(
                        f"confirm {lesson_id}: cannot revive, active cap {book.cap} reached"
                    )
                book.dormant.remove(lesson)
                lesson.retired = ""
                book.active.append(lesson)
                log.append(f"revived lesson:{lesson_id} from dormant")
            lesson.confirmed += 1
            lesson.mentions += 1
            lesson.last_confirmed = stamp
            lesson.runs_since_confirmed = 0
            lesson.history.append(f"confirmed {stamp} — {op['grounding']}")
            if lesson.status == "charter-review" and lesson.confirmed > lesson.disconfirmed:
                lesson.status = "active"
            log.append(f"confirmed lesson:{lesson_id} (now {lesson.confirmed})")
        elif kind == "disconfirm":
            lesson.disconfirmed += 1
            lesson.mentions += 1
            lesson.history.append(f"disconfirmed {stamp} — {op['grounding']}")
            if lesson.disconfirmed >= lesson.confirmed:
                lesson.status = "charter-review"
                log.append(
                    f"disconfirmed lesson:{lesson_id} (now {lesson.disconfirmed}) — "
                    "flagged charter-review"
                )
            else:
                log.append(f"disconfirmed lesson:{lesson_id} (now {lesson.disconfirmed})")
        elif kind == "mention":
            lesson.mentions += 1
            log.append(f"mentioned lesson:{lesson_id} (now {lesson.mentions})")
        elif kind == "retire":
            if section == "dormant":
                raise LessonsDeltaError(f"retire {lesson_id}: already dormant")
            book.active.remove(lesson)
            lesson.retired = f"{stamp} — {op['reason']}"
            book.dormant.append(lesson)
            log.append(f"retired lesson:{lesson_id}")

    if tick:
        book.run_tick += 1
        demoted: list[Lesson] = []
        for lesson in book.active:
            lesson.runs_since_confirmed += 1
            if lesson.runs_since_confirmed > book.dormancy_runs:
                demoted.append(lesson)
        for lesson in demoted:
            book.active.remove(lesson)
            lesson.retired = f"{stamp} — auto-dormant: unconfirmed for {book.dormancy_runs} runs"
            book.dormant.append(lesson)
            log.append(f"auto-demoted lesson:{lesson.lesson_id} to dormant")
        log.append(f"tick -> run {book.run_tick}")

    return log


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("delta", type=Path, help="JSON delta file with work_id, tick, ops")
    parser.add_argument("--file", type=Path, default=Path(".agent-work/LESSONS.md"))
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    try:
        delta = json.loads(args.delta.read_text(encoding="utf-8"))
        book = load_playbook(args.file)
        log = apply_delta(book, delta)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"error: cannot read delta: {exc}", file=sys.stderr)
        return 1
    except LessonsDeltaError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if args.dry_run:
        print("DRY RUN — no write")
    else:
        args.file.parent.mkdir(parents=True, exist_ok=True)
        args.file.write_text(render_playbook(book), encoding="utf-8")

    for line in log:
        print(line)
    print(
        f"playbook: {len(book.active)} active / {len(book.dormant)} dormant "
        f"(cap {book.cap}, run {book.run_tick})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
