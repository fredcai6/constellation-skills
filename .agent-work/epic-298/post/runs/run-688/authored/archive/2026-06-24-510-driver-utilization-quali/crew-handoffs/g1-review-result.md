# Review Result

## Assigned Gate
`g1-review` (C1 #510, work-id 510-driver-utilization-quali, branch feat/c1-driver-utilization-510)

## Result
`APPROVE`

## Handoff compliance
The change does exactly what the handoff asked, within allowed scope. Public API delivered:
- `causal_predict(clock, values, sigmas, *, clock_target, step_var, strictly_pre)` — one-sided GP prediction.
- `build_car_ceiling(*, store_df, year, constructor, target_round, strictly_pre, config) -> CarCeilingResult` — causal as-of ceiling assembly producing a `PhysicsParameterSet` + propagated covariance wrapped in a `CapabilityEnvelope`.

All close criteria verified:
- **Causal exclusion truly excludes future sessions** — PROVEN, not just asserted. `test_future_session_does_not_change_prior` builds two stores (with/without a round-5 session), runs `build_car_ceiling` at `target_round=2` on each, and asserts `theta_D` is identical to `rel_tol=1e-9`. The mechanism is real: `_filter_causal` masks `round_idx <= target_round` before any pooling, so a round-5 row never enters the data. `test_strictly_pre_W_excludes_own_session` proves the strictly-pre slice excludes W's own session by asserting the result equals the analytically-derived round-1-only value (`1.10/(2*808)`).
- **`strictly_pre` clock-shift trick is sound** for integer rounds: `clock_target = target_round - 0.5`. Since `round_idx` values are integers, the `<= clock_target` condition in `causal_predict` excludes exactly the target round (round W's integer can never equal a half-integer), and `_filter_causal` independently applies `round_idx < target_round`. Both layers agree; the half-integer shift is robust.
- **Bridge faithful** — `theta_D = cda_closed/(2·MASS_KG)` verified to `rel_tol=1e-6` (`test_theta_D_from_cda_closed`); `theta_D_std` likewise; `theta_R` from coast; power as a single-point curve `theta_P_times=[0.0], theta_P_values=[p_max]`; braking `a_b/b_b`, traction `a_t/b_t`, lateral `A0/A2` carried direct; sigmas mapped through to covariance blocks. `MASS_KG=808.0` imported from the canonical `src.physics.longitudinal_fit`.
- **Envelope reaches the sim only via `CapabilityEnvelope.from_parameters`** (car_prior.py:532) — no second inline scalar sim anywhere in the module.
- **Inputs validated** with field/expectation/actual messages (`_validate_store_df`, `_filter_constructor`, `_filter_causal`); absent ceiling left `None` (Gsat fallback), never fabricated.

Re-ran the focused suite independently: `py -m pytest tests/unit/physics/test_car_prior.py -q` → **27 passed in 0.25s**.

## Scope drift
Clean. `git status -s` shows only the three new project files (`src/physics/utilization/__init__.py`, `src/physics/utilization/car_prior.py`, `tests/unit/physics/test_car_prior.py`), plus the work area `.agent-work/510-driver-utilization-quali/` and `.agent-work/templates/.baseline/**` churn (skill-freshness noise, explicitly pre-cleared in the handoff — not part of this gate). No existing file modified.

Specific exclusions confirmed untouched:
- `DriftFit.predict` in `src/physics/layer2/pooling.py` is **unchanged** — read and verified the symmetric `|clock - target|` smoother is intact. The new `causal_predict` is an additive function in the new module; `test_symmetric_smoother_not_broken` confirms `DriftFit.predict` still functions.
- No driver-utilization (G2) code; no `scripts/ideal_*` changes; no second inline lap sim; no five-view estimator or pooling-math change; no evo-region import (grep for `evo_predictor|evo_region|from src.evo|import evo` in `car_prior.py` returns zero matches).

## Evidence verdict
Required evidence present and genuinely demonstrative. TDD satisfied: implementer observed `ModuleNotFoundError` test-first, then 27 green. The L1 tests check closed-form formulas with `math.isclose(rel_tol=1e-6)` against hand-computed expected values; the L3 causal tests compare two independent `build_car_ceiling` runs and check the strictly-pre output against an analytically-derived scalar — this is behavior verification, not tautological self-assertion. `simplification_limits --paths ...` → PASS (2 files), re-confirmed.

## Code/doc quality
Minimal, maintainable, well-documented. The module docstring carries the full bridge table, covariance policy, causal contract, k_tire/g_track defaults, ceiling rule, and canonical-path note — serves as the contract doc for G2 consumers. Helpers are small and named for intent. Input validation is first-class with actionable messages. Covariance handling prefers the real measured 2×2 blob and falls back to a `sigma^2` diagonal only when the blob is absent/invalid (`_build_2x2_cov`, `_pick_representative_blob`).

One harmless redundancy (not a defect): `_causal_pool` re-applies an inner `causal_mask = c_f <= clock_target` even though `df_causal` was already filtered by `_filter_causal`. It is a defensive safety belt that cannot corrupt results; flagged as an out-of-scope observation only.

## Map impact verdict
- **Evidence supports claimed change:** Yes. The new-capability claim (causal as-of car ceiling from the five-view store) is backed by the L1 bridge tests and L3 causal-exclusion tests, all green.
- **Constraints not violated:** Yes. `physics_region_no_evo_import` honored (imports only `src.physics.*`); as-of contract explicit (`target_round` required, no silent fallback); single canonical path; honest covariance.
- **Notes match the diff:** Yes. Map Impact notes accurately describe `struct:physics` new sub-package, read-only consumption of `struct:physics.layer2`, the `PhysicsParameterSet` bridge, and the `from_parameters` path. No overstated or missing structural/capability impact.
- **Decision candidates surfaced:** Yes. The clock-proxy choice (`round_idx` vs `upgrade_clock`) is surfaced as a local decision with rationale and routed to triage; `decision:ideal_lap_sim_two_sided_evaluator` honored (ceiling=None left for Gsat).
- **Durable context routed:** Yes. Two triage candidates filed (upgrade-clock upgrade; pooled-covariance blob / `fallback_channels` field). No durable context dropped.

## Reconciliation check
No reconciliation blockers. The new sub-package sits cleanly under `struct:physics` alongside `layer2/`. The `round_idx`-vs-`upgrade_clock` divergence is documented in Map Impact and filed as triage — it is NOT a silent contradiction of the dev-clock design; causal ordering is preserved. Cartographer should fold `src/physics/utilization/` and a candidate `purpose:physics_utilization` capability into the map at the reconcile step.

## Scrutiny point rulings (explicit)

### Scrutiny point 1 — `round_idx` used as the development clock instead of FIA `upgrade_clock`
**Ruling: APPROVE-with-tracked-triage.**

Reasoning: The causal as-of contract depends only on **monotone ordering** of the clock, and `round_idx` is strictly monotone and always present in the store. The causal filter is `round_idx <= target_round` (`_filter_causal`), so no future session can leak regardless of clock scale — causal correctness is independent of whether the clock is round count or cumulative upgrade count. The `#492` design uses `upgrade_clock` (`src/physics/layer2/upgrades.py`, consumed in `pool_driver.py:113`) because the cumulative upgrade count de-aliases development from circuit and makes `step_var` mean "drift per upgrade." Using `round_idx` instead changes only the **drift-rate magnitude / `step_var` units** ("drift per round"), not the as-of cutoff or the ordering. Critically, `step_var` is re-estimated by `fit_drift` over the same causal subset on the same `round_idx` axis, so the units are internally self-consistent within this call — the value isn't mismatched against a differently-scaled clock. The divergence is documented in the module (`clock = round_idx (uniform development proxy; avoids upgrades.yaml dependency)`), the implementer flagged it, and a triage candidate is filed to upgrade to `upgrade_clock` when `upgrades.yaml` is reliably present. It does NOT silently contradict the dev-clock design in a way that corrupts the ceiling. This is a tracked simplification, not a correctness break — APPROVE.

### Scrutiny point 2 — covariance = most-recent session's 2×2 blob rather than a pooled blob
**Ruling: APPROVE — honest enough for G1.**

Reasoning: `_pick_representative_blob` returns the most-recent valid 2×2 covariance blob from the causal slice (or, absent any blob, a `sigma^2` diagonal built from the pooled per-scalar sigmas). This is *a real measured covariance* produced by the estimator — it is NOT nominal, fabricated, or hand-set. The honest-covariance-first-class requirement bars fabricated/nominal uncertainty; it does not require the theoretically-optimal pooled blob. The pooled-blob alternative would need either a pooled-blob column in the store schema (absent) or per-session-blob combination here (deferred, correctly flagged out-of-scope/triage). The most-recent blob can slightly under- or over-state the multi-session pooled uncertainty, but it carries genuine measured off-diagonal correlations from actual data, and the diagonal entries on the fallback path come from the causally-pooled sigmas (which DO shrink with session count via `causal_predict`). So the scalar-level uncertainty is genuinely pooled; only the 2×2 *correlation structure* is most-recent rather than pooled. That is an honest measured approximation, not a break of the first-class-covariance contract — APPROVE, with the pooled-blob upgrade tracked in triage.

## Blockers
- None.

## Out-of-scope observations
- `_causal_pool` (car_prior.py:291-293) applies a redundant inner `causal_mask = c_f <= clock_target` re-filter; `df_causal` is already filtered by `_filter_causal`. Harmless safety belt, not a logic error — candidate for a one-line simplification in a future pass.
- Triage candidate (implementer-filed, endorsed): upgrade the clock proxy from `round_idx` to `upgrade_clock` from `upgrades.yaml` when that file is reliably present, so `step_var` becomes drift-per-upgrade.
- Triage candidate (implementer-filed, endorsed): add a proper pooled 2×2 covariance (requires a pooled-blob in the store schema or per-session-blob combination here), and an explicit `fallback_channels: list[str]` field on `CarCeilingResult` so G2 consumers can tell which channels used config defaults vs pooled values (the `as_of_means["A2"]` key is populated even when A0/A2 fell back to config defaults).

## Workflow Feedback
- **Handoff gaps:** The handoff was thorough — it carried the two scrutiny points, close criteria, map anchors, exclusions, and evidence expectations explicitly, which made the review tractable. One minor friction: the handoff's "How to Inspect the Diff" suggests `git diff --no-index /dev/null src/physics/utilization/car_prior.py`; on this Windows/Git-Bash setup `/dev/null` works but the simpler path was just reading the three new files, which I did. Not a blocker.
- **Context rediscovered:** I had to read `src/physics/layer2/upgrades.py`, `pooling.py`, and `pool_driver.py` myself to rule on scrutiny point 1 with confidence (to confirm exactly what `upgrade_clock` feeds and that `DriftFit.predict` was untouched). The handoff named these files but did not summarize the `upgrade_clock` → `fit_drift` data flow; a one-line note ("`upgrade_clock` feeds `fit_drift`'s clock arg in `pool_driver.py:113-114`") would have saved a lookup. Acceptable for a scrutiny point that explicitly demanded judgment.
- **Instructions improvised around:** The reviewer skill's `REVIEW_RESULT.template.md` references `skills/workbench/references/status-model.md` for status values, which is not available in this context; I used the standard values from the template field labels (`complete`/`partial`/etc.). The engine `record` subcommand requires `--result` (not a positional) and `consolidate` uses `--verdict`/`--summary` (not `--result`/`--finding`); the skill text did not spell these flags out, so I discovered them from `--help`. Minor, self-resolving.
- **What would have made this easier:** A one-line data-flow note for the `upgrade_clock` design in the handoff (where it is consumed and what `step_var` means under it) would have removed the only nontrivial lookup. Otherwise the handoff was well-scoped.

## Return status
`complete`
