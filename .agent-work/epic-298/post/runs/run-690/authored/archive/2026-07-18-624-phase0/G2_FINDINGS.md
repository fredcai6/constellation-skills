# G2 findings — wide-sigma A/B checkpoint (Phase-0 probe, informational)

**Status:** INFORMATIONAL. Per Pre-Ruling #3 ("float rather than build Phase 1-6 machinery")
and the handoff's Protected Intent, this probe exercises the EXISTING
`driver_residual_states` residual-history injection seam only. No new modeling, no
Phase-6 BT injection, no `src/` modification, no `params/gold/*` default change.

Reproduced by: `py scripts/g2_wide_sigma_ab.py --stage baseline`, `--stage injected`,
`--stage compare` (or `--check` to rerun all three) from `C:/Programs/f1-624`.

<!-- machine-parseable headline lines, do not reword -->
HEADLINE_BASELINE: brier=0.13028701052631578 log_loss=0.7155998887783401 n_drivers=20 unresolved_teams=0
HEADLINE_INJECTED: brier=0.13028701052631578 log_loss=0.7155998887783401 n_drivers=20 unresolved_teams=0
HEADLINE_G0: spearman_r=nan n=20
HEADLINE_G1: baseline_brier=0.13028701052631578 injected_brier=0.13028701052631578 delta=0.0

## Weekend used

2025 Japan, round 3 (`f1_data_2025.db`), seed 42. `session_estimates` has Q rows for
all 10/10 constructors that weekend; `Q` session_classification has the full 20-driver
field; the team/constructor alias scheme (reused from `scripts/g1_correlation_screen.py`'s
`normalize_team`/`match_constructor`/`EXTRA_ALIASES`) resolves all 10 teams with zero
ambiguity — verified live before building the script, not assumed.

## Exact seam used (verified against source, not memory)

- `DriverResidualStateEntry` / `DriverResidualState`
  (`src/evo_predictor/driver_residual_history_adapter.py:9-24`).
- `build_neutral_driver_residual_history_field` reads only `entry.residual_mean` /
  `entry.residual_variance` per driver (`driver_residual_history_adapter.py:32-115`).
- `RuntimeModuleContext.driver_residual_states: Mapping[task, DriverResidualState]`
  (`src/evo_predictor/module_context.py:25`), consumed by
  `_make_runtime_driver_residual_history` via
  `context.driver_residual_states.get(adapter.task)`
  (`src/evo_predictor/module_adapters/_runtime_builders.py:562`).
- External injection point: `SampledEvoRuntime.predict_from_features(runtime_context=...)`
  (`src/evo_predictor/sampled_runtime.py:200-217`) — the same method
  `SampledEvoRuntime.predict()` calls internally. `build_sampled_runtime_features`
  (`src/evo_predictor/data_adapter/_helpers.py:197-282`) returns a
  `SampledRuntimeFeatureSet` whose `.runtime_context` is a frozen `RuntimeModuleContext`,
  safely overridden via `dataclasses.replace(feature_set.runtime_context,
  driver_residual_states={"quali": state})` from `scripts/g2_wide_sigma_ab.py`
  (a standalone external driver script) — **no `src/` file was modified**. This
  confirms the seam is externally-usable exactly as the handoff hoped;
  **no STOP condition was hit on injectability**.

## Sigma-widening formula (exact, as implemented)

```
floor_variance   = lateral_mech_grip_g_sigma**2 + lateral_aero_grip_g_sigma**2
widened_variance = floor_variance * 16.0        # 16x variance == 4x SD
residual_mean    = lateral_mech_grip_g + lateral_aero_grip_g   (= lateral_total_grip_g)
```

**Justification:** `floor_variance` is a conservative independence-assumption floor
for the composite axis (sum of two components), deliberately NOT using the stored
`lateral_covariance` blob (see "Discrepancy note" below) per the handoff's explicit
instruction. The 16x variance / 4x SD inflation reflects two unquantified sources
of extra uncertainty beyond the floor: (a) per `x7-basis-map-RESULT.md` section (c),
the store's covariance blobs are within-view only, with no cross-view coupling and
no accounting for shared upstream trajectory-estimation noise across Braking/
Traction/Lateral views that draw from the same fitted trajectory; (b) there is no
calibration between the physics store's g-unit scale and the model's own
pi/sigma_pi latent scale — injecting a raw physics value onto that scale carries a
translation uncertainty no physics-side sigma captures at all.

For 2025 Japan: the naive per-component floor SD ranges **0.21–0.67 g** across the
10 constructors, while the pre-registered axis's own field spread (max − min
`lateral_total_grip_g` across constructors) is **~0.90 g** (2.80–3.74 g) — i.e. even
the un-inflated floor SD is already comparable to the whole field's spread. The 4x
SD inflation pushes the injected SD to **~0.84–2.68 g**, at or above that field
spread — deliberately weak/humble relative to the very quantity it carries — while
remaining well below the seam's own built-in "neutral" scale
(`DriverResidualHistoryConfig.neutral_sigma = 10.0` ⇒ variance 100), so the
injection is nominally "exercised, not fully swamped to neutral" **by variance
alone**. See the Honest read below for why this reasoning turned out not to matter.

