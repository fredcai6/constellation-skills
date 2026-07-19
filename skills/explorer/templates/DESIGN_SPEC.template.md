# Design Spec — <topic>

**UNCONFIRMED — DO NOT CUT**

_Draft state. This spec has not passed the confirm gate. `verify_spec_confirmed.py` refuses it until the Confirmation block below is filled (Status CONFIRMED, confirmer, date) and every Disposition cell in the Critic findings table is filled. Do not cut issues or epics from this document while the marker line above stands._

## Confirmation

- **Status: DRAFT — UNCONFIRMED — DO NOT CUT**
- Confirmed by:
- Date:
- Critic findings dispositioned: NO — every row in the Critic findings table must carry a Disposition before confirm
- Assumptions exercised:
- Assumptions accepted untested:

> To confirm: delete the loud `UNCONFIRMED — DO NOT CUT` marker line at the top, set Status to `CONFIRMED`, fill Confirmed by and Date, record the assumptions lines, and ensure no Disposition cell is empty. The confirm gate records a human `user-decision` alongside this block; the engine does not cryptographically prove a human made the call, so the filled block plus the downstream refusal are the mechanical backstops.

## Intent

<The point, stated plainly: what itch this serves, for whom, and what "done" feels like. One or two paragraphs. This is the intent the critic's intent-fit lens tests the design against.>

## Exploration record (digest)

<A digest of how the design was shaped — not the full transcript.>

- **Cycles run:** <flavors and the arc, e.g. shotgun -> compare -> refine>
- **Excursion answers:** <each named question and its verdict, INCLUDING scoped nulls — "this spike of X under conditions Y failed", never generalized to the idea class without evidence spanning it>
- **Rejected approaches, with reasons:** <what was considered and dropped, and why — a cull is a scoped verdict that can come back>
- **Open threads carried:** <anything unresolved at convergence>

## Chosen design

<The design itself. Describe every interface in deep-module terms — interface = everything a caller must know (invariants, ordering, error modes, config, performance), not just the type surface. Present in complexity-scaled sections; mark per-section approval. For every load-bearing interface, record the design-it-twice outcome (constraints compared, recommendation or hybrid) or the stated reason it was skipped as trivial.>

- **Per-section approval:** <mark each load-bearing section approved, and by whom>
- **Transcription-grade restoration:** <if this design restores one body of role-specific doctrine verbatim (transcription-grade) into structurally different roles under a no-paraphrase constraint, pre-name the adapted per-role wording HERE — spell out each divergent target's clause, not just a role-noun swap — since the constraint forbids the implementer from inventing the structural substitution. See the explorer "Spec phase" doctrine.>

## Testing pathways

<The end goal is deep, testable, and tested pathways. For each pathway: how it is exercised and how it could be falsified. Name what this run tests versus what is deferred to a later drill.>

## Out of scope

<What this design deliberately does not do, and candidates deferred to triage.>

## Critic findings and dispositions

<The cold adversarial review's findings. The columns below are contractual and machine-parsed — do not rename them. Disposition is one of EDIT / RE-EXPLORE / REJECT; a RE-EXPLORE reopens the explore step. Every row must carry a Disposition and a Reason before the spec can confirm.>

| ID | Lens | Severity | Finding | Disposition | Reason |
|---|---|---|---|---|---|
| F1 | intent-fit | MAJOR | worked example: the critic's attack on a deliberate decision |  |  |
