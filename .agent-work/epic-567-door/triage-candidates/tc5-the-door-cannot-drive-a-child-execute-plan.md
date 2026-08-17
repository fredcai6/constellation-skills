# Triage candidate: the door cannot drive a Commander's child `execute.json` plan

**Status:** not filed. Held to closeout per the epic's standing ruling.

**Found by:** the Admiral of epic-567-door, 2026-08-17, adjudicating lane F's artifacts mid-wave.

**Proposed pairing:** **#559** — it is the boundary of #559's own claim. The door became the
interface for a run's spine; it did not become the interface for the child plan that same run
drives through its `execute` step.

## Measured

- Lane F's `.agent-work/567-f/execute.json.journal`: `start`, `attest`, `advance` under session
  id **`commander-567-f-execute`** — hand-supplied on the CLI, not the door's assignment-keyed
  `constellation/567-f/lane-f/commander-delegated`.
- Lane H's journal: same shape, `commander-567-h-execute`. **Two independent lanes**, so this is
  structural rather than one Commander's improvisation.
- Lane F made **70** door calls. Every one targets `spine.json`. **None** targets `execute.json`.
- The door ships 12 verbs. None takes a target file except `spine_bind` and `spine_open`.
  `spine_advance`'s `from_child` consumes a child checklist's consolidation as evidence; it does
  not drive the child's gates.

## Inferred, and flagged as inference

A Commander cannot bind its child plan even in principle, because `spine_bind` is refused while
the door holds an active lease on a different spine — and a mid-run Commander always holds one on
its own `spine.json`. The refusal shape was measured today against the epic spine (*"is under an
active lease held as … that is the very identity this bind would take"*), but the exact
lease-held-then-bind-child case was **not** constructed and is not claimed as measured.

## Why this is a trade rather than a defect

The property that makes `spine_bind` safe — one checkout's work-area tree per process, one spine
per process, refused while leased elsewhere — is precisely what closes the child-plan path. The
isolation bought the identity guarantee that #559 needed and cost the ability to drive a second
plan file from the same process. Recording it as a trade, with both halves named, rather than as
an oversight.

## Consequence for the sweep

The CLI is the **only** documented path for a step every Commander performs. Any doctrine sweep
has to either leave that instruction standing with its reason, or the door needs a verb that
drives a named child plan. Deleting the text without one of those two would remove the only route
through a gate the corpus requires.
