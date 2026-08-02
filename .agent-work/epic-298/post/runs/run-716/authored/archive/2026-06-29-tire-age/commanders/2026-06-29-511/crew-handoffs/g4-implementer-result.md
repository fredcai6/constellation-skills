# Implementation Result — G4 supplant scoring + per-axis verdict rubric

Status values follow `skills/workbench/references/status-model.md`.

## Assigned gate
`g4` — issue #511 W3 tyre-age capstone: the SUPPLANT test (does physics μ_tyre(age) carry
real per-(race,compound) degradation-ordering signal vs the incumbent lap-time estimators?).

---

## REWORK (truth reshape) — Admiral-ratified, this is the current result

The first pass BLOCKED the real-data verdict: the handoff's per-stint `lap_time ~ tyre_life`
truth is fuel-confounded and inverts the compound ordering. The Admiral ratified the
fuel-corrected reshape; the commander refined the verdict to a cross-modal criterion. This
section is the authoritative outcome; the original-pass detail is retained below for audit.

### Completed slice (rework)
- `build_truth_cells` now computes the FUEL-CORRECTED truth: per race it fits, by OLS,
  `lap_time ~ driver_fixed_effects + fuel·lap_number + Σ_compound (k_compound·tyre_life)`
  and takes each compound's `tyre_life` coefficient as the (race,compound) degradation cell
  (weight = clean-lap count), centred within race. Pure lap-time + `lap_number` only — NO
  physics mass/fuel curve, NO telemetry/grip channel, NO #443 sensor (anti-circular).
