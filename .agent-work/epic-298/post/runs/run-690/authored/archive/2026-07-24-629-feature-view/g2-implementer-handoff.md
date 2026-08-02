# Implementer Handoff — G2

## Gate
`g2`

## Task
Build `src/physics/feature_view/build_weekend_state.py` — composes real
`WeekendStateRecord` rows (G1's dataclass, `src/physics/feature_view/records.py`) from
`src.physics.weekend_state.model.WeekendStateModel`'s fitted output, and writes them via
`src.physics.feature_view.store.FeatureViewStore.insert_weekend_state` (G1, already built and
merged on this branch).

Key seams (verified from source, cite exactly — do not re-derive from memory):
- `WeekendStateModel` (`src/physics/weekend_state/model.py:90-204`): construct with
  `WeekendStateModel(axes=None, weekend_key=DEFAULT_WEEKEND_KEY, season_key=DEFAULT_SEASON_KEY)`
  (defaults to all 11 axes from `frame.AXES`). Call `.fit(train_df)` then `.transform(df)` (or
  the `.car_signal(df)` alias — same method). `.model_cols()` returns `{axis: f"{axis}_car_signal"}`
  — the F6-measured column per axis. `.layer_sigma_cols()` returns, per axis, the list
  `[f"{axis}_layer1_sigma", f"{axis}_l2_delta_sigma", f"{axis}_l3_relative_sigma",
  f"{axis}_l3_fieldcar_sigma", f"{axis}_l3_absolute_sigma", f"{axis}_car_signal_sigma"]`. Use
  BOTH methods to enumerate columns — do not hand-guess a `{axis}_something` naming convention.
- `frame.py` (`src/physics/weekend_state/frame.py:24-42`): `AXES` (11-axis list), `KEY_COLUMNS
  = ["year", "gp_name", "constructor", "round_idx"]` — one row per car-weekend. `load_frame()`
  reads `session_type='Q'` only from the ABSOLUTE main-checkout `physics_estimates.db` — you do
  NOT need to call `load_frame()` in this gate's own code; your composer function takes an
  ALREADY-TRANSFORMED DataFrame (the output of `model.transform(df)`) as its input, so it has
  no direct DB dependency of its own (mirrors `WeekendStateModel`'s own leak-free design: the
  model doesn't read the DB, callers feed it a frame).
- `estimate_store_fields.effective_axis_sigma`/`.normalize_axis_status` (already imported into
  `src/physics/feature_view/store.py` — reuse the SAME import, do not add a second one) — for
  the explicit-unknown per-axis status you attach to each `WeekendStateRecord`'s `axis_status`
  dict. Since `WeekendStateModel`'s output carries no per-axis "resolved"/"unresolved" label of
  its own (it's a physics decomposition, not the layer2 fit-quality store), your composer marks
  an axis `"resolved"` when its `{axis}_car_signal` value + sigma are both non-null/non-NaN,
  else `"unresolved"` (a real per-row check, not a blanket constant) — document this rule
  explicitly since it's a NEW convention this gate introduces (not something WeekendStateModel
  itself states).
- `src/physics/feature_view/records.py`'s `WeekendStateRecord(year, gp_name, session_type,
  constructor, model_version, axis_values, axis_sigma, axis_status)` (frozen dataclass, no
  `round_idx` field currently — see note below) and
  `src/physics/feature_view/store.py`'s `FeatureViewStore.insert_weekend_state(record)`
  (plain append-only INSERT, raises `sqlite3.IntegrityError` on a duplicate
  `(year, gp_name, session_type, constructor, model_version)` key — this is EXPECTED/desired
  behavior, not a bug to work around).

## Protected Intent
The composer must never fabricate an axis value/sigma/status — an axis WeekendStateModel could
not resolve (NaN car_signal or sigma) is marked `"unresolved"` with a widened sigma via
`effective_axis_sigma`, never silently dropped or zero-filled.

## Note on `round_idx`
`WeekendStateRecord` (G1's dataclass) has no `round_idx` field, but `WeekendStateModel`'s
`KEY_COLUMNS` include it (needed to distinguish weekends within a year). Since `session_type`
is always `"Q"` for this model's current input (per `frame.py`'s `WHERE session_type='Q'`),
and the record's natural key is `(year, gp_name, session_type, constructor, model_version)`,
`gp_name` already disambiguates the weekend within a year (one GP per weekend) — `round_idx` is
redundant with `gp_name` for this key's uniqueness and is NOT required in the stored record.
This is a decision you may make directly (it's a straightforward schema-fit observation, not a
scope-widening call) — just state it explicitly in your module's docstring so a future reader
doesn't wonder where `round_idx` went. Do NOT modify `records.py` in this gate (G1's dataclass
is frozen/closed) — if you find `round_idx` is genuinely needed for some case (e.g. an event
appearing twice with the same `gp_name` in odd historical calendar corrections), STOP and
report it as a blocker rather than silently dropping data or hand-editing G1's closed file.

## Test Mode
TDD required — synthetic frame first (per `tests/unit/physics/weekend_state/test_model.py`'s
own convention, cite it exactly: `make_frame(seed=626, years=(2022,2023), n_rounds=12,
n_con=8)` builds a small store-shaped frame with `AXES = ["drag_area_closed_m2", "max_power_w",
"brake_decel_ms2"]` — reuse or closely mirror this pattern for your own test fixture, do not
require a live `physics_estimates.db`).

## Close Criteria
- `src/physics/feature_view/build_weekend_state.py` exists with a function (name your choice,
  e.g. `build_weekend_state_records(model: WeekendStateModel, transformed_df: pd.DataFrame,
  *, model_version: int) -> list[WeekendStateRecord]`) that, given an already-fitted
  `WeekendStateModel` and its `.transform()` output, produces one `WeekendStateRecord` per row
  of the input frame.
- Every axis's `axis_status` entry is `"resolved"`/`"unresolved"` per a REAL per-row,
  per-axis check (not a constant) — test both branches explicitly (construct a row with a NaN
  car_signal for one axis, confirm it's marked `"unresolved"` with a correspondingly widened
  sigma via `effective_axis_sigma`; a fully-resolved row is marked `"resolved"` with its sigma
  passed through unchanged).
- Records write successfully via `FeatureViewStore.insert_weekend_state` (use a `tmp_path` DB,
  never a committed path).
- No `src.evo_predictor` import anywhere in the new file.
- `py -m pytest tests/unit/physics/feature_view -q` green (G1's 27 tests + this gate's new
  ones, all still passing).
- `py -m src.utils.simplification_limits --paths src/physics/feature_view` clean (note the
  correct flag is `--paths`, not a bare positional — G1's reviewer found the handoff template's
  literal command wrong; use the corrected form).

## Allowed Scope
New file `src/physics/feature_view/build_weekend_state.py`; new test file(s) under
`tests/unit/physics/feature_view/` (e.g. `test_build_weekend_state.py`).

## Specific Exclusions
Do NOT modify `src/physics/feature_view/records.py` or `store.py` (G1, closed/reviewed — if you
find a genuine defect or gap, STOP and report it as a blocker, do not patch it yourself). Do NOT
modify `src/physics/weekend_state/` (read-only consumer). Do NOT read the real
`data/physics_estimates.db` in this gate's tests (synthetic frame only, per Test Mode).

## Constraints
- `constraint:physics_region_no_evo_import`.
- Reuse `effective_axis_sigma`/`normalize_axis_status` (imported from
  `src.physics.layer2.estimate_store_fields`, same import path `store.py` already uses) — do
  not reimplement the widening logic.
- DB hygiene: tests use `tmp_path`.

## Map Anchors (inbound)
- **Structural:** `struct:physics.weekend_state` (read-only), `struct:physics.feature_view`.
- **Capability:** `WeekendStateModel.fit/transform/car_signal/model_cols/layer_sigma_cols`.
- **Constraints/assumptions:** `constraint:physics_region_no_evo_import`.
- **Evidence expectations:** explicit-unknown contract applied per-axis, per-row (not blanket).

## Deliverable Path Check
- **Committed** — `src/physics/feature_view/build_weekend_state.py`; verify via
  `git check-ignore` exiting 1 before your final check.
- **Committed** — new test file(s) under `tests/unit/physics/feature_view/`.

## Required Evidence
- Full pytest output for `py -m pytest tests/unit/physics/feature_view -q`.
- A concrete example (paste it) of one resolved-axis row and one unresolved-axis row's
  produced `WeekendStateRecord`, showing the `axis_status`/`axis_sigma` difference.
- `simplification_limits` output (use `--paths`, not a bare positional arg).

## Verification Commands

```bash
export PATH="/c/Users/fredc/AppData/Local/Microsoft/WindowsApps:$PATH"
py -m pytest tests/unit/physics/feature_view -q
py -m src.utils.simplification_limits --paths src/physics/feature_view
grep -rn "evo_predictor" src/physics/feature_view/build_weekend_state.py || echo "clean"
git check-ignore src/physics/feature_view/build_weekend_state.py; echo "exit=$?"
```

Note: on this box, bare `py` may resolve to a pytest-less interpreter via a shell wrapper at
`~/.local/bin/py`; prepend `/c/Users/fredc/AppData/Local/Microsoft/WindowsApps` to `PATH` (the
real Windows py launcher lives there) before running any `py`/pytest command, in Bash-tool
sessions. If your environment doesn't hit this, ignore it.

## Suggested Model Tier
Simple bounded — this is a straightforward composition over two already-built, already-cited
seams; the per-row resolved/unresolved rule is the only genuine judgment call, and it's
pre-specified above.

## Authority
The `round_idx` schema-fit observation (see note above) is pre-authorized as stated; anything
beyond that (e.g. genuinely needing `round_idx`) is a stop condition, not a decision to make
alone.

## Stop Conditions
Stop and return if: `round_idx` turns out to be genuinely required (duplicate `gp_name` within
a year that the natural key can't disambiguate); `WeekendStateModel`'s actual output columns
don't match `model_cols()`/`layer_sigma_cols()`'s stated shape; a decision outside this
handoff's authority is needed.

## Return Format
Return IMPLEMENTER_RESULT: completed slice, files changed, test mode satisfied, evidence
produced, assumptions used, stop conditions hit, out-of-scope observations, workflow feedback.
