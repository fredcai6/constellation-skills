# Implementation Result

Status values follow `skills/workbench/references/status-model.md`.

## Assigned gate
`g4`

## Completed slice
Built `src/physics/feature_view/build_lap_evidence.py`, a pure composer function
`build_lap_evidence_records(latents, *, year, gp_name, session_type, model_version,
quali_fuel_kg=mass_model.NOMINAL_QUALI_FUEL_KG, track_evolution=None,
session_max_track_evolution=None) -> list[LapEvidenceRecord]` that turns
already-extracted `FpLapLatent` objects into `LapEvidenceRecord` rows: straight-copies
`mass_kg`/`mass_sigma_kg`/`run_purpose`/`compound`, computes
`representativeness_weight` via the real `observation_features`/`observation_weight`
functions (never hand-rolled), honors the DB-read boundary for `track_evolution` via
an optional caller-supplied `{lap_number: cumulative_track_laps}` mapping, and never
sets `unit_class_residuals` (stays at G1's reserved default).

## Scope
**Files changed:**
- `src/physics/feature_view/build_lap_evidence.py` (new)
- `tests/unit/physics/feature_view/test_build_lap_evidence.py` (new)

**Specific exclusions touched:** no — `records.py`, `store.py`,
`build_weekend_state.py`, `build_car_basis.py`, `fp_lap_latent.py`,
`fp_representativeness.py`, and `mass_model.py` were read-only references, never
modified.

## Behavior changed
Yes — new capability. Adds the fourth-of-four Phase-5 composer: real
`LapEvidenceRecord` rows can now be produced from `FpLapLatent` lists for
`FeatureViewStore.insert_lap_evidence` to persist. No existing behavior changed.

## Map Impact

- **Structural anchors touched:** `struct:physics.feature_view` — new module-leaf
  `build_lap_evidence.py` added alongside G1/G2/G3's `records.py`/`store.py`/
  `build_weekend_state.py`/`build_car_basis.py`. `struct:physics.layer2` (read-only:
  `fp_lap_latent.FpLapLatent`, `fp_representativeness.observation_features`/
  `observation_weight`) and `struct:physics` (`mass_model.NOMINAL_QUALI_FUEL_KG`) —
  consumed, not modified.
- **Capabilities added/changed/affected:** `build_lap_evidence_records` — new. Turns
  a list of `FpLapLatent` into a list of `LapEvidenceRecord`, completing the
  composer set (`build_weekend_state_records`, `build_car_basis_posterior_records`,
  now `build_lap_evidence_records`) that G5's `FeatureViewRow` assembly can draw on.
- **Constraints/assumptions touched:** `constraint:physics_region_no_evo_import` —
  honored (no `evo_predictor` import; verified by grep and a dedicated test).
  DB-read boundary — honored: the composer never calls the DB-reading extractor
  function in `fp_lap_latent.py` and accepts `track_evolution` only as an optional
  pre-computed mapping.
- **Decision candidates / resolved decisions:** Decision pressure 3
  (`unit_class_residuals` reserved slot, per `MISSION_FRAME.md`) — carried exactly
  as already resolved, not re-decided. No new decision surfaced.
- **Claims/evidence produced:** `representativeness_weight` genuinely emergent —
  confirmed the composer never feeds `session_type` (or any session label) into
  `observation_features`/`observation_weight`, which structurally cannot accept one
  (no such parameter exists on either function).
- **Trust limitations / drift found:** none found — all cited seams matched the
  handoff's citations exactly (fields, signatures, line ranges).
- **Triage candidates:** none raised.

## Test mode
**Required:** `test-first (TDD)`
**Satisfied:** yes — `tests/unit/physics/feature_view/test_build_lap_evidence.py`
written before `build_lap_evidence.py` existed; RED observed
(`ModuleNotFoundError: No module named 'src.physics.feature_view.build_lap_evidence'`)
before the module was created, then implementation made all 9 tests pass GREEN.

## Evidence

```bash
$ export PATH="/c/Users/fredc/AppData/Local/Microsoft/WindowsApps:$PATH"
$ py -m pytest tests/unit/physics/feature_view -q
============================= test session starts =============================
platform win32 -- Python 3.14.3, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Programs\f1-629
configfile: pyproject.toml
plugins: anyio-4.13.0, hypothesis-6.152.9, cov-7.1.0, mock-3.15.1
collected 57 items

tests\unit\physics\feature_view\test_append_only_contract.py ..          [  3%]
tests\unit\physics\feature_view\test_as_of_leakage.py .....              [ 12%]
tests\unit\physics\feature_view\test_build_car_basis.py ...............  [ 38%]
tests\unit\physics\feature_view\test_build_lap_evidence.py .........     [ 54%]
tests\unit\physics\feature_view\test_build_weekend_state.py ......       [ 64%]
tests\unit\physics\feature_view\test_records.py ..........               [ 82%]
tests\unit\physics\feature_view\test_store.py ..........                 [100%]

============================= 57 passed in 0.85s ==============================

$ py -m src.utils.simplification_limits --paths src/physics/feature_view
PASS (6 files checked)

$ grep -rn "evo_predictor\|extract_fp_lap_latent" src/physics/feature_view/build_lap_evidence.py || echo clean
clean

$ git check-ignore src/physics/feature_view/build_lap_evidence.py; echo "exit=$?"
exit=1
```

**Result:** pass — 57/57 tests green (48 prior G1/G2/G3 tests unaffected + 9 new),
simplification_limits clean, grep clean, file not gitignored.

### Concrete example — `representativeness_weight` matches a direct call

```
>>> latent = FpLapLatent(driver='VER', lap_number=7, stint_id=1, lap_in_stint=3,
...     compound='SOFT', tyre_life=2, run_purpose='push', fuel_kg_est=11.0,
...     fuel_sigma_kg=8.0, mass_kg=790.0, mass_sigma_kg=8.0, valid_lap=True,
...     track_status=None)
>>> rec = build_lap_evidence_records([latent], year=2024, gp_name='gp1',
...     session_type='FP3', model_version=1)[0]
>>> rec.representativeness_weight
0.9975119324990797
>>> observation_weight(observation_features(latent,
...     quali_fuel_kg=mass_model.NOMINAL_QUALI_FUEL_KG,
...     track_evolution=None, session_max_track_evolution=None))
0.9975119324990797
>>> rec.representativeness_weight == _  # exact match
True
```

### Concrete example — `track_evolution` mapping present vs. absent differs

```
>>> recs_with = build_lap_evidence_records([latent], year=2024, gp_name='gp1',
...     session_type='FP2', model_version=1, track_evolution={7: 50})
>>> recs_without = build_lap_evidence_records([latent], year=2024, gp_name='gp1',
...     session_type='FP2', model_version=1, track_evolution=None)
>>> recs_with[0].representativeness_weight
0.997646072487396
>>> recs_without[0].representativeness_weight
0.9975119324990797
>>> recs_with[0].representativeness_weight != recs_without[0].representativeness_weight
True
```

A third test (`test_track_evolution_mapping_missing_lap_number_falls_through_to_none`)
also confirms a `lap_number` absent from a non-empty mapping produces the identical
weight as `track_evolution=None` entirely — the fallback is never fabricated.

## TDD evidence, if required

- Failing test observed:
  ```
  $ py -m pytest tests/unit/physics/feature_view/test_build_lap_evidence.py -q
  ImportError while importing test module ...
  E   ModuleNotFoundError: No module named 'src.physics.feature_view.build_lap_evidence'
  1 error in 0.47s
  ```
- Passing test observed:
  ```
  $ py -m pytest tests/unit/physics/feature_view/test_build_lap_evidence.py -q
  .........
  9 passed in 0.39s
  ```
- Refactor while green: yes — one docstring wording fix (the module docstring
  initially named the DB-reading extractor function literally, which tripped the
  module's own `test_no_evo_import_and_no_extract_fp_lap_latent` grep-style check;
  reworded to describe it without the literal string, same class of self-tripping
  G3's own why_trail already flagged for `fuse_dual_cda`). No logic change.

## Docs/contracts touched
- none — no committed doc/contract needed updating; the module's own docstring
  states the DB-read-boundary and reserved-slot design decisions per the handoff's
  instruction to restate them there.

## Assumptions
- None beyond the handoff's own pre-specified design (the `track_evolution`
  DB-read boundary and the `unit_class_residuals` reserved slot were both already
  decided in the handoff/MISSION_FRAME.md and carried exactly, not re-decided).

## Stop conditions hit
- None. `FpLapLatent`'s fields, `observation_features`/`observation_weight`'s
  signatures, and `NOMINAL_QUALI_FUEL_KG`'s value all matched the handoff's
  citations exactly on inspection — no re-derivation from memory was needed and
  no authority gap arose.

## Out-of-scope observations
- None found in this gate's scope. (For completeness: G5's `FeatureViewRow`
  assembly, the eventual consumer of this composer's output alongside G2's/G3's,
  is explicitly out of scope here per the launch order and was not touched.)

