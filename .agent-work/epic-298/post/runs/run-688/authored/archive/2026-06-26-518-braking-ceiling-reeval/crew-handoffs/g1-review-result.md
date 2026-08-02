# Review Result

## Assigned Gate
`g1 — Calibrate the decoupled longitudinal estimator HPs across the full 2023-Q season`

## verdict: APPROVE

---

## Survey Checks

### r0-context: PASS
Loaded: CREW_CONTEXT, engine-config, handoff, implement-result, diff, key files, scoreboard.py,
session_braking.py, validate script, calibration JSON, calibration MD. All context loaded before
inspecting the change.

---

### r1-handoff: PASS
The change does exactly what the handoff asked:
- A reproducible calibration harness (`decoupled_calibration.py`) and a season-sweep CLI
  (`calibrate_decoupled_hp_2023Q.py`) were built and run across 220/220 2023-Q cases.
- A true-regime validation script (`_validate_true_regime.py`) using the production `run_case()`
  path confirmed the DEFAULT HP against 12 representative cases.
- The `make_synthesis_variant(**hp)` factory was added to `decoupled_longitudinal.py` (additive only).
- 32 unit tests added; 184 layer2 tests pass.
- Reports produced. No `_DEFAULT_*` constant changed (DEFAULT confirmed-as-calibrated).
- Close criteria satisfied: HP decision justified by true-production-regime validation, persisted
  via confirmation of existing named constants, reasoning is sound (see r3-evidence below).

---

### r2-scope: PASS
Allowed scope only was touched:
- `src/physics/layer2/decoupled_longitudinal.py` — one additive factory function, 45 lines.
- `src/physics/layer2/decoupled_calibration.py` — new module (harness only).
- `scripts/calibrate_decoupled_hp_2023Q.py` — new CLI script.
- `scripts/_validate_true_regime.py` — new validation script.
- `tests/unit/physics/layer2/test_decoupled_calibration.py` — new unit test file.
- `reports/physics/decoupled_hp_calibration_2023Q.{json,md}` — gitignored.

`git diff --stat` confirms only `decoupled_longitudinal.py` is tracked as modified (1 file, 45
insertions, 0 deletions). All new files are untracked/gitignored as expected.

**Specific exclusions — all confirmed untouched:**
- `braking_view.clean_longitudinal_from_raw` — not in diff; used read-only (imported in
  `decoupled_calibration.py` for the fast extractor, but NOT modified).
- `scoreboard.py` `score_variant`, `braking_knee`, `non_throttle_ringing` metric core — not in
  diff; no tracked changes.
- Built-in variants (`BUILTIN_VARIANTS`, `_variant_gaussian`, `_variant_kind3`) — not in diff.
- `EstimateStore`, `car_prior`, utilization layer, production views (`session_braking`,
  `session_traction`, `session_coast`) — grep confirms zero imports in new files.
- `_DEFAULT_*` constants — confirmed at original values: `_DEFAULT_TV_LAMBDA=0.10`,
  `_DEFAULT_SIG_A_SOFT_BRAKE=0.10`, all others unchanged.

---

### r3-evidence: PASS (with one evidence-availability note — not a blocker)

**Tests — independently re-run:**
```
py -m pytest tests/unit/physics/layer2/ -q
184 passed in 90.07s (0:01:30)
```
Matches implementer's claimed 184 passed.

**Simplification limits — independently re-run:**
```
py -m src.utils.simplification_limits --paths src/physics/layer2/decoupled_longitudinal.py src/physics/layer2/decoupled_calibration.py
PASS (2 files checked)
```
Matches implementer's claim.

**True-regime validation evidence:**

The handoff says to verify against `reports/physics/true_regime_validation_2023Q.json`. That file
is ABSENT from `reports/physics/` (gitignored, not regenerated before review). However:

1. The per-case table is embedded in `decoupled_hp_calibration_2023Q.md` (True-Regime Validation
   section, added 2026-06-25). The per-case data is complete (12 rows, all scores, knee/ringing/ok
   per variant) and internally consistent.

2. `_validate_true_regime.py` is present and was inspected. It calls `run_case()` from
   `scoreboard.py` directly — confirmed to use the production smoother-based regime (see r4).

