# Review Result

## Assigned Gate
`g1-review — Common Scoreboard Harness (work-id 496-physics-aware-estimator)`

## Result
`verdict: APPROVE`

## Handoff compliance
All four deliverables match the task statement:
- `src/physics/layer2/scoreboard.py` NEW — pure metric core + injected-variant seam + two built-in variants
- `tests/unit/physics/layer2/test_scoreboard.py` NEW — 25 synthetic-array unit tests, no real sessions
- `scripts/validate_refine_505.py` REFACTORED — `_knee_and_ringing` removed; all 4 call sites replaced with `score_variant`; baseline JSON write added to `main()`
- `reports/physics/scoreboard_baseline_2023Q.json` GENERATED — Belgium/Monaco/Bahrain 2023 Q VER

Stop conditions from the handoff were not triggered: metric core is pure + correct, comparability holds, seam accepts arbitrary estimators, baseline reproduces #505, tests pass, no evo import.

## Scope drift
None. Only `scripts/validate_refine_505.py` was tracked-modified (git diff --stat: 1 file). The new files `scoreboard.py` and `test_scoreboard.py` are untracked additions. None of the specific exclusions (`smoother.py`, `accel_obs.py`, `trajectory_refine.py`, `braking_view.py`, `calibration.py`, `session_fit.py`) appear in the diff.

## Evidence verdict
All evidence independently re-run and confirmed:

1. **Unit tests (independently re-run):** `py -m pytest tests/unit/physics/layer2/test_scoreboard.py -q` → 25 passed in 0.18s. Confirmed — not just trusting implementer's pasted output.
2. **No layer2 regressions:** `py -m pytest tests/unit/physics/layer2/ -q` → 126 passed in 90.39s.
3. **Simplification limits on new files:** `py -m src.utils.simplification_limits --paths src/physics/layer2/scoreboard.py tests/unit/physics/layer2/test_scoreboard.py` → PASS (2 files checked). Confirmed independently.
4. **Baseline JSON spot-checked:**
   - Belgium gaussian `knee_gap_vs_raw`: -34.929 - (-38.839) = +3.910 ✓ (matches JSON: 3.9099250...)
   - Bahrain `ringing_over_ceiling`: 0.458 - (-2.862) = 3.320 ✓ (matches JSON: 3.320691...)
   - Bahrain `ringing_ok=false`: 0.458 > -2.862 + 1e-6 ✓
   - All three circuits match #505 references within <0.01 m/s² (well within 0.5 m/s² tolerance).
5. **TDD evidence:** RED (ModuleNotFoundError) → GREEN (25 pass) → no refactor — satisfies test-led requirement.

## Code/doc quality
- **Metric core is pure + deterministic:** `braking_knee` and `non_throttle_ringing` are plain functions on numpy arrays; no I/O, no side effects, no global state. Output is deterministic given the same array inputs.
- **Signs/units correct:** decel is negative; `braking_knee = min(a_long[brake])` returns the most-negative value (deepest decel); `non_throttle_ringing = max(a_long[non_throttle])` returns the most-positive spurious signal. Explicit in module docstring and `VariantScore` field docs.
- **NaN handling:** both pure functions return `float("nan")` when the mask is empty; tested explicitly.
- **Masks + raw reference fixed across variants:** `CaseInputs.__post_init__` builds `brake_mask` and `non_throttle_mask` from `regime` once; `a_long_raw` comes from `clean_longitudinal_from_raw` once in `_build_case_inputs`. In `run_case`, `inp` is built once and then `inp.brake_mask`, `inp.non_throttle_mask`, `inp.a_long_raw` are passed to `score_variant` unchanged for every variant. Only `a_long_variant` (the output of the variant callable) changes.
- **VariantFn seam is genuinely open:** `VariantFn = Callable[[CaseInputs], np.ndarray]`. `run_case` / `run_scoreboard` accept any `dict[str, VariantFn]` — callers can inject an arbitrary estimator without editing the core. Verified in code: the loop `for name, fn in variant_fns.items(): a_long_v = fn(inp)`.
- **No evo imports:** grep for `^from src.evo_predictor`, `^from src.latent_power`, `^from src.compound_prior` in both new files → no hits. The one grep match is in a module-level docstring comment, not an import statement.
- **Simplification limits:** PASS on new files. Pre-existing violations on `validate_refine_505.py` confirmed to predate G1 (stash test: CC=43, fn_lines=136/196 before G1; CC=44, fn_lines=139/213 after — violations pre-existed, G1 nudged slightly).
- **No mutable module-level state in src/:** `BUILTIN_VARIANTS` is a plain `dict` of pure functions — effectively a constant; no mutable runtime state.
- **`decision:two_cycle_external_anchor_design` honored:** `raw_a_long` from `clean_longitudinal_from_raw` is the fixed unbiased reference, explicitly documented in `score_variant` docstring.
- **`decision:smoother_rounds_braking_knee` honored:** the seam preserves both gaussian (cycle-1-only) and kind3 (two-cycle) as named built-in variants; the design explicitly supports comparing them head-to-head.

