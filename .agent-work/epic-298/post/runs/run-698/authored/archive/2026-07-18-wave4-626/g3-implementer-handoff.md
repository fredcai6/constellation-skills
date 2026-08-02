# Implementer Handoff

## Gate
`g3` — Layer 2: structured within-session evolution (smooth grip latent for track rubbering-in) with σ + an honest identifiability test. THIS IS THE CRUX GATE — an honest "unidentifiable, float" is a valid, valuable outcome.

## Task
Build `src/physics/weekend_state/layer2_evolution.py`: a SMOOTH grip latent over session time capturing track rubbering-in (the F9 foot-gun a weekend-constant field median hides — cars qualify at different track-rubbering states), carrying honest σ. Then TEST honestly whether it earns its keep, and REPORT the truth.

## Key data facts (verified this run — use them, they change the framing)
- `damage_integrals.db:grip_bin_obs` HAS **Q-session** rows (14,968), NOT only race — so you can build the within-session grip-evolution curve on ACTUAL qualifying (`session_type='Q'`), materially reducing (not eliminating) the race-vs-Q domain gap. Columns: per (year,gp,session,driver,stint,lap,bin) `mu_lat_p90`/`mu_comb_p90` (grip), `tyre_life`, `mass_kg`, `rho`, `v_mean`, `n_samples`.
- BUT grip_bin_obs only covers **2023 and 2024**. The physics-estimates Q store spans 2019–2026. So Layer 2's within-session latent is IDENTIFIABLE only on 2023–2024; elsewhere it must be a WIDE-σ prior (near-zero mean, honest uncertainty), NOT a fabricated value. State this coverage limit loudly.
- `damage_lap_integrals.cumulative_track_laps` (join on year,gp,session,driver,stint,lap) is the track-rubbering proxy (accumulated laps on track = rubber laid). Within a Q session its range is short (few laps) vs a race — the within-Q rubbering signal is SMALL and confounded with `tyre_life` (fresh→used) and `mass_kg`. You must control for tyre_life + mass to isolate the track-evolution component.
- Absolute path: `C:/Programs/f1Brainz/data/damage_integrals.db`.

## What to build
- A smooth latent (GP or penalized/smoothing spline) modeling grip vs a within-session time axis (cumulative_track_laps, or session-clock proxy) PER WEEKEND, controlling for tyre_life + mass, with honest σ — the "track state improved by Δ grip across the session" curve. This is a FIELD-LEVEL / track property (shared across cars), not a per-car signal.
- An `apply` path that uses this latent to adjust the Q weekend-state decomposition where identifiable (2023-24), and falls back to a wide-σ near-zero prior elsewhere.

## Protected Intent (F5 — the trap to avoid)
A **season-time** smooth track/conditions latent is NOT a valid Layer-2 analog — that is Layer 3's OWN trajectory axis, and filling Layer 2 with a season-time curve DOUBLE-COUNTS Layer 3. Layer 2 MUST be a genuinely WITHIN-session signal. **If the only reachable signal turns out to be season-time (i.e. the within-session rubbering signal is not identifiable from grip_bin_obs), DECLARE Layer 2 unidentifiable-at-this-granularity and STOP-and-return a FLOAT** (report the held-out evidence) — do NOT fill it with a season-time latent, do NOT fake an in-sample win.

## Honest test (mandatory — this is the deliverable as much as the layer)
1. **Does it earn its keep?** Whether removing this layer reduces HELD-OUT car-signal noise, via OUT-OF-SAMPLE / LOO prediction (lesson:loo-residual-diagnostic — a self-weighted smoother pins predictions to their own value and is structurally blind to the σ-over-claim it must detect; use leave-one-out / train-test, never self-inclusive). Use the g1 frozen held-out split (`holdout.py`) and g1 `floor.py` metric.
2. **Orthogonality check:** confirm the L2 within-session latent is NOT collinear with the L3 season trajectory (compute the correlation / shared variance between the L2 latent series and a season-time trend). High collinearity ⇒ confounded, not identified ⇒ that is a float, not a pass.
- If Layer 2 cannot be identified / cannot earn its keep on held-out data: REPORT it with the held-out numbers (a verdict finding + a FLOAT per Pre-Ruling 2). This is a COMPLETE, valuable outcome — the honest null is explicitly accepted. Do NOT silently drop the layer and do NOT manufacture a win.

