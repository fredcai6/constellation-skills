# Reviewer Handoff

## Gate
`g3` — Layer 2 within-session evolution grip latent with σ + identifiability test. Outcome: layer BUILT + a principled FLOAT (per-car correction not viable on the frozen split). Your job: confirm the honesty is real, not a lazy drop or a faked win.

## Survey State Location
`.agent-work/wave4-626/g3-review/review.json`.

## What Was Implemented
`src/physics/weekend_state/layer2_evolution.py` + `test_layer2_evolution.py` (12 tests). A smooth field-level within-session grip latent (penalised spline over `cumulative_track_laps`, controlling corner-bin FE + tyre_life), honest per-weekend σ, wide-σ near-zero fallback outside the identifiable region, + LOO harness + orthogonality check + `EARNS_KEEP_VERDICT`. Finding: within-session signal is REAL (b_ctl=+0.00196 g/lap, t=28.4, LOO −2.56% held-out RMSE, orthogonality r²≈0 vs season-time) but as a per-car Layer-2 correction on g1's frozen 2019-2026 split it FLOATS (grip_bin_obs Q is 2023-only; store has no per-car representative-lap session-time; units are grip-g not the 11 axes). Result: `.agent-work/wave4-626/g3-implementer-result.md`.

## How to Inspect the Diff
UNCOMMITTED tree; `git status --porcelain` then read `layer2_evolution.py` + its test directly (untracked).

## Task Statement
Build Layer 2 and honestly test if it earns its keep; float if unidentifiable. Full task: `.agent-work/wave4-626/g3-implementer-handoff.md`.

## Close Criteria (each a review check)
- The LOO / held-out test is genuinely OUT-OF-SAMPLE (disjoint folds, NOT self-inclusive) — verify by reading the harness, and re-run the test. This is the load-bearing honesty check (lesson:loo-residual-diagnostic).
- The orthogonality-vs-season-trajectory check is real and reported (r²≈0 means genuinely within-session, NOT the F5 season-time double-count trap) — confirm the layer is NOT a disguised season-time latent.
- The honest-null / FLOAT is REPORTED with held-out numbers, NOT hidden and NOT faked into an in-sample win; the wide-σ fallback is genuinely mean-0 wide-σ (no fabricated values outside the 2023 coverage).
- The float reasoning is principled (a real data/architecture limit: no per-car session-time bridge in the store), not a cop-out to avoid building — verify the layer IS actually built + fits a real signal.
- No evo import; no `data/*.db` staged.

## Allowed Scope
`src/physics/weekend_state/layer2_evolution.py`, its test.

## Specific Exclusions
No Layers 3/4; g1/g2 files/estimator/evo/config untouched. (grip_bin_obs is outside your worktree DB — Commander-verified, note-not-block.)

## Constraints the Implementation Must Respect
LOO/out-of-sample discipline; no fabricated values outside coverage (wide-σ prior only); `constraint:physics_region_no_evo_import`; σ explicit; absolute DB paths; no data/*.db commit.

## Map Anchors (inbound)
- Structural: `layer2_evolution.py` (NEW); `damage_integrals.db:grip_bin_obs` (Q, 2023).
- Capability: within-session grip latent with σ.
- Constraints: LOO diagnostic; no evo import.
- Decision: DC1 — build+test+report; FLOAT sanctioned (Pre-Ruling 2 / F5).

## Evidence Produced
`py -m pytest tests/unit/physics/weekend_state/test_layer2_evolution.py -q` → 12 passed (commander re-ran: 12 passed). LOO + orthogonality numbers in the implementer result.

## Suggested Model Tier
Stronger — you must judge whether an honest-null/float is genuine vs a disguised silent-drop; that's a judgment call, not a checkbox.

## Stop Conditions
BLOCK if: the LOO is actually self-inclusive, the orthogonality check is absent/wrong, the "float" hides a layer that was never really built or was faked, fabricated values exist outside coverage, or an evo import / data/*.db staged.

## Return Format
Return REVIEW_RESULT to `.agent-work/wave4-626/g3-reviewer-result.md`: verdict (APPROVE = the built layer + honest float is sound / BLOCK), per-check findings, blockers, out-of-scope observations, workflow feedback.
