# scripts.verify_diagnosis
scripts/verify_diagnosis.py, 197 lines, 3 holes

Refuse an unreproduced diagnosis — the constellation-diagnose RAIL.

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

imports stdlib: __future__.annotations, argparse, json, pathlib.Path, sys
imported by: none found

```python
VALID_ALTITUDES = ('runtime', 'disconnect')
VALID_STATUSES = ('suspected', 'confirmed', 'explained-by-design')
VALID_ROUTES = ('triage', 'reviewer', 'note')
```

- [DiagnosisError](DiagnosisError.md) class: Raised when a finding record fails the rail — the refusal.
- [_require](_require.md) function: HOLE: no docstring
- [_nonempty](_nonempty.md) function: HOLE: no docstring
- [verify_structure](verify_structure.md) function: Rule 1: the loop's basic shape — symptom, altitude, oracle, status.
- [verify_map_staleness_caveat](verify_map_staleness_caveat.md) function: Rule 2: a disconnect-altitude finding carries the map-staleness caveat.
- [_exception_cosigned](_exception_cosigned.md) function: True only when an INDEPENDENT reviewer co-signed the exception AND a log
- [verify_reproduce_before_claim](verify_reproduce_before_claim.md) function: Rule 3 (THE RAIL): a confirmed cause must carry a named falsifier + an
- [verify_route](verify_route.md) function: Rule 4: route out (don't fix). A confirmed fault goes to triage/reviewer;
- [verify_diagnosis](verify_diagnosis.md) function: Raise DiagnosisError on any failed rule; return None if the finding record
- [main](main.md) function: HOLE: no docstring