## Test Mode
Test-after allowed. The load-bearing tests are the LOO identifiability harness + the orthogonality check.

## Close Criteria
- `layer2_evolution.py` fits a within-session smooth grip latent (2023-24 Q identifiable region) with honest σ + a wide-σ fallback prior elsewhere; the coverage limit is explicit in code + result.
- The identifiability test is genuinely OUT-OF-SAMPLE (LOO / train-test on g1's split), not self-weighted.
- The orthogonality-vs-L3-season-trajectory check is computed and reported.
- The result states honestly whether Layer 2 earns its keep, or is unidentifiable → float, WITH the held-out numbers.
- `test_layer2_evolution.py` passes (smoother fit + LOO harness + orthogonality); a test asserts the LOO path is not self-inclusive and the fallback is wide-σ.
- No evo import; no `data/*.db` staged.

## Allowed Scope
`src/physics/weekend_state/layer2_evolution.py`; `tests/unit/physics/weekend_state/test_layer2_evolution.py`. MAY read g1 (`frame`,`floor`,`holdout`) and g2 (`layer1_physics`).

## Specific Exclusions
Do NOT build Layers 3/4 (g4). Do NOT modify g1/g2 files, estimator, evo, config. Do NOT commit/modify `data/*.db`.

## Constraints
- Python `py`. Absolute DB paths into `C:/Programs/f1Brainz/data/*`.
- LOO/out-of-sample discipline is MANDATORY for the smoother diagnostic (lesson:loo-residual-diagnostic).
- `constraint:physics_region_no_evo_import`. Layer carries explicit σ.
- Do NOT fabricate values outside the 2023-24 identifiable region — wide-σ prior only.

## Map Anchors (inbound)
- Structural: `layer2_evolution.py` (NEW); `damage_integrals.db:grip_bin_obs` (Q rows, 2023-24) + `damage_lap_integrals.cumulative_track_laps`.
- Capability: within-session track-evolution grip latent with σ.
- Constraints: LOO/out-of-sample smoother diagnostic; no evo import.
- Decision: DC1 — build+test+report; FLOAT if fundamentally unidentifiable or season-time-collinear (Pre-Ruling 2 / F5).
- Confidence flag: DC1 data-granularity + 2023-24-only coverage — verify identifiability, surface to Admiral if unidentifiable.

## Deliverable Path Check
- Committed: `src/physics/weekend_state/layer2_evolution.py`, its test (not gitignored). Untracked until staged.

## Required Evidence
- `py -m pytest tests/unit/physics/weekend_state/test_layer2_evolution.py -q` → pass.
- The held-out LOO result: does removing Layer 2 change held-out car-signal noise, with numbers.
- The orthogonality-vs-season-trajectory number.
- Explicit statement: earns-its-keep / unidentifiable-float, with the coverage caveat.

## Verification Commands
```bash
cd C:/Programs/f1-626
py -m pytest tests/unit/physics/weekend_state/test_layer2_evolution.py -q
```

## Suggested Model Tier
Stronger — identifiability reasoning, the season-time confound trap, and the honest-null/float judgment are the hardest reasoning in the whole run.

## Authority
Build+test+report is frozen. You MAY conclude "unidentifiable → float" (that is sanctioned and valuable). You may NOT fill Layer 2 with a season-time latent to force a pass, and may NOT drop the layer silently.

## Stop Conditions
Stop and return a FLOAT (in the result, clearly marked FLOAT-TO-ADMIRAL) if: the within-session signal is not identifiable from grip_bin_obs, or it is collinear with the L3 season trajectory, or the 2023-24-only coverage makes held-out evaluation impossible on the frozen split. Report the held-out evidence that led you there.

## Return Format
Return IMPLEMENTER_RESULT to `.agent-work/wave4-626/g3-implementer-result.md`: completed slice (or float), files changed, test output, the LOO held-out numbers, the orthogonality number, the coverage caveat, the honest earns-keep/float verdict, assumptions, stop conditions, out-of-scope observations, workflow feedback.
