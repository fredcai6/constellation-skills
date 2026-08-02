# Powered held-out run — handback spec + resume command (#513 Phase 4 G7)

The falsifiable machinery is complete and proven (harness `fp_gate.py` + its GateExtractor Protocol seam;
36 tests incl. non-riggable NULL + leakage). The POWERED real held-out run is compute-deferred — this
file makes it one specified job away.

## Why deferred (measured)
- Per-driver smooth+apex = **120 s** (Hungary 2023 FP2 VER, 8 laps). `apex_pace` needs the **full field**
  per session for a valid cross-car pace regression, so a session ≈ 30-40 min; a weekend (FP1+FP2+FP3+Q)
  ≈ 2-2.5 h; the frozen 16-weekend LOWO ≈ **37 h**. Even fastest-2-laps-per-driver only ~halves it, and a
  2-weekend slice (~72 min) yields just 2 LOWO folds — too few for the paired-bootstrap significance verdict.
- Not safely babysittable with in-turn waiters in one commander session (the reap-trap the launch order flagged).

## The real GateExtractor to build (implements `fp_gate.GateExtractor`)
A crew-built + reviewed module (recommended — NOT hand-rolled), e.g. `src/physics/layer2/fp_gate_extractor.py`:
- `fp_observations(weekend_id)`: for each FP session (FP1/FP2/FP3), smooth every driver via
  `session_braking._driver_samples` (reuse the shared cache), extract apexes per lap via
  `apex_extract.extract_apex_observations`, pool cross-car per session via `capability.apex_pace` to get
  each car's `grip_value` (PRIMARY, mass-free). Emit per (car, session) — or per (car, session, stint) with
  a per-stint centred residual under the session's shared `beta` if within-session grip variation is wanted.
  Attach `latent` from `fp_lap_latent.extract_fp_lap_latent` (representative lap), `track_evolution` from
  `session_race.session_cumulative_track_laps`, `fp_mass_sigma_kg` from `mass_model.fp_mass(...).sigma_kg`,
  and (SECONDARY) `power_value` from the full 5-view fit on a BOUNDED subset only.
- `q_targets(weekend_id)`: Q session → `apex_pace` per car → `grip_capability` (+ optional `power_capability`).
- **CLOCK arm note:** `sessions.session_start_time_utc` is NULL in the season DBs, so `hours_to_q` must come
  from the nominal weekend schedule (FP1 ≈ 26 h, FP2 ≈ 22 h, FP3 ≈ 3 h, Q = 0). This is faithful to
  "clock-distance-to-Q" (it is the session-recency baseline the learned arm must beat).

## Resume command (once the extractor exists)
```bash
cd /c/Programs/f1-513 && OPENBLAS_NUM_THREADS=4 OMP_NUM_THREADS=4 PYTHONPATH=/c/Programs/f1-513 \
  py scripts/fp_representativeness_gate.py --year 2023 \
     --weekends "Abu Dhabi,Australia,Bahrain,Canada,Great Britain,Hungary,Italy,Japan,Las Vegas,Mexico,Miami,Monaco,Netherlands,Saudi Arabia,Singapore,Spain" \
     --db data/f1_data_2023.db --extractor real --lowo --paired-bootstrap 10000 \
     --out reports/physics/fp_representativeness_gate_2023.json
```
Run DETACHED (Start-Process -WindowStyle Hidden), state-note before detach, poll a completion artifact with
BOUNDED in-turn waiters. Budget ~37 h wall (single-thread-capped; #650). Frozen split hash `f1725bd81cd3eefa`.

## Compute-reduction levers (if a powered-but-cheaper run is wanted)
- fastest-K-laps-per-driver (K=2-3) cuts per-driver cost ~2-4x (fewer laps, still enough on-limit apexes).
- Persist a per-(session,driver) apex cache (parquet) so re-runs/experiments are free after the first pass.
- Cornering-dominated circuits first (Hungary/Monaco/Singapore/Spain) where `apex_pace` is strongest.