## Map impact verdict

- **Evidence supports claimed change:** Yes. Baseline JSON reproduces #505 numbers exactly (<0.01 m/s²), confirming the scoreboard infrastructure is measurement-equivalent to the prior inline implementation. The new injectable-variant capability is demonstrated by two built-in variants running identically.
- **Constraints not violated:** `constraint:physics_region_no_evo_import` — no actual evo imports in either new file. `decision:two_cycle_external_anchor_design` — raw reference is from `clean_longitudinal_from_raw`, fixed, not re-derived. `decision:smoother_rounds_braking_knee` — both smoother variants preserved and head-to-head comparable.
- **Notes match the diff:** Yes. Map Impact notes list `struct:physics.layer2` (new `scoreboard.py` — correct), new capability (injectable-variant scoreboard — correct), constraints honored (confirmed above). The notes are accurate representations of what changed.
- **Decision candidates surfaced:** The implementer flagged the session double-loading issue (acceptable for a script, noted as a future seam improvement) and the `student_t` variant omission (only gaussian + kind3 specified in handoff). No authority decision was required.
- **Durable context routed:** Three triage candidates explicitly called out: session double-load, pre-existing simplification violations, unused imports. All three are correctly scoped as out-of-scope / pre-existing. Cartographer update (architecture doc for new `scoreboard.py` module) noted as a follow-up — not blocking for this gate.

## Reconciliation check
The new `src/physics/layer2/scoreboard.py` adds a module to `struct:physics.layer2` that is not yet reflected in `docs/architecture/index.md`. This is a Cartographer task (noted by the implementer), not a blocker. No public contract docs need updating (no committed schema changes; the baseline JSON is a generated output, not a committed schema). The refactored `validate_refine_505.py` behavior is externally identical (same numeric outputs, additional JSON write).

## Blockers
- none

## Out-of-scope observations
1. **Session double-load (triage candidate, cosmetic):** `run_scoreboard` in `main()` calls `load_quali_session` for each case via `run_case`; `_run_one_circuit` also loads the same session. Net effect: each circuit's session is loaded twice per `py scripts/validate_refine_505.py` run. No correctness issue; acceptable for a validation script with no performance SLA. A `session` parameter in `run_case` / `CaseInputs` seam would fix it in G2. Flag for Commander.
2. **Pre-existing simplification violations in `validate_refine_505.py` (pre-existing, not block):** CC=43→44 in `main()`, fn_lines=136→139 in `_run_one_circuit`, fn_lines=196→213 in `main()`. All three violations confirmed to predate G1 via stash test. G1 added minimal lines; root violations are pre-G1 cleanup territory (#504-style). Route to Triage.
3. **Unused imports in `validate_refine_505.py` (pre-existing, cosmetic):** `driver_num`, `driver_streams`, `stint_span` imported from `src.preprocessing.trajectory.loaders` but unused. Confirmed pre-existing (present in `git show HEAD:scripts/validate_refine_505.py`). Not introduced by G1.
4. **Cartographer update needed:** `docs/architecture/index.md` does not yet list `src/physics/layer2/scoreboard.py`. The implementer correctly notes this as a Cartographer task. Route to Cartographer at Commander closeout.
5. **`student_t` variant not in BUILTIN_VARIANTS:** The cycle-1-only Student-t variant (nu_proc=4.0, no kind=3) appears in the script's printed table but was intentionally omitted from the scoreboard JSON per the handoff spec. If G2 wants it as a named variant, it can be added. No action needed now.

## Workflow Feedback

- **Handoff gaps:** The "How to Inspect the Diff" section uses `cat` (not a valid Windows command); on Windows this would need `type` or a Read tool. Minor but would confuse a reviewer trying to follow the instructions literally. Field: `How to Inspect the Diff`.
- **Context rediscovered:** Needed to stash-and-restore to verify that simplification violations were pre-existing (handoff asserted they were, but needed independent verification). Stash test was straightforward; a `git show HEAD:file | py -m src.utils.simplification_limits` approach would have been cleaner but doesn't work (simplification_limits needs a real file path). The stash approach is the right method — no handoff gap here, just noting the technique.
- **Instructions improvised around:** The skill's checklist-engine.md reference was not found at the expected path (`C:\Users\fredc\.claude\skills\constellation-reviewer\references\checklist-engine.md` — file does not exist). Drove the survey items from the REVIEW_SURVEY.template.json structure directly (r0 through r5), which is the correct behavior per skill instructions ("do the closest compliant thing and report the misfit"). The engine script (`scripts/checklist_engine.py`) was also not found in the repo — not needed for this review.
- **What would have made this easier:** The implementer's evidence section was thorough and accurately predicted every check. One improvement: the handoff's "spot-check one metric by hand" instruction could name which metric and which case to spot-check (e.g., "verify Belgium gaussian `knee_gap_vs_raw` using the formula `knee - raw_knee`") — this would save time deciding what "spot-check" means in this context.

## Return status
`complete`
