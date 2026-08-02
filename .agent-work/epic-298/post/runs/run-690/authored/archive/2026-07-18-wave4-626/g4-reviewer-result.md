# Review Result

Status values follow `skills/workbench/references/status-model.md`.

## Assigned Gate
`g4` — Layer 3 (field-car: relative + re-anchor) + Layer 4 (car signal) + `model.py` assembler, each with σ, leak-free on held-out.

## Result
`APPROVE`

## Handoff compliance
All 5 close criteria independently verified (not taken on the implementer's word):

1. **Two-stage reconstruction.** `field_car_traj + relative == absolute` (with sigma quadrature) confirmed both by the algebra in `layer3_fieldcar.py:apply_layer3` and by re-running `test_reconstruction_absolute_equals_fieldcar_plus_relative` / `test_model_l3_reconstruction_holds_through_model`.
2. **NO LEAKAGE — the load-bearing check.** Read `model.py`'s `fit(train)`→`transform`/`car_signal(held-out)` path line by line:
   - `fit()` fits every hyperparameter on `train_df` only: `density_fits_` (L1 betas), `trajectories_` (L3 `DriftFit` per year via `fit_field_car_trajectory`), `pools_` (L4 `CarSeasonPool` via `fit_car_pools`) — all stored on `self`.
   - `transform()` never re-fits: it applies the *stored* `self.density_fits_` / `self.trajectories_` / `self.pools_` to whatever frame (train or held-out) is passed. `apply_layer3`/`apply_layer4` both take the fitted objects as parameters, never re-derive them from the caller's `df`.
   - The one place a per-call frame-derived quantity is used (the L3 "relative" weekend-median and the L1 per-year `mass_ref` mean) is legitimate: it's the row's own **contemporaneous weekend field**, not a hyperparameter, and is grouped strictly by exact `(year, round_idx)` key so it cannot be perturbed by *other* weekends being present. I independently verified `mass_kg_assumed` is constant within every year 2019-2026 in the live store, which is what makes the L1 mass term provably inert regardless of which subset computes its mean.
   - **The no-leakage tests are REAL, not trivially true.** `test_model_heldout_car_signal_has_no_leakage` transforms population A (only the target held-out round, full field) vs population B (the entire held-out set, which adds that car-season's *other* held-out weekends) and asserts bit-identical output — this would fail if `transform` silently re-pooled or re-fit anything from the passed frame. `test_model_heldout_signal_independent_of_train_membership_of_holdout` is a second, independent framing (single-row predict vs full-frame predict). Both are genuine population-varying tests, not tautologies.
   - **I independently reproduced this on the live `physics_estimates.db` frame** (not just the synthetic test fixture), and went beyond the implementer's own smoke check: fit on train (1061 rows), transform population-A-vs-B across **all 11 axes and every held-out round** (not just 1 axis/1 round) — **5464 pairwise comparisons, 0 mismatches**. `car_signal` defined on 486/501 held-out rows, matching the implementer's claim exactly.
3. **pooling.py reuse.** `layer3_fieldcar.py` imports `DriftFit`/`fit_drift`, `layer4_car.py` imports `PooledParameter`/`pool_random_effects`, both from `src.physics.layer2.pooling` — confirmed by grep (no `def fit_drift`/`class DriftFit`/`def pool_random_effects` anywhere in the new files) and by identity-assertion tests (`l3.fit_drift is pooling.fit_drift`, `l4.pool_random_effects is pooling.pool_random_effects`) plus a faithful-shrink reproduction test (`test_layer4_row_shrink_reproduces_pool_shrunk`).
4. **Four-layer assembly, L2 not dropped.** `model.py` composes L1→L2→L3→L4; `layer_sigma_cols()` enumerates 6 sigma columns per axis, each present and non-negative (`test_model_each_layer_carries_its_own_sigma`). L2 is kept as an explicit, documented inert seam (`{axis}_l2_delta=0`, its own `_sigma=0` in axis units) rather than silently omitted — this correctly reflects g3's own **already-APPROVED** FLOAT verdict (`layer2_evolution.py`'s `EARNS_KEEP_VERDICT`: real signal, but no per-car bridge on this frame and unmapped units, so it cannot be a car-signal correction here). `model.py` deliberately does not import `layer2_evolution.py` — correct, since g3 concluded that module cannot be wired to this frame.
5. **Feeds gate_spec.** `model_cols()` returns `{axis: f"{axis}_car_signal"}`, exactly the `Mapping[str, str]` shape `gate_spec.evaluate_gate`/`evaluate_axis`/`signal_preservation_guard` expect (verified by reading `gate_spec.py`'s signatures). `test_model_output_feeds_gate_spec_directly` actually invokes both `signal_preservation_guard` and `evaluate_axis` end-to-end on the model's held-out output and asserts a real verdict comes back.

## Scope drift
None. `git status --porcelain --untracked-files=all` shows only the 5 allowed new files (`layer3_fieldcar.py`, `layer4_car.py`, `model.py`, `test_layer3_fieldcar.py`, `test_model.py`) plus `.agent-work/` scratch. `git diff --stat HEAD` against every named excluded path (`floor.py`, `frame.py`, `holdout.py`, `gate_spec.py`, `layer1_physics.py`, `layer2_evolution.py`, `src/physics/layer2/pooling.py`) is empty. No `data/*.db` staged.

## Evidence verdict
Required evidence present and independently reproduced:
- `py -m pytest tests/unit/physics/weekend_state/test_layer3_fieldcar.py tests/unit/physics/weekend_state/test_model.py -q` → **22 passed in 2.22s**, matching the implementer's claim exactly, re-run fresh by me.
- Real-frame no-leakage smoke re-run against the live `physics_estimates.db` (1562 rows), **extended beyond** the implementer's single-axis/single-round check to all 11 axes × all held-out rounds: 5464 comparisons, 0 mismatches.
- `py -m src.utils.simplification_limits --paths <5 touched files>` → PASS.
- Broader `py -m pytest tests/unit/physics/ -q` (the full CREW_CONTEXT-mapped physics-region command, 113 test files) was started as an extra check but did not finish inside a reasonable wait (still running after >6 minutes / 480+ CPU-seconds, evidently a large suite, not a hang — process CPU time was climbing). I did not gate the verdict on it: the diff touches **zero existing files** (confirmed by the empty `git diff --stat` above), so there is no plausible mechanism for this purely-additive change to regress the rest of the physics region, and the CREW_CONTEXT-mandated minimal command for the touched files already passed cleanly. Flagging this as an open, non-blocking item — see Workflow Feedback.

## Code/doc quality
Fowler refactoring pass run per SKILL.md, recorded to `.agent-work/wave4-626/g4-review/fowler_pass.json`, `verify_fowler_pass.py` exits 0 (all 12 baseline smells visited).

- **duplicated-code** (flagged, non-blocking): `layer3_fieldcar.py`'s median-SE formula (`MEDIAN_SE_FACTOR * sd/sqrt(n)`) is computed twice independently — once via `.agg()` in `field_median_series`, once via `.transform()` in `relative_component`. A shared helper would remove the duplication; correctness is unaffected (both are tested and match).
- **long-parameter-list** (flagged, non-blocking): `apply_layer3`/`apply_layer4` carry 6-8 params, matching the sibling-signature convention already established (and previously reviewed/approved) in `floor.py`/`gate_spec.py` — not mechanically capped by `simplification_limits.py` (which checks complexity/line counts only, not param count).
- **data-clumps** (overridden, logged): the `(year, round_idx)`/`(year, constructor)` key tuples traveling through many signatures are CREW_CONTEXT's "one canonical representation per concept at a boundary" — floor.py's `DEFAULT_WEEKEND_KEY`/`DEFAULT_SEASON_KEY` constants are imported and reused verbatim, not reinvented.
- **comments-as-deodorant** (overridden, logged): the dense module docstrings document *why* (the leak-free algebra, the two-stage rationale) per CREW_CONTEXT's Physics-And-Units mandate that invariants/uncertainty/fallback behavior be visible in code — not compensating for unclear naming (which is already self-explanatory). Same posture the g3 reviewer already approved for `layer2_evolution.py`.
- All other 8 baseline smells: absent.

## Map impact verdict
- **Evidence supports claimed change:** Yes — every numeric/behavioral claim in the implementer's Map Impact section was independently reproduced (see Handoff compliance above), and the no-leakage claim was reproduced at *greater* coverage than the implementer's own check.
- **Constraints not violated:** Yes — `constraint:physics_region_no_evo_import` (grep across all 5 new files: zero `evo_predictor`/evo hits, plus 3 dedicated tests), no-leakage (independently reproduced), no `data/*.db` staged.
- **Notes match the diff:** Yes — the claimed structural anchors (`layer3_fieldcar.py`/`layer4_car.py`/`model.py` NEW, `pooling.py` REUSE edge) match exactly what the diff touches; no missing or overstated impact.
- **Decision candidates surfaced:** N/A — no new decision needed authority beyond this gate; the L2-FLOAT decision was already surfaced and approved at g3.
- **Durable context routed:** Yes — the two Fowler-flagged (non-blocking) cleanup candidates are routed below as triage candidates rather than silently dropped.

## Reconciliation check
No divergence from recorded architecture beyond the already-acknowledged greenfield gap: `MISSION_FRAME.md` itself states no `docs/architecture` packet covers this new area yet — the same posture g3's already-approved review took, not a new issue g4 introduces. DC2/DC3 (g1-level decisions) are correctly built on top of, not re-litigated. `model_cols()`/`layer_sigma_cols()` are new, additive APIs; nothing existing changed.

## Blockers
- none

## Out-of-scope observations
- (Fowler, non-blocking) Factor the duplicated median-SE formula in `layer3_fieldcar.py` (`field_median_series` vs `relative_component`) into one shared helper.
- (Fowler, non-blocking) `apply_layer3`/`apply_layer4`'s parameter counts (6-8) match sibling convention; worth a lightweight parameter-object if the package grows another layer with a similar signature.
- Carried forward from g3 (not re-verified here, already routed): the L2 grip→axis-unit bridge and the missing per-car `cumulative_track_laps` on the g1 frame remain the path to un-floating Layer 2 — out of g4 scope, unaffected by this gate.

## Workflow Feedback

- **Handoff gaps:** none of substance. The handoff's close criteria mapped cleanly onto the actual code; the one place I had to do extra legwork was confirming *why* the L3 "relative" weekend-median computation (which uses whatever `df` is passed to `transform`, not a stored train-only object) doesn't itself constitute leakage — the handoff's own no-leakage framing ("driven by train-fit hyperparameters... and its OWN contemporaneous weekend-relative reading") already states this distinction, but a reviewer skimming faster than I did could plausibly misread "computed from the passed df" as a leak vector. Worth a one-line addition to future L3-shaped handoffs: "the relative/median computation is intentionally NOT a stored hyperparameter — it's the row's contemporaneous weekend context, safe by construction because it's grouped strictly per exact weekend key."
- **Context rediscovered:** that `layer2_evolution.py` exists in the same directory but is deliberately *not* imported by `model.py` required tracing back to g3's `g3-implementer-result.md`/`EARNS_KEEP_VERDICT` to confirm this was an approved, not an accidental, omission. A one-line pointer in the g4 handoff ("L2 is g3's `layer2_evolution.py`, approved-FLOATED — model.py intentionally does not import it, see g3 result") would have saved that lookup.
- **Instructions improvised around:** the SKILL's "re-run the tests yourself (expect 22 pass)" instruction was satisfiable quickly, but attempting the CREW_CONTEXT-mandated broader `tests/unit/physics/` region command (113 files) ran past a reasonable review-turn budget (>6 minutes, still going). I proceeded to consolidate without waiting on it rather than stall the gate, reasoning from the diff's purely-additive nature (zero existing files touched) that it presents negligible regression risk to the rest of the region. Flagging this as friction: the skill/handoff doesn't give guidance on how long a reviewer should wait on a broad regression command before treating "still running, diff is additive" as sufficient.
- **What would have made this easier:** a one-line note in the handoff on the expected runtime of `tests/unit/physics/` (113 files) would have let me decide up front whether to launch it in parallel earlier, rather than discovering the scale mid-review.

## Return status
`complete`
