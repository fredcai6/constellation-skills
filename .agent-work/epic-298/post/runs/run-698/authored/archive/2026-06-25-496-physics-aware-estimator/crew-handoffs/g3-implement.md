# Implementer Handoff — G3 Synthesis + Land (M7 + M3)

## Gate
g3-implement (work-id 496-physics-aware-estimator, branch `feat/physics-aware-estimator-496`, MAIN checkout)

## Task
Productionize the **M7+M3 synthesis** into one coherent, single-canonical-path longitudinal
estimator in `src/`, with honest covariance and L1–L4 evidence, and PROVE it on the G1 scoreboard:
it must pass BOTH acceptance circuits at once (deep Bahrain knee AND Monaco ring_ok) without
regressing Belgium. This is the composition the G2 portfolio bet on.

## The synthesis (what to build)
A **decoupled 1D physics-constrained longitudinal filter** (M3) whose soft acceleration observation
is the **TV-denoised raw `a_long`** (M7), tightly coupled on the braking arc. Concretely:
- **Backbone = M3** (`.agent-work/496-physics-aware-estimator/spikes/m3/filter_m3.py`): the 1D
  Kalman-RTS smoother on state `[v, a]` with regime-dependent jerk process variance. It owns
  `a_long`; the 2D `StintSmoother` keeps geometry only. A 1D filter has NO 2D position coupling →
  Monaco ringing structurally vanishes (spike: 13.1 → 2.97, ring_ok). KEEP this property.
- **Observation = M7** (`.agent-work/496-physics-aware-estimator/spikes/m7/m7_tv_filter.py`): the
  edge-preserving TV/IRLS denoise of `inp.a_long_raw` (preserves the brake-onset step, kills sensor
  noise). Feed the DENOISED `a_long` as M3's soft accel obs (`a_soft_obs`), with a TIGHT
  `sig_a_soft` on braking-arc samples (incl. the ONSET SAMPLE — the raw −52 peak is the FIRST
  sample of each braking run; do NOT trim it) and loose elsewhere.
- **The crux:** in the M3 spike, `sig_a_soft = 35*3 = 105` was too loose to deepen Bahrain (knee
  stayed −39). Tightening the coupling on the (TV-denoised) braking arc is what should pull the knee
  to the raw −52 WITHIN the 1D filter (which does not ring). Tune `sig_a_soft` (braking vs other),
  the TV `lam`, and the jerk process variance so the scoreboard passes both circuits.
- **Ride-along levers (use only if they help the scoreboard, and only intentionally):** M8's
  positive-`a_long` safety clip in non-throttle (`spikes/m8/`), M4's onset detector
  (regime ∪ `dv/dt`) for anchor placement (`spikes/m4/`). Do not add them if M3+M7 alone passes.

