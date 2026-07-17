#!/usr/bin/env python
"""Deterministically apply structured lesson delta operations to a LESSONS.md playbook.

The LLM proposes operations (add/amend/confirm/disconfirm/mention/retire/defer/apply/
export/resolve) in a JSON delta file; this script validates and applies them mechanically.
The LLM never writes the playbook directly. All-or-nothing: any invalid op rejects the
whole delta.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from agent_work_root import durable_root


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
DEFAULT_APPLY_RECURRENCES = 1
DEFAULT_APPLY_CONFIRMED = 3
# Bound on the seen-work-ids dedup ring stored in the playbook-state header: keep the
# most recent N ticking work-ids so a burst from one work-id ages the clock only once
# without letting the header grow unbounded. Old entries fall off; re-ticking a work-id
# that has aged out simply ages once more, which is harmless.
TICKED_WORK_ID_RETENTION = 50

STATE_RE = re.compile(
    r"<!--\s*playbook-state:\s*run-tick=(\d+)\s+cap=(\d+)\s+dormancy-runs=(\d+)"
    r"(?:\s+apply-recurrences=(\d+))?(?:\s+apply-confirmed=(\d+))?"
    r"(?:\s+ticked-work-ids=(\S*))?\s*-->"
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
    bank_reason: str = ""  # why this is carried in the bank to re-observe, not fixed now
    mentions: int = 1
    confirmed: int = 0
    disconfirmed: int = 0
    recurrences: int = 0
    status: str = "active"
    added: str = ""
    last_confirmed: str = "none"
    runs_since_confirmed: int = 0
    target: str = ""
    deferred_at: int = -1
    retired: str = ""  # parse-only back-compat: legacy files carry this; the engine never sets it
    history: list[str] = field(default_factory=list)

    def render(self) -> str:
        lines = [
            f"### lesson:{self.lesson_id}",
            f"- scope: {self.scope}",
            f"- task-class: {self.task_class}",
            f"- statement: {self.statement}",
            f"- grounding: {self.grounding}",
        ]
        # Rendered only when set, so legacy lessons without it round-trip identically
        # (parse defaults it to ""). Every lesson added going forward carries one.
        if self.bank_reason:
            lines.append(f"- bank-reason: {self.bank_reason}")
        if self.target:
            lines.append(f"- target: {self.target}")
        lines += [
            f"- mentions: {self.mentions}",
            f"- confirmed: {self.confirmed}",
            f"- disconfirmed: {self.disconfirmed}",
        ]
        # Debt counter is rendered only when it has accrued, so non-constellation
        # lessons stay clean and round-trip identically (parse defaults it to 0).
        if self.recurrences:
            lines.append(f"- recurrences: {self.recurrences}")
        lines += [
            f"- status: {self.status}",
            f"- added: {self.added}",
            f"- last-confirmed: {self.last_confirmed}",
            f"- runs-since-confirmed: {self.runs_since_confirmed}",
        ]
        if self.deferred_at >= 0:
            lines.append(f"- deferred-at: {self.deferred_at}")
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
    apply_recurrences: int
    apply_confirmed: int
    preamble: str
    active: list[Lesson]
    ticked_work_ids: list[str] = field(default_factory=list)

    def find(self, lesson_id: str) -> Lesson | None:
        for lesson in self.active:
            if lesson.lesson_id == lesson_id:
                return lesson
        return None


def _default_preamble() -> str:
    return (
        "# Lessons Playbook\n\n"
        "<!-- playbook-state: run-tick=0 cap=20 dormancy-runs=10 apply-recurrences=1 apply-confirmed=3 ticked-work-ids= -->\n\n"
        "Open problems carried forward — NOT a log of everything learned. If a lesson is\n"
        "understood and fixable, apply the fix and record it in AGENT_FEEDBACK; do not\n"
        "bank it here. A lesson lives here only because it needs to be re-observed to be\n"
        "understood, so every `add` states a bank-reason (what re-observation will\n"
        "clarify). Reaching the cap is a failure mode — it means the bank is being used\n"
        "to accumulate instead of to adjudicate. Read the Active section at the Commander\n"
        "context step. Never edit by hand or by LLM: apply structured deltas via\n"
        "apply_lessons_delta.py, which enforces cap, grounding, and counter rules.\n\n"
        "Counter semantics split by scope: for most scopes a confirm is trust\n"
        "(the lesson held again). For a constellation-scoped lesson it is the\n"
        "opposite — a recurrence of an unfixed shared-machinery defect, so it\n"
        "accrues recurrences (debt) and flags recurrence-debt. Pay the debt by\n"
        "exporting to CONSTELLATION_FEEDBACK and fixing upstream. Once the fix\n"
        "ships, `resolve` the lesson (cite the shipping PR): it goes terminal\n"
        "(fixed-upstream) — never ripe again, a later confirm is ignored rather\n"
        "than re-exported, and it ages out of the playbook on its own. Do not keep\n"
        "confirming a constellation defect into a permanent workaround.\n"
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
                bank_reason=current.get("bank-reason", ""),
                mentions=int(current.get("mentions", "1")),
                confirmed=int(current.get("confirmed", "0")),
                disconfirmed=int(current.get("disconfirmed", "0")),
                recurrences=int(current.get("recurrences", "0")),
                status=current.get("status", "active"),
                added=current.get("added", ""),
                last_confirmed=current.get("last-confirmed", "none"),
                runs_since_confirmed=int(current.get("runs-since-confirmed", "0")),
                target=current.get("target", ""),
                deferred_at=int(current.get("deferred-at", "-1")),
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
        text = _default_preamble() + "\n## Active\n"
    else:
        text = path.read_text(encoding="utf-8")

    state = STATE_RE.search(text)
    if not state:
        raise LessonsDeltaError(f"playbook missing playbook-state marker: {path}")
    run_tick, cap, dormancy = (int(state.group(i)) for i in (1, 2, 3))
    apply_recurrences = int(state.group(4)) if state.group(4) else DEFAULT_APPLY_RECURRENCES
    apply_confirmed = int(state.group(5)) if state.group(5) else DEFAULT_APPLY_CONFIRMED
    # Seen-work-ids dedup ring (comma-joined, most-recent-last). Absent field or empty
    # value -> empty ring; a stray empty entry is corruption, so fail visibly.
    raw_ticked = state.group(6)
    if raw_ticked:
        ticked_work_ids = raw_ticked.split(",")
        if any(not wid for wid in ticked_work_ids):
            raise LessonsDeltaError(
                f"playbook malformed ticked-work-ids header: {raw_ticked!r}"
            )
    else:
        ticked_work_ids = []

    active_idx = text.find("\n## Active")
    if active_idx == -1:
        raise LessonsDeltaError(f"playbook missing '## Active' section: {path}")
    dormant_idx = text.find("\n## Dormant")

    preamble = text[:active_idx].rstrip("\n")
    if dormant_idx != -1 and dormant_idx > active_idx:
        # Legacy file: parse the Active slice up to the graveyard, discard the
        # graveyard entirely (it is GC'd on the next render).
        active_block = text[active_idx + len("\n## Active") : dormant_idx]
    else:
        active_block = text[active_idx + len("\n## Active") :]

    return Playbook(
        run_tick=run_tick,
        cap=cap,
        dormancy_runs=dormancy,
        apply_recurrences=apply_recurrences,
        apply_confirmed=apply_confirmed,
        preamble=preamble,
        active=parse_lessons(active_block),
        ticked_work_ids=ticked_work_ids,
    )


def render_playbook(book: Playbook) -> str:
    preamble = STATE_RE.sub(
        f"<!-- playbook-state: run-tick={book.run_tick} cap={book.cap} "
        f"dormancy-runs={book.dormancy_runs} apply-recurrences={book.apply_recurrences} "
        f"apply-confirmed={book.apply_confirmed} "
        f"ticked-work-ids={','.join(book.ticked_work_ids)} -->",
        book.preamble,
    )
    parts = [preamble, "", "## Active", ""]
    for lesson in book.active:
        parts.append(lesson.render())
        parts.append("")
    return "\n".join(parts).rstrip("\n") + "\n"


def ripe_lessons(book: Playbook) -> list[Lesson]:
    """Threshold-ripe lessons still awaiting an apply/export/defer disposition."""
    ripe: list[Lesson] = []
    for lesson in book.active:
        if lesson.status == "charter-review":
            continue
        if lesson.scope == "constellation":
            # exported = queued upstream (awaiting the fix); fixed-upstream = the fix
            # shipped. Neither is ripe: the first is already settled by its export, the
            # second is terminal.
            if lesson.status in ("exported", "fixed-upstream"):
                continue
            if lesson.recurrences < book.apply_recurrences:
                continue
            count = lesson.recurrences
        else:
            if lesson.confirmed < book.apply_confirmed:
                continue
            if not lesson.target:
                continue
            count = lesson.confirmed
        if lesson.status == "deferred" and lesson.deferred_at >= count:
            continue
        ripe.append(lesson)
    return ripe


def _apply_threshold_ripe(book: Playbook, lesson: Lesson) -> bool:
    """Is this non-constellation lesson ripe for apply?

    Apply only ever reaches non-constellation lessons (constellation is refused
    earlier in the apply branch), so ripeness here is `confirmed >= apply_confirmed`
    — the same threshold `ripe_lessons()` uses for non-constellation lessons.
    Single source of the number; do not fork it.
    """
    return lesson.confirmed >= book.apply_confirmed


def _is_doctrine_target(target: str) -> bool:
    """A path is a doctrine artifact (an agent reads it; no unit test grades it) when it
    ends in `.md` OR contains `.template.` — covers SKILL.md, _shared/*.md, docs/** prose,
    and *.template.json / *.template.md spine/checklist/handoff templates. Everything else
    (`.py`, `.js`, …) is a code target and is exempt. Pure path rule: never inspects
    contents or judges quality."""
    path = target.strip().lower()
    return path.endswith(".md") or ".template." in path


def _stamp(work_id: str) -> str:
    return f"{date.today().isoformat()} ({work_id})"


def _stamp_date(stamp: str) -> str:
    """Extract the ISO date from a "YYYY-MM-DD (work-id)" stamp for same-epoch
    comparison. A bare token like "none" (unset last-confirmed) returns itself and
    never matches a real date."""
    return stamp.split(" (", 1)[0]


def validate_delta(delta: dict) -> tuple[str, bool, list[dict]]:
    work_id = delta.get("work_id")
    if not work_id or not isinstance(work_id, str):
        raise LessonsDeltaError("delta requires a non-empty string work_id")
    # The ticked-work-ids header ring stores work-ids comma-joined; a comma or
    # whitespace inside one would mis-split the ring on round-trip.
    if re.search(r"[,\s]", work_id):
        raise LessonsDeltaError(
            f"work_id {work_id!r} must not contain commas or whitespace"
        )
    tick = delta.get("tick", False)
    ops = delta.get("ops", [])
    if not isinstance(ops, list):
        raise LessonsDeltaError("delta ops must be a list")
    if not tick and not ops:
        raise LessonsDeltaError("delta is a no-op: provide ops or tick=true")

    for op in ops:
        kind = op.get("op")
        lesson_id = op.get("id", "")
        if kind not in ("add", "amend", "confirm", "disconfirm", "mention", "retire", "defer", "apply", "export", "resolve"):
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
            # The playbook holds open problems carried forward to re-observe — not a log
            # of everything learned. Banking a lesson must justify the lingering: if you
            # can fix it this run, apply the fix and record it in AGENT_FEEDBACK instead
            # of adding a lesson. So every add states why it is banked, not fixed.
            if not str(op.get("bank_reason", "")).strip():
                raise LessonsDeltaError(
                    f"add {lesson_id}: bank_reason is required — say what re-observation "
                    "will clarify (why this is banked to watch again rather than fixed now). "
                    "If it is understood and fixable, apply the fix + note it in "
                    "AGENT_FEEDBACK; do not bank it."
                )
        if kind in ("confirm", "disconfirm") and not str(op.get("grounding", "")).strip():
            raise LessonsDeltaError(
                f"{kind} {lesson_id}: grounding citation is required (no citation, no count)"
            )
        if kind == "amend":
            if not str(op.get("grounding", "")).strip():
                raise LessonsDeltaError(
                    f"amend {lesson_id}: grounding citation is required (what justifies the change)"
                )
            if not any(str(op.get(f, "")).strip() for f in ("statement", "scope", "task_class")):
                raise LessonsDeltaError(
                    f"amend {lesson_id}: provide at least one of statement/scope/task_class"
                )
            if op.get("scope") and op["scope"] not in SCOPES:
                raise LessonsDeltaError(
                    f"amend {lesson_id}: scope must be one of {', '.join(SCOPES)}"
                )
        if kind == "retire" and not str(op.get("reason", "")).strip():
            raise LessonsDeltaError(f"retire {lesson_id}: reason is required")
        if kind == "defer" and not str(op.get("reason", "")).strip():
            raise LessonsDeltaError(f"defer {lesson_id}: reason is required")
        if kind == "apply" and not str(op.get("applied_evidence", "")).strip():
            raise LessonsDeltaError(f"apply {lesson_id}: applied_evidence citation is required")
        if kind == "export" and not str(op.get("grounding", "")).strip():
            raise LessonsDeltaError(f"export {lesson_id}: grounding (CONSTELLATION_FEEDBACK citation) required")
        if kind == "resolve" and not str(op.get("resolution", "")).strip():
            raise LessonsDeltaError(
                f"resolve {lesson_id}: resolution citation is required "
                "(the shipping PR / commit / issue that fixed it upstream)"
            )
    return work_id, bool(tick), ops


def apply_delta(book: Playbook, delta: dict) -> list[str]:
    work_id, tick, ops = validate_delta(delta)
    log: list[str] = []
    stamp = _stamp(work_id)

    # Retires first so retire-before-add can satisfy the cap within one delta.
    ordered = sorted(ops, key=lambda op: 0 if op["op"] in ("retire", "apply") else 1)

    for op in ordered:
        kind, lesson_id = op["op"], op["id"]
        lesson = book.find(lesson_id)

        if kind == "add":
            if lesson:
                raise LessonsDeltaError(f"add {lesson_id}: id already exists")
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
                    bank_reason=str(op["bank_reason"]).strip(),
                    target=str(op.get("target", "")).strip(),
                    added=stamp,
                )
            )
            log.append(f"added lesson:{lesson_id}")
            continue

        if not lesson:
            raise LessonsDeltaError(f"{kind} {lesson_id}: no such lesson")

        if kind == "amend":
            old_statement = lesson.statement
            if str(op.get("statement", "")).strip():
                lesson.statement = str(op["statement"]).strip()
            if op.get("scope"):
                lesson.scope = op["scope"]
            if str(op.get("task_class", "")).strip():
                lesson.task_class = str(op["task_class"]).strip()
            if str(op.get("target", "")).strip():
                lesson.target = str(op["target"]).strip()
            lesson.history.append(f"amended {stamp} — {op['grounding']} (was: {old_statement})")
            log.append(f"amended lesson:{lesson_id} (counters preserved)")
            continue

        if kind == "confirm":
            # Terminal state: a constellation lesson already fixed upstream must not be
            # resurrected. Ignore the confirm outright — no debt, no dormancy reset, no
            # status flip — so the tombstone keeps aging toward GC while the fleet's
            # install-lagged re-observations can no longer re-ripen it into another export.
            # This is the core of the anti-churn contract.
            if lesson.scope == "constellation" and lesson.status == "fixed-upstream":
                lesson.history.append(f"confirm ignored {stamp}: fixed upstream — {op['grounding']}")
                log.append(
                    f"confirm skipped lesson:{lesson_id} — fixed upstream; not re-counted "
                    "(retire locally once your install carries the fix)"
                )
                continue
            lesson.mentions += 1
            lesson.last_confirmed = stamp
            lesson.runs_since_confirmed = 0
            if lesson.scope == "constellation":
                lesson.recurrences += 1
                lesson.status = "recurrence-debt"
                lesson.history.append(
                    f"recurred {stamp} (constellation debt, not trust) — {op['grounding']}"
                )
                log.append(
                    f"recurrence-debt lesson:{lesson_id} (now {lesson.recurrences} unfixed "
                    "recurrence(s)) — export to CONSTELLATION_FEEDBACK and fix upstream; "
                    "confirming a constellation defect logs debt, not trust"
                )
            else:
                lesson.confirmed += 1
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
            book.active.remove(lesson)
            log.append(f"deleted lesson:{lesson_id} — {op['reason']}")
        elif kind == "apply":
            if lesson.scope == "constellation":
                raise LessonsDeltaError(
                    f"apply {lesson_id}: constellation lessons cannot be applied in-project; "
                    "use export to queue the fix upstream"
                )
            effective_target = str(op.get("target", "")).strip() or lesson.target
            if not effective_target:
                raise LessonsDeltaError(
                    f"apply {lesson_id}: target required (set on the lesson or in the op)"
                )
            # Reproduction-drill gate: a ripe doctrine apply pays out (deletes the lesson)
            # only if it carries a drill reference — the process-doc analogue of a
            # regression test. Field-presence ONLY: never open the drill file, never judge
            # its quality (same doctrine as the engine — mechanism, not quality). Non-ripe
            # applies and code-target applies are exempt.
            drill = str(op.get("drill", "")).strip()
            if _is_doctrine_target(effective_target):
                # Reshaping doctrine (an .md / .template.* an agent reads) is a human call,
                # ripe or not. A delegated/autonomous run cannot self-authorize it: with no
                # human present it cannot honestly cite human authority, so it must surface
                # the apply (defer 'needs human'), which is where the human can also rule
                # "wait, observe it again". Code targets are exempt — their test suite is the
                # behavioral check.
                if str(op.get("authority", "")).strip().lower() != "human":
                    raise LessonsDeltaError(
                        f"apply {lesson_id}: doctrine target {effective_target!r} requires "
                        "human authorization (authority=\"human\") — reshaping doctrine is a "
                        "human call. In a delegated/autonomous run, surface the apply instead "
                        "of self-applying: defer it with reason 'needs human'."
                    )
                # A ripe doctrine apply additionally needs a reproduction drill — the
                # process-doc analogue of a regression test (dead doctrine reads as progress).
                if _apply_threshold_ripe(book, lesson) and not drill:
                    raise LessonsDeltaError(
                        f"apply {lesson_id}: ripe doctrine target {effective_target!r} requires "
                        "a reproduction drill — add a 'drill' field referencing "
                        "docs/superpowers/drills/<lesson-id>.md (run the before/after arm drill "
                        "first; see lessons-auditor SKILL)"
                    )
            book.active.remove(lesson)
            authority = str(op.get("authority", "")).strip()
            log.append(
                f"applied lesson:{lesson_id} -> {effective_target} (paid; deleted) "
                f"— {op['applied_evidence']}"
                + (f" authority={authority}" if authority else "")
                + (f" drill={drill}" if drill else "")
            )
        elif kind == "export":
            if lesson.scope != "constellation":
                raise LessonsDeltaError(
                    f"export {lesson_id}: only constellation-scoped lessons export upstream"
                )
            lesson.status = "exported"
            lesson.history.append(f"exported {stamp} — {op['grounding']}")
            log.append(
                f"exported lesson:{lesson_id} to CONSTELLATION_FEEDBACK "
                f"(pinned until upstream ships) — {op['grounding']}"
            )
        elif kind == "resolve":
            # The upstream fix has shipped. Mark the constellation lesson terminal:
            # never ripe again, immune to confirm-resurrection, and — unlike an unpaid
            # constellation lesson, which is pinned from auto-delete — now eligible for
            # ordinary dormancy GC so the tombstone self-cleans once the fleet stops
            # re-observing it. Ends the export-every-run churn a shipped fix would
            # otherwise keep generating across install-lagged projects.
            if lesson.scope != "constellation":
                raise LessonsDeltaError(
                    f"resolve {lesson_id}: only constellation-scoped lessons are fixed upstream "
                    "(project/doctrine lessons are paid by apply, or deleted by retire)"
                )
            lesson.status = "fixed-upstream"
            lesson.history.append(f"resolved {stamp} — {op['resolution']}")
            log.append(
                f"resolved lesson:{lesson_id} — fixed upstream ({op['resolution']}); "
                "no longer ripe, no longer re-exported, ages out of the playbook"
            )
        elif kind == "defer":
            count = lesson.recurrences if lesson.scope == "constellation" else lesson.confirmed
            lesson.status = "deferred"
            lesson.deferred_at = count
            lesson.history.append(f"deferred {stamp} at {count} — {op['reason']}")
            log.append(f"deferred lesson:{lesson_id} at {count} — {op['reason']}")

    if tick:
        if work_id in book.ticked_work_ids:
            # Dedup by work-id: a burst of apply invocations from one work-unit ages
            # the dormancy clock only once, so it cannot expire a lesson on its own.
            log.append(
                f"tick skipped: work-id {work_id!r} already aged this playbook "
                "(no double-aging)"
            )
        else:
            book.run_tick += 1
            book.ticked_work_ids = (book.ticked_work_ids + [work_id])[-TICKED_WORK_ID_RETENTION:]
            tick_date = _stamp_date(stamp)
            expired: list[Lesson] = []
            for lesson in book.active:
                lesson.runs_since_confirmed += 1
                # Unpaid constellation lessons are pinned: shared-machinery debt persists
                # until fixed upstream — never silently auto-deleted. Once resolved
                # (fixed-upstream), the pin lifts and the tombstone ages out normally.
                if lesson.scope == "constellation" and lesson.status != "fixed-upstream":
                    continue
                if lesson.runs_since_confirmed <= book.dormancy_runs:
                    continue
                # Same-epoch guard: a lesson never dies on the same date it was added or
                # last confirmed, regardless of its count. Aging still incremented above;
                # only expiry is guarded.
                if tick_date in (_stamp_date(lesson.added), _stamp_date(lesson.last_confirmed)):
                    continue
                expired.append(lesson)
            for lesson in expired:
                book.active.remove(lesson)
                log.append(
                    f"auto-deleted lesson:{lesson.lesson_id} "
                    f"(unconfirmed for {book.dormancy_runs} runs)"
                )
            log.append(f"tick -> run {book.run_tick}")

    return log


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("delta", type=Path, nargs="?", help="JSON delta file with work_id, tick, ops")
    parser.add_argument("--file", type=Path, default=None)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--ripe", action="store_true", help="list ripe-unpaid lessons and exit")
    args = parser.parse_args(argv)

    # Default only: resolve the durable playbook root so a linked-worktree run reads
    # and writes the MAIN checkout's playbook. An explicit --file always wins.
    target = args.file if args.file is not None else durable_root() / ".agent-work" / "LESSONS.md"

    if args.ripe:
        book = load_playbook(target)
        for lesson in ripe_lessons(book):
            print(f"{lesson.lesson_id}\t{lesson.scope}\ttarget={lesson.target or 'CONSTELLATION_FEEDBACK.md'}")
        return 0
    if args.delta is None:
        parser.error("delta file is required unless --ripe is given")

    try:
        delta = json.loads(args.delta.read_text(encoding="utf-8"))
        book = load_playbook(target)
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
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(render_playbook(book), encoding="utf-8")

    for line in log:
        print(line)
    print(
        f"playbook: {len(book.active)} active (cap {book.cap}, run {book.run_tick})"
    )
    debt = [l for l in book.active if l.scope == "constellation" and l.recurrences > 0
            and l.status != "fixed-upstream"]
    if debt:
        total = sum(l.recurrences for l in debt)
        print(
            f"recurrence-debt: {len(debt)} constellation lesson(s), {total} unfixed "
            "recurrence(s) — fix upstream, don't keep confirming"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
