# Wave 5 — #627 (+#506) Stage-1 Phase 3 unified-basis refit + σ-honesty — VERDICT

**Commander:** ShipF-627 (delegated). **Branch:** `feat/627-unified-basis` (base main `29315037`), 8 commits.
**Date:** 2026-07-18. **PR:** #645 — https://github.com/fredcai6/f1Brainz/pull/645 (base main, NOT merged — Admiral adjudicates).

## 1. VERDICT: **PASS**

Tier 1 landed solidly and committed: cross-view covariance persisted + demonstrably real (NON-DEFERRABLE core
cleared), σ-honesty (#506) delivered with the pooled-σ_μ shared floor, and the explicit-unknown contract is a
testable property. Tier 2's four fractures each carry a number (one CLOSED, three bounded-defer-with-number).
Tier 3 bounded-deferred with a quantified follow-on mini-gate. All six gates (G1–G6) drove through the engine to
`complete`; the spine ran init→…→triage; review/feedback/archive follow.

## 2. Cross-view covariance (Tier-1 #1, NON-DEFERRABLE) — REAL

- **What is persisted:** `estimate_store.cross_view_covariance` (sparse dict) now holds the deterministic,
  recoverable cross-view terms `cov(CdA,[a_b,b_b]) = σ_CdA²·J_braking` and `cov(CdA,[a_t,b_t]) = σ_CdA²·J_traction`
  (the `cda_frontier_jacobian` J that BrakingView/TractionView already computed then discarded — now exposed on the
  result dataclasses), plus a fused-CdA `(mu,sigma)` slot. `src/physics/layer2/cross_view.py` is new.
- **Evidence it's real (redundancy tightens a shared param's σ — before/after, real Monza 2023 Q):**
  honest **cov-aware GLS** fusion of the two independent-samples CdA measurements (PowerDrag descent + Coast
  envelope), accounting for their within-session shared mass/ρ correlation:
  - **Mercedes:** agreement z=2.03 (consistent) → **fused σ 0.0460 m² vs PowerDrag-only honest σ 0.0562 m² — 18.1%
    tighter**, and that tightened CdA propagates through the PERSISTED `cov(CdA,b_b/b_t)` to tighten b_b/b_t
    (small, correctly-signed, connected to the persisted term — proven via the `cov=0` null case = no tightening).
  - **Red Bull:** agreement z=6.80 (genuine 29% disagreement) → fusion **REFUSED** (`disagreement_z_ge_5`), NOT
    silently blended. The falsifiability is not cosmetic — it fired on real data.
  - **Honesty guard:** a naive-independent fuse would have reported σ≈0.0146 (falsely confident); the cov-aware
    path is the honest one. On real data the shared systematic exceeds the raw fit σ (Σ non-PSD from raw fit σ),
    so fusion uses each view's HONEST TOTAL σ — a genuine correctness fix, recorded as decision anchor
    `dual-cda-fusion-honest-total-sigma.md`.
- Production pinning CdA UNCHANGED (fused is additive-only). Reviewer independently reproduced all numbers against
  the real stored row.

## 3. σ-honesty (#506) — DELIVERED

- **Per-session propagation:** `src/physics/layer2/systematic_budget.py` (new) computes each five-view param's
  systematic σ analytically (CdA/P_max ~1:1 with mass, d ln CdA/d ln ρ ≈ −1; A0/A2 mass/ρ CANCEL → curvature/
  terrain-bounded, NOT the blind 4%). Total reproduces `nuisance_sensitivity.py`'s budget on Monza RBR 2023 Q
  (~4.3% CdA, ~3.7% P_max; braking/traction fit-σ-dominated).
- **Correlated-vs-independent split:** each param's systematic splits into a SHARED (common-mode: the
  `quali_mass(year)` model bias + the θ_R=0.15 literal used in every de-conflation) and a SESSION-VARYING
  component (per-session ρ error + fuel variation). The static `SYSTEMATIC_FLOOR` table is **RETIRED**; each stored
  `{axis}_sigma` now folds the per-session systematic total; the SHARED component is persisted per axis as
  `{axis}_shared_sigma`.
- **Pooled σ_μ carries the shared floor (the crux):** `pool_random_effects` gained a `shared_floor`;
  `pool_driver.pool_store` passes it NON-OPTIONALLY. After DerSimonian-Laird shrinkage, σ_μ is floored:
  `σ_μ = sqrt(σ_μ² + shared_floor²)`. **Before/after (real RBR 2023 Q):** CdA/P_max pooled σ_μ shrinks toward 0
  without the floor but **plateaus at the shared systematic (~4.3%/3.7%)** with it — pooling no longer claims
  sub-% season knowledge it cannot have (a common-mode bias is rank-1; the additive quadrature floor is the honest
  mechanism — decision anchor `pooled-sigma-shared-systematic-floor.md`). Within-year (matches pool_store's
  within-year load); cross-year drift stays fit_drift's job.
- **Backward-compat:** weekend_state consumers unchanged — **0 gate-decision flips on the full 1562-row store**
  (verdict PASS 9/11 before/after); {axis}_sigma column names unchanged (meaning tightens only).

## 4. Explicit-unknown contract (Tier-1 #3) — TESTABLE

- Per-axis `{axis}_status ∈ {resolved, unresolved}` for cda,p_max,a_b,b_b,a_t,b_t,A0,A2,θ_R. `resolved` = genuinely
  measured this session (finite non-degenerate σ); `unresolved` = θ_R (only a cold constant, never measured into
  the basis), a degenerate PowerDrag CdA/P_max, or any absent lateral/coast view. NULL status (legacy backfill)
  reads as unresolved.