## Protected Intent
A per-session MEASUREMENT improvement (not a predictor). It must (a) recover the real heavy-braking
knee, (b) not ring, (c) carry honest covariance, (d) be ONE canonical path. The downstream consumer
is the under-calling C1 ceiling (#518) and the braking/lateral frontier fits.

## Test Mode
TDD where pure (the TV denoise, the 1D filter kernel, the synthetic-step recovery). Test-after for
the real-session scoreboard parity (needs the cache).

## Close Criteria (each proven)
- A new module `src/physics/layer2/decoupled_longitudinal.py` (name negotiable) exposing:
  - the 1D physics-constrained longitudinal filter returning `a_long` AND its per-sample variance
    (honest covariance: the filter's smoothed `P[1,1]` → `sigma_a`); NEVER a point estimate without σ.
  - a `VariantFn` (e.g. `variant_synthesis`) consuming `CaseInputs` (the G1 scoreboard seam) so it
    is measured identically to the baselines.
  - the TV-denoise helper (edge-preserving) and the onset-aware tight-coupling logic.
- **Scoreboard proof** (`run_scoreboard` on `[(2023,"Bahrain","VER"),(2023,"Monaco","VER"),(2023,"Belgium","VER")]`,
  cache `C:/Programs/f1Brainz/data/telemetry`), reported for `synthesis` + `gaussian` + `kind3`:
  - **Bahrain:** `knee_gap_vs_raw` materially smaller than baseline +12.7 (target ≤ ~2–3 m/s²).
  - **Monaco:** `ringing_ok == True` (`ringing_over_ceiling ≤ 0`).
  - **Belgium:** knee not worse than the `kind3` baseline (−37.4) by more than ~0.5 m/s².
  - If it CANNOT pass all three at once, report the best honest configuration + exactly what
    trades off — that is a CONTEXTUAL finding for G4, not a thing to fake (set-aside allowed).
- **L1–L4 evidence:**
  - L1 analytical: synthetic known sharp-decel step → recovered knee within tolerance (adapt M3's
    `synthetic_sanity_check`).
  - L2 invariant: covariance positive-definite / σ_a finite > 0 everywhere; TV denoise preserves a
    known step edge (edge-preservation unit test).
  - L3 limit: with the anchor coupling → ∞ loose, reduces toward the speed-only baseline; with σ→0
    tight, `a_long` tracks the (denoised) raw on the braking arc.
  - L4 benchmark: the scoreboard parity above (the 3-circuit table).
- `tests/unit/physics/layer2/test_decoupled_longitudinal.py` covering the pure kernels (TV denoise,
  1D filter, synthetic recovery, covariance positivity). Green.
- No layer2 regressions: `py -m pytest tests/unit/physics/layer2 -q`.
- `py -m src.utils.simplification_limits --paths <new files>` clean.
- `constraint:physics_region_no_evo_import` honored.

## Allowed Scope
- NEW `src/physics/layer2/decoupled_longitudinal.py` + its test.
- You MAY add a `variant_synthesis` registration usable by `scripts/validate_refine_505.py` or a
  small driver under `scripts/` to emit the proof table + a dashboard plot to `reports/physics/`.
- You MAY read (not modify) the preserved spike code and the existing smoother/accel_obs/braking_view.

## Specific Exclusions
- Do NOT wire the new estimator into production `braking_view` / the capability ceiling / evo — this
  gate is MEASURED-not-wired (the wiring + C1 re-eval is the gated follow-on #518). Producing the
  estimator + the proof + the retire-assessment is the deliverable.
- Do NOT replace the 2D `StintSmoother` or do a full joint collocation (rejected: evolutionary only).
- Do NOT pull in #499 (CdA naming) or #504 (smoother split) unless genuinely required — if you do,
  flag it as an intentional, tracked choice in the result (per the user's opportunistic-if-intentional rule).

## Constraints
- `py` launcher. Single canonical path — no dual estimators/shims without a tracked exit.
- Honest covariance is first-class (σ_a per sample).
- Physics L1–L4 with units/bounds/invariants explicit (`a_long` signed m/s², decel negative).
- `decision:two_cycle_external_anchor_design`: the anchor magnitude must be the TV-denoised RAW
  `a_long` (an edge-preserving transform of raw only — NEVER re-read from a smoothed trajectory).
  Onset-arc placement EXTENDS the plateau-only invariant — document this extension and why it stays
  external & un-biased (it is the decision candidate this gate surfaces).
- `decision:smoother_rounds_braking_knee`: moving `a_long` to a decoupled 1D filter (speed is the
  only good longitudinal observable) is consistent with this anchor — record the new decision candidate
  "longitudinal a_long from a decoupled 1D filter fed by the raw-onset anchor, not the 2D smoother".

## Map Anchors (inbound)
- **Structural:** `struct:physics.layer2` (new module); reads `struct:preprocessing.trajectory`
  (smoother, AccelObs), `braking_view.clean_longitudinal_from_raw`, scoreboard seam.
- **Capability:** `purpose:physics_estimation` — braking/lateral frontier inputs stop under-calling.
- **Constraints/decisions:** `decision:two_cycle_external_anchor_design`,
  `decision:smoother_rounds_braking_knee`, `constraint:physics_region_no_evo_import`.
- **Evidence:** scoreboard passes Bahrain+Monaco+Belgium together; honest covariance; L1–L4.
- **Confidence flag:** physics packet Open Question (trajectory consumption bypasses the artifact
  boundary). Do NOT silently re-plumb loaders; if you touch them, flag to Triage.

## Required Evidence
- `py -m pytest tests/unit/physics/layer2/test_decoupled_longitudinal.py -q` (green).
- `py -m pytest tests/unit/physics/layer2 -q` (no regressions).
- The 3-circuit scoreboard proof table (synthesis + gaussian + kind3; knee/gap/ringing/ring_ok).
- The synthetic-step L1 recovery numbers.
- `py -m src.utils.simplification_limits --paths <new files>` PASS.
- A short retire-assessment of `clean_longitudinal_from_raw` (can the synthesis replace it as the
  braking-capability input? deciding numbers) — for the G4 verdict.

## Verification Commands
```bash
py -m pytest tests/unit/physics/layer2/test_decoupled_longitudinal.py -q
py -m pytest tests/unit/physics/layer2 -q
py -m src.utils.simplification_limits --paths src/physics/layer2/decoupled_longitudinal.py tests/unit/physics/layer2/test_decoupled_longitudinal.py
# plus your scoreboard-proof driver
```

## Suggested Model Tier
stronger (Opus) — heaviest gate: composes two mechanisms, lands real covariance-bearing code, tunes
to pass two competing acceptance circuits, full L1–L4.

## Authority
The winner set (M7+M3) and the evolutionary constraint are decided (user). You decide the module
internals, HP tuning, and exact composition. You may NOT: wire into production/evo, replace the 2D
smoother, or claim GO if the scoreboard does not pass both circuits (report honestly → CONTEXTUAL).

## Data Locations (absolute — main checkout)
- FastF1 telemetry cache: `C:/Programs/f1Brainz/data/telemetry` (2023 cached).
- Preserved spike reference code: `C:/Programs/f1Brainz/.agent-work/496-physics-aware-estimator/spikes/{m3,m7,m4,m8}/`.

## Stop Conditions
Stop and return if: the composition cannot pass both circuits even after honest tuning (return the
best config + the tradeoff as a CONTEXTUAL finding), a needed seam is missing, allowed scope must be
exceeded, or a decision outside this authority is needed.

## Return Format
Return IMPLEMENTER_RESULT to `.agent-work/496-physics-aware-estimator/crew-handoffs/g3-implement-result.md`:
completed slice, files changed, test mode satisfied, the scoreboard proof table, L1–L4 evidence, the
covariance treatment, the two-cycle-invariant extension statement, the decoupled-longitudinal
decision candidate, the clean_longitudinal_from_raw retire-assessment, assumptions, stop conditions,
out-of-scope observations, and Workflow Feedback.