- `classify_axis_verdict` rewritten to the commander's CROSS-MODAL criterion: GO requires
  physics tracks the fuel-corrected truth (within-race P > 0.5) AND monotone-up per-compound
  k AND honest covariance; NOT gated on "physics beats γ" (γ is same-modality, home-field);
  physics-vs-{γ, absolute-C#} + #443 ride as CONTEXT. 2σ is a reference, not a gate.
- Scoring core, LOO, physics prediction unchanged.

### CORRECTED-PROBE NOTE (load-bearing — please read)
My first-pass probe used **stint** fixed-effects and reported a "monotone SOFT 0.095 >
MEDIUM 0.071 > HARD 0.066", which the addendum/Admiral approval leaned on. That probe was
**statistically invalid**: with per-stint FE, `lap_number = stint_offset + tyre_life` and the
stint intercept absorbs the offset, so the fuel term is collinear with degradation — the
design is **rank-deficient in all 22 races** and `lstsq` returned a min-norm artifact. The
correct identification uses **DRIVER** fixed-effects (cross-stint `lap_number` spread within a
driver identifies fuel separately from wear); it is **full-rank in all 22 races**. I adopted
driver-FE. Consequence: the corrected truth does NOT reproduce the expected monotone compound
ladder — see the finding.

### Files changed
- `src/physics/layer2/tyre_supplant.py` (reshaped `build_truth_cells`, driver-FE
  `race_degradation_slopes`, cross-modal `classify_axis_verdict`, `is_monotone_up_k`)
- `tests/unit/physics/layer2/test_tyre_supplant.py` (19 tests; new fuel-corrected recovery +
  naive-slope-not-used regression + rank-deficiency guard + cross-modal verdict branches)
- `.agent-work/511/g4-implementer-rework-plan.json` (rework engine plan)
- (scratch, NOT committed) `…/scratchpad/g4_supplant_report.py`

### Evidence (rework)

**Block 1 — unit suite (green)**
```bash
py -m pytest tests/unit/physics/layer2/test_tyre_supplant.py -q
```
`19 passed`. Includes `test_build_truth_cells_recovers_fuel_corrected_wear`,
`test_naive_per_stint_slope_is_not_used` (planted fuel ramp: the fuel-corrected truth recovers
positive wear; the naive per-stint slope is sign-inverted/negative for every compound),
`test_race_degradation_slopes_skips_unidentified_single_stint_drivers` (rank guard), and the
cross-modal verdict branches.

**Block 2 — simplification_limits (clean)**
```bash
py -m src.utils.simplification_limits --paths src/physics/layer2/tyre_supplant.py tests/unit/physics/layer2/test_tyre_supplant.py
```
`PASS (2 files checked)`.

**Block 3 — evo-free (paste)**
```
imports: ['__future__','dataclasses','numpy','pandas','sqlite3','src.common.pairwise_ordering','src.physics.layer2.tyre_separation','typing']
evo-free ok
```

**Block 4 — real-data supplant report on the FUEL-CORRECTED truth (2023, read-only)**
```
=== TRUTH-CELL SUMMARY (fuel-corrected, driver-FE lap-time channel) ===
races=22  cells=60  total_clean_laps=20059
per-compound centred deg-slope (median, robust): HARD +0.0023  MEDIUM -0.0021  SOFT +0.0011   <- ~FLAT, not monotone

=== PREDICTOR SCORES (within-race pairwise P + magnitude R2) on the NEW truth ===
physics_primary      P=0.4492  R2=0.0416  cells=54  races=20
physics_pooled_loo   P=0.3683  R2=0.0363  cells=60  races=22
abs_cnumber          P=0.3679  R2=0.0346  cells=60  races=22   (absolute-C# floor; DB int, NOT evo)
gamma_placeholder    P=0.3679  R2=0.0346  cells=60  races=22   (placeholder; LIVE gamma wired in G5)

physics per-compound mean k = {HARD 0.000498, MEDIUM 0.001625, SOFT 0.008962}  monotone_up=True

=== PER-AXIS VERDICT (lateral_mech) ===
verdict=CONTEXTUAL
reason="physics does NOT cross-modally track the lap-time truth (P=0.449 not > 0.52)"
inputs: monotone_k=True, honest_covariance=True, g3_separates=True
context P (triangulation only): abs_cnumber=0.368, gamma_placeholder=0.368
NOTE (modality): truth is lap-time-family (= compound_prior gamma). A physics WIN/MATCH is
strong cross-modal validation; a non-win is AMBIGUOUS (lap-time incumbent has home-field) ->
triangulate with the #443 telemetry cross-check; do NOT NO-GO on physics-loses-to-gamma.
```

### Supplant finding (the deliverable question)
**Does physics carry real degradation-ordering signal? — On this evidence, NO cross-modal
confirmation; verdict CONTEXTUAL (not GO, not NO-GO).**

- The reshape WORKED as a confound fix: the fuel-corrected truth is physically sane (positive
  degradation, no more impossible −0.24 SOFT). But once correctly identified (driver-FE), the
  lap-time per-lap degradation does NOT separate cleanly by compound — the within-race centred
  medians are ~flat (HARD +0.002 / MEDIUM −0.002 / SOFT +0.001). In each compound's actual
  run-window the per-lap pace loss is comparable; soft is pitted before its cliff, so its clean
  laps capture the gentle part (a stint-window-selection effect, not a fuel artifact).
- Physics μ_tyre(k) is a clean, monotone-up, G3-separable, LOO-honest grip-DECAY axis
  (HARD 0.0005 < MEDIUM 0.0016 < SOFT 0.0090). But it does NOT cross-modally reproduce the
  lap-time degradation ordering: physics P=0.449 (≈ coin-flip, slightly below), LOO P=0.368.
  Grip-decay-RATE (physics) and run-window lap-time-degradation (truth) are genuinely different
  quantities → no cross-modal confirmation.
- Per the commander's criterion this is CONTEXTUAL, NOT NO-GO: physics is a coherent measured
  axis (monotone + separable + honest), it simply isn't validated by the independent lap-time
  channel. It is NOT gated on beating γ (the same-modality incumbents also sit at ~0.37, below
  physics — physics is the BEST of the four predictors here, but none track this near-flat
  truth). G5's LIVE γ + #443 telemetry cross-check are the triangulation that can promote or
  retire this CONTEXTUAL.
- This aligns with the standing project read (#512: regime-capability is fine-margin /
  circuit-conditional, not a clean axis; "ceilings aren't pace"): the physics tyre-DECAY axis
  is real and clean but is not, by itself, a lap-time-degradation supplant.

### Assumptions (rework)
- DRIVER fixed-effects (not stint) are mandatory for fuel/degradation identification; races
  whose design is rank-deficient (e.g. all single-stint drivers) yield no cells (fail-visible).
- Fuel = a single global linear term in `lap_number` per race; driver FE absorbs per-driver
  base pace and per-stint fuel offset. The truth uses lap-time + lap_number only.
- Within-race centring (lap-count-weighted) makes the cell relative degradation; harmless for
  within-race ordering. Robust cross-race summary uses the median (the plain mean is noisy).
- Verdict thresholds (mine): P signal margin 0.02 over coin-flip; monotone-up k tolerance 1e-12;
  honest covariance = G3 oos_rmse ≤ 1.25× in-sample. 2σ NOT consulted in the verdict.

### Test mode
**Required:** test-after (synthetic load-bearing). **Satisfied:** yes — 19/19 green incl. the
fuel-corrected planted recovery and the naive-slope-not-used regression.

### Map Impact (rework)
- **Structural:** `struct:physics.layer2` `tyre_supplant.py` — truth now a driver-FE
  fuel-corrected cross-stint OLS; consumes `struct:common` `pairwise_ordering` + G3
  `tyre_separation`. Reads `lap_times`/`race_stint_estimates`/quali `session_estimates` read-only.
- **Constraints:** `constraint:physics_region_no_evo_import` honored; anti-circular held (truth
  lap-time+lap_number only). `lesson:loo-residual-diagnostic` honored.
- **Claims/evidence:** physics tyre-decay is a clean monotone axis but does NOT cross-modally
  reproduce the fuel-corrected lap-time degradation ordering (P=0.449) → lateral_mech CONTEXTUAL.
- **Decision:** `decision:regime_readiness_rubric` (#512) — cross-modal verdict criterion
  realized (GO=tracks-truth+monotone+honest; not gated on beating γ; modality caveat).
- **Trust limitation:** my first-pass stint-FE probe was rank-deficient/invalid; corrected to
  driver-FE. Any downstream reliance on that probe's "monotone" numbers must be retired.

### Stop conditions hit (rework)
- None blocking. The reshape landed cleanly, evo-free, anti-circular. The headline EXPECTATION
  (monotone truth, physics GO) was NOT met — surfaced honestly as CONTEXTUAL with the
  corrected-probe note, not forced to GO.

### Out-of-scope observations
- The fuel-corrected lap-time per-lap degradation being ~flat across compounds (window-selection)
  is itself a finding worth carrying into G5/Phase-P: a clean lap-time "which-compound-degrades-
  more" truth may need a nonlinear/stint-window-aware degradation model, not a linear slope.
- Physics is the best of the four predictors here (0.449 vs incumbents 0.368) but all are below
  0.5 → the near-flat truth is weakly orderable; treat per-compound P on it cautiously.

### Workflow Feedback (rework)
- **Handoff/approval gap:** the reshape was approved on my own probe, which I had not yet
  validated for identifiability. The probe's stint-FE design was rank-deficient (a min-norm
  artifact produced a spurious monotone ladder). I caught and corrected it (driver-FE) before
  baking — but a "verify the probe's design is full-rank before escalating a reshape" step
  would have prevented an approval resting on an invalid number. I have flagged this to the
  commander explicitly.
- **Tension between instructions:** the addendum said "keep all 16 tests green"; the later
  verdict-criterion refinement required changing `classify_axis_verdict` and its tests. I kept
  the scoring-core/physics/LOO tests intact and updated only the truth + verdict tests to the
  ratified criterion (now 19 tests). Reporting the misfit per crew doctrine.
- **What would help:** state the identification model (driver-FE, full-rank requirement) and
  the expected-vs-honest-outcome posture in the reshape addendum, so a non-monotone honest
  result is anticipated rather than surprising.

### Return status (rework)
`complete` — reshape landed: fuel-corrected driver-FE truth, cross-modal verdict, 19 tests +
3 clean evidence blocks + real-data report. Honest finding: physics tyre-decay is a clean
monotone axis but does NOT cross-modally track the (near-flat) fuel-corrected lap-time
degradation truth → lateral_mech CONTEXTUAL. G5 wires the live γ + #443 triangulation.

---

## ORIGINAL PASS (audit trail — superseded by the REWORK above)

The first pass delivered the evo-free supplant scoring core + verdict rubric (proven by
synthetic tests) but BLOCKED the real-data verdict on a material truth-channel reshape: the
handoff's per-stint `lap_time ~ tyre_life` slope is fuel-confounded (within a stint `tyre_life`
and race-lap are perfectly collinear), so it measured net stint trend, not degradation —
SOFT showed a physically-impossible −0.24 s/lap centred slope, and physics (P=0.387), LOO
(0.220), and a naive hardness incumbent (0.220) all fell below coin-flip against it. That block
was bubbled to the commander, the Admiral approved the fuel-corrected reshape, and the rework
above is the result. The scoring core, neutral metric usage, LOO design, and evo-free / anti-
circular guarantees were unchanged by the rework; only `build_truth_cells`' slope computation
and the verdict criterion changed.