3. The key numbers claimed — default 11/12 (91.7%) ringing_ok, mean_knee_gap +0.70; candidate
   11/12, +2.60; gaussian 1/12, kind3 1/12; Mexico/PER ringing=3.95 both — are present in the
   `.md` table with per-case breakdown. The aggregate is consistent with the per-row data.

The missing `true_regime_validation_2023Q.json` is an evidence-availability gap (the separate JSON
file the handoff directed review to is gone), but the equivalent data in the `.md` is sufficient
for verification. This is logged as workflow friction below, not a blocker.

---

### r4-quality: PASS

**Check A — True-regime validation genuinely uses production smoother-based regime (not raw-regime):**

CONFIRMED. `_validate_true_regime.py` imports `run_case` from `scoreboard.py`. `run_case` calls
`_build_case_inputs(session, driver)` which calls `_driver_samples` + `_to_kinematic_samples` from
`session_braking.py`. `_to_kinematic_samples` uses `SegmentClassifier().classify_samples(processed,
controls)` where `processed` is **smoother-derived telemetry** (output of `smoother_to_processed_telemetry`).
The `regime` in `CaseInputs` is therefore smoother-classified — NOT the raw throttle/brake
approximation used by the fast raw-data extractor in the calibration harness.

This is the critical distinction. The true-regime validation genuinely uses the production path.

**Check B — DEFAULT-wins reasoning is sound:**

From `.md` True-Regime Validation table:
- DEFAULT: 11/12 ringing_ok (91.7%), mean_knee_gap +0.70 m/s²
- Candidate: 11/12 ringing_ok (91.7%), mean_knee_gap +2.60 m/s²
- Both above the 85% stop-condition threshold on the true regime.
- DEFAULT wins by 1.9 m/s² tighter knee (closer to raw) at equal ringing_ok count.
- The reasoning is sound: equal ringing_ok → tie broken by knee depth → DEFAULT wins.

The close criterion "same ringing_ok (11/12) as the candidate but a tighter knee (+0.70 vs
+2.60 m/s² gap)" is verified in the table.

**Check C — DEFAULT-confirmation is honest (not a dodge):**

