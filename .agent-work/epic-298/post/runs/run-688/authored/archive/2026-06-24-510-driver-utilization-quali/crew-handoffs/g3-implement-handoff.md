# Implementer Handoff

## Gate
g3-implement (C1 #510, work-id 510-driver-utilization-quali, branch feat/c1-driver-utilization-510)

## Task
Build the **single canonical characterization run** for driver utilization, plus a traceable dashboard and a
recorded readiness verdict, and **consolidate the ideal-lap sim onto one path**. Three deliverables:

### (1) Canonical characterization entrypoint
A tested orchestration seam, e.g. `src/physics/utilization/characterize.py`, that for a list of `(year, gp_name,
driver)` cases:
- builds the constructor's **causal as-of car ceiling** via G1 `car_prior.build_car_ceiling(store_df, year,
  constructor, target_round, ...)`,
- loads the driver's realised best quali lap + ribbon the way `src/physics/sim_evaluator.py::evaluate_session`
  does (`session_fit.load_quali_session`, `session_fit.fit_session_full` for `.best_distance`/`.best_speed_real`,
  `ribbon.build_session_ribbon`),
- calls G2 `regime_utilization.estimate_driver_utilization(ceiling, track_df, driver_distance, driver_speed, ...)`,
- returns a tidy per-(driver, session) result (per-regime U_r + σ + consistency + n-points + `split_is_impure`).
Keep the data-loading (cache/DB) in a thin wrapper; keep the orchestration logic testable with injected seams
(so the smoke test does NOT touch the 38 GB cache).

### (2) Dashboard (traceable, reproducible)
`scripts/driver_utilization_dashboard.py` that runs the entrypoint over a **bounded representative subset** and
emits a traceable readout: raw store → car prior → per-regime utilization (with σ) → plotted figure(s) +
a CSV/markdown table. Output to `reports/physics/` (gitignored), `matplotlib.use("Agg")`, ASCII only.
**Subset (do NOT run the full field — it is a multi-hour re-fit sweep):** ~8–12 driver-sessions spanning
regime-mix and team strength, e.g. a slow/mechanical circuit (Monaco/Singapore/Hungary), a power/low-drag circuit
(Monza/Las Vegas/Spa), and a mixed circuit (Silverstone/Suzuka), across a strong team (Red Bull), a midfield team,
and a weak team (Williams/Haas). The prototype `scripts/ideal_vs_actual.py` CASES list is a good starting set.
Document the exact subset run. The entrypoint must be **capable** of the full 216-row sweep (resumable / a `--limit`
or case-list arg) even though this gate only runs the subset.

### (3) Single-path consolidation (the canonicalization decision)
The user decided: **canonicalize the ideal-lap sim path** (`PhysicsParameterSet → CapabilityEnvelope →
PhysicsSimulator`) and **retire the inline scalar quasi-static sim**. Today `scripts/ideal_lap_compare.py` holds an
inline `sim_lap` (quasi-static forward-backward) + a `_params` bridge prototype, and `scripts/ideal_vs_actual.py`
imports them. Resolve to ONE path:
- Remove/replace the inline `sim_lap` + `_params` so the ideal lap comes from the canonical
  `build_car_ceiling`/`CapabilityEnvelope`/`PhysicsSimulator` path. Either delete the two prototype scripts (their
  function is superseded by the new dashboard) **or** rewrite them to call the canonical entrypoint. After this gate
  there must be **no second inline ideal-lap sim** in `scripts/` and one canonical path. State which you did and why.
- If anything imported from those prototypes is still needed (e.g. `build_track`, `field_drivers`), relocate it to a
  proper module rather than leaving a diagnostic script as a library.

### (4) Readiness verdict
Write `.agent-work/510-driver-utilization-quali/VERDICT.md`: a **recommended** readiness verdict — **GO**
(trustworthy enough to become a feature), **CONTEXTUAL** (usable as a flagged readout, not a clean capability), or
**NO-GO** (documented negative result) — with the evidence behind it:
- **Coverage:** which circuits/teams/regimes the subset covered, and what is NOT covered (be honest — a subset is
  CONTEXTUAL-leaning unless the signal is unambiguous).
- **Separability:** do the per-regime utilizations separate drivers/teams in a physically sensible way (e.g. a known
  strong qualifier shows high utilization; regime profiles differ across circuits as expected)? Show the numbers.
- **Covariance honesty:** are the σ_U sane and do they widen where the ceiling is thin (few sessions, fallback
  channels)? Note the lap-sampling-σ omission (disclosed in G2).
- **The impure-split caveat** restated.
The verdict is a RECOMMENDATION; the Commander will bring it to the user for ratification. Do not over-claim.

### (5) Smoke test
`tests/unit/physics/test_driver_utilization_dashboard.py`: a fixture-backed smoke test of the entrypoint using a
TINY synthetic store + injected realised lap (NO live cache/DB), asserting the orchestration returns well-formed
per-regime rows. Keep it fast and deterministic.

## Protected Intent
A reproducible, traceable characterization that lands an HONEST verdict (a CONTEXTUAL or NO-GO with good evidence is
a valid, valuable outcome — do not inflate to GO), on ONE canonical sim path, without wiring anything into evo.

## Test Mode
Test-after allowed for the dashboard/orchestration glue; the smoke test is required and must be fixture-backed.
Physics evidence: the real-data run is the L4-flavoured field check; keep its outputs in `reports/` (gitignored).

## Close Criteria
- `src/physics/utilization/characterize.py` (tested seam) + `scripts/driver_utilization_dashboard.py` produce the
  per-regime utilization readout over the documented subset; figures + table in `reports/physics/`.
- The inline scalar sim is GONE; one canonical ideal-lap path remains; prototype scripts superseded/retired/rewritten.
- `.agent-work/510-driver-utilization-quali/VERDICT.md` written with a recommended GO/CONTEXTUAL/NO-GO + evidence.
- `tests/unit/physics/test_driver_utilization_dashboard.py` green (fixture-backed, no live cache).
- `py -m src.utils.simplification_limits` clean on touched src/ + tests/ paths.

## Allowed Scope
NEW: `src/physics/utilization/characterize.py`, `scripts/driver_utilization_dashboard.py`,
`tests/unit/physics/test_driver_utilization_dashboard.py`, `.agent-work/510-driver-utilization-quali/VERDICT.md`,
`reports/physics/*` (gitignored outputs). MODIFY/RETIRE: `scripts/ideal_lap_compare.py`,
`scripts/ideal_vs_actual.py` (consolidation). Reading/reusing: `car_prior.py`, `regime_utilization.py`,
`sim_evaluator.py`, `physics_simulator.py`, `ribbon.py`, `session_fit.py`, `estimate_store.py`.

## Specific Exclusions
- Do NOT run the full 216-row sweep (multi-hour). Bounded subset only.
- Do NOT modify G1 `car_prior.py` or G2 `regime_utilization.py` (consume them; if a real defect blocks you, STOP and
  report).
- Do NOT wire anything into evo; no evo-region import.
- Do NOT commit reports/ artifacts or the 38 GB cache; reports/ is gitignored.

## Constraints
- `constraint:physics_region_no_evo_import`. Single canonical execution path (the inline scalar sim must be retired).
- DB-only for analysis; offline FastF1 cache (`data/telemetry`) for telemetry; absolute paths to untracked data.
- Generated dashboard artifacts are derived (out of git). `py` not `python`. Validate public inputs.
- Honest covariance + verdict must be evidence-backed; no over-claim.

## Map Anchors (inbound)
- **Structural:** `struct:physics` (canonical entrypoint + dashboard); `scripts/ideal_vs_actual.py`,
  `scripts/ideal_lap_compare.py` (prototypes to supersede); `src/physics/utilization/*` (G1+G2);
  `data/physics_estimates.db` (store), `data/telemetry` (cache).
- **Capability:** driver utilization measurement → characterization dashboard + readiness verdict.
- **Constraints:** single canonical execution path; DB-only / offline-cache telemetry; derived artifacts out of git.
- **Decision anchors:** `decision:ideal_lap_sim_two_sided_evaluator` — its Review Trigger fires; the verdict consumes
  the sim-vs-real gap as the driver signal. The single-path canonicalization is the user's decision (this gate
  enacts it).
- **Evidence expectations:** reproducible dashboard (raw → plotted) + fixture smoke test green; VERDICT.md
  GO/CONTEXTUAL/NO-GO with coverage + separability + covariance-honesty evidence.

## Data Locations (untracked — absolute paths)
- Estimate store: `C:/Programs/f1Brainz/data/physics_estimates.db` (216 rows, year=2023, session Q, status ok).
- FastF1 offline cache: `C:/Programs/f1Brainz/data/telemetry` (38 GB).
- Output dir: `C:/Programs/f1Brainz/reports/physics/` (gitignored).
- The prototype scripts define `_CACHE = data/telemetry`, `_DB = data/physics_estimates.db`, `_OUT = reports/physics`.

## Required Evidence
- `py -m pytest tests/unit/physics/test_driver_utilization_dashboard.py -q` (green).
- `py -m src.utils.simplification_limits --paths <touched>` (clean).
- The dashboard run log (subset cases, output file paths) + the VERDICT.md content.
- A statement of the single-path consolidation (what was retired/rewritten; proof no inline sim remains).

## Verification Commands
```bash
py -m pytest tests/unit/physics/test_driver_utilization_dashboard.py -q
py -m src.utils.simplification_limits --paths src/physics/utilization/characterize.py scripts/driver_utilization_dashboard.py tests/unit/physics/test_driver_utilization_dashboard.py
# real-data dashboard (bounded subset) — run once, keep outputs in reports/ (gitignored):
py scripts/driver_utilization_dashboard.py   # (with whatever subset/limit arg you implement)
```

## Suggested Model Tier
Stronger-ish: the canonicalization (retiring the inline sim cleanly), the bounded real-data run, and the
evidence-backed verdict reasoning carry the risk.

## Authority
Decided (do not relitigate): canonicalize the ideal-lap sim path and retire the inline scalar sim; bounded subset
(not full sweep) for this gate; verdict is a RECOMMENDATION the Commander ratifies with the user. You may decide:
the exact subset (document it), the dashboard layout, the entrypoint's full-sweep arg shape, retire-vs-rewrite of
the prototype scripts, and the recommended verdict (with honest evidence).

## Stop Conditions
Stop and return if: allowed scope must be exceeded; a real defect in G1/G2 blocks the run; the real-data run cannot
complete in bounded time even on a small subset (report what you got); or retiring the inline sim would break a
consumer you cannot relocate cleanly.

## Return Format
Return IMPLEMENTER_RESULT to `.agent-work/510-driver-utilization-quali/crew-handoffs/g3-implement-result.md`:
completed slice, files changed (incl. retired/rewritten prototypes), test mode satisfied, evidence (pasted pytest +
simplification_limits + dashboard run log), the recommended verdict + its evidence summary, the single-path
consolidation statement, assumptions, stop conditions, out-of-scope observations, Workflow Feedback.
