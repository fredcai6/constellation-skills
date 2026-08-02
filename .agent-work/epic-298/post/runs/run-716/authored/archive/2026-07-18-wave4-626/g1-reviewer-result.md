# Review Result

Status values follow `skills/workbench/references/status-model.md`.

## Assigned Gate
`g1` — Frozen metric harness (frame / floor / holdout / gate_spec)

## Result
`APPROVE`

## Handoff compliance
All Close Criteria independently satisfied. `frame.py` loads `session_estimates` (Q, `fit_status='ok'`) from the absolute main-checkout DB (`C:/Programs/f1Brainz/data/physics_estimates.db`), opened strictly read-only via a `mode=ro` sqlite URI (an accidental write now raises rather than silently mutating the shared store — exceeds the constraint). `floor.py` reproduces the 624-phase0-baseline-lock x4 table for all 11 axes within tolerance; re-ran `test_floor_reproduction.py` myself (12/12 pass) AND independently called `per_axis_stats()` fresh against the live DB for 3 axes (`drag_area_closed_m2`, `max_power_w`, `lateral_aero_grip_g`) — exact match to the doc, not merely trusting the shipped test. `holdout.py`'s `round_idx % 3 == 0` split is deterministic (re-ran twice, identical `pd.testing.assert_frame_equal`), documented, and leaves all 81 trusted car-seasons with >=2 held-out weekends (test-confirmed). `gate_spec.py` encodes F1/F2/F3 as frozen; see per-check detail below.

## Scope drift
None. `git status --porcelain` shows exactly 3 untracked paths: `.agent-work/wave4-626/` (workflow artifacts), `src/physics/weekend_state/` (5 files matching Allowed Scope), `tests/unit/physics/weekend_state/` (4 files, matching Allowed Scope + the permitted test `__init__.py`). No estimator (`src/physics/layer2/*`), evo, or production config touched; no g2-g5 model layer built.

## Evidence verdict
Required evidence present and independently reproduced, not just trusted:
- `py -m pytest tests/unit/physics/weekend_state/test_floor_reproduction.py tests/unit/physics/weekend_state/test_holdout_split.py tests/unit/physics/weekend_state/test_gate_spec.py -q` → **25 passed** (re-ran myself, matches the claimed evidence).
- `grep -n "^import\|^from" src/physics/weekend_state/*.py | grep -i evo` → empty (re-ran).
- `git status --short | grep -i "\.db"` → empty (re-ran).
- Reproduced-vs-624 table: independently spot-checked 3 of 11 axes directly against the live store (not the test), exact match.

## Code/doc quality

**Load-bearing fidelity check (floor.py vs x4).** Read both `floor.py` and `.agent-work/archive/2026-07-17-explore-physics-evo-hookup/excursions/x4-analysis/normalization_stability.py` side by side. `field_and_noise_stats()` is structurally the same computation as x4's `per_axis_stats()`, generalized to an arbitrary `value_col`/`weekend_key`/`season_key`: same `MIN_FIELD=6`/`MIN_WEEKENDS=4` constants (frozen, "do not retune" comment), same field_sigma = median-over-well-populated-weekends of cross-constructor SD, same noise_sd = median-over-trusted-car-seasons of within-car-season own-mean SD, same `N_weekends = (noise_sd/field_sigma)**2`. This is genuine logic equivalence, not numeric-coincidence — confirmed by re-deriving 3 axes independently against the live DB (see Evidence verdict), which is the strongest possible test that the reimplementation is the same computation, not merely close.

