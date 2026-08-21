# Latitude Contract - 20260820-deficiency-cleanup

## Epic intent

Reconcile the local defect ledger with current main and the live GitHub issue graph, complete the bounded cleanup repairs, and prepare an independently criticized architecture choice without silently widening the epic.

## Success shape

- Wave 1 and the bounded implementation lane in Wave 2 are implemented and independently reviewed on local branches.
- The architecture cluster has at least two concrete candidates, a cold critique, an issue reconciliation, and a recommendation ready for human convergence.
- Honest negative findings are acceptable when they retire a stale premise or show that an issue should be closed or re-scoped.
- Issue #639 is routed to epic #572, with #575 retaining the Windows proof obligation.

## Checkpoint protocol

The Admiral is cleared to execute local work through the end of Wave 2. Stop and present before choosing or implementing an architecture candidate, mutating GitHub, pushing branches, opening pull requests, or merging to main.

## Decision classes

| Decision class | Authority | Rule |
|---|---|---|
| Bounded implementation within #500, #613, #636, or the mechanical closeout part of #638 | Delegated | Preserve stated issue intent, add regression evidence, and remain inside the named files and behaviors. |
| Architecture for the #634/#638/#632/#357/#369/#615 cluster | Surfaced | Delegate evidence gathering, alternatives, and critique; human chooses before implementation. |
| Scope reconciliation for #457 and CONSTELLATION_DEFECTS.md | Delegated for analysis | Any GitHub edit, closure, reopening, or new issue is surfaced. |
| Local feature branches and commits | Delegated | Do not stage or overwrite unrelated user work. |
| Merge into a temporary epic integration branch | Delegated | Only after review evidence and conflict adjudication. |
| Merge to main | Surfaced | Requires human approval at the checkpoint. |
| Push, PR creation, or GitHub mutation | Surfaced | Requires explicit authorization. |
| Bounded fix-now work discovered inside an approved lane | Delegated | The cause, files, behavior, and tests must remain within that lane. |
| New implementation lane or cross-cutting scope | Surfaced | Record it as float-up work; do not absorb it. |
| Model or spend choice | Delegated | Use the least-powerful adequate model and keep waves bounded. |
| Production-facing default or compatibility change | Surfaced | Proceed only when an inherited human ruling already settles it. |
| Doctrine or reusable lesson change | Surfaced | Record candidates; do not apply them during the epic. |
| Any unlisted class | Surfaced | Out-of-taxonomy decisions always escalate. |

## Float-up routing

Commander decisions that fit a delegated class are decided and logged by the Admiral. Architecture choices, scope expansion, external publication, GitHub mutation, production defaults, and unlisted decisions float to the human checkpoint. A Commander encountering one of these must stop that lane with evidence instead of guessing.

## Communication and budget

Use concise wave-boundary updates and report material exceptions immediately. Run three bounded Wave 1 lanes, then one bounded Wave 2 implementation lane plus architecture alternatives and cold critique. Prefer the least-powerful adequate model and stop if evidence invalidates the wave split.

### Model-tier policy

- The Admiral retains the frontier tier for epic decomposition, cross-lane adjudication, and the human checkpoint.
- Every new Commander, Implementer, Reviewer, Cartographer, Scout, critic, and reconciliation subagent launches on `gpt-5.6-terra` by default.
- The Admiral simplifies each handoff enough for Terra before dispatch.
- Escalation above Terra requires a concrete task failure or complexity finding and a logged Admiral ruling. Existing completed evidence is not rerun solely to change its model tier.

## Pre-rulings

| Ruling | Grade | Basis |
|---|---|---|
| Route #639 to #572 and retain #575 as its proof obligation. | Settled | Human decision. |
| Wave 1 is #500, #636, and the mechanical closeout half of #638. | Settled | Human approval. |
| Wave 2 is residual #613 plus architecture evidence and issue reconciliation, not architecture implementation. | Settled | Human approval. |
| The tightened #500 refresh-consumption behavior is acceptable. | Settled | Existing confirmed design artifact. |
| Split #638 into mechanical closeout wiring and a separate authority/architecture decision. | Settled | Human approval of the wave plan. |
| No publication or merge to main before the checkpoint. | Settled | Inherited repository and GitHub authority boundary. |
| Delegated Commander and crew work defaults to gpt-5.6-terra; the Admiral keeps the stronger tier. | Settled | Human direction on 2026-08-20. |

## Expiry

This contract expires at the end of Wave 2, or earlier if evidence invalidates the mechanical/architecture split or requires an external action not listed above.

## Confirmation

Confirmed by Tommy on 2026-08-20: the plan is approved; continue autonomously and return at the architecture checkpoint.
