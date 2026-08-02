# Latitude Contract: `601-fantasy-league`

Confirmed by the human (Tommy / fredcai6) 2026-07-12 ("sounds good, go forth!"). The
dial between "I don't care, go" and "float me the details." Re-confirm on expiry or
when the ground shifts under it.

## Epic Intent
Make the model capable of winning Tommy's ~20-player F1 fantasy league, live during 2026
(find ~7.5 pts/race vs its current self). **This wave (the bitten-off chunk)** = the
Track-1 weekly-loop foundation that the Belgium (2026-07-19) shakedown runs through.
The outcome that must not be violated: the DB stays the single source of truth (no live
FastF1 calls from analysis); no human heuristics hard-coded; no leakage into walk-forward.

## Success Shape
This wave is DONE when: (#603) Austria R8 + Silverstone R9 are collected into the season
DBs + Parquet mirror and verified; (#604) the `race-week` command seam is designed-it-twice
(interface settled BEFORE the Friday data path) and a working wrapper exists that emits a
submittable ranked top-10; (#602) the consolidated mission statement lands in AGENTS.md +
CLAUDE.md with the stale 24-param evo description corrected. A measured negative on any
sub-question is a complete, successful deliverable if honestly reported. Belgium itself is
a PLUMBING SHAKEDOWN, not a quality verdict — one race's score is noise-dominated.

## Checkpoint Protocol
Stop-and-present at each wave boundary. I run a wave, bring Tommy the result in plain
English (summary + decision asks + evidence on demand), he clears the next. Not cleared to
run autonomously across wave boundaries.

## Decision Classes

| Class | Disposition |
|---|---|
| Architecture / structural change | surfaced |
| Data/physics/evo boundary crossing | surfaced |
| Scope change (issue added/dropped/re-scoped) | surfaced |
| Merge to main | **surfaced** (stop-and-ask at the merge gate) |
| Push branch / open PR | **delegated** (pre-cleared this wave — run to the merge gate) |
| Issue filing | delegated (log as RULING) |
| Issue closing | surfaced |
| File deletion | surfaced |
| Fix-now triage (bounded fix applied immediately) | delegated (log as RULING) |
| Spend / budget / model tier | delegated (Sonnet default; log escalations) |
| Production defaults / user-visible behavior | surfaced |
| Apply a lesson / fold doctrine | surfaced (default); constellation lessons always exported |
| **Out-of-taxonomy** | **always escalates, with one line on why it fit no class** |

## Permission prerequisites

| Delegated class | External actions implied | Pre-clearance or fallback |
|---|---|---|
| Push / open PR | `git push`, `gh pr create` | Pre-cleared by "go forth" this wave. Fallback if classifier vetoes: one live approval, batch the rest to the checkpoint. |
| Issue filing | `gh issue create/comment` | Autonomous per ORCHESTRATOR_CONTEXT. Fallback: file at checkpoint. |
| Fix-now triage | edits on task branch | Autonomous on task branch. |

## Float-Up Routing
Commander `user-decision` floats: adjudicate inside delegated classes (log RULING),
escalate surfaced + out-of-taxonomy to Tommy. Commander context queries: answer from epic
knowledge and continue; reach Tommy out-of-band when beyond my knowledge/latitude.

## Comms
Plain English by default; technical depth on demand. Minimize jargon/acronyms (user pref).

## Budget / Model Parameters
Commanders + crew on **Sonnet** by default (standing preference); escalate only where a
task genuinely needs more. No hard compute/time budget; research-program pacing (days are
soft per the spec). Session-window aware — state-note before any detached compute.

## Pre-Rulings
Overridable by Tommy at any checkpoint.
- **#604 seam design-it-twice runs FIRST** (critic IF4) — the interface is settled and
  presented before the wrapper is built against it.
- **#603 collection uses the existing `collect_evo_data.py` / launch_collect path** (rate-limit
  aware); no new bespoke collectors. Data is untracked — launch orders carry absolute
  main-checkout paths (lesson:worktree-untracked-data).
- **Belgium lineup uses the beam search's *balanced* lane** as the stated default (critic IF3),
  mean-score lane as fallback; the emitted report names which lane produced the list.
- **The 2GB `f1_data_2023.db` swell is out of scope for this wave** (belongs to #608 housekeeping);
  #603 commits only the R8/R9 season-DB deltas + Parquet, and must not sweep the 2023 telemetry.
- Honest-null on any sub-question is an acceptable, complete deliverable if reported.

## Expiry
After this wave's PRs merge, OR if the ground shifts (Belgium data lands early / a blocking
dependency surfaces). Crossing it forces a contract-refresh decision before further dispatch.

## Confirmation
2026-07-12 — confirmed by Tommy ("sounds good, go forth!"). Recorded as user-decision
evidence on the latitude step.
