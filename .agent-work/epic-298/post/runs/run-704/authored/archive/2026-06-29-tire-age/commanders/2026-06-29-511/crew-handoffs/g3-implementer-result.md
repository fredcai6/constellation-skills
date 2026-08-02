# Implementation Result — G3 separation (f_tyre vs g_track)

Status values follow `skills/workbench/references/status-model.md`.

## Assigned gate
`g3` — issue #511 W3 tyre-age capstone: the subtle separation (f_tyre vs g_track).

## Completed slice
A new evo-free module that separates per-compound tyre decay `f_tyre(compound, age)` from
within-weekend track evolution `g_track`, over the populated 1,040-stint
`race_stint_estimates` store (2023), in the crossed log-grip model

    grip_axis(stint) = car_envelope(driver→constructor, gp)   [FIXED, from quali, relative]
                       + f_tyre(compound) = base + decay k     [TARGET]
                       + g_track(gp, cumulative_track_laps)     [per-circuit slope, partial-pooled]
                       + noise

Per-axis VECTOR built: **lateral_mech** (primary), **lateral_aero** (honest-null), **traction**
(speculative). Season-pooled per-compound `k` via `pooling.pool_random_effects` with a
STRUCTURAL-ONLY monotone prior (`k_SOFT ≥ k_MEDIUM ≥ k_HARD`, `k ≥ 0`); per-circuit g_track
slope shrunk via `pool_random_effects`; car anchored RELATIVE (centred) from the quali
`session_estimates` store. Identifiability diagnostic + leave-one-circuit-out LOO for every
residual/stability number.

## Scope
**Files changed:**
- `src/physics/layer2/tyre_separation.py` (new, 525 lines)
- `tests/unit/physics/layer2/test_tyre_separation.py` (new)
- `.agent-work/511/g3-implementer-plan.json` (my own engine plan)

**Specific exclusions touched:** `no` — W2 modules, the quali path, `pooling.py`, and both
stores are untouched (read-only). No evo import. No `.db` written or committed (canonical DBs
opened `file:…?mode=ro`).

## Behavior changed
`yes` — new measured axis: a per-compound tyre-decay / track-evolution separation over the
race-stint store. No existing behaviour altered (additive new module + test only).

## Map Impact
- **Structural anchors touched:** `struct:physics.layer2` — new leaf `tyre_separation.py`;
  consumes the `pooling.py` seam (`pool_random_effects`) and reads both stores read-only.
- **Capabilities added/changed/affected:** `purpose:physics_utilization` — first
  cross-session decomposition of tyre decay vs track evolution from the race-stint store
  (a Phase-C MEASURED-not-wired output).
- **Constraints/assumptions touched:** `constraint:physics_region_no_evo_import` honored
  (imports: `__future__, dataclasses, json, numpy, pandas, sqlite3, typing,
  src.physics.layer2.pooling`); `lesson:loo-residual-diagnostic-over-self-weighted-predictor`
  honored (leave-one-circuit-out for every residual/stability/covariance number).
- **Decision candidates:** the W3 crossed log-grip model + the net-new within-weekend
  `g_track` term (a new pooling structure: per-circuit slope on `cumulative_track_laps`,
  partial-pooled). Surface to Cartographer as a measured-axis decision.
- **Claims/evidence produced:** lateral tyre decay separates cleanly and monotonically;
  fresh-grip base does NOT separate by compound; see Evidence below.
- **Triage candidates:** see Out-of-scope observations.

## Test mode
**Required:** `test-after` (handoff: test-after acceptable; load-bearing test is the
planted-recovery synthetic).
**Satisfied:** `yes` — planted-recovery synthetic recovers planted base, k, and track slope
within tolerance; monotone-prior-enforced test; default-prior-is-no-op (anti-circular) test;
honest-null + LOO + coverage-collapse + bad-axis tests; evo-free AST test. 9/9 green.

## Evidence

### Block 1 — planted-recovery + full unit suite (green)
```bash
py -m pytest tests/unit/physics/layer2/test_tyre_separation.py -q
```
**Result:** pass — `9 passed in 0.27s`.
Covers: `test_planted_recovery_lateral` (base/k/track recovered within tol, separates=True),
`test_car_removal_beats_naive` (car-confounded-with-compound: removing the quali car anchor
beats the naive per-compound mean), `test_monotone_prior_enforced` (planted inversion forced
monotone), `test_default_prior_is_noop_anticircular` (default bakes no magnitude; injected
tight prior moves k), `test_lateral_aero_honest_null`, `test_loo_diagnostic_present_and_stable`,
`test_coverage_collapse_returns_honest_null`, `test_bad_axis_raises`, `test_module_is_evo_free`.

