# Review Result

Status values follow `skills/workbench/references/status-model.md`.

## Assigned Gate
`g1` (work-id `575-fuel-burn-calibration`, issue #575)

## Result
`APPROVE`

## Handoff compliance
Yes. The change builds exactly what the handoff asked: a standalone,
zero-fit `src/physics/burn_rate_calibration.py` implementing
`lap_burn_kg = flow_rate_cap_kg_per_s * mean_throttle_fraction *
lap_duration_s`, a cited per-season `FUEL_REGULATIONS` table, a per-lap pure
formula with hand-computed unit tests, a per-(season, circuit) aggregator
with no pooling, and a lap-time-slope cross-check function. A companion
`scripts/validate_burn_rate_hypothesis.py` runs across 2019-2026 and
Bahrain/Spain(-or-Barcelona-Catalunya)/Silverstone(stored as "Great
Britain")/Monaco, printing the throttle-integral table, the cross-check
table, the Monaco-vs-free-flow pattern callout, and the SC/VSC-vs-green
ratio versus the hardcoded `SC_BURN_FRACTION`. `mass_model.py` is untouched.
All within allowed scope (new files only; everything else read-only).

## Scope drift
None. `git status --porcelain` shows only new untracked files: the three
in-scope new files (`src/physics/burn_rate_calibration.py`,
`scripts/validate_burn_rate_hypothesis.py`,
`tests/unit/physics/test_burn_rate_calibration.py`), the `.agent-work/`
workflow scaffolding, and the 7 pre-existing untracked scratch scripts named
in the handoff (`mass_validation_dashboard.py`, `mass_fuel_dashboard.py`,
`bahrain_frontier_validation.py`, `build_lateral_load_cache.py`,
`lateral_load_unitization.py`, `tyre_age_overview.py`,
`tyre_degradation_validation.py`) plus an unrelated `data/race_stint_estimates.db`.
`git diff HEAD -- src/physics/mass_model.py` is empty (confirmed byte-for-byte
unchanged; it is a tracked file with zero diff, not merely absent from a
untracked listing). The scratch scripts' mtimes (2026-06-29 through
2026-07-01, before/around this gate's work) are consistent with them being
untouched by this gate; `find data -newer .agent-work/.../MISSION_FRAME.md`
shows no DB in `data/` was modified after the mission frame was written,
confirming no batch re-population script ran. No specific exclusion was
touched.

## Evidence verdict
All three verification commands were re-run independently (not taken from
the pasted result) and reproduce exactly:
- `py -m pytest tests/unit/physics/test_burn_rate_calibration.py -q` ->
  **38 passed in 0.25s** (matches claim). Tests include hand-computed values
  for `per_lap_burn_kg` (including the handoff's own worked example: 100 kg/h
  cap, throttle=1.0, 60s -> 1.6667 kg), regulation-table correctness for 2019
  and 2026 boundary years, and aggregator/cross-check tests against a
  synthetic `DBSession`-shaped `MagicMock` (no live DB), following the
  `test_session_race.py` fixture convention as claimed.
- `py scripts/validate_burn_rate_hypothesis.py` -> reproduces the full
  per-(season, circuit) throttle-integral table, the lap-time-slope
  cross-check table, and the SC/VSC ratio table **numerically identical** to
  the implementer's pasted output, including the headline finding: free-flow
  circuits (Bahrain/Spain/Silverstone) mean %error = **80.2%** over 22
  season-circuit points, Monaco mean %error = **365.2%** over 7 points,
  pattern observed as claimed. Also reproduces the 3 skipped combinations
  (2020 Monaco cancelled, 2026 Bahrain absent from calendar, 2026 Great
  Britain not yet run) and the SC/VSC ratio cluster (~0.82-1.01 at most
  circuits, one 2024 Monaco small-sample outlier at 2.781).
- `py -m src.utils.simplification_limits --paths src/physics/burn_rate_calibration.py scripts/validate_burn_rate_hypothesis.py tests/unit/physics/test_burn_rate_calibration.py`
  -> **PASS (3 files checked)**.

The evidence is honest, not cherry-picked: the script's own output states the
model under-predicts observed slope magnitude at most free-flow points, and
the result file does not paper over the large free-flow error before
reporting the Monaco pattern. This matches the handoff's Authority-section
instruction to report plainly rather than tune the method to agree.

## Code/doc quality
Minimal and maintainable. `per_lap_burn_kg` is a pure function with explicit
input validation (negative-value `ValueError`s naming the field, per
CREW_CONTEXT's interface rules). `FUEL_REGULATIONS` is a frozen-dataclass
dict mirroring `mass_model.SEASON_BASE_KG`'s existing pattern. The
per-(season, circuit) functions (`season_burn_rate_estimate`,
`lap_time_slope_cross_check`, `sc_vsc_burn_ratio`) each operate on one
`(year, gp_name)` at a time with no shared/module-level mutable state and no
loop that aggregates across seasons or circuits internally — confirmed by
reading the source (no cross-call accumulation) and by the dedicated test
`test_no_cross_circuit_averaging`. `sqlite3` connections use `file:...?mode=ro`
URI read-only mode, consistent with CREW_CONTEXT's "open canonical DBs
read-only" rule. Regulatory citations in the module docstring match
`MISSION_FRAME.md`'s verified figures exactly (100 kg/h / 110 kg 2019-2025;
70 kg/h / 70 kg 2026). `grep -rn "import fastf1"` across all three new files
returned no matches; a separate grep for `evo_predictor|latent_power|
compound_prior` only matched docstring prose describing the constraint, not
actual imports — `constraint:physics_region_no_evo_import` is honored. A
fresh `grep -rl "burn_rate_calibration" src/` (excluding the module itself)
returned nothing, confirming the module is genuinely unwired/standalone as
claimed.

## Map impact verdict
- **Evidence supports claimed change:** Yes — the claimed capability (new
  standalone regulation-anchored estimator + cross-check + SC/VSC
  diagnostic) is exactly what was built and independently reproduced above.
- **Constraints not violated:** Yes — zero-fit held (only a literal cited
  constant and one documented, non-fitted reused sensitivity constant,
  `_PACE_S_PER_KG`, carried from the reference dashboard as instructed), no
  cross-season/circuit pooling, DB/telemetry-store-only access, no evo-region
  imports, `mass_model.py` untouched (confirmed zero diff on a tracked file,
  not just "absent from status").
- **Notes match the diff:** Yes — the implementer's Map Impact section
  correctly scopes `struct:physics`/`struct:data` as read-only reference and
  correctly states no other `src/` file imports the new module (verified).
- **Decision candidates surfaced:** Yes — the large free-flow cross-check
  error (80.2% mean) is surfaced as a new decision candidate for wiring
  discussion, not silently resolved or hidden; `decision:burn_rate_calibration_design`
  is correctly treated as already-resolved (not re-litigated), matching
  `MISSION_FRAME.md`'s decision-anchor language.
- **Durable context routed:** Yes — two out-of-scope findings (stale
  `sessions.has_telemetry` flag; `RuntimeWarning` overflow in
  `build_db_session` for NaN lap times) are named as triage candidates in the
  implementer's result and are carried forward here (see Out-of-scope
  observations) rather than fixed inline or dropped.

## Reconciliation check
No concerns. This is genuinely new structure (no prior packet documents a
burn-rate calibration module, matching the handoff's "Map confidence flags:
none"). The module sits cleanly as a new leaf under `struct:physics`,
read-only against `mass_model.py` and the telemetry-store seam, with no
wiring — nothing for Commander to reconcile against the existing structural
baseline.

## Blockers
- none — confirmed after review: all three verification commands pass on
  independent re-run, scope is clean, `mass_model.py` has zero diff, no
  pre-existing scratch script was touched, zero-fit/no-pooling/DB-only
  constraints all hold on direct source inspection.

## Out-of-scope observations
- The stale `sessions.has_telemetry` flag in the per-season SQLite DBs
  (`data/f1_data_{year}.db`) does not reflect actual telemetry-store
  coverage (confirmed: 2023 Bahrain reads `has_telemetry=0` despite
  `TelemetryStore.has_session` returning True) — worth a follow-up issue
  either to recompute it from the telemetry store or to stop reading it as a
  coverage signal anywhere else in the codebase. I spawned a background task
  (`task_0b0e8e73`) for this.
- `build_db_session` (`src/data/telemetry_session.py`, read-only reference,
  not modified in this gate) emits `RuntimeWarning: overflow encountered in
  multiply` from `pd.to_timedelta(..., unit="s")` when a session's
  `lap_time_s` column has NaN values — I observed this warning live in my own
  independent run of `scripts/validate_burn_rate_hypothesis.py`, confirming
  the implementer's claim. Non-crashing (NaN correctly becomes `NaT`,
  filtered downstream), but noisy across many (year, circuit) combinations.
  Recorded as triage candidate `tc1` in the survey checklist.
- No files were staged or committed as of this review (`git status
  --porcelain` shows every new file as untracked `??`); the handoff notes
  "Commander handles the actual `git add`/commit," so this is expected, not a
  defect, but flagging it so Commander doesn't assume the files are already
  staged.

## Workflow Feedback
- **Handoff gaps:** None material. The one real gap — the
  `simplification_limits` verification command missing `--paths` — was
  already caught and corrected by the implementer and confirmed by me on
  re-run with the corrected form; the reviewer handoff's own Close Criteria
  already state the corrected `--paths` form, so no further fix needed here.
- **Context rediscovered:** The `references/checklist-engine.md` path the
  constellation-reviewer `SKILL.md` cites does not exist inside the
  `constellation-reviewer` skill's own bundle — it only exists under the
  sibling `constellation-workbench` skill
  (`C:\Users\fredc\.claude\skills\constellation-workbench\references\checklist-engine.md`).
  I found it by globbing all installed skills' reference files; a fresh
  reviewer run without that fallback would stall trying to read a path that
  isn't there.
- **Instructions improvised around:** I omitted `--finding <text>` on every
  `record`/`consolidate` call to the engine (the CLI supports it via
  `--finding FINDING`, confirmed via `record --help`), even though the
  skill's own item imperatives say "record pass/fail with a finding." All ten
  survey items in the resulting `review.json` show `"finding": null`. This
  was my own oversight, not a tool gap — the engine does not enforce a
  non-null finding on `record --result pass`, so nothing refused the calls,
  and by the time I noticed (during a final read-back after `consolidate`),
  the checklist was already closed and I judged re-opening/re-recording ten
  already-complete items riskier than carrying the substantive findings in
  this REVIEW_RESULT.md instead (which it does, in full, above).
- **What would have made this easier:** (1) Fix the `constellation-reviewer`
  skill's own reference to `references/checklist-engine.md` — either bundle
  a copy in this skill's own `references/` directory, or have `SKILL.md`
  point explicitly at the `constellation-workbench` sibling path so a fresh
  agent doesn't have to glob every installed skill to find it. (2) Nothing
  else — the rest of the handoff (seam citations, close criteria, allowed
  scope, stop conditions) was accurate and let me verify everything without
  further rediscovery.

## Return status
`complete`
