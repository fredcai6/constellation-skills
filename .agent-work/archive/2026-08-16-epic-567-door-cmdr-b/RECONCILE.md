# Reconcile — cmdr-567-b

No `docs/architecture` packet map exists in this repo (skill-source repo, confirmed
DEGRADED-UNPARSEABLE at `context`). Per the reconcile step's own doctrine for this case:
"reconcile the structural record directly instead: fold the change into the schema or
design doc it actually touches, and where the change touched neither, record a reasoned
no-op as compliant."

## Design doc this change touches

`docs/superpowers/specs/2026-07-07-crew-backend-design.md` Decision 2 ("the result
contract is backend-invariant ... reused verbatim, never forked") is now stale: this run's
fix intentionally narrows it for `ExternalBackend` only (a new spine-evidence gate layered
on top of the shared, unforked exists-AND-fresh base). Both the implementer and reviewer
independently confirmed this drift (see `g1-implement-implementer-result.md` Map Impact,
`g1-reviewer-result.md` Map impact verdict) and it is written as a triage candidate:
`.agent-work/567-b/triage-candidates/tc1-crew-backend-design-doc-drift.md`.

## Reasoned no-op: the doc is NOT edited here

The launch order's File Ownership section states plainly: "Sole writer this wave of: the
ExternalBackend dispatch path and its tests." That names `scripts/run_crew.py` and
`tests/test_crew_launcher.py` — not `docs/superpowers/specs/*.md`. Editing the spec doc,
even a small, low-risk prose fix, is not inside that stated scope, and the launch order's
Inherited Latitude reserves "any scope change" for a float to the Admiral, not a unilateral
decision at reconcile. Rather than stretch the fence at the very last step of the run, the
doc drift is left exactly where it already is: accurately triaged, not filed, not silently
fixed. This is the compliant no-op the reconcile step's own doctrine names for a change
that touches a design doc this lane does not own the authority to edit.

## No other structural record to fold into

No schema file, no other design doc, no `docs/architecture` map. Nothing else to
reconcile.

## Rework addendum (post-return, g2)

The Admiral's post-return diagnosis and the g2 rework it triggered touched no design doc
at all — 2 test files (test-only edits, no contract/spec they document), 1 episode
assertion (fixed via its own dedicated writer, `restate-assertion`), and confirmed (but
did not edit) `map/INDEX.md` staleness, explicitly left to the Admiral. A third triage
candidate was added (`tc3-imperative-detector-homograph-allowlist-growth.md`), same
disposition as tc1/tc2: recorded, not filed, not fixed outside this lane's authority. No
change to this reconcile step's original conclusion.
