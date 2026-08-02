# Issue #380 — Problem Statement & Reconciliation (Commander)

## The bounded ask
Route `qs_*` (quali-sim / push-regime) practice features through a **push-regime
fresh-pace β** (gate-recovered, monotone-down C1→C6), while `lr_*` (long-run /
managed) features stay on the existing **race-regime β** from `compound_prior`.
Behind a **default-preserving config flag**. Piece 1 = **β only** (γ did not
identify; out of scope). Reach is small (~13% of qs_* pairs cross-compound).

## Admiral ruling (standing order R1)
INJECT the gate-recovered β behind the existing `CompoundNormalizer` interface.
Do **NOT** re-fit or modify `compound_prior` (that is sibling #382's territory).

## Reconciliation against current artifacts (done before wiring)

### 1. Where the gate β lives
The harness `scripts/fit_compound_crossover_gate.py` and
`docs/evo/compound_crossover_gate_findings.md` referenced by the issue do **not**
exist on `main`. They live on `origin/claude/compound-regime-feasibility`
(commits 581c617, df57111, 3efc9ff). The §7/§7.1/§7.5 design-doc content the issue
cites is also only on that branch (not yet merged to main).

### 2. The gate-recovered β (primary pooled fit, single global phi)
`normalized_fractional` effect space, reference C3 (matches
`parameter_means.beta_C*`). Strictly monotone-down, every adjacent step ≫ 2 SE:

| C# | β (gate)   | β_se    |
|----|-----------|---------|
| C1 | +0.003012 | 0.00059 |
| C2 | +0.001237 | 0.00033 |
| C3 |  0 (ref)  | —       |
| C4 | −0.002422 | 0.00037 |
| C5 | −0.005498 | 0.00056 |
| C6 | −0.007365 | 0.00092 |

Gold (race-regime) β by contrast: ~0, non-monotone, wrong-signed C1
(C1 −0.001376, C2 +0.000306, C3 +0.000106, C4 +0.000282, C5 −0.008107).
γ did NOT identify (non-monotone, spec-sensitive) → Piece 1 ships β only.

### 3. The normalizer interface (injection target)
`src/compound_prior/runtime_normalization.py`:
- `CompoundNormalizer(artifact)` where `artifact: CompoundPriorArtifact` holds
  `parameter_means["beta_C*"]` / `["gamma_C*"]`.
- `normalize_lap_time(...)` adjusts each lap to "equivalent C3 at age 0":
  `adjustment = (target_effect − source_effect) * baseline`, where
  `effect_fraction(c, age) = beta_c + gamma_c * age`.
- A push-β normalizer = a `CompoundNormalizer` over a `CompoundPriorArtifact`
  with `beta_C*` replaced by the gate values, **γ unchanged** (γ stays race-regime).

### 4. The consumption path (where qs_* vs lr_* split)
`src/evo_predictor/practice_preprocessor/_compute.py :: compute_practice_features`
(and `compute_constructor_race_features_from_laps`):
- `_split_run_buckets()` / `_classify_stints()` splits clean laps into
  `long_run` (managed) and `quali_sim`/`short_run` (push) **before** normalization.
- The SAME `compound_normalizer` is currently passed to BOTH buckets' compute
  calls (`_compute_sector_features`, `_compute_representative_features`,
  `_compute_quantile_features`, `_compute_bucket_repeatability_features`).
- qs_* features derive exclusively from the `quali_sim` bucket; lr_* from `long_run`.

⇒ The buckets are already physically separated. Injection = pass the push-β
normalizer to the quali_sim compute calls, keep the race-β normalizer on long_run.

## Injection design (minimal, interface-preserving)
1. Add optional `quali_sim_compound_normalizer: CompoundNormalizer | None = None`
   to `compute_practice_features` (and the constructor variant). `None` ⇒ fall
   back to `compound_normalizer` for the quali_sim buckets ⇒ **byte-identical to
   today** (no-regret guardrail).
2. Build the push-β normalizer at the point the race-β `compound_normalizer` is
   constructed; gate on a config flag.
3. Config flag in `configs/evo/gold_defaults.toml [data]`, modeled on the existing
   `recent_history_form_encoding` precedent:
   `qs_compound_beta_regime = "race"` (default) | `"push"`.
   Threaded through the same path that flag uses (config.py → run.py →
   orchestration/adapters → data_adapter/_build.py).
4. Gate-β values + artifact-derivation helper live in a small new module under
   `src/evo_predictor/` (the F1-specific push anchor), NOT in `compound_prior`
   (whose fitter is #382's lane). The values are sourced from the feasibility
   findings; recorded with provenance.

## Lane discipline (siblings)
- #379 owns practice preprocessor / evidence aggregation — do NOT pull in the
  feasibility branch's preprocessor refactor or the §7.6 SQ/rank-blend changes.
- #382 owns the compound_prior fitter — do NOT re-fit; only consume its artifact.
- Do NOT pull the feasibility branch's `pace-encoding-368` (median-relative)
  `gold_defaults.toml` epochs/lr changes — unrelated to #380.
- §7/§8 doc note: APPEND-shaped only (Admiral resolves doc merges).

## Validation (per issue)
- β monotone-down C1→C6 (assert in a unit test over the injected values).
- Default flag ("race") ⇒ identical features to pre-change (regression test).
- "push" flag ⇒ qs_* adjustments change on cross-compound laps; lr_* unchanged.
- Cross-compound-subset check: the FP3-beats-model gap narrows on the
  cross-compound qs_* subset specifically (not overall — ~no overall movement is
  expected and honest).
