# Triage Recommendation: Persist verbatim classification status for DNF truth

## Classification
`feature, missing capability anchor, research hardening`

## Source checklist/artifact
- Issue #606 decomposition methodology and DNF proxy audit

## Structural anchor
`struct:data`

## Cartographer mismatch class
`missing capability anchor`

## Problem
`session_classifications` stores ordinal position but discards FastF1's verbatim `Status`, so DNF/reliability opportunity cannot be identified from canonical classification facts.

## Current truth
Across 2,036 race-classification rows for 2022–2026, there are no P30 sentinel rows and no status column. The existing `get_race_results()` derives a `<90%` lap-completion proxy, but it omits drivers with no timed race lap, misses late retirements, and cannot distinguish mechanical failure from other causes.

## Desired/future concern
Persist source status losslessly and expose a strict read API so #389 can define and test an explicit reliability taxonomy without overloading ordinal finishing position.

## Evidence
- `src/data/schema.sql` `session_classifications`
- `src/data/load_fastf1.py` already reads result `Status`
- `src/data/database/_results.py` lap-completion proxy
- Issue #606 full-corpus DNF audit

## Impact
DNF capacity is currently unidentifiable rather than zero. Proceeding with #389 would either use a biased proxy or encode an ungrounded status taxonomy.

## Suggested scope
Add nullable verbatim `status TEXT`, persist it through classification collection/upsert, provide concrete read and batch-read methods, define an explicit tested status taxonomy at the consumer boundary, and backfill classifications for 2022–2026 using the existing collector path.

## Non-goals
Do not build the DNF sampler tail or tune reliability effects in this issue.

## Acceptance criteria
- [ ] Schema migration adds nullable `status TEXT` without changing existing position semantics.
- [ ] Collector and upsert preserve FastF1 Status verbatim and fail clearly on malformed rows.
- [ ] Read-only single/batch APIs return status with provenance.
- [ ] 2022–2026 classifications are backfilled and audited for coverage, nulls, and observed status vocabulary.
- [ ] Tests define which statuses count as reliability/DNF opportunity; unknown statuses remain explicit.
- [ ] Issue #389 is updated to depend on this evidence before its capacity gate.

## Recommended priority
`high`

**Reason:** It is the minimum truth-enablement step allowed by the #606 capacity verdict.

## Related artifacts
- Epic #601
- Issues #606 and #389

## Disposition
`filed`

**Detail:** filed as #617

## Issue creation authority
`create issue directly`
