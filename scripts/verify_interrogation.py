#!/usr/bin/env python
"""Refuse a self-answered or unsigned interrogation — the interrogator RAIL.

This is the mechanically-enforced rail for the `constellation-interrogator`
sharpening (DESIGN_SPEC Section D1). The interrogator drives a survey to a joint
understanding; this script is the gate the interrogation RECORD must clear before
that understanding may be called consolidated. It enforces the two locked
behaviors in code, so neither can rest on the agent's self-assertion:

  * FACTS-VS-DECISIONS SPLIT. Every question is typed `fact` or `decision`. A
    `fact` is a question the agent may resolve by exploring the codebase; a
    `decision` is a genuine choice that must block on the human/counterpart.
      - A `decision` marked `resolved` MUST carry a non-empty `human_answer` —
        a decision is NEVER self-answered by the agent (the DECISION-BLOCK).
      - A `fact` marked `resolved` MUST carry non-empty `code_evidence` — a
        resolved fact is grounded in code/docs, not asserted (the split's other
        edge). A resolved fact needs NO human answer; that is what "allowed" means.

  * NO-QUIT-EARLY FINISH GATE. A record marked `consolidated: true` MUST carry a
    joint-understanding `signoff` — a real human exchange with a non-empty `by`
    AND `statement` — AND no question may still be `open`. Loop termination is not
    the gate; the explicit sign-off that questioning is complete is. Absent it,
    consolidation is REFUSED.

A defended exception to the finish gate (e.g. an async counterpart) requires a
`rail_exception` carrying a non-empty `reviewer_cosign` (the INDEPENDENT reviewer,
never the author) AND a non-empty `log` entry — self-assertion never passes. The
exception covers the finish gate ONLY; it never excuses a self-answered decision.

Everything else — whether the questioning actually dug deep, whether the recorded
understanding is right — is the INDEPENDENT reviewer's judgment (DESIGN_SPEC TF8),
deliberately NOT gated here. Standard library only.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

VALID_MODES = ("delegated", "interactive")
VALID_KINDS = ("fact", "decision")
VALID_STATUSES = ("resolved", "open", "skipped")


class InterrogationError(Exception):
    """Raised when an interrogation record fails the rail — the refusal."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise InterrogationError(message)


def _nonempty(value: object) -> bool:
    return bool(str(value).strip()) if value is not None else False


def verify_structure(record: object) -> dict:
    """The record's basic shape: a goal, a mode, and a non-empty typed question
    list with unique ids and valid kind/status."""
    _require(isinstance(record, dict), "record is not a JSON object")
    assert isinstance(record, dict)

    _require(_nonempty(record.get("goal")),
             "record.goal is missing or empty (the handed-in goal being resolved)")

    mode = record.get("mode")
    _require(mode in VALID_MODES,
             f"record.mode is {mode!r}, expected one of {'/'.join(VALID_MODES)}")

    questions = record.get("questions")
    _require(isinstance(questions, list) and len(questions) > 0,
             "record.questions is missing or empty (an interrogation asks at least one question)")
    assert isinstance(questions, list)

    seen: set[str] = set()
    for idx, q in enumerate(questions):
        _require(isinstance(q, dict), f"question #{idx} is not an object")
        qid = str(q.get("id", "")).strip()
        _require(bool(qid), f"question #{idx} is missing an id")
        _require(qid not in seen, f"duplicate question id {qid!r}")
        seen.add(qid)
        _require(_nonempty(q.get("question")), f"question {qid!r} has no question text")
        kind = q.get("kind")
        _require(kind in VALID_KINDS,
                 f"question {qid!r} kind is {kind!r}, expected one of {'/'.join(VALID_KINDS)}")
        status = q.get("status")
        _require(status in VALID_STATUSES,
                 f"question {qid!r} status is {status!r}, expected one of {'/'.join(VALID_STATUSES)}")
    return record


def verify_split(record: dict) -> None:
    """The facts-vs-decisions split, enforced per resolved question.

    Only `resolved` questions are gated — `open` (mid-loop) and `skipped`
    (overcome by an earlier answer) questions carry neither obligation.
    """
    for q in record["questions"]:
        if q.get("status") != "resolved":
            continue
        qid = q["id"]
        if q["kind"] == "decision":
            _require(
                _nonempty(q.get("human_answer")),
                f"DECISION-BLOCK: question {qid!r} is a resolved decision with no "
                f"human_answer — a decision is never self-answered by the agent; it "
                f"blocks on the human/counterpart.",
            )
        else:  # fact
            _require(
                _nonempty(q.get("code_evidence")),
                f"question {qid!r} is a resolved fact with no code_evidence — a fact "
                f"is resolved by exploring the code/docs, not asserted.",
            )


def _exception_cosigned(record: dict) -> bool:
    """True only when an INDEPENDENT reviewer co-signed the finish-gate exception
    AND a log entry records it. Self-assertion (no reviewer_cosign) is not enough."""
    exc = record.get("rail_exception")
    if not isinstance(exc, dict):
        return False
    return _nonempty(exc.get("reviewer_cosign")) and _nonempty(exc.get("log"))


def verify_finish_gate(record: dict) -> None:
    """The no-quit-early finish gate: a consolidated record needs the joint-
    understanding sign-off AND no open question — or a reviewer-cosigned exception."""
    if not record.get("consolidated"):
        return  # mid-interrogation: the gate has not been reached yet

    open_qs = [q["id"] for q in record["questions"] if q.get("status") == "open"]
    _require(
        not open_qs,
        f"cannot consolidate: questions still open {open_qs} — a joint understanding "
        f"is not reached while questions remain open.",
    )

    signoff = record.get("signoff")
    signed = (
        isinstance(signoff, dict)
        and _nonempty(signoff.get("by"))
        and _nonempty(signoff.get("statement"))
    )
    if signed:
        return
    if _exception_cosigned(record):
        return
    raise InterrogationError(
        "FINISH-GATE: a consolidated interrogation needs a joint-understanding "
        "signoff (a real human exchange: non-empty `by` + `statement`) — that the "
        "loop terminated is not enough. No reviewer-cosigned rail_exception "
        "(reviewer_cosign + log) covers it either. Self-assertion never closes an "
        "interrogation."
    )


def verify_interrogation(record: object) -> None:
    """Raise InterrogationError on any failed rule; return None if the record
    clears the rail. Order is deliberate: shape first, then the split, then the
    finish gate."""
    record = verify_structure(record)
    verify_split(record)
    verify_finish_gate(record)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("record", help="path to the interrogation-record JSON")
    args = parser.parse_args(argv)

    try:
        record = json.loads(Path(args.record).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"REFUSED: cannot read record: {exc}", file=sys.stderr)
        return 1

    try:
        verify_interrogation(record)
    except InterrogationError as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return 1

    consolidated = bool(record.get("consolidated"))
    print(f"interrogation ok: {args.record} "
          f"(mode={record.get('mode')}, questions={len(record['questions'])}, "
          f"consolidated={consolidated})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
