# Latitude Contract: `509-w2`

Confirmed by the human before wave 1. The dial between "I don't care, go" and
"float me the details." Re-confirm on expiry or when the ground shifts under it.

## Epic Intent
Push epic #509 (connected physics → prediction pipeline) forward by clearing a disjoint batch of Phase-F foundation + adjacent-correctness sub-issues in parallel: #503, #494, #527, #501, #475. Outcome that must not be violated: the physics fit/measurement base stays trustworthy and reproducible — no regression to the C1 utilization path, `sim_evaluator`, or the published-F1 known-answer tests; disjoint write-territories so lanes don't corrupt each other.

## Success Shape
Each of the five issues reaches one of: merged PR (done-bar: tests + honest covariance where applicable + single canonical path), or an honest-null / set-aside-with-remainder-captured (issue note + clear resume point). A measured negative or a documented "no change warranted" is a complete deliverable. Not every issue must merge — but none may be left silently incomplete.

## Checkpoint Protocol
**Cleared to completion (full autonomy overnight).** User is AFK until morning. No wave-boundary stop; run all four lanes to green/reviewed PRs, merge them myself, run full closeout. What reaches the user: ONE consolidated plain-English report in the morning (per-issue verdict + evidence + what merged + anything blocked/deferred). Evidence on demand.

## Decision Classes

| Class | Disposition |
|---|---|
| Architecture / structural change | delegated (within the five issues' stated scope; #494 schema granularity pre-ruled in Q1) |
| Scope change (issue added/dropped/re-scoped) | delegated for re-scoping/deferring *within* this batch; surfaced (out-of-band) for adding a NEW issue |
| Merge to main | delegated (user said "merge them myself") |
| Issue filing / closing | delegated (may file follow-up issues for deferred remainder; may close the five on merge) |
| Spend / budget / model tier | delegated (Sonnet default; Opus for Lane A) |
| Production defaults / user-visible behavior | delegated within stated issue scope; surfaced if a change reaches beyond physics into evo/prediction outputs |
| Physics-model convention change beyond the five issues' scope | surfaced (out-of-band) |
| **Out-of-taxonomy** | **always escalates, with one line on why it fit no class** |

## Float-Up Routing
When a Commander floats — a `user-decision` **or a context query**: for a decision, adjudicate inside delegated classes and log a RULING; escalate surfaced classes and out-of-taxonomy to the human out-of-band (the user is asleep — escalate only if truly blocking; otherwise set the lane aside with a remainder note and continue the others). For a context query, answer from epic knowledge and continue the Commander.

## Comms
Plain English by default; technical depth on demand. One consolidated morning report. (See [[user-plain-english]], [[user-no-sycophancy]].)

## Budget / Model Parameters
Commanders: Sonnet for Lanes B/C/D; Opus for Lane A (#503→#494 — schema design + migration + larger blast radius). No hard compute/time budget — user accepts a long run. Session-window awareness: detached/background commanders; state-note-first; recover-don't-restart on stalls.

## Pre-Rulings
Foreseeable ambiguities ruled in advance; each is overridable by the human at any checkpoint.
- **#503→#494 sequencing:** #503 (boundary consolidation: remove `fastf1` import from `session_fit.py`, route through `preprocessing.trajectory` seam) lands first; #494 (cache→SQLite source swap + flying-lap telemetry store + 2022–2024 backfill) lands second, one writer of `session_fit.py`.
- **#494 storage:** per-lap flying-lap windows; schema extensible; backfill 2022–2024 only.
- **#527:** re-apply banking at apply-time; retire `_TERRAIN_INFLATION`; flat tracks byte-unchanged; banked-corner truth test.
- **#475:** additive validation only this wave; defer the `session_fit.py` in/out-lap filtering code fix to a follow-up sequenced after Lane A.
- **#501:** additive post-processing only (new `ForceResidualAnalyzer`); no edits to the estimation layer / Lane-A files.
- **Honest-null is acceptable** for any lane; a "no change warranted" verdict (esp. #527 if banked-corner impact proves negligible) is a complete deliverable.
- **verify_worktree_isolation.py is absent** — launch orders substitute a native-git isolation gate (`git rev-parse --show-toplevel` matches the assigned worktree).

## Expiry
Event: completion of this single wave's closeout, OR a blocking out-of-taxonomy decision that cannot wait until morning. Whichever first forces a refresh.

## Confirmation
2026-06-27 — confirmed by user: "okay with all, talk to you in the morning" (approving the proposed plan + Q1/Q2/Q3 defaults + pre-rulings). Recorded as user-decision evidence on the latitude step.
