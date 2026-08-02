# Implementer Handoff — G4

## Gate
`g4`

## Task
Build `src/physics/feature_view/build_lap_evidence.py` — composes real `LapEvidenceRecord`
rows (G1's dataclass) from ALREADY-EXTRACTED `src.physics.layer2.fp_lap_latent.FpLapLatent`
objects (the composer does NOT call `extract_fp_lap_latent` itself — same pattern as G2/G3:
the composer takes already-computed domain objects as input, never reads the DB directly,
keeping it testable on synthetic fixtures). Writes via
`FeatureViewStore.insert_lap_evidence` (G1, closed/frozen this run).

## Key seams (verified from source — cite exactly, do not re-derive from memory)

- `FpLapLatent` (`src/physics/layer2/fp_lap_latent.py:71-114`, frozen dataclass): fields
  `driver: str`, `lap_number: int`, `stint_id: int`, `lap_in_stint: int`, `compound: str`,
  `tyre_life: Optional[int]`, `run_purpose: str`, `fuel_kg_est: float`,
  `fuel_sigma_kg: float`, `mass_kg: float`, `mass_sigma_kg: float`, `valid_lap: bool`,
  `track_status: Optional[str]`. This is the mass/mode-posterior source for
  `LapEvidenceRecord.mass_kg`/`mass_sigma_kg`/`run_purpose`/`compound`.
- `observation_features(latent: FpLapLatent, *, quali_fuel_kg: float, track_evolution:
  Optional[int], session_max_track_evolution: Optional[int] = None) -> ObservationFeatures`
  and `observation_weight(features: ObservationFeatures, *, params: WeightParams =
  DEFAULT_WEIGHT_PARAMS) -> float` (`src/physics/layer2/fp_representativeness.py:277-329`) —
  the representativeness-weight pipeline. `quali_fuel_kg`: use
  `src.physics.mass_model.NOMINAL_QUALI_FUEL_KG` (`src/physics/mass_model.py:62`, value
  `10.0`) as the default reference — this is the repo's own named constant for exactly this
  purpose, do not hardcode a literal `10.0` yourself.
- **`track_evolution` requires a DB read this gate does NOT perform.**
  `session_race.compute_cumulative_track_laps(session_id, first_clean_lap_num, db_path)`
  (`src/physics/layer2/session_race.py:268-`) is the real per-lap track-evolution source, but
  it needs a live `session_id`/`db_path` — out of scope for a synthetic-fixture composer (same
  DB-read boundary G2/G3 already respected). Your composer function accepts
  `track_evolution: Optional[dict[int, int]] = None` — an OPTIONAL caller-supplied mapping
  `{lap_number: cumulative_track_laps}` — and looks up each latent's own `lap_number` in it,
  passing `None` through to `observation_features` when the mapping is absent OR the specific
  lap_number is missing from it (never fabricates a track-evolution number; `track_evolution_
  score`'s own None-safety already handles a `None` input via `NEUTRAL_TRACK_EVOLUTION_SCORE`,
  cited in that function's docstring — reuse that None-safety, don't reimplement a fallback).
  State this DB-read-boundary decision explicitly in your module docstring (mirrors the
  established composer pattern — a future Phase-6 caller pre-computes and supplies this map).
- `src/physics/feature_view/records.py`'s `LapEvidenceRecord(year, gp_name, session_type,
  driver, lap_number, model_version, representativeness_weight, mass_kg, mass_sigma_kg,
  run_purpose, compound, unit_class_residuals=None, unit_class_residual_status="unresolved")`
  — a `__post_init__` guard RAISES `ValueError` if `unit_class_residuals` is set. **Do not
  attempt to compute it — leave it at its default.** The reason (already in the class
  docstring, restate briefly in your module docstring too): the real per-lap telemetry
  extractor that would produce a genuine grip/power-class residual against the fitted
  car-basis (`fp_gate_real_extractor.RealGateExtractor`) is itself flagged G7-deferred /
  compute-deferred per the base commit's own message — never fabricate this value here.
- `year`/`gp_name`/`session_type` are NOT fields on `FpLapLatent` (it only carries per-lap
  identity within one already-known session) — your composer function takes them as explicit
  parameters (the caller already knows which session it extracted `FpLapLatent`s from, since
  it called `extract_fp_lap_latent(year, gp, session_type, ...)` to get them).

## Protected Intent
`unit_class_residuals` MUST remain `None` (enforced by G1's `__post_init__` guard — do not
bypass it, do not edit G1's closed `records.py`). The representativeness weight must be
computed via the real `observation_weight`/`observation_features` functions, not
approximated or hand-rolled.

## Test Mode
TDD required — synthetic `FpLapLatent` fixtures (construct 2-3 directly, covering a
`"push"` run_purpose lap and a `"long_run"` lap at minimum, per
`fp_representativeness.run_purpose_score`'s own scoring table — check that table in
`fp_representativeness.py` before picking test values, so your synthetic run_purpose labels
are ones the real scorer actually recognizes). No live DB read required (per the composer's
own DB-read boundary — see above).

## Close Criteria
- `src/physics/feature_view/build_lap_evidence.py` exists with a composer function (e.g.
  `build_lap_evidence_records(latents: list[FpLapLatent], *, year: int, gp_name: str,
  session_type: str, model_version: int, quali_fuel_kg: float =
  mass_model.NOMINAL_QUALI_FUEL_KG, track_evolution: Optional[dict[int, int]] = None) ->
  list[LapEvidenceRecord]`) producing one `LapEvidenceRecord` per input latent.
- `representativeness_weight` matches calling `observation_weight(observation_features(latent,
  quali_fuel_kg=..., track_evolution=..., session_max_track_evolution=...))` directly — test
  this equality against the real functions, not a hand-computed expected value.
- `mass_kg`/`mass_sigma_kg`/`run_purpose`/`compound` are copied straight from the input
  `FpLapLatent` (no transformation).
- `unit_class_residuals` stays `None`/`"unresolved"` on every produced record — one explicit
  test asserting this.
- The `track_evolution` optional-mapping lookup is tested both ways: (a) a lap whose
  `lap_number` IS in the mapping produces a different weight than (b) a lap whose
  `lap_number` is NOT in the mapping (or when `track_evolution=None` entirely) — confirming
  the lookup genuinely affects the computed weight rather than being silently ignored.
- No `src.evo_predictor` import; `extract_fp_lap_latent` (the DB-reading function) is NOT
  imported/called in this new file (grep-verifiable) — only `FpLapLatent` the dataclass.
- `py -m pytest tests/unit/physics/feature_view -q` green (all prior + new tests).
- `simplification_limits --paths src/physics/feature_view` clean.

## Allowed Scope
New file `src/physics/feature_view/build_lap_evidence.py`; new test file(s) under
`tests/unit/physics/feature_view/` (e.g. `test_build_lap_evidence.py`).

## Specific Exclusions
Do NOT modify `records.py`/`store.py` (G1), `build_weekend_state.py` (G2), or
`build_car_basis.py` (G3) — all closed/reviewed. Do NOT modify
`src/physics/layer2/fp_lap_latent.py`, `fp_representativeness.py`, or
`src/physics/mass_model.py` (read-only consumers). Do NOT call `extract_fp_lap_latent` or read
any live DB in this gate's tests.

## Constraints
- `constraint:physics_region_no_evo_import`.
- Reuse `observation_features`/`observation_weight` (call, don't reimplement the logistic form).
- `unit_class_residuals` never fabricated — enforced by G1's `__post_init__`.
- DB hygiene: tests use synthetic in-memory `FpLapLatent` objects, no DB at all needed for this
  gate's own tests (the composer itself performs no DB read).

## Map Anchors (inbound)
- **Structural:** `struct:physics.layer2` (read-only: `fp_lap_latent`,
  `fp_representativeness`), `struct:physics` (`mass_model.NOMINAL_QUALI_FUEL_KG`),
  `struct:physics.feature_view`.
- **Capability:** `observation_weight`, `observation_features`, `FpLapLatent`.
- **Constraints/assumptions:** `constraint:physics_region_no_evo_import`.
- **Decision anchors:** decision pressure 3 (unit-class residuals) — RESOLVED as reserved
  slot per MISSION_FRAME.md; do not re-decide.
- **Evidence expectations:** representativeness weight is genuinely emergent (never
  session-label-derived) — confirm your composer never reads `session_type` into the weight
  computation itself (it's only used for the record's own identity fields, not fed to
  `observation_features`/`observation_weight`, which never accept a session_type argument at
  all — a good sign this constraint is structurally impossible to violate here).

## Deliverable Path Check
- **Committed** — `src/physics/feature_view/build_lap_evidence.py`; `git check-ignore` exit 1.
- **Committed** — new test file(s).

## Required Evidence
- Full pytest output.
- A concrete example of one produced `LapEvidenceRecord` showing the representativeness
  weight matches a directly-computed `observation_weight(observation_features(...))` call.
- The two `track_evolution`-mapping-present-vs-absent examples showing a different weight.
- `simplification_limits` output; grep confirming `extract_fp_lap_latent` is not imported.

## Verification Commands

```bash
export PATH="/c/Users/fredc/AppData/Local/Microsoft/WindowsApps:$PATH"
py -m pytest tests/unit/physics/feature_view -q
py -m src.utils.simplification_limits --paths src/physics/feature_view
grep -rn "evo_predictor\|extract_fp_lap_latent" src/physics/feature_view/build_lap_evidence.py || echo clean
git check-ignore src/physics/feature_view/build_lap_evidence.py; echo "exit=$?"
```

## Suggested Model Tier
Simple bounded — straightforward composition over two already-cited pure functions; the only
genuine judgment point (the track_evolution DB-read boundary) is pre-specified above.

## Authority
The reserved-slot decision (`unit_class_residuals`) and the DB-read-boundary design
(`track_evolution` as an optional pre-computed mapping) are already made — carry them exactly
as specified; do not re-decide either.

## Stop Conditions
Stop and return if: `FpLapLatent`'s actual fields don't match this handoff's citation;
`observation_features`/`observation_weight`'s actual signatures differ from what's cited; a
decision outside this handoff's authority is needed.

## Return Format
Return IMPLEMENTER_RESULT: completed slice, files changed, test mode satisfied, evidence
produced, assumptions used, stop conditions hit, out-of-scope observations, workflow feedback.
