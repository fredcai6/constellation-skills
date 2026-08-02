# Latitude Contract: `epic-659`

Confirmed by Fred (owner) 2026-07-25 before wave 1. The dial between "I don't care, go" and
"float me the details." Re-confirm on expiry (the #670 gate) or when the ground shifts under it.

## Epic Intent
Build 1 (quali-side, 2023-first) of the physics decomposition: reassemble measured capability
envelopes into per-car **reference laps**, measure each driver as **utilization of their own
reference** conditioned on the circuit's segment composition. Car = reference; driver = utilization.
This changes the physics→prediction **payload**, not the injection mechanism. Deliverable is stores +
instruments; nothing wires into live prediction (deliberately deferred). The connective pipeline is a
durable asset that ends the five-lineage rediscovery loop regardless of the size of the driver term.

## Success Shape
Build 1 running end-to-end on 2023 — per-weekend segment maps, a grip baseline, a season-scale
class-grain utilization store, fitted fingerprints, the join producing quali-side weekend priors — with
the instrument panel reporting the **size** of every signal. **A measured null is a complete, successful
deliverable** (owner no-kill ruling): weak signal routes to structural work, never abandonment. Steering
is by **allocation, not gating**.

## Checkpoint Protocol
Stop-and-present at **every wave boundary**: a plain-English brief (what merged, what the wave proved,
what's next) before dispatching the following wave. Two **hard human stops** are non-negotiable:
- **#660 up front** — Fred freezes the constant set before Wave 1 touches real data.
- **#670** — go/no-go before the season-scale run; allocation decisions after.
What reaches Fred at a checkpoint: plain-English summary, decision asks, evidence on demand.

## Decision Classes

| Class | Disposition |
|---|---|
| Architecture / structural change (data↔physics↔evo boundary) | **surfaced** |
| Scope change (issue added/dropped/re-scoped) | **surfaced** |
| Merge to main (green + reviewed AFK PR) | **delegated** |
| Issue filing (follow-on debt) | **delegated** |
| Issue closing (epic children) | **delegated** (batched at wave checkpoint) |
| Fix-now triage (bounded fix applied immediately) | **delegated** |
| Spend / budget / model tier | **delegated** |
| Production defaults / user-visible behavior | **surfaced** (epic is toggle-gated, out-of-scope for live by design) |
| Frozen-constant values (F12 discipline) | **surfaced — Fred only, via #660** |
| **Out-of-taxonomy** | **always escalates, with one line on why it fit no class** |

- **Apply a lesson / fold doctrine** — surface. Constellation lessons always exported, never silently confirmed. Doctrine graduations (.md/.template) need authority=human.

## Permission prerequisites

| Delegated class | External actions implied | Pre-clearance or fallback |
|---|---|---|
| Merge to main | `gh pr merge` on green+reviewed AFK PR | Fallback (project default is ask-first-merge): if the harness classifier vetoes a delegated merge, take one human approval in the moment, batch remaining equivalent merges to the next wave checkpoint. |
| Issue filing | `gh issue create` for follow-on debt | Autonomous per ORCHESTRATOR_CONTEXT (create is autonomous). |
| Issue closing | `gh issue close` on merged children | Batched at wave checkpoint; fallback = surface the batch if vetoed. |
| Model tier | Agent-tool `model:` selection | Autonomous within Sonnet-default; Opus escalation for #661/#666/#667 pre-cleared here. |

## Float-Up Routing
Commander floats: **decisions** — adjudicate inside delegated classes (log a RULING), escalate surfaced
classes and out-of-taxonomy to Fred out-of-band. **Context queries** — answer from epic knowledge and
continue the Commander; reach Fred out-of-band only when the answer is beyond my knowledge or latitude.
Frozen-constant questions route to #660 (Fred), never self-answered.

## Comms
Plain English by default (minimize per-project jargon), technical depth on demand. No sycophancy —
surface alternatives and critiques tersely. Rationale-heavy decisions in plain text, not AskUserQuestion.

## Budget / Model Parameters
Commanders + crew on **Sonnet** (repo default per [[subagent-model-sonnet]]). **Opus** escalation
pre-cleared for the two design-it-twice-bearing load-bearing interfaces — B/#661 (SegmentMap) and
G/#666 (DriverFingerprint) — and the join H/#667. Season-scale compute is gated at #670 (HITL), so no
long detached run launches without Fred's go. Usage-limit window is a wave-sizing input; defer a wave's
dispatch past a near reset rather than launching into it.

## Pre-Rulings
- decision:honest-null-is-complete — a measured null (weak/absent signal) is a complete successful deliverable; route to structural work, never abandonment.
  @grade: settled/human · leans all-waves
- decision:frozen-constants-source — every threshold is pre-registered via #660 before the first real-data run; no agent picks or tunes a threshold after seeing data; post-hoc change requires a new named constant set + full re-run.
  @grade: settled/human · leans C/#662,E/#664,G/#666,I/#668
- decision:build1-consumes-638-vocabulary — Build 1 consumes the existing validated #638 class vocabulary as-is; the per-era Student-t refit + F12 gate are deferred to backfill (open deferral, stated, not silent).
  @grade: settled/human · leans B/#661,C/#662,G/#666
- decision:pre-quali-constraint — predictions are made before quali; the quali anchor is post-facto calibration only.
  @grade: settled/human · leans E/#664,I/#668
- decision:lowest-dimensionality — escalation layers stay dormant in schemas; activate on demand only.
  @grade: settled/human · leans B/#661,G/#666
- decision:no-baked-normality — Student-t / heavy-tailed forms wherever feasible.
  @grade: settled/human · leans D/#663,G/#666
- decision:660-menu-then-freeze — I compile the exploration's candidate constant values into a proposal menu; Fred ratifies/freezes. #660 gates Wave 1, runs parallel to the rest of Wave 0.
  @grade: settled/human · leans C/#662

## Expiry
Expires at the **#670 gate** (event). I re-confirm rope there regardless — that is where the expensive
season-scale compute and the allocation decisions live. Also re-confirm on any ground-shift (a surfaced
architecture/scope change that Fred re-rules).

## Confirmation
2026-07-25 — confirmed by Fred ("confirmed"), recorded as user-decision evidence on the latitude step.
Interrogator-machinery misfit noted: the latitude conversation used the interrogator *method* (one-at-a-time,
facts-vs-decisions, recommend-an-answer, explicit sign-off) but did NOT stand up a separate interrogation
survey engine — the Admiral spine's latitude gate already carries the human-confirmation postcondition, and
a second parallel survey lease on the same work would be double machinery. Reported for closeout audit.