Full per-constructor numbers are recorded in `g2_injected_output.json`'s
`physics_axes` block (e.g. Ferrari: mech=3.739, aero=0.00038, total=3.740,
floor_variance=0.0752, widened_variance=1.203).

## G0 / G1 reads

- **G0** (does the injected field perturb the quali stage output, in the
  pre-registered sign direction?): **UNDEFINED (nan), n=20.** The per-driver
  "expected quali position" (probability-weighted mean over
  `StageSnapshot.position_distribution`) is **bit-identical** between the baseline
  and injected runs for all 20 drivers — the delta is exactly 0.0 everywhere, so
  the Spearman correlation against `lateral_total_grip_g` is undefined (constant
  vector). The injection produced **zero observable perturbation**, not a small
  one.
- **G1** (pairwise Brier of quali predictions, injection vs baseline): **identical
  to 16 significant figures** — `0.13028701052631578` in both runs, delta = 0.0
  exactly. Same for pairwise log-loss (`0.7155998887783401` both).

## Root cause of the null (found during compare, verified against the loaded manifest)

The bit-identical outputs are **not** a "swamped by wide variance" story. They are
because **the currently-loaded production gold manifest never activates the
residual-history module for any stage**:

- The registered module name for this seam is `driver_quali_power_from_residual_history`
  (and its `race_start`/`race` siblings), distinct from the already-productionized
  `driver_quali_power_from_recent_history` module
  (`src/evo_predictor/module_adapters/_registry.py:237-264`).
- `params/gold/sampled_runtime_manifest.json`'s quali-stage `fusion_order`/`steps`
  list is exactly `["constructor_quali_power_from_recent_history",
  "driver_quali_power_from_recent_history",
  "constructor_quali_power_from_race_weekend",
  "driver_quali_power_from_race_weekend"]` — **no `residual_history` module is
  present**, confirmed by `grep -c residual_history params/gold/sampled_runtime_manifest.json`
  → `0`, and `grep -l residual_history params/gold/*.json` → no matches across
  **every** manifest in `params/gold/`.
- Because `SampledEvoRuntime._run_stage` only invokes adapters for
  `enabled_stage_module_names(stage)` (i.e. modules present in the loaded stage
  config), `_make_runtime_driver_residual_history` — and therefore
  `context.driver_residual_states.get('quali')` — is **never called** during a
  `sampled-predict` run against this manifest, regardless of what
  `driver_residual_states` is populated with externally.

This matches and sharpens the handoff's own map-confidence flag ("the
`driver_residual_states` seam has ZERO current callers that populate it
non-empty... expect the unexpected"): the deeper reason isn't just "nothing
populates it" — it's that **nothing in any current production manifest even reads
it**, because the module that reads it isn't wired into any stage's active fusion
steps. The seam is real, code-complete, and externally injectable exactly as
described — but currently dormant/unreachable via any production `sampled-predict`
invocation. Activating it would require adding
`driver_quali_power_from_residual_history` (etc.) to a manifest's stage `steps`
list, which is a manifest/config change, not a code change — outside this probe's
scope (informational only, no `params/gold/*` default change per Specific
Exclusions).

## CPU>0 confirmation (headless-deadlock regression check, #623)

- **Baseline run** (`g2_baseline_run.log`): exit 0, wall clock not explicitly
  timed (methodology gap — see below), completed within a single `Start-Process`
  + two `Get-Process -Id <pid>` CPU-time samples 8s apart (both read 0.14s CPU on
  the launcher PID) before `ReadToEnd()` unblocked. **Caveat, stated honestly:**
  sampling a single PID by ID is unreliable on Windows because `py.exe` may hand
  off to a child `python.exe` process under a different PID; the flat 0.14s/0.14s
  reading is inconclusive as a CPU-activity signal by itself. The run's *output*
  (a real, sane, non-degenerate Brier=0.1303 result over 20/20 resolved drivers,
  written to disk) is the actually-decisive evidence against the #623 deadlock
  signature (which manifests as indefinite non-completion producing no output),
  independent of the CPU-sampling caveat.
- **Injection run** (`g2_injection_run.log`): exit 0, **wall clock explicitly
  measured at 208.9s (~3.5 min)**, matching the handoff's "~3-4 min per race"
  reference. CPU confirmed actively rising across 6 samples at 0.5s intervals
  (summed CPU-seconds across all `py`/`python` processes on the machine: 2382.89
  → 2383.92 → 2384.77 → 2385.80 → 2386.83 → 2387.89 — a steady ~1.03 CPU-second
  increase per 0.5s wall-clock sample, i.e. genuinely consuming a full core, not
  idling at 0%). This is unambiguous positive evidence against the #623 deadlock
  signature.