### Block 2 — evo-free assertion (paste)
```bash
py -c "import ast,sys; src=open('src/physics/layer2/tyre_separation.py').read(); \
mods=[n.module or '' for n in ast.walk(ast.parse(src)) if isinstance(n,ast.ImportFrom)]+\
[a.name for n in ast.walk(ast.parse(src)) if isinstance(n,ast.Import) for a in n.names]; \
bad=[m for m in mods if 'evo_predictor' in m or 'latent_power' in m or 'compound_prior' in m]; \
print('EVO-FREE FAIL',bad) or sys.exit(1) if bad else print('evo-free ok')"
```
**Result:** pass — `evo-free ok`.
Imports: `['__future__','dataclasses','json','numpy','pandas','sqlite3','src.physics.layer2.pooling','typing']`.

### Block 3 — simplification_limits (clean)
```bash
py -m src.utils.simplification_limits --paths src/physics/layer2/tyre_separation.py tests/unit/physics/layer2/test_tyre_separation.py
```
**Result:** pass — `PASS (2 files checked)`. (file < 1000 lines, all functions < 100 lines, CC < 20.)

### Block 4 — real-data smoke (1,040-stint store, read-only)
```bash
py -c "from src.physics.layer2.tyre_separation import separate_all, summarize; \
res=separate_all('C:/Programs/f1Brainz/data/race_stint_estimates.db','C:/Programs/f1Brainz/data/physics_estimates.db',year=2023); ..."
```

**lateral_mech (PRIMARY)** — n=923 dry-lateral stints (HARD 369 / MEDIUM 367 / SOFT 187):
- Per-compound pooled lateral **k MONOTONE-UP**:
  `HARD 0.001213 (σ 1.19e-4) < MEDIUM 0.002729 (σ 2.36e-4) < SOFT 0.003271 (σ 3.94e-4)`.
- Per-compound base (contrast vs HARD, log space): `{HARD 0, MEDIUM 0, SOFT 0}` ENFORCED;
  **raw WLS contrasts were MEDIUM −0.0032, SOFT −0.0508** (softer = lower age-0 grip), clipped
  to 0 by the monotone+non-negative prior → base is genuinely null/inverted, not just clamped.
- `g_track` pooled slope = **+0.00749 log-grip per 100 cumulative track laps** (rubber-in),
  τ=0.00097 (small genuine circuit spread); per-circuit shrunk slopes span Bahrain 0.00724 ..
  Qatar 0.00765; **Mexico flagged thin (4 stints) and shrunk to the pooled mean (0.00749)**.
- IDENTIFIABILITY: cond(XᵀWX)=1050.5, **max |base↔track corr| = 0.191 (LOW) → separates=True**.
  Variance fractions: circuit 0.481, noise 0.343, car 0.159, track 0.013, tyre_base 0.004.
- LOO (leave-one-circuit-out, 20 folds): oos_rmse 0.1886 ≈ in_sample_rmse 0.1886 (honest, no
  overfit); k-stability (std across folds) HARD 6.2e-5 / MEDIUM 1.3e-4 / SOFT 2.8e-4 → **very stable**.

**traction (SPECULATIVE)** — n=879:
- k MONOTONE-UP: `HARD 0.001491 < MEDIUM 0.005548 < SOFT 0.007754`, LOO-stable (≤9.1e-4).
- separates=True (cond 265, alias 0.215) BUT base honest-null (noise var 0.659; oos_rmse 0.79
  in log space ≈ 2.2× scatter) → the decay ladder holds, the level does not.

**lateral_aero (HONEST-NULL)** — `b_aero ≈ 0` in 572/923 stints; everything ≈0, no decay axis.
Honest-null confirmed.