The calibration `.json` is NOT modified to show false success — it still records
`ringing_ok_rate: 0.077` (the raw-regime result) and `split_decision_candidate: true`.
The `.md` header block explains the resolution ("true-regime validation confirmed raw-regime
stop condition was an artifact") and directly contradicts the JSON's `hp_not_persisted: true` by
documenting the update.

The following are explicitly reported, not buried:
- **Raw-regime artifact:** documented in `.md` "Raw-Regime Sweep Context" section and `.json`
  `regime_approximation_note`.
- **Mexico/PER failure:** table row shows ringing=3.95 (N) for BOTH default and candidate; the
  `.md` Finding #4 explains it as circuit-level, not HP-resolvable.
- **gaussian/kind3 weak:** `.md` aggregate table shows 1/12 (8.3%) for both; documented in Finding #5.

DEFAULT-confirmation is honest. The existing defaults ARE the calibrated values — confirmed, not
assumed.

**Check D — constraint:physics_region_no_evo_import honored:**

`grep` on all new files finds zero imports from `src.evo_predictor`, `src.latent_power`,
`src.compound_prior`. The constraint declaration in the `decoupled_calibration.py` module docstring
is a comment, not an import.

**Check E — decision:two_cycle_external_anchor_design honored:**

In `decoupled_calibration.py`:
- `_extract_fastest_lap_raw` calls `clean_longitudinal_from_raw(t_raw, v_raw, t_spd)` to get
  `a_long_raw` from the raw speed sensor. This is the TV-denoised raw signal — the two-cycle
  external anchor. The anchor is NOT re-read from a smoothed trajectory.

In `make_synthesis_variant._variant`:
- `estimate_longitudinal(inp.t, inp.v, inp.a_long_raw, inp.regime, ...)` receives `a_long_raw`
  directly from the input object. No re-smoothing of the anchor.

The anchor-source invariant is respected throughout the fast extractor and the variant factory.

**Check F — HP grid in named constants, no hidden inline tuning:**

`HP_GRID_SPEC` and `HP_GRID_SECONDARY_DEFAULTS` and `DEFAULT_HP` are module-level named constants
in `decoupled_calibration.py`. The module docstring explicitly flags: "edit here to adjust sweep
resolution; no hidden inline tuning." No hardcoded HP values appear in function bodies except
via these constants.

**Check G — No production wiring:**

`decoupled_calibration.py` and the scripts are standalone harnesses. No changes to
`EstimateStore`, no call sites modified, no production pipeline entry point altered. The
`make_synthesis_variant` factory is additive on `decoupled_longitudinal.py` and is not wired into
any production path.

**Check H — Honest covariance preserved:**

`estimate_longitudinal` is called with the same covariance structure — the factory only varies
the named HP parameters. The covariance model in the estimation core is unchanged (not in diff).

**Check I — Code quality against CREW_CONTEXT rules:**

- `py` used consistently.
- Module-level state: only immutable constants (`HP_GRID_SPEC`, `DEFAULT_HP`, etc.) — no mutable
  runtime state in `src/`.
- Input validation: `run_season_calibration` raises `RuntimeError` with message when
  `n_scored_total < min_sessions_required`.
- `print()` confined to CLI scripts/orchestration — library functions (`build_hp_grid`,
  `aggregate_scores`, etc.) are pure.
- Existing `clean_longitudinal_from_raw` utility reused, not duplicated.
- `logging.getLogger` not used in library code — but `decoupled_calibration.py` uses `print()`
  conditionally on `verbose`. This is a minor style deviation but `verbose=True` print is
  consistent with the calibration harness pattern used elsewhere in scripts; acceptable.

---

### r5-reconciliation: PASS

**Map Impact notes verified:**

The implementer's Map Impact notes match the diff and evidence:

- `struct:physics.layer2` — `decoupled_calibration.py` added as sibling to
  `decoupled_longitudinal.py`. Accurate: new file in `src/physics/layer2/`.
- `capability:decoupled_1d_hp_calibration` (new) — the harness is a new capability, not wired
  into production. Accurate.
- `constraint:physics_region_no_evo_import` and `decision:two_cycle_external_anchor_design` —
  both honored (verified above). Notes accurately claim this.
- `decision:decoupled_1d_longitudinal` — "VER/3-circuit" Known-Limits flag resolved by
  season-wide evidence. The resolution is evidence-backed: 11/12 on the true production regime
  across 6 circuit types (low-speed Monaco, high-speed Belgium/Monza, high-altitude Mexico,
  street Singapore, Bahrain). This is NOT an asserted resolution — it is backed by the
  per-case table in the `.md`.
- Triage candidates routed: Mexico/PER systematic failure → #497 (terrain); true-regime
  validation integration suggestion → documented. Both are surfaced, not dropped.

**Docs/contracts:**
No architecture docs were modified. The decision anchor `decision:decoupled_1d_longitudinal`
resolution would need a Cartographer update to remove the "VER/3-circuit" Known-Limits flag —
this is correctly flagged as a triage/Cartographer task, not silently assumed done.

---

## Handoff compliance
The change did exactly what the handoff asked within allowed scope. Close criteria are met.
The HP decision is justified by the true production-regime validation. DEFAULT-confirmation is
honest. `_DEFAULT_*` unchanged. Required tests pass. No exclusions touched.

## Scope drift
No drift. One tracked modification (`decoupled_longitudinal.py`), four new untracked files
all within allowed scope. Zero exclusion touches confirmed by diff and grep.

## Evidence verdict
Tests pass (184/184, independently verified). Simplification limits pass (independently verified).
True-regime validation: JSON missing but `.md` contains equivalent per-case table, internally
consistent. Not re-running the 12-minute script as the handoff permits inspection of the script +
report. The `_validate_true_regime.py` script correctly calls `run_case()` (production regime
confirmed by code inspection). Evidence is sufficient for APPROVE.

## Code/doc quality
Minimal, maintainable, tested. Pure functions in the library module, print confined to scripts.
Named constants for all HPs. No hidden inline tuning. No production wiring. Honest covariance.
Anchor-source invariant respected. No evo imports. 32 new unit tests cover all pure functions
without FastF1 cache dependency.

## Map impact verdict

- **Evidence supports claimed change:** Yes. The `.md` per-case table backs the 11/12 ringing_ok
  claim for both variants. The raw-regime artifact explanation is documented with the regime
  approximation note. DEFAULT-wins is evidence-backed.
- **Constraints not violated:** Both `constraint:physics_region_no_evo_import` and
  `decision:two_cycle_external_anchor_design` are confirmed honored.
- **Notes match the diff:** Yes. Structural, capability, constraint, and decision notes accurately
  describe what was touched. No overstated claims.
- **Decision candidates surfaced:** Yes. Mexico/PER circuit-level failure is surfaced as
  triage (→ #497). Raw-regime calibration ambiguity is surfaced as workflow feedback.
- **Durable context routed:** Triage candidates documented. The `decision:decoupled_1d_longitudinal`
  resolution requires a Cartographer map update (the "VER/3-circuit" flag removal); this is out of
  scope for this gate and correctly flagged. Implementer correctly notes "No architecture docs
  modified" — Cartographer reconcile needed.

## Reconciliation check
`decision:decoupled_1d_longitudinal` Known-Limits "VER/3-circuit" flag is now resolved by
season-wide evidence. The architecture map needs a Cartographer update to record this resolution.
This is out of scope for G1 but should be a Cartographer/triage item for Commander closeout. Not
a blocker.

## Blockers
- None.

## Out-of-scope observations

1. **`true_regime_validation_2023Q.json` not regenerated before review.** The handoff directed
   review to this file; it was absent. The equivalent data appears in the `.md` and was
   verifiable, but the separate JSON artifact was not available. Future handoffs should either
   note that this file must be present for review, or explicitly point to the `.md` table.

2. **Cartographer map update needed:** `decision:decoupled_1d_longitudinal` Known-Limits flag
   ("tuned on VER/3 circuits") is now resolved. The architecture map should record the resolution.
   Triage candidate for Commander closeout.

3. **`decoupled_hp_calibration_2023Q.json` raw-regime state not back-filled.** The JSON still
   records `split_decision_candidate: true` and `hp_not_persisted: true` from the raw-regime stop
   condition. Only the `.md` documents the resolution. This is honest (raw-regime run result is
   preserved accurately) but could mislead a future reader who reads the JSON without the `.md`.
   Minor — not a blocker.

4. **Mexico/PER high-altitude ringing failure (ringing=3.95, both HPs):** Documented as
   circuit-level condition. Likely relevant to terrain-join module issue #497. Triage candidate.

---

## Workflow Feedback

- **Handoff gaps — `true_regime_validation_2023Q.json` reference:** The handoff says "verify
  against `reports/physics/true_regime_validation_2023Q.json`" but that file was absent at review
  time (gitignored and not regenerated). The `.md` contained the equivalent data, so the review
  was completable, but a handoff that points to a specific artifact should confirm the artifact
  exists OR say "if absent, verify via the `.md` True-Regime Validation table." Suggest adding
  a note: "if JSON absent, inspect the True-Regime Validation section of the `.md`."

- **Context rediscovered:** The reviewer had to trace `_build_case_inputs → _driver_samples →
  _to_kinematic_samples → SegmentClassifier` to confirm the regime is smoother-based, not raw.
  The handoff crux says "(a) the true-regime validation genuinely uses the production
  smoother-based regime (not the fast raw-regime)" but did not provide the call chain to verify
  this. Future handoffs for smoother-vs-raw regime distinction should name the call chain:
  `run_case → _build_case_inputs → _to_kinematic_samples → SegmentClassifier` = smoother regime.

- **Instructions improvised around:** none — confirmed after review. The handoff instructions
  were clear and actionable. The skill instruction to "drive through the engine" was adapted to
  direct inline execution (recording check results as I go) rather than writing a JSON file first,
  since the engine script is a CLI tool and the review should be done inline per skill guidance.

- **What would have made this easier:** Add to the handoff a "key call chain" box for the
  crux check: "smoother regime confirmed via: `run_case → _build_case_inputs →
  _to_kinematic_samples (session_braking.py) → SegmentClassifier`." This would make the
  regime-authenticity check a 30-second grep rather than a multi-file trace.

---

## Return status
`complete`
