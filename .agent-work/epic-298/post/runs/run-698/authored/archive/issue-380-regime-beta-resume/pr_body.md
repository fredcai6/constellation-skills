Closes #380. Thrust A Step 2 — Piece 1.

> **Rebased 2026-06-05 onto current `main` (`d801832`).** This PR was first cut on `fa9e48b`; `main` has since advanced through #400 (median-only practice encoding), #401 (`entity_count`), #402 (σ key-sets), and #404 (#382 γ-degeneracy). Conflicts resolved with intent-preservation (both sides' semantics kept); **evidence below re-validated on #400's new median-relative encoding** (the original numbers were measured on the now-removed minmax encoding).

## What shipped
The compound fresh-pace effect is regime-dependent (§7.1): under a qualifying push a softer compound is faster fresh (~1%/step intercept); under managed race pace it is not. `compound_prior` fits one **race-regime** β and applies it to both regimes, leaving the full compound artifact in the quali-sim (`qs_*`) features.

This routes `qs_*` (push) features through the **gate-recovered push-regime β** while `lr_*` (managed) features keep the race-regime β — **injected behind the existing `CompoundNormalizer` interface**, β-only (γ untouched), behind a default-preserving flag.

- **`src/evo_predictor/compound_push_regime.py`** (new): gate-recovered push β (monotone-down C1→C6, ref C3; provenance `docs/evo/compound_crossover_gate_findings.md` — now on `main` via #400) + `build_push_regime_normalizer(race_artifact)` → a `CompoundNormalizer` over a β-substituted copy of the race artifact (γ + all other fields unchanged). The `compound_prior` **fitter is not modified**. The vendored β constants are verified equal to the on-`main` findings doc's primary pooled fit.
- **`practice_preprocessor/_compute.py`**: laps are already split into quali-sim vs long-run buckets *before* normalization (unchanged by #400's rewrite), so `compute_practice_features` / `compute_constructor_race_features_from_laps` gained an optional `quali_sim_compound_normalizer` routed only to the quali-sim bucket. Default `None` ⇒ falls back to `compound_normalizer` ⇒ **byte-identical** to before.
- **`configs/evo/gold_defaults.toml [data] qs_compound_beta_regime`** (`"race"` default | `"push"`), validated in `gold_cycle/config.py`, plumbed through the gold-cycle training path and the runtime `EvoPipeline`; `data_adapter/_build.py::_resolve_quali_sim_normalizer` builds the push normalizer from the race normalizer's own artifact when `"push"`.

## Validation (model-free, honest) — re-validated on the median-relative encoding
`scripts/validate_qs_compound_beta_regime.py` — qs_* best-lap pairwise sign-accuracy vs actual-Q, split cross-compound vs overall.

**2022–2025 (new median-relative encoding): CROSS +0.60pp (0.7131→0.7191) vs OVERALL +0.26pp (0.7014→0.7040)** — the push β helps the cross-compound subset specifically (~2.3× the overall delta), with muted overall movement as expected. This is the §7.5 minority slice (≤13% of qs_* pairs); a real correctness fix, **not** the quali solution.

The signal is **encoding-invariant by construction**: the push β adjusts raw lap times *upstream* of feature normalization, and the harness scores *within-event pairwise order*, which #400's monotone median-relative normalization preserves exactly. So **no β-unit change was required** when minmax → median-relative. (For reference, the original minmax measurement was CROSS +0.55pp / OVERALL +0.29pp; the fresh result is marginally stronger. Pair counts shifted slightly — 6212→6284 overall — consistent with #400's sprint FP1+SQ short-run bucketing.)

## Scope
β-only — γ (degradation) did not identify and is out of scope; #382 has since measured the γ axis as *confounded* (well-resolved but wrong-signed), confirming the β-only scope and that the pooled β is the right artifact (§7.7). Piece 3 (vector latent) untouched. Append-only §8 note in `docs/evo/prediction_ceiling_and_priorities.md`; architecture map reconciled in `docs/architecture/`.

## Evidence
- 347 targeted tests green (push regime, practice preprocessor + constructor, gold config + runner, data adapter incl. qs-resolver, orchestration, labeled-batches + record, pipeline + validation, run CLI) — re-run post-rebase.
- pyright clean on all 9 touched src files.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
