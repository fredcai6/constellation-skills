# Constellation Feedback (staged export — runner-durability-130)

## 2026-07-19 — engine-CLI result-reading ergonomics
**Lesson:** engine-cli-rail-banner-obscures-results
**Scope:** constellation (workbench checklist_engine.py CLI)
**Observation:** `checklist_engine.py` prints the `RAIL: ...` guidance banner to stderr on EVERY
invocation (including `attest`/`start`/`attach`/`advance`). When an agent reads results with the
common `... 2>&1 | tail -1`, the banner is what `tail` returns, masking the actual result/refusal
line — I repeatedly had to `grep -v '^RAIL'` or inspect the spine JSON directly to confirm an op
landed. Minor, but it makes headless driving noisier and error-prone.
**Suggestion:** route the RAIL banner to a distinct stream/prefix the caller can reliably strip, or
emit the operative result as the LAST stderr line. Non-blocking.

## 2026-07-19 — flag-candidate arg shape differs from sibling verbs
**Lesson:** engine-cli-flag-candidate-arg-shape
**Scope:** constellation (workbench checklist_engine.py CLI)
**Observation:** most engine verbs take repeated `--field k=v`; `flag-candidate` instead requires
`--from` + `--statement` and rejects `--field`. First attempt errored. Minor discoverability friction.
**Suggestion:** accept `--field`-style args on `flag-candidate` too, or note the divergence in the
verb help. Non-blocking.
