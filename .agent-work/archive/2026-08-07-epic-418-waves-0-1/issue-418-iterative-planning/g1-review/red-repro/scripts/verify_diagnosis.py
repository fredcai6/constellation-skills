#!/usr/bin/env python
"""Refuse an unreproduced diagnosis — the constellation-diagnose RAIL.

This is the single mechanically-enforced rail for the `constellation-diagnose`
skill (DESIGN_SPEC Section B): **reproduce-before-you-claim**. Diagnose runs one
loop — reproduce -> localize -> hypothesize -> instrument -> verify — over a
finding record; this script is the gate that record must clear before a cause
may be called *confirmed*. A "confirmed" cause that carries no named falsifier
and no observed reproduce/instrument result is refused here, in code, so the
claim can never rest on self-assertion.

The finding record is one JSON object (schema: skills/diagnose/references/loop.md
and templates/FINDING.template.json). It exits NON-ZERO (and raises
`DiagnosisError`) on any of these:

  1. STRUCTURAL BASICS — a non-empty `symptom` (observed behavior disagreeing
     with intent); an `altitude` of `runtime` or `disconnect`; a non-empty
     `oracle` (the reproduce mechanism: a test at runtime altitude, the map/
     intent-as-probe at disconnect altitude); a `status` of
     suspected/confirmed/explained-by-design.

  2. DISCONNECT MAP-STALENESS CAVEAT — a `disconnect`-altitude finding must carry
     a non-empty `map_staleness_caveat`. The map/intent is the oracle for a
     disconnect and a stale map yields false verdicts (DESIGN_SPEC Section B
     accepted risk, TF6); the caveat is carried on the record so the reviewer
     weighs it. Oracle-soundness is deliberately NOT gated — only that the
     caveat is present.

  3. THE RAIL — reproduce-before-you-claim. A `confirmed` finding must satisfy
     EITHER the reproduce path — a non-empty `falsifier` (what observation would
     disprove this cause) AND a non-empty `observed_result` (the reproduce/
     instrument result actually seen) — OR the exception path: a
     `rail_exception` carrying a non-empty `reviewer_cosign` (the INDEPENDENT
     reviewer, never the author) AND a non-empty `log` entry. Self-assertion —
     a confirmed claim with neither reproduce evidence nor a reviewer co-sign —
     never passes (DESIGN_SPEC Section B, TF1/TF3). *Falsifier for this rail: a
     confirmed finding with no reproduce evidence and no co-sign passes.*

  4. ROUTE-OUT, DON'T-FIX — diagnose diagnoses; it does not fix. A `confirmed`
     real fault routes OUT (`triage` or `reviewer`); an `explained-by-design`
     finding is handed back as a `note`. This encodes that diagnose owns no fix
     and no durable truth (DESIGN_SPEC Section B).

Everything else about the investigation — whether the localized mechanism is the
RIGHT one, whether the map the disconnect probe trusted is itself sound — is the
INDEPENDENT reviewer's judgment, deliberately NOT gated here. Standard library
only.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

VALID_ALTITUDES = ("runtime", "disconnect")
VALID_STATUSES = ("suspected", "confirmed", "explained-by-design")
VALID_ROUTES = ("triage", "reviewer", "note")


class DiagnosisError(Exception):
    """Raised when a finding record fails the rail — the refusal."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise DiagnosisError(message)


def _nonempty(value: object) -> bool:
    return bool(str(value).strip()) if value is not None else False


def verify_structure(finding: object) -> dict:
    """Rule 1: the loop's basic shape — symptom, altitude, oracle, status."""
    _require(isinstance(finding, dict), "finding is not a JSON object")
    assert isinstance(finding, dict)

    _require(_nonempty(finding.get("symptom")),
             "finding.symptom is missing or empty (the observed behavior that disagrees with intent)")

    altitude = finding.get("altitude")
    _require(
        altitude in VALID_ALTITUDES,
        f"finding.altitude is {altitude!r}, expected one of {'/'.join(VALID_ALTITUDES)}",
    )

    _require(
        _nonempty(finding.get("oracle")),
        "finding.oracle is missing or empty (the reproduce mechanism: a test at "
        "runtime altitude, the map/intent probe at disconnect altitude)",
    )

    status = finding.get("status")
    _require(
        status in VALID_STATUSES,
        f"finding.status is {status!r}, expected one of {'/'.join(VALID_STATUSES)}",
    )
    return finding


def verify_map_staleness_caveat(finding: dict) -> None:
    """Rule 2: a disconnect-altitude finding carries the map-staleness caveat."""
    if finding.get("altitude") == "disconnect":
        _require(
            _nonempty(finding.get("map_staleness_caveat")),
            "disconnect-altitude finding carries no map_staleness_caveat — the "
            "map/intent is the oracle and a stale map yields false verdicts "
            "(accepted risk; the caveat must be present for the reviewer to weigh)",
        )


def _exception_cosigned(finding: dict) -> bool:
    """True only when an INDEPENDENT reviewer co-signed the exception AND a log
    entry records it. Self-assertion (no reviewer_cosign) is not enough."""
    exc = finding.get("rail_exception")
    if not isinstance(exc, dict):
        return False
    return _nonempty(exc.get("reviewer_cosign")) and _nonempty(exc.get("log"))


def verify_reproduce_before_claim(finding: dict) -> None:
    """Rule 3 (THE RAIL): a confirmed cause must carry a named falsifier + an
    observed reproduce/instrument result, OR a reviewer co-signed exception."""
    if finding.get("status") != "confirmed":
        return
    reproduced = _nonempty(finding.get("falsifier")) and _nonempty(finding.get("observed_result"))
    if reproduced:
        return
    if _exception_cosigned(finding):
        return
    raise DiagnosisError(
        "REPRODUCE-BEFORE-YOU-CLAIM: a 'confirmed' cause needs a named falsifier "
        "AND an observed reproduce/instrument result. Neither is present, and no "
        "reviewer-cosigned rail_exception (reviewer_cosign + log) covers it. "
        "Self-assertion never confirms a cause."
    )


def verify_route(finding: dict) -> None:
    """Rule 4: route out (don't fix). A confirmed fault goes to triage/reviewer;
    an explained-by-design finding is handed back as a note."""
    status = finding.get("status")
    route = finding.get("route")
    if status in ("confirmed", "explained-by-design"):
        _require(
            route in VALID_ROUTES,
            f"finding.route is {route!r}, expected one of {'/'.join(VALID_ROUTES)}",
        )
    if status == "confirmed":
        _require(
            route in ("triage", "reviewer"),
            f"a confirmed fault must route OUT to triage or reviewer (diagnose "
            f"does not fix); route={route!r}",
        )
    if status == "explained-by-design":
        _require(
            route == "note",
            f"an explained-by-design finding is handed back as a note; route={route!r}",
        )


def verify_diagnosis(finding: object) -> None:
    """Raise DiagnosisError on any failed rule; return None if the finding record
    clears the rail. Order is deliberate: shape first, then the reproduce gate."""
    finding = verify_structure(finding)
    verify_map_staleness_caveat(finding)
    verify_reproduce_before_claim(finding)
    verify_route(finding)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("finding", help="path to the finding-record JSON")
    args = parser.parse_args(argv)

    try:
        finding = json.loads(Path(args.finding).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"REFUSED: cannot read finding: {exc}", file=sys.stderr)
        return 1

    try:
        verify_diagnosis(finding)
    except DiagnosisError as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return 1

    status = finding.get("status")
    print(f"finding ok: {args.finding} (altitude={finding.get('altitude')}, status={status})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
