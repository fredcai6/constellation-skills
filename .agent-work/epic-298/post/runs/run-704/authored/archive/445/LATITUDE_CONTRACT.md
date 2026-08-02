# Latitude Contract: `445`

Confirmed by the human before wave 1. Re-confirm on expiry or when the ground shifts under it.

## Epic Intent
Build a measurement-trusted physics layer: a unified best-known-truth trajectory per lap with covariance, constrained by realistic physics (sector-time anchors, track-manifold geometry, cross-instrument consistency) — ultimately feeding physics-derived features into the evo A/B path (Phase 3), or bounding the bet at characterization cost if an earlier gate fails. Five strictly-gated phases: #446 (0a grading harness, FIRST) → #447 (0b instrument characterization + GO/NO-GO) → #448 (Phase 1 estimator competition) → #449 (Phase 2 force attribution) → #450 (Phase 3 features into evo). Spec: `docs/superpowers/specs/2026-06-10-physics-state-space-direction-design.md`.

## Success Shape
Either Phase 3 ships gate-passing physics features into the evo A/B harness, **or an earlier gate fails and the negative result is documented**. A measured NO-GO at 0b (or any later gate) is a complete, successful epic outcome — honest nulls are deliverables, not failures.

**Amended 2026-06-12 (Phase 1 checkpoint):** a Phase 1 null is no longer a *terminal* outcome. The user's direction: "failure isn't an option — let's see if it's bugs, but if it's not, we come back and see what other ideas we can come up with." A persistent null after the bounded fix-and-rerun wave returns to the user for a strategy-brainstorm checkpoint rather than closing the epic. Honest measurement remains the bar — no gate-softening to manufacture a pass.

## Checkpoint Protocol
**Cleared autonomous through Phase 0a (#446) and Phase 0b (#447), including the 0a→0b gate** (it is mechanical: harness exists and grades). **From the 0b GO/NO-GO onward: stop-and-present at every phase boundary.** Each checkpoint hook delivers a **detailed write-up**: what was measured, the verdict and its evidence, what the next phase would do, and any decision asks. Plain-English summary first, technical depth beneath.

## Decision Classes

| Class | Disposition |
|---|---|
| Architecture / structural change (within `src/physics/`+`src/preprocessing/` region, per existing map) | delegated |
| Architecture change crossing data/physics/evo region boundaries | surfaced |
| Scope change (issue added/dropped/re-scoped) | surfaced |
| Merge to main (green + reviewed PRs) | **delegated** (each logged as RULING; gated on check exit codes, sequential) |
| Merge with failing checks, or after two review blocks | surfaced |
| Issue filing (triage candidates, follow-ups) | delegated |
| Issue closing (epic child after its phase merges + verdict posted) | delegated; closing anything else surfaced |
| Spend / model tier (within Opus-commander/Sonnet-crew envelope) | delegated; session-window-sized compute flagged before launch |
| Production defaults / user-visible behavior / promoted-path changes outside physics region | surfaced |
| GO/NO-GO gate verdicts (0b and later phase gates) | **surfaced** — gate evidence presented, human ratifies the fork |
| **Out-of-taxonomy** | **always escalates, with one line on why it fit no class** |

## Float-Up Routing
Commander `user-decision`s: adjudicated inside delegated classes as logged RULINGs; surfaced classes and out-of-taxonomy go to the human with the Commander's evidence attached. During the autonomous 0a/0b stretch, surfaced-class floats still stop the line — autonomy does not convert surfaced classes to delegated.

## Comms
Plain English by default ([[user-plain-english]]); technical depth on demand. Detailed write-up at every checkpoint hook.

## Budget / Model Parameters
Commanders: **Opus** (all phases — 0b's measurement model is the epic's load-bearing artifact). Crews: **Sonnet**. No hard compute ceiling; flag any launch that looks session-window-sized; wave heavy ships into fresh windows. Plan session limits are a known kill vector — budget-aware waving.

## Operating Constraints (from the human)
- All Commander work in **isolated worktrees**, never the main checkout. Admiral's own footprint in the main checkout is `.agent-work/` scratch only.
- **Other work is in progress in parallel** (expected non-impacting). Verify main freshness before every dispatch and merge; hold rebases to wave boundaries; if parallel work lands something conflicting, stop-and-relaunch on fresh ground.

## Pre-Rulings
Each overridable by the human at any checkpoint.
- Telemetry for Phase 0 is **already on disk** (`outputs/cache/`, ~36GB FastF1 cache) — never re-pull from FastF1/Jolpica. Load offline via `fastf1.Cache.enable_cache('outputs/cache')`.
- Use raw per-stream samples (`session.car_data` / `session.pos_data`), **never** the merged `get_telemetry()` product — the merged product is the diagnosed root cause of the old estimator's failure.
- The DB-only constraint governs prediction/analysis code; Phase 0 instrument characterization may read the cache offline as collection-side work (per epic #445 text).
- Sector/lap truth comes from `data/f1_data_<year>.db` `lap_times`.
- Physics work lives in the physics region (`src/physics/`, `src/preprocessing/`); no coupling to evo before Phase 3, and Phase 3 goes through the standard isolated-module A/B path with Brier primary.
- 0b gate target (from spec/epic): sector-time anchors (~50ms) + reduced chi-square ≈ 1; cross-residuals are a diagnostic only (streams' clocks not assumed independent).
- Physics model changes require truth-anchored evidence at the highest applicable L1–L4 tier (orchestrator context).

## Expiry
Event: **each phase-boundary checkpoint** (rolling — re-confirmed at every stop-and-present from Phase 1 onward). Time backstop: 7 days without human contact forces a contract-refresh before further dispatch.

## Confirmation
2026-06-11 — confirmed by user ("go go go"); recorded as user-decision evidence on the spine's latitude step (e-latitude-1).
2026-06-11 — re-confirmed at the 0b GO/NO-GO checkpoint: GO ratified, same terms, stop-and-present at every remaining phase boundary.