- **Self-critical note:** the baseline run's CPU-check methodology (single-PID,
  2 samples 8s apart) was weaker than the injection run's (process-name sum, 6
  samples at 0.5s). In hindsight the baseline run likely took a comparable ~3-4
  min too (the elapsed wall-clock for that `Start-Process`+`ReadToEnd()` call was
  not printed, so this cannot be confirmed retroactively) — it just wasn't proven
  as rigorously. Both runs produced complete, correct, non-degenerate output, so
  the #623 regression check passes either way; the methodology gap is reported
  here per "verify claimed side-effects against the world," not glossed over.

## Discrepancy note: `lateral_covariance` in the store (flagged honestly, not acted on)

While verifying the seam (m1/m2), the `session_estimates` schema was inspected
directly (`sqlite_master` DDL) and confirmed to include a `lateral_covariance`
column, alongside `braking_covariance`, `traction_covariance`,
`power_drag_covariance`, `coast_covariance`. Per `x7-basis-map-RESULT.md` section
(c), each of these blobs is "a single view's own 2×2 covariance, WITHIN-view
only" — for `lateral_covariance`, that is exactly
`Cov(lateral_mech_grip_g, lateral_aero_grip_g)`, the two components summed to
form the pre-registered primary axis `lateral_total_grip_g`. This is a more
precise/narrower fact than the implementer handoff's summary phrasing ("there is
NO stored cross-view covariance... sum of two correlated-in-reality-but-
UNCOUPLED-in-the-store components") might suggest on a first read — the two
components ARE jointly fit with a stored covariance term, it is just *within*-view
(mech↔aero), not *cross*-view (e.g. lateral↔braking) or upstream-shared-noise
coupling. Using `Var(sum) = Var(mech) + Var(aero) + 2·Cov(mech,aero)` via
`lateral_covariance` would in principle be a more exact within-view variance than
the independence-assumption floor used here. **This was deliberately NOT done**:
the handoff's Authority section explicitly pre-decided the conservative-floor +
inflation approach as an example formula and instructed not to re-litigate the
seam/formula choice, and the broader x7(c) point about missing cross-view /
shared-upstream-noise coupling still applies regardless of this within-view
nuance. Flagged here as a precision correction for the next probe's
pre-registration, not acted on in this run.

## Honest read — what this does and does NOT show

**What it shows:**
1. The `driver_residual_states` injection seam is **code-complete and externally
   injectable** without any `src/` modification — confirmed by actually doing it,
   not just reading the contract. This is a genuinely positive, load-bearing
   result for future work planning around this seam.
2. The headless `sampled-predict` runtime is **not hung/deadlocked** under this
   modification (#623 stays fixed) — both runs completed with real output; the
   injection run's CPU/wall-clock evidence is unambiguous, the baseline run's
   less rigorously proven but its correct output is still decisive.
3. **Populating `driver_residual_states` today has ZERO effect on any
   `sampled-predict` run against the current production gold manifest**, because
   the module that reads it is not among any stage's active fusion steps in any
   manifest under `params/gold/`. This is a **structural** null (module not
   wired into the manifest), not a **statistical** null (signal swamped by wide
   variance) — the sigma-widening formula and its justification are recorded
   above for completeness and for the next probe, but they were never actually
   tested against real fusion behavior in this run, because the module never
   fired.

**What it does NOT show:**
- It does NOT show that the residual-history module would perturb output "a
  little" — it shows the module wasn't invoked at all this run. Whether a
  *wired-in* residual-history module, fed the same widened-sigma physics
  estimate, would move the fused field measurably is genuinely untested here.
- It does NOT test whether the sigma-widening formula's magnitude choice (16x
  variance / 4x SD) is well-calibrated — that question is moot until the module
  is actually wired into a manifest's fusion steps.
- It is NOT the Phase-3 unified-basis result, and it is NOT a verdict on whether
  physics-informed residual history would help evo's predictions — it is a
  narrower, purely mechanical finding: the seam wires correctly end-to-end from
  outside `src/`, but is currently a dead branch in production because no
  manifest activates its module.
- No causal or predictive-value claim is made about the pre-registered axis
  itself; G1's `pairwise_brier_against_actual` numbers reported here reflect
  the CURRENT production quali fusion (unaffected by this probe either way),
  not a physics-informed prediction.

## Scoped null / positive statement

This specific test (constructor-broadcast `lateral_total_grip_g` physics
estimates, injected via `RuntimeModuleContext.driver_residual_states` with a
16x-variance-inflated independence floor, run against `sampled-predict` for
2025 Japan Q with the currently-published `params/gold/sampled_runtime_manifest.json`,
seed 42) produces **zero observable effect** on quali-stage predictions or
Brier score, because the residual-history module is not among that manifest's
active quali-stage fusion steps — **not** because the injected signal was too
weak or too wide. The seam itself is confirmed mechanically sound and externally
usable. This does not speak to what would happen if the module WERE wired into a
manifest's fusion steps, to other weekends, to the race_start/race tasks
specifically, or to a different sigma-widening formula — those are untested
variants, not closed questions.
