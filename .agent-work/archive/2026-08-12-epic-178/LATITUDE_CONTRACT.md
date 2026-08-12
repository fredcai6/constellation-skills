# Latitude Contract: `epic-178` (Context Governor v1)

Confirmed by the human before wave 1. The dial between "I don't care, go" and
"float me the details." Re-confirm on expiry or when the ground shifts under it.

## Epic Intent
Ship the Context Governor v1 exactly as the CONFIRMED DESIGN_SPEC in the epic body prescribes: a proactive, portable way for constellation agents to hand off cleanly at a good work seam before context death, as a byproduct of continuous why-logging. Four modules — Why-capture (engine schema), Gauge (writer + reader), Trip (two-band gate policy), Refresh (reach-up relaunch). **Posture is experimental-v1: ship minimal, measure in use, cull from experience — not perfect.** The outcome that must not be violated: the shipped mechanism matches the post-review amendments in the spec (single `why` field, no migration pass, trimmed 4-field gauge record, gate-boundary-only Trip, uniform engine-native `refresh-request`), and nothing in the spec's "Out of scope" gets built.

## Success Shape
All five child issues (#179 #180 #181 #182 #183) dispositioned: merged green+reviewed, or honest-null closed with a logged reason, or deferred with a ruling. A measured negative (e.g. "the CC gauge writer can't reliably parse fill from the live transcript") is a **complete, successful deliverable** if honestly scoped — the spec already accepts CC-only, unproven-but-wanted pieces. Falsifiable tests from the spec's Testing Pathways pass where mechanical; qualitative judges (refresh "didn't re-derive", SOFT-judgment quality) are recorded observations, not unit gates.

## Checkpoint Protocol
**Cleared to run autonomously through the AFK work** (#179, #181, #182), polling actively — no turn ends to "wait." **Stop-and-present at:**
1. Each wave boundary — a brief plain-English status (what merged, what's next) before dispatching the next wave.
2. The two **HITL** issues — #180 (Gauge writer) and #183 (Refresh sign-off). **Default (human-confirmed):** push each as far as I can autonomously and surface only the *irreducible* human action — for #180 the actual `settings.json` hook edit + eyes on the fill estimate against your real transcript; for #183 the qualitative "did the fresh agent resume without re-deriving the why?" sign-off. I build everything up to that seam so your action is a minimal, well-framed decision. Overridable to hard-stop at any checkpoint.
3. Any surfaced-class or out-of-taxonomy decision.

What reaches you at a checkpoint: plain-English summary first, decision asks called out, evidence (diffs, test output) on demand.

## Decision Classes

| Class | Disposition |
|---|---|
| Architecture / structural change | **delegated** *within* the CONFIRMED spec; **surfaced** if a choice contradicts, extends, or is silent in the spec |
| Scope change (issue added/dropped/re-scoped) | **surfaced** |
| Merge to main | **delegated** (green + independently reviewed only) |
| Issue filing / closing | **delegated** (file triage follow-ups; close child issues on verified merge) |
| Fix-now triage (bounded fix applied immediately, not filed) | **delegated** |
| Spend / budget / model tier | **delegated** |
| Production defaults / user-visible behavior (threshold numbers, exempt-gate lists) | **delegated** to ship a spec-consistent placeholder default *labeled as first-run-calibration TBD*; **surfaced** if a default is a real judgment call the spec didn't set |
| **Out-of-taxonomy** | **always escalates, with one line on why it fit no class** |

- **Apply a lesson / fold doctrine** — **surfaced** (default). Doctrine graduation at closeout needs human authority; code-target graduations (test suite as proof) stay autonomous. Constellation debt is always exported, never silently confirmed.

## Permission prerequisites

| Delegated class | External actions implied | Pre-clearance or fallback |
|---|---|---|
| Merge to main | `gh pr merge`, `git push` | Fallback: if the classifier vetoes, one human approval in the moment, remaining equivalent merges batched to the next checkpoint (per the worked example). |
| Issue filing / closing | `gh issue create/close/comment` | Fallback: same — surface once, batch the rest. |
| Gauge writer (#180) | edit to your `~/.claude/settings.json` (PostToolUse hook) | **HITL by design** — never written without your explicit go; this is a checkpoint, not a delegated action. |

## Float-Up Routing
Commander floats: adjudicate inside delegated classes and log a RULING; escalate surfaced/out-of-taxonomy to you. Context queries: answer from epic knowledge and continue the Commander; reach you out-of-band when the answer is beyond my knowledge or latitude.

## Comms
Plain English by default (per your standing preference — dialect stays in agent artifacts), technical depth and raw evidence on demand.

## Budget / Model Parameters
Commanders and crew at the **least-powerful-model-that-works**, escalating only for the engine-schema work (#179, highest blast radius) and Trip policy (#182). Default crew tier: Sonnet for bounded AFK implementation/review; Opus for #179's engine surgery. No Fable subagents (per standing constraint). Session-window aware; poll, don't idle.

## Pre-Rulings
Foreseeable ambiguities ruled in advance; each overridable at any checkpoint.
- **Engine-edit hazard (#179):** #179 rewrites `scripts/checklist_engine.py`, the engine driving THIS spine. Ruling: implement/review #179 in an isolated worktree; before merging it to main, verify the new engine still reads and drives this spine (`current` on `epic-178/spine.json` succeeds) in a throwaway check; only then merge and continue. If the new engine breaks my spine, treat as an INCIDENT and stop.
- **Wave-0 shared contract:** #180 (writer) and #181 (reader) must agree on the gauge.json record. Freeze it from the spec's post-review amendment — `{schema_version, fill_fraction, model, observed_at}` — in both launch orders. Keep the reader OUT of `checklist_engine.py` (its own module) to avoid a merge conflict with #179.
- **Honest-null is success:** a commander returning a well-scoped measured negative (esp. #180's fill-estimate validation) has delivered, not failed.
- **Spec is the authority:** where a module body in the spec differs from the Post-review amendments list, the amendments govern (the spec says so explicitly).

## Expiry
After **Wave 1 merge**, or on any ground-shift (a commander surfaces a spec contradiction; the engine-edit hazard bites; scope proves wrong). Crossing it forces a contract-refresh before further dispatch.

## Confirmation
2026-07-18 — Confirmed by Fred. Explicit grant: *"im pre-giving you wide lattitude, this has been thoroughly designed. make sure you understand then lets take the whole thing out."* Wide latitude to run the full epic autonomously, surfacing only the irreducible HITL actions (#180, #183), scope changes, and spec contradictions. HITL-handling sub-question defaulted to push-autonomously-surface-irreducible (overridable at any checkpoint). Recorded as user-decision evidence on the latitude step.
