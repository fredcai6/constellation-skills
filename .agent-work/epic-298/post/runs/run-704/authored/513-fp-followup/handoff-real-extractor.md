# Implementer Handoff — Real GateExtractor (Admiral Phase-4 expansion; feeds the thin demo)

## Task
Build the REAL `fp_gate.GateExtractor` against real telemetry: `src/physics/layer2/fp_gate_real_extractor.py`
with a `make_extractor(*, year, weekends, db_path, sessions=("FP2","FP3"), max_drivers=None,
max_laps_per_driver=None, cache=None) -> GateExtractor` factory. It is the vehicle for a thin, bounded,
ILLUSTRATIVE-NOT-EVIDENTIAL demonstration run — NOT the frozen F10 verdict. It must NOT modify the frozen
harness (`fp_gate.py`, `fp_representativeness.py`) or GATE_PROTOCOL.

## Protected Intent
Prove the pipeline runs end-to-end on real telemetry and de-risk the eventual powered run. Correctness of
the SHAPES it emits matters (the harness consumes them); statistical power does NOT (demo is thin/underpowered).

## Test Mode
test-after allowed (this is compute-glue over reviewed seams); unit-test the pure helpers (nominal clock
schedule, per-car grip assembly) on synthetic inputs. A tiny 1-weekend/2-car smoke is the integration proof.

## What it must implement (the `GateExtractor` Protocol — read `fp_gate.py:128` and the RawFpObservation/
RawQTarget dataclasses at `fp_gate.py:69-131`)
- `fp_observations(weekend_id) -> Sequence[RawFpObservation]`: for each FP session in `sessions`, load via
  `session_fit.load_quali_session(year, weekend_id, session_type, DEFAULT_CACHE)`, then for each driver (cap
  at `max_drivers` by session classification order if set), smooth via
  `session_braking._driver_samples(session, driver, cache=<shared dict>)` (REUSE one shared cache across
  sessions/views — the ~2.4x saver), extract apexes per flying lap via
  `apex_extract.extract_apex_observations(processed_df_for_lap)` (cap laps at `max_laps_per_driver` by
  fastest lap_time if set). Pool cross-car per session via `capability.apex_pace({car:[ApexObservation]})`
  → each car's `grip_value` = its `ApexPace.pace` (PRIMARY, mass-free). Map DRIVER→CONSTRUCTOR via
  `session_classifications` (reuse the pattern from `session_race`/`session_cumulative_track_laps`).
  Emit ONE RawFpObservation per (constructor, session): `car_id`=constructor, `session_type`,
  `hours_to_q` from the NOMINAL weekend schedule (FP1≈26, FP2≈22, FP3≈3, Q=0 — DB session_start_time_utc is
  NULL, document this), `latent`=the constructor's representative (fastest clean) lap's `FpLapLatent` from
  `fp_lap_latent.extract_fp_lap_latent`, `track_evolution`=`session_race.session_cumulative_track_laps(...)`,
  `session_max_track_evolution`=None (let the harness compute it), `grip_value`, `power_value`=None (SECONDARY
  deferred — the demo is grip-only; harness handles None), `fp_mass_sigma_kg`=`mass_model.fp_mass(year).sigma_kg`.
- `q_targets(weekend_id) -> Sequence[RawQTarget]`: load the Q session, same apex→apex_pace per constructor →
  `RawQTarget(car_id=constructor, grip_capability=ApexPace.pace, power_capability=None)`.

## Grain note (document, don't over-engineer)
One observation per (constructor, session) is the demo grain — the within-session representativeness variation
that F3 needs is coarser here (session-level), which is acceptable for an ILLUSTRATIVE demo; note it as a
demo simplification vs the powered run's finer (per-run) grain.

## Allowed Scope
- New `src/physics/layer2/fp_gate_real_extractor.py`.
- New `tests/unit/physics/layer2/test_fp_gate_real_extractor.py` (pure-helper unit tests + a mock-session
  test; do NOT load real telemetry in unit tests).
- Do NOT touch `fp_gate.py`, `fp_representativeness.py`, GATE_PROTOCOL, or any frozen file.

## Constraints
- physics-region: no evo/latent_power/compound_prior/fastf1 imports.
- Reuse the shared `_driver_samples` cache dict across all sessions/drivers in one extractor instance.
- No data/*.db writes; read-only. `git status --short data/` clean.
- `py -m src.utils.simplification_limits --baseline --paths <touched>` PASS (files < 1000 lines).
- Never raise on a missing driver/session — skip with a logged reason (the demo tolerates gaps).

## Required Evidence
- `py -m pytest tests/unit/physics/layer2/test_fp_gate_real_extractor.py -q` green.
- A tiny REAL integration smoke: instantiate `make_extractor(year=2023, weekends=["Hungary"], db_path=
  "data/f1_data_2023.db", sessions=("FP2",), max_drivers=4, max_laps_per_driver=2)` and call
  `fp_observations("Hungary")` — paste the count + one RawFpObservation repr (this WILL take a few min;
  run it with a timeout and if too slow paste the partial + note it). `git status --short data/` clean.

## Verification Commands
```bash
cd /c/Programs/f1-513 && PYTHONPATH=/c/Programs/f1-513 py -m pytest tests/unit/physics/layer2/test_fp_gate_real_extractor.py -q
```

## Suggested Model Tier
`stronger` — real seam composition (apex→apex_pace pooling, driver→constructor mapping, representative-lap latent).

## Authority
The Protocol shapes are FROZEN (read fp_gate.py). The grain (per-constructor-per-session), the nominal clock
schedule, and grip-only-for-demo are DECIDED (Ship I). Do not modify the frozen harness.

## Stop Conditions
Stop and return if the Protocol shapes can't be satisfied from the real seams, or a frozen file would need editing.

## Return Format
IMPLEMENTER_RESULT to `.agent-work/513-fp-followup/result-real-extractor.md` + SendMessage to "ShipI-513":
completed slice, files, test evidence, the real smoke output, assumptions, stop conditions, workflow feedback.
