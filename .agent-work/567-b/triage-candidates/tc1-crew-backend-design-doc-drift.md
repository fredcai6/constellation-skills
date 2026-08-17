# Triage candidate: crew-backend-design spec Decision 2 is now stale

**Not filed — a recommendation only, per launch order `decision:no-issue-filing`.**

## What
`docs/superpowers/specs/2026-07-07-crew-backend-design.md` Decision 2 states: "The result
contract is backend-invariant ... every backend honors the same four durable properties
... reused verbatim, never forked." This lane's fix (`scripts/run_crew.py`,
`ExternalBackend.verify()`) intentionally narrows that for `ExternalBackend` only: the
base `result_exists`/`result_fresh` contract stays shared and unforked, but a NEW
spine-evidence requirement is layered on top of `ExternalBackend` alone, so
`CliBackend.verify()` and `ExternalBackend.verify()` no longer behave identically on a
fresh result with no spine evidence (see `PLAN_ALTERNATIVES.md` "Revision after cold
critic" and the rewritten `BackendInvariantContractTests` in
`tests/test_crew_launcher.py` for the justification and the red/green proof).

## Why it matters
A reader of the spec file would believe the two backends still verify identically. They
no longer do, for a specific, documented, evidence-backed reason (#432). The spec's prose
is stale relative to shipped code.

## Suggested disposition
Update Decision 2's prose in the spec (or add a superseding note) to record the
`ExternalBackend`-only narrowing and point at #432/epic-567 as the reason. Small, doc-only
change; no code change implied.

## Source
Surfaced by the g1 implementer in `IMPLEMENTER_RESULT` ("Out-of-scope observations"),
confirmed by the Commander at integration.