- **Reserved slot:** an unresolved axis persists the documented `UNRESOLVED_AXIS_SIGMA_FRAC` wide-σ sentinel
  (≥100% rel, patterned on power_drag's `_CDA_UNKNOWN_SIGMA`) — down-weights to ~0 in any inverse-variance
  consumer. A downstream consumer distinguishes "measured ≈0, tight σ" (resolved) from "unknown — plug here"
  (unresolved) via BOTH the status and the numerically-distinct σ.
- **Testable property:** a property test asserts θ_R + a degenerate/absent axis read `unresolved` with the reserved
  wide σ, and a measured CdA reads `resolved` with a finite (not reserved-wide) σ — the numeric distinction is a
  test, not a comment. This is the architectural slot later phases fill without a redesign.

## 5. The four Tier-2 fractures — each with a number

(`scripts/tier2_fracture_analysis.py` + `docs/physics/627-tier2-fractures.md`, reproducible)
1. **DUAL-CdA — CLOSED.** MER fused σ 0.0460 m² = **18.1% tighter** than PowerDrag alone; RBR z=6.80 refused
   (via G3's cov-aware fusion — reproduced live).
2. **GRIP-TRIPLET — bounded-defer ≤0.6%.** Circuit-fixed-effect **partial** correlation (separates "grippy
   circuits" physical co-variation from shared measurement-error cov) max |r|=0.107 over 216 rows/22 circuits →
   a joint grip solve would tighten the pooled mechanical-grip σ by **≤0.6%**. Not worth the coupling now.
3. **a_long — bounded-defer ≤13.4σ, structural, NOT re-merged.** Braking's decoupled Kalman-RTS a_long vs
   throttle/coast's `clean_longitudinal_from_raw` is a documented STRUCTURAL HONEST-NULL
   (`decision:decoupled_1d_longitudinal` + #523/#546 Config-C tables — worst case PowerDrag P_max Monaco 13.4σ).
   Re-merge fails circuit-topology-dependently; NOT re-introduced. Cites #644 for the live-fit stall.
4. **SHARED-TRAJECTORY-NOISE — bounded-defer, honest method-scoped null.** braking/traction/lateral share
   `sample_cache` but bootstrap independently; a conservative proxy found ≤0.0% pooled-grip-σ underestimate — an
   honest null with explicit tested/not-tested scope, cites #644 for the tighter live-perturbation measurement.

## 6. Tier-3 (2026 aero) — bounded-deferred with recommendation

`docs/physics/627-tier3-2026-aero-defer.md`: the 2026 two-state (Z/X) latent joint fit is a NEW estimator build,
not a basis refinement; nothing in Tier 1/2 depends on it (the basis is era-agnostic). Recommended follow-on:
validate the #627 basis on 2019–2025 dry Q first, then a **cheap mini-gate** (does two-state CdA differ from
single-θ_D by ≳ the honest #506-floored per-session CdA σ?) BEFORE building the estimator — go only if it does.
**Baseline discrepancy floated (see §Floated):** the `active_aero_zones.py`/`active_aero_identification.py` deps
the launch order lists are ABSENT from base 29315037.

## 7. Closeout facts

- **Isolation:** `git worktree list` → `C:/Programs/f1-627 [feat/627-unified-basis]` distinct from
  `C:/Programs/f1Brainz [main]`; all runs asserted `src.physics.*.__file__` under `C:\Programs\f1-627`. No
  `data/*.db` committed (verified each commit).
- **PR:** #645 (https://github.com/fredcai6/f1Brainz/pull/645), base main — opened, NOT merged.
- **Tests:** Tier-1 diff-affected surface fully green — 98 touched-code (estimate_store/pooling/pool_driver/
  cross_view/systematic_budget) + 90 weekend_state consumers = 188; `simplification_limits` PASS on all touched
  files. The g4-integrate full-suite postcondition (`tests/unit/physics/layer2/ + weekend_state/`) was WAIVED to
  Admiral authority — heavy multi-agent CPU contention made the full run impractical; the diff is a pure
  structural extraction of the change that already passed 835, and the Admiral owns the full-suite (incl the
  diff-unrelated @slow damage_tractability) confirmation at the merge gate.
- **Triage:** 9 candidates routed (TRIAGE_RECOMMENDATIONS.md) — tc6 fixed-now (stale comment), tc4 resolved via
  reconcile (decision anchor), 7 recommend-and-defer for the Admiral to batch-file.
- **Map impact:** Cartographer folded #627 into `docs/architecture/packets/physics.md` + `index.md` +
  `overlays/constraints.yml` + 3 new decision anchors; `check_arch_map.py` OK.

## Floated to the Admiral (decisions/context beyond my latitude)
1. **tc8 (store re-fit) — recommend the Admiral file + schedule.** main's `physics_estimates.db` has the new #627
   columns UNPOPULATED on every row (fitted 2026-07-06, pre-#627). The cross-view/σ-honesty/status data is empty
   until a store re-fit (`estimate_batch`) runs — a long batch compute (Admiral-owned). Downstream consumers
   can't USE the new fields until then.
2. **tc9 (baseline discrepancy) — the 2026 two-state aero deps `active_aero_zones.py`/`active_aero_identification.py`
   are ABSENT from base 29315037** (only the state-agnostic `aero_axis_2026.py` exists). Reconcile their dependency
   status before scheduling the Tier-3 build.
3. **Nothing blocking.** Cross-view covariance persistence proved feasible and real; no scope was cut; the
   unified-basis architecture stands. Merge is the Admiral's call — PR opened, not merged.