**F1 signal-preservation guard.** `fit_train_trajectory` fits a per-car-season OLS line on **train rows only** (`train_df`), and `signal_preservation_guard` scores the model's held-out output against that train-only trajectory's out-of-sample prediction (`trajectory_residual_rms`) plus a direct residual against the true held-out reading, each bounded by `accuracy_sigma_multiple * stored_sigma`. A `collapsed` check independently catches near-constant output on a car-season whose true held-out spread cleared a floor — this is NOT gameable by self-dispersion alone (a model can't win by just being flat; it fails `collapsed` if the true trajectory moved). Re-ran `test_over_shrinker_fails_signal_preservation_guard` and `test_over_shrinker_axis_does_not_beat`: the constant-per-car-season over-shrinker registers `guard_pass=False`, `n_car_seasons_guard_pass=0`, `beats=False` — genuinely punished, not a self-dispersion self-own-goal.

**F2 paired comparison.** `paired_holdout_floor_per_car_season` recomputes the raw x4 floor **on `holdout_df` alone** (never touches the 624 full-sample table or `floor.per_axis_stats`); `evaluate_axis` pairs it against `model_holdout_spread_per_car_season` (also `holdout_df`-only) restricted to the intersection of car-seasons, per car-season. Genuinely paired on identical held-out weekends, not full-sample-vs-holdout apples-to-oranges.

**F3 pinned rule.** `bootstrap_car_season_diff` resamples car-seasons (not rows) with a fixed seed (`BOOTSTRAP_SEED=626_001`); `evaluate_axis`'s `beats` requires both `model_median < floor_median` (strict) AND the bootstrap's lower quantile `> 0` — `test_tie_is_not_a_beat` (re-run, passes) confirms an exact-tie oracle model does NOT register a beat despite `guard_pass=True`. `evaluate_gate`'s `passed = n_beats >= BEAT_THRESHOLD_AXES(7)` matches the launch order's `>=7/11` exactly; `test_seven_of_eleven_beats_passes_the_gate` / `test_six_of_eleven_beats_does_not_pass_the_gate` bracket the threshold on both sides.

**Fowler pass** (full record: `.agent-work/wave4-626/g1-review/fowler_pass.json`, `verify_fowler_pass.py` exits ok): 5 smells flagged as minor, non-blocking observations for a future gate (long-method in `signal_preservation_guard`; duplicated-code between the two per-car-season spread helpers; a `(weekend_key, season_key)` data-clump threaded through ~10 call sites; primitive-obsession on bare axis-name strings; a 9-parameter `evaluate_gate`). 1 overridden with a logged standard (`speculative-generality` on `field_and_noise_stats`'s column-parameterization — the handoff explicitly requires this generality for g2-g5 reuse, and 2 real caller shapes already exist in this diff). 6 absent. None rise to a blocker.

**Region verification.** Ran the CREW_CONTEXT-mandated broader region command (`py -m pytest tests/unit/physics/ -v`, 1735 items) as supplementary due diligence beyond the handoff's own narrower Verification Commands. It progressed very slowly (appeared to stall for several minutes on a pre-existing, unrelated test, `test_damage_tractability.py`, then resumed) and did not finish inside this review's time budget. Judged non-blocking: this diff adds **only new, previously-nonexistent files** (confirmed via `git status`) and modifies zero existing physics source, so it carries no regression risk to that suite regardless of the slow test's own health.

## Map impact verdict

- **Evidence supports claimed change:** yes — independently reproduced (see above), not merely trusted.
- **Constraints not violated:** yes — no evo import, no `data/*.db` staged, absolute-path read-only DB access, `py` invocation throughout.
- **Notes match the diff:** yes — Structural/Capability/Constraint/Decision-anchor/Claims-evidence entries in `g1-implementer-result.md`'s Map Impact section all match what was actually built; DC3 resolution matches `MISSION_FRAME.md`'s DC3 anchor exactly.
- **Decision candidates surfaced:** DC3 (held-out split rule) was correctly resolved within the implementer's granted authority and documented. One NEW decision candidate found by this review (not previously surfaced) and routed via `flag-candidate` (see triage below) rather than blocking, since it falls outside F1/F2/F3 as literally frozen by the launch order and outside the implementer's authority to unilaterally change ("implement it exactly; do not soften or re-tune").
- **Durable context routed:** yes — implementer's own out-of-scope observations (collapse-threshold unit sensitivity, `model_cols` contract documentation, `n_car_seasons_considered` reporting) are appropriately routed to Commander/Triage. This review adds one more (below).

## Reconciliation check
No docs/architecture packet exists yet for this new area; the implementer correctly notes this and defers reconcile, consistent with a greenfield module with no prior recorded architecture to diverge from.

## Blockers
- none

## Out-of-scope observations
- **[Triage candidate, flagged to the engine as `tc1`]** `gate_spec.evaluate_axis`/`evaluate_gate` has no minimum-car-season-coverage floor at the **axis** level: an axis-beat is a binary pass regardless of how many car-seasons contributed (`n_car_seasons_considered` is reported but not gated on). Demonstrated concretely, not hypothetically: the g1 test suite's own F1/F3 tests (`test_genuine_improver_passes_guard_and_registers_beat`, `test_seven_of_eleven_beats_passes_the_gate`) already exercise exactly **n=1** covered car-season per toy axis (only `CS_DEV` ever gets a `model_col` value; `CS_B`/`CS_C` never do), and that single-car-season result registers as a full "beat" toward the `>=7/11` tally — the bootstrap on a single diff value has zero variance, so its lower quantile trivially clears the noise margin. A real g2-g5 model that legitimately abstains/floats on hard car-seasons (DC1's own sanctioned honest-null pattern for Layer 2) could win an axis-beat by covering only its easiest 1-2 car-seasons, with no coverage-fraction penalty in the binary `n_beats>=7` rule. This is **not** in scope of F1 (over-shrinkage)/F2 (pairing)/F3 (bootstrap unit/tie) as literally frozen by the launch order — all three are correctly implemented — and it is **not** something g1's implementer had authority to unilaterally fix (the Authority section pins F1/F2/F3 "implement it exactly; do not soften or re-tune"). Recommend Commander/Admiral decide before g5 whether `evaluate_gate` needs a per-axis minimum-coverage floor (e.g. `n_car_seasons_considered >= some_fraction * total_held_out_car_seasons`) before an axis-beat counts, or whether this is an accepted risk given the `mde_power_sanity` helper already exists as a softer, non-gating signal.
- Fowler-pass minor observations (non-blocking, see Code/doc quality above and full record at `.agent-work/wave4-626/g1-review/fowler_pass.json`): long-method in `signal_preservation_guard`; duplicated pattern between `paired_holdout_floor_per_car_season`/`model_holdout_spread_per_car_season`; `(weekend_key, season_key)` data-clump across ~10 call sites; bare-string axis names (primitive obsession); `evaluate_gate`'s 9-parameter signature. All flagged as future-cleanup candidates for whichever gate next touches this file, not g1 defects.

## Workflow Feedback

- **Handoff gaps:** none blocking. The handoff and `PLAN_CRITIC_DISPOSITIONS.md` together gave an unusually precise spec (exact F1/F2/F3 mechanics, exact x4 formula citations, exact tolerances) that made independent verification fast and unambiguous.
- **Context rediscovered:** none beyond the ordinary read of `MISSION_FRAME.md` to cross-check DC3 against the implementer's stated resolution — a legitimate cross-reference, not a gap.
- **Instructions improvised around:** the handoff's suggested region-verification command (`py -m pytest tests/unit/physics/ -v`, CREW_CONTEXT's project-wide rule) is disproportionately slow for a purely-additive greenfield package (1735 items, stalled several minutes on an unrelated pre-existing test) relative to the review turn's time budget. I ran it as supplementary due diligence but did not let it gate the verdict, reasoning that a diff which touches zero existing files carries no regression risk to that suite. Future handoffs/reviews for purely-additive new packages could explicitly scope the "region suite" expectation down to "the new package's own tests + an import/collection smoke check of the broader region," reserving the full region run for changes that touch existing files.
- **What would have made this easier:** none — this was one of the more thoroughly-specified handoffs I've reviewed; the explicit "Reference sources (cite exactly)" section made the load-bearing fidelity check fast.

## Return status
`complete`
