#!/usr/bin/env python
"""Refuse a skipped smell or a silent override — the reviewer Fowler-pass RAIL.

This is the mechanically-enforced rail for the `constellation-reviewer`
sharpening (DESIGN_SPEC Section D3). The reviewer drives a survey whose
`r6-fowler` item runs a refactoring / code-smell pass in the sense of Martin
Fowler's *Refactoring*. This script is the gate the Fowler-pass RECORD must clear
before that item may record pass. It enforces the two locked behaviors in code,
so neither can rest on the reviewer's self-assertion:

  * VISIT-EVERY-SMELL. The pass must render a verdict on every smell in Fowler's
    baseline catalog (`REQUIRED_SMELLS`). A record that omits a baseline smell is
    REFUSED — the pass cannot be silently narrowed so a present smell is never
    looked at. Each smell carries exactly one verdict:
      - `flagged`    — smell present and worth raising; needs a non-empty finding.
      - `overridden` — smell present but a DOCUMENTED REPO STANDARD makes it
                       acceptable, so it is NOT flagged. This is the bounded
                       override: it MUST carry a logged reason — a non-empty
                       `override.repo_standard` (the standard that wins) AND a
                       non-empty `override.reason` (why it subordinates the smell).
                       "Repo standard wins" is never a silent, unexplained
                       dismissal (the OVERRIDE-LOG rail).
      - `absent`     — smell not present in the diff; no further obligation.

  * The Fowler smells are JUDGMENT CALLS, always subordinate to the repo's
    documented standards — never hard violations. The rail does NOT decide whether
    a smell is really present or whether an override is wise; it only refuses a
    SKIPPED smell and a silent (unlogged) override. Which smells to flag, and
    whether the pass genuinely sharpened the review, is the INDEPENDENT reviewer's
    judgment (DESIGN_SPEC TF8), deliberately NOT gated here.

A defended exception — skipping the whole pass (e.g. a docs-only diff with no code
to smell-test) — requires a `rail_exception` carrying a non-empty `reviewer_cosign`
(the INDEPENDENT reviewer, never the author) AND a non-empty `log`. Self-assertion
never passes. The exception covers the whole-pass skip ONLY; it never excuses a
single unlogged override once the pass is run. Standard library only.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Fowler's baseline smell catalog (the ~12 the pass must visit). Names are the
# smell concepts from *Refactoring*, not any external skill's wording.
REQUIRED_SMELLS = (
    "long-method",
    "large-class",
    "duplicated-code",
    "feature-envy",
    "data-clumps",
    "primitive-obsession",
    "long-parameter-list",
    "shotgun-surgery",
    "divergent-change",
    "message-chains",
    "speculative-generality",
    "comments-as-deodorant",
)
VALID_VERDICTS = ("flagged", "overridden", "absent")


class FowlerPassError(Exception):
    """Raised when a Fowler-pass record fails the rail — the refusal."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise FowlerPassError(message)


def _nonempty(value: object) -> bool:
    return bool(str(value).strip()) if value is not None else False


def _exception_cosigned(record: dict) -> bool:
    """True only when an INDEPENDENT reviewer co-signed a whole-pass skip AND a log
    entry records it. Self-assertion (no reviewer_cosign) is not enough."""
    exc = record.get("rail_exception")
    if not isinstance(exc, dict):
        return False
    return _nonempty(exc.get("reviewer_cosign")) and _nonempty(exc.get("log"))


def verify_structure(record: object) -> dict:
    """The record's basic shape: a diff reference and a smell list with unique,
    known smell names and valid verdicts."""
    _require(isinstance(record, dict), "record is not a JSON object")
    assert isinstance(record, dict)

    _require(_nonempty(record.get("diff_ref")),
             "record.diff_ref is missing or empty (what was smell-tested)")

    smells = record.get("smells")
    _require(isinstance(smells, list) and len(smells) > 0,
             "record.smells is missing or empty (the Fowler pass renders a verdict per smell)")
    assert isinstance(smells, list)

    seen: set[str] = set()
    for idx, s in enumerate(smells):
        _require(isinstance(s, dict), f"smell #{idx} is not an object")
        name = str(s.get("smell", "")).strip()
        _require(bool(name), f"smell #{idx} is missing a smell name")
        _require(name in REQUIRED_SMELLS,
                 f"smell {name!r} is not in Fowler's baseline catalog "
                 f"{'/'.join(REQUIRED_SMELLS)}")
        _require(name not in seen, f"duplicate smell entry {name!r}")
        seen.add(name)
        verdict = s.get("verdict")
        _require(verdict in VALID_VERDICTS,
                 f"smell {name!r} verdict is {verdict!r}, expected one of "
                 f"{'/'.join(VALID_VERDICTS)}")
    return record


def verify_visit_every_smell(record: dict) -> None:
    """Visit-every-item: every baseline smell has a verdict — unless a reviewer-
    cosigned exception covers skipping the whole pass."""
    present = {str(s.get("smell", "")).strip() for s in record["smells"]}
    missing = [name for name in REQUIRED_SMELLS if name not in present]
    if not missing:
        return
    if _exception_cosigned(record):
        return
    raise FowlerPassError(
        f"the Fowler pass skipped baseline smell(s) {missing} — every smell must "
        f"carry a verdict (visit-every-item). Skipping the whole pass needs a "
        f"reviewer-cosigned rail_exception (reviewer_cosign + log); a self-asserted "
        f"skip never passes."
    )


def verify_overrides_logged(record: dict) -> None:
    """The bounded override rail: an `overridden` verdict (smell present but a
    documented repo standard wins, so NOT flagged) needs a logged reason — the
    standard that wins AND why. A `flagged` verdict needs a finding."""
    for s in record["smells"]:
        name = str(s.get("smell", "")).strip()
        verdict = s.get("verdict")
        if verdict == "flagged":
            _require(
                _nonempty(s.get("finding")),
                f"smell {name!r} is flagged with no finding — a flagged smell "
                f"records what was found.",
            )
        elif verdict == "overridden":
            override = s.get("override")
            _require(
                isinstance(override, dict),
                f"OVERRIDE-LOG: smell {name!r} is overridden with no override block "
                f"— 'repo standard wins' is never a silent dismissal; log the "
                f"standard and the reason.",
            )
            assert isinstance(override, dict)
            _require(
                _nonempty(override.get("repo_standard")),
                f"OVERRIDE-LOG: smell {name!r} is overridden with no "
                f"override.repo_standard — name the documented standard that "
                f"subordinates the smell.",
            )
            _require(
                _nonempty(override.get("reason")),
                f"OVERRIDE-LOG: smell {name!r} is overridden with no "
                f"override.reason — say why the standard subordinates the smell.",
            )


def verify_fowler_pass(record: object) -> None:
    """Raise FowlerPassError on any failed rule; return None if the record clears
    the rail. Order is deliberate: shape first, then visit-every-smell, then the
    override-log rail."""
    record = verify_structure(record)
    verify_visit_every_smell(record)
    verify_overrides_logged(record)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("record", help="path to the Fowler-pass record JSON")
    args = parser.parse_args(argv)

    try:
        record = json.loads(Path(args.record).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"REFUSED: cannot read record: {exc}", file=sys.stderr)
        return 1

    try:
        verify_fowler_pass(record)
    except FowlerPassError as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return 1

    flagged = [s["smell"] for s in record["smells"] if s.get("verdict") == "flagged"]
    overridden = [s["smell"] for s in record["smells"] if s.get("verdict") == "overridden"]
    print(f"fowler pass ok: {args.record} "
          f"(smells={len(record['smells'])}, flagged={flagged}, overridden={overridden})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
