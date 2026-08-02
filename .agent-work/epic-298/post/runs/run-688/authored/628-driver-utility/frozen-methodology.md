# FROZEN METHODOLOGY — #628 held-out driver-utility gate

**FROZEN 2026-07-18, BEFORE any deficit/outcome number was computed.** Only COVERAGE was inspected to form
the split (fit_status='ok' counts per round + driver session counts + rosters from the `drivers` column) —
NO `g_deficit` / δ / RMSE / variance value was looked at. This is the coverage/outcome firewall (critic
MINOR-3): MAY inspect support/coverage; MUST NOT inspect outcomes. Changing anything below after seeing
numbers voids the freeze.

## Bounded slice
- Season **2023**, session type **Q**. Store: `C:/Programs/f1Brainz/data/physics_estimates.db`
  (`session_estimates`, both-cars-pooled per constructor-session).
- **Rounds 1–12** (coverage: all 12 rounds have 10/10 ok constructor-sessions; 20 drivers carry ≥8 sessions;
  DEV=8, RIC=2 are the thin tail).
- Compute: the per-driver lean trace (~28 s/case) over ~20 drivers × ~12 rounds ≈ 240 cases ≈ ~1.9 h,
  OS-detached + resumable (G5). Round 1 has no causal history → its `strictly_pre` ceiling raises → error row
  (skipped); usable TRAIN observables therefore begin at round 2.

## Train / held-out split (frozen)
- **TRAIN = rounds 1–8** (usable 2–8 after the round-1 causal-history exclusion).
- **HELD-OUT = rounds 9–12** (4 held-out rounds; each has ample prior history for a `strictly_pre` ceiling).
- δ per (driver, axis) is fit on TRAIN observables ONLY (via G2 `estimate_driver_utility`); a driver's
  held-out rounds never enter their own δ (leave-round-out, enforced by the G3 harness disjointness assert).
- Drivers with < `MIN_RESOLVED_SESSIONS` (=3) usable TRAIN sessions on an axis → that (driver,axis) is
  `unresolved` (reserved wide σ) and excluded from the RESOLVED corner-verdict aggregates (still reported).

## Axes
Four tiling regimes = axes: `braking, slow_corner, fast_corner` (the CORNER axes — falsifiable weight) and
`straight` (the POWER/straight axis — **calibration-confounded NEGATIVE CONTROL**, never counts toward the
verdict; measured `u_straight>1` shows the causal ceiling under-predicts straight speed, so a near-zero
centered variance there is CONSISTENT WITH but not a validation of "power≈0 driver utility").

## Pass / honest-null RUBRIC (pre-committed, corner axes only)
Evaluated OUT-OF-SAMPLE on held-out rounds 9–12, over resolved (driver,axis):

- **Limb 1 — recomposition.** Per corner axis, held-out RMSE of `g_obs − δ_driver` (model) vs `g_obs − 0`
  (δ=0 car-only baseline). **PASS-limb-1** iff RMSE_model < RMSE_baseline on **≥ 2 of the 3 corner axes**
  AND the pooled-corner RMSE improvement is **≥ 0.05 m/s** (a small but real out-of-sample gain). Otherwise
  limb-1 is an **honest-null**.
- **Limb 2 — per-axis structure.** Cross-driver variance of the per-axis-CENTERED δ. **PASS-limb-2** iff, for
  **≥ 2 of the 3 corner axes**, the centered cross-driver δ variance **exceeds the straight-axis centered
  variance** (driver signal concentrates in corners, not on the confounded straight). Report
  `var_corner / var_straight` per axis. Otherwise honest-null.
- **Overall gate = PASS** iff **BOTH** limb-1 and limb-2 pass on the corner axes. Otherwise **PASS-with-
  honest-null** (a complete, reportable deliverable — no kill switch, nothing tuned toward a pass).

## Leakage materiality diagnostic (on real data, in G5 — NOT a gate)
On the earliest held-out round (round 9), additionally compute the held-out replication with a NON-CAUSAL
(through-W, `strictly_pre=False`) ceiling and compare to the causal one. **Pre-committed magnitude: 0.15 m/s.**
- Inflation ≥ 0.15 m/s ⇒ the causal apparatus is materially protecting the gate.
- Inflation < 0.15 m/s ⇒ report as **EITHER** the causal apparatus is immaterial at this leverage **OR** the
  diagnostic is underpowered — **NEVER silently a pass** (mirrors the frozen G3 unit self-test).

## Reputational smell-test (NON-GATING)
Rank drivers by resolved corner-axis δ and juxtapose reputation. **Smell test ONLY** — never pass/fail.

## Named limits (carry into verdict)
1. **No external driver-utility ground truth** — held-out replication is the substitute (stated per launch order).
2. **Cross-round contamination attenuated, NOT eliminated** — the `strictly_pre` ceiling for round W still
   pools driver d's own rounds < W (which also feed δ_d), and the store has no per-driver physics estimate, so
   this cannot be removed; the within-session leak IS closed. (critic SERIOUS-2)
3. **Straight/power axis is calibration-confounded** — a negative control, not a validated ≈0. (critic SERIOUS-1)
4. **δ is teammate-relative** — within-constructor δ are mutually anchored (compressed); cross-constructor
   variance is cleaner. (critic MINOR-2)
5. **Bounded slice** — 2023-Q rounds 1–12 only; a null here kills only this test under these conditions, not
   the idea class (scoped-null doctrine).
