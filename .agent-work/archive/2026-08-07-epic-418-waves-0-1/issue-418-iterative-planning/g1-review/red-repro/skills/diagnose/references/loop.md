# The diagnose loop and finding-record schema

The finding record is one JSON object — the evidence of a diagnose run and the
input to the rail (`scripts/verify_diagnosis.py`). It is evidence, never a fix.

## Finding-record fields

- `symptom` (string, required) — the observed behavior that disagrees with what
  was intended. Non-empty.
- `altitude` (string, required) — `runtime` (code does the wrong thing; the
  oracle is a test) or `disconnect` (execution drifted from the map/intent; the
  oracle is the map/intent used as a runtime probe). No other value.
- `oracle` (string, required) — the reproduce mechanism: name the failing test,
  or the map/intent claim being probed against actual behavior. Non-empty.
- `status` (string, required) — `suspected` (mid-loop), `confirmed` (reproduced),
  or `explained-by-design` (behavior is intended; not a fault).
- `cause` (string) — the localized mechanism the loop found.
- `falsifier` (string) — the named observation that would disprove `cause`.
  **Required (non-empty) for a `confirmed` finding** (unless a reviewer-cosigned
  exception covers it).
- `observed_result` (string) — the reproduce/instrument result actually seen
  (e.g. "expected 5, got 6"). **Required (non-empty) for a `confirmed` finding**
  (unless a reviewer-cosigned exception covers it).
- `map_staleness_caveat` (string) — **required (non-empty) for a `disconnect`
  finding**: the note that the map/intent oracle may be stale and the reviewer
  must weigh it. Oracle-soundness is not independently gated (accepted risk).
- `route` (string) — where the finding goes; diagnose does not fix.
  **Required for `confirmed` and `explained-by-design`.** A `confirmed` fault
  routes OUT — `triage` or `reviewer`. An `explained-by-design` finding is a
  `note`. No other value.
- `rail_exception` (object) — the ONLY way a `confirmed` cause skips the
  reproduce evidence. Requires:
  - `reviewer_cosign` (string) — the INDEPENDENT reviewer's name/id, never the
    author's. Non-empty.
  - `log` (string) — why this trivial case may skip the loop. Non-empty.
  Self-assertion (no `reviewer_cosign`) never passes the rail.

## The rail (`verify_diagnosis.py`)

Refuses (exits non-zero) on: an empty `symptom`; an `altitude` not in
`runtime`/`disconnect`; an empty `oracle`; a `status` not in the three values; a
`disconnect` finding with no `map_staleness_caveat`; a `confirmed` finding with
no (`falsifier` + `observed_result`) and no cosigned `rail_exception`; a
`confirmed` fault not routed to `triage`/`reviewer`; an `explained-by-design`
finding not routed to `note`. Whether the mechanism found is the RIGHT one, and
whether a trusted map is itself sound, are the independent reviewer's judgment —
not gated here.

## One loop, both altitudes

The loop — reproduce -> localize -> hypothesize -> instrument -> verify — is
identical at both altitudes. Only the **reproduce** step's oracle changes: a test
that fails on a runtime bug; the map/intent probed against actual behavior for a
disconnect. Everything downstream (localize, hypothesize with a falsifier,
instrument, verify) is the same investigation over the same finding record.
