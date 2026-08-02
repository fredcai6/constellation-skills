# Latitude Contract: `453`

Confirmed by the human before wave 1. Re-confirm on expiry or when the ground shifts under it.

## Epic Intent
Evo maintenance track for the physics-primary era: only non-physics-limited work (lap-time-derived features, model-side investigation, process). Three ordered waves ending in the #440 gold refresh + walk-forward checkpoint. Nothing counts as "better" until #440 scores it against the leakage-free backtest.

- Wave 1 (parallel-safe): #410 pooled multi-season compound β fit; #413 wire `qs_compound_beta_regime` into runtime manifest; #451 localize the ~19pp race_weekend quali-channel under-extraction.
- Wave 2 (informed by W1): #425 all-FP min-sector practice-pace feature; #394 race recent-history pace-gap form re-encoding; #395 race-start recent-history form encoding. Ship into config/defaults; no individual gold regens — changes accumulate.
- Wave 3 capstone: #440 full gold refresh + walk-forward backtest, runbook-driven (`docs/evo/analysis_refresh.md` FIRST).

## Success Shape
Waves 1–2 dispositioned (ship / measured no), then #440 executed: pipeline_validation green, new bundle built, walk-forward fantasy score vs prior baseline recorded. **A measured negative (honest null) is a complete, successful deliverable** — explicitly so for #451 and all Wave-2 investigations. Epic closes on the #440 report.

## Checkpoint Protocol
**Cleared autonomous through all three waves** — no stop-and-confirm at wave boundaries, provided the Admiral is convinced the requests are met. **File a descriptive written report between each wave** (user is AFK; reports are the visibility surface). **HARD STOP before merging/promoting the gold bundle in #440** — promotion requires explicit user sign-off.

## Decision Classes

| Class | Disposition |
|---|---|
| Architecture / structural change | surfaced |
| Scope change (issue added/dropped/re-scoped) | surfaced |
| Merge to main | **delegated** — after each wave, gated on green checks (exit codes) + Admiral diff review; quality bar applies |
| Issue filing / closing | delegated for epic-child issue closes that follow a merged PR or a measured-null verdict; new-issue filing for follow-ups delegated; anything else surfaced |
| Spend / budget / model tier | delegated within the tiers below |
| Production defaults / user-visible behavior | delegated for Wave-2 config/default changes (they're the epic's point); **gold-bundle promotion surfaced (hard stop)** |
| Measured-null disposition | delegated — Admiral may close an issue on a clean measured-no |
| **Out-of-taxonomy** | **always escalates, with one line on why it fit no class** |

## Float-Up Routing
Commander `user-decision`s: adjudicate inside delegated classes, log a RULING. Surfaced classes and out-of-taxonomy go to the user; user is AFK, so park the blocked item, proceed with unblocked work, and batch the escalation into the wave report unless the epic cannot proceed at all.

## Comms
Plain English by default, technical depth on demand. Rationale-heavy decisions in plain text (remote-control rendering). Between-wave reports: descriptive, written to `.agent-work/453/reports/` and summarized in chat.

## Budget / Model Parameters
- Commanders: **Sonnet** default; **Opus** for #451 and #440.
- Crews: **Sonnet** — every launch order must say so.
- Subagent use encouraged ("don't be afraid to sub agent").
- No explicit budget ceiling. Heavy compute (#440 regen/NN training) runs foreground in the commander per lessons; launch heavy ships in fresh session windows.

## Pre-Rulings
Foreseeable ambiguities ruled in advance; each is overridable by the human at any checkpoint.
- DB-only analysis — no FastF1/Jolpica calls from analysis code; if data is missing, plan ingestion, never a fallback.
- Brier is primary for gold comparison, against a calibrated stable baseline.
- Honest null is a complete deliverable; commanders must not force positives.
- No backtest leakage: walk-forward, explicit as-of cutoffs, no silent latest-value fallback.
- #440 is runbook-first: read `docs/evo/analysis_refresh.md` before acting.
- Generated artifacts are regenerated, never hand-edited.
- Wave-2 items ship into config/defaults but do NOT individually trigger gold regens.

## Expiry
Event-based: the contract expires at the **#440 gold-promotion hard stop**. Everything up to and including building the new bundle and producing the walk-forward comparison is in-contract; promotion and anything after requires fresh user confirmation.

## Confirmation
2026-06-11 — confirmed by user in-session ("charge through the waves... merge up after each wave as long as the work looks quality... definitely stop before merging the gold bundle. agree with model tiers, tell commanders the crew should be sonnet."). Recorded as user-decision evidence on the latitude step.