## Workflow Feedback
- **Handoff gaps:** none — the handoff's field/signature citations for
  `FpLapLatent`, `observation_features`/`observation_weight`, and
  `NOMINAL_QUALI_FUEL_KG` all matched the actual source exactly on verification,
  so no rework was needed from a citation error.
- **Context rediscovered:** none beyond what the handoff already named — reading
  `build_car_basis.py` (G3) as the sibling composer pattern (cited in the handoff)
  was sufficient orientation; its own why_trail (visible in
  `g3-implementer-plan.json`) also pre-flagged the exact "docstring names a
  forbidden literal string, trips its own grep-style test" failure mode this run
  hit again independently (for `extract_fp_lap_latent` instead of `fuse_dual_cda`)
  — useful to know this is a recurring shape across composer gates in this epic,
  not a one-off.
- **Instructions improvised around:** none — the plan's 4-item shape (context,
  straight-copy+real-weight, reserved-slot+track_evolution, full-verify) matched
  the actual work cleanly; as in G3, the TDD test file was written once covering
  both m1's and m2's planned test surface (a single coherent composer is simpler
  to build correctly than staging it half-implemented across two gates), and m2's
  "red" postcondition was attested as an honest targeted-verification re-run
  rather than a fresh fail-then-pass cycle — flagged explicitly in the engine's
  `why` text at that gate, same pattern G3's own why_trail already used.
- **What would have made this easier:** nothing concrete to flag — this handoff
  pre-specified the one genuine judgment point (the `track_evolution` DB-read
  boundary) exactly, so there was no ambiguity to resolve during the build.

## Return status
`complete`