## Per-axis separation finding (the core deliverable)
- **LATERAL (primary): the DECAY axis separates CLEANLY.** Per-compound lateral `k` is
  monotone-up, well-conditioned (cond 1050), low tyre↔track aliasing (0.19), and LOO-stable
  (fold std ≤ 2.8e-4). The pit-staggered fleet identifies tyre vs track: multiple compounds
  run at overlapping `cumulative_track_laps`, and the same compound runs across different track
  states → base/slope aliasing stays at 0.19. **The fresh-grip BASE does NOT separate by
  compound** — raw SOFT contrast is −0.05 (i.e. softer shows slightly *lower* age-0 grip, an
  extrapolation artifact since soft tyres run short), pinned to 0 by the structural monotone
  prior. So the compound signal lives in the **decay rate, not the age-0 level** — a physically
  honest, anti-circular result (no #443 magnitudes used).
- **TRACTION (speculative): k separates (monotone, LOO-stable) but the level is honest-null**
  (66% residual variance) — confirms "a stretch".
- **g_track is a real, small, positive within-weekend rubber-in slope** (+0.75% grip / 100
  laps on lateral), cleanly partitioned from tyre (1.3% of variance vs the 48% circuit
  intercept), Mexico down-weighted.

## Docs/contracts touched
- `none` — new internal measured module; no committed schema/contract changed. The result
  dataclasses (`AxisSeparation`, `CompoundEffect`, `TrackEvolution`, `Identifiability`,
  `LOODiagnostic`) are the module's own API surface; `summarize()` gives a report-friendly view.

## Assumptions
- `lateral_g0` / `traction_a0` are the age-0 intercept of `p0·exp(−k·age)+b_aero·v²`
  (confirmed in `stint_estimator.py`: "p0 = grip at the age reference", age is ABSOLUTE
  tyre_life) → the base is already age-normalized; no per-stint age confound in the base.
- The crossed model works in **log-grip** for the multiplicative axes (lateral_mech,
  traction; both >0); **linear** for the additive aero term.
- The quali car anchor is used as a **fixed relative offset** (centred per quali session in
  the same space). The absolute quali-vs-race grip-level difference is absorbed by the
  per-circuit intercept. The relative *spread* is assumed comparable between quali and race;
  if quali pushes harder than race, car_rel slightly over-corrects (an accepted handoff design
  trade — anchor from quali, do not re-fit car from race noise).
- `cumulative_track_laps` is scaled by 100 inside the design so the slope is "per 100 laps"
  and `cond(XᵀWX)` is well-conditioned (numerical only; variance fractions unchanged).
- Compound base is identified relative to HARD (reference contrast); monotone enforced by
  precision-weighted isotonic (PAVA) projection.

## Stop conditions hit
- `none`. A non-evo separation IS possible; coverage supports per-compound LATERAL pooling
  (369/367/187); structural-only priors close it (NO #443 magnitudes were needed — the
  anti-circular line held); no W2/pooling/store modification was required.

## Out-of-scope observations
- **Base genuinely inverts (raw SOFT −0.05).** Worth a triage note: the age-0 fresh-grip
  *level* is not a clean compound discriminator from race stints (soft tyres are rarely run
  fresh-and-long, so the `g0` intercept is a noisy extrapolation). The decay `k` is the robust
  discriminator. Phase-P should carry the per-compound **k vector**, not a fresh-grip base.
- **Traction base is honest-null** (a0 spans 1e-6..160; 66% residual variance). If traction is
  wanted beyond decay, the per-stint traction_a0 fit quality needs attention (→ #557 territory).
- Quali has 22 GPs, race 20 GPs — the 2 quali-only GPs simply don't join; benign.
- The `separates` boolean keys off the tyre↔track alias correlation (the actual pit-stagger
  question), with `cond` reported as numerical context — a raw condition number alone would
  mislabel a well-identified fit as aliased.

## Workflow Feedback
- **Handoff gaps:** The handoff said "Read-only via `RaceStintStore(...).load(...)`", but
  `RaceStintStore.__init__` runs `CREATE TABLE IF NOT EXISTS` on construction — i.e. it opens
  the canonical DB in WRITE mode (idempotent, but not read-only). To honor CREW_CONTEXT
  ("open canonical DBs read-only `file:…?mode=ro`") I read via a small `mode=ro` SELECT helper
  that mirrors the store's JSON-decode, rather than instantiating the store. The handoff should
  either bless the `mode=ro` read path or note the store-construction write.
- **Context rediscovered:** The lateral/traction model form (`g0` = grip at *age 0*, not at
  `tyre_life_start`) was load-bearing for the no-age-confound argument and was only in
  `stint_estimator.py`'s docstring; the handoff's "lateral_g0 (grip at the age reference)" was
  ambiguous about whether the reference is 0. Worth stating explicitly in future W3 handoffs.
- **Context rediscovered:** The handoff's level note ("quali ~3.2 g vs race ~2.0 g") disagreed
  with the store (quali mean 2.77, race g0 median 3.17). It didn't matter (car anchor is used
  centred/relative, so absolute level is irrelevant), but the conflicting numbers cost a
  verification pass to resolve.
- **Instructions improvised around:** `pooling.py` has no within-weekend term (as flagged); I
  built `g_track` as a per-circuit WLS slope on `cumulative_track_laps` partial-pooled via
  `pool_random_effects` — within the handoff's "build a lightweight one" latitude.
- **What would have made this easier:** Pre-state in the handoff that the per-compound signal
  is expected in DECAY (k), not the age-0 base — the raw base inversion looked like a bug until
  the model form confirmed it is physically expected.

## Return status
`complete`
