# Problem statement — issue #420 (productionize the quali pace anchor)

## The ask (bounded)

Move the cross-channel pace anchor from the #414 prototype
(`scripts/scope_quali_anchor_414.py`, measurement-grade, on main) into the
**production race_weekend quali head's inference path**, behind a config key.
At inference, blend the head's latent field `pi` with a z-standardized
`best_across_fp` min-sector practice-pace ordering, per event:

```
pi' = (1-alpha) * z(pi) + alpha * z(-anchor)      # pi-space (higher = faster)
```

where `anchor` = per-driver min-sector practice-pace (lower seconds = faster),
so `-anchor` orders faster→higher to match `pi`. `z(.)` = within-event
standardize. This is mathematically identical to the prototype's
`s = (1-alpha)*z(-pi) + alpha*z(-best_across_fp)` lower-better blend (both are
order-equivalent; sign-acc is the metric).

## Measured basis (must reproduce through production path, within tolerance)

§7.6.3 (#414), headline 2018-2024 LOSO, shared non-tie pairs, race_weekend:
- alpha=0.5: overall 0.6153 → 0.7452 (ceiling 0.8061); EASY/far(gap>=9)
  0.6926 → 0.8691 (ceiling 0.9365). ~68%/72% gap recovered.
- OOS-2025 reproduces (+0.72/+0.80). C3: magnitude-only is an exact ordering
  no-op — the lever is the ordering signal, not calibration.

## Attach point (pre-ruled 1; confirmed by recon)

`src/evo_predictor/sampled_runtime.py` `_run_stage()`, the line that appends a
module's `ModuleFieldResult` to `fields` (currently line 358), gated on:
- `task == "quali"` AND `module_name == "driver_quali_power_from_race_weekend"`.

This is the single seam where the freshly-produced per-module `pi` AND the
`features: RaceFeatures` (carrying the per-driver anchor) are both in scope,
upstream of `_canonicalize_stage_event_ids` and `fuse_module_fields_ordered`.
It is INSIDE the quali head's output path, NOT at the fusion layer (per ruling).

## Anchor source at inference (the key reproduction question)

`DriverFeatures.qs_theoretical_best` (models/_features.py:44) — "quali sim
theoretical best (sum of min sectors)" — is the production min-sector practice
pace, already in `RaceFeatures` at inference, keyed per driver_id. NO new DB
read needed (satisfies DB-only canon trivially; it is already a DB-derived
feature).

CORRESPONDENCE CAVEAT (must measure + explain — ruling 5): the prototype's
`best_across_fp` = min over FP1/FP2/FP3 of (min-sector theoretical best) over
ALL clean laps. Production `qs_theoretical_best` = min-sectors over
SHORT-STINT (quali-sim-classified, stint_size <= QUALI_SIM_MAX_LAPS) clean laps
pooled across FP sessions. Same signal family (FP min-sector pace), slightly
different lap population (quali-sim filter). Whether this reproduces §7.6.3 is
an EMPIRICAL question the acceptance gate answers. The raw-seconds variant is
`qs_best_raw` (NaN when missing); normalized `qs_theoretical_best` is monotone
within event so identical for sign-acc ordering. Missing-anchor drivers
(NaN/sentinel) must be handled explicitly (drop from blend, keep their original
pi) — no silent impute (canon).

## Sign convention (confirmed)

`field_solve` produces `pi` with higher = faster/ahead (GLOSSARY; prototype uses
`-pi` as lower-better source). Anchor is a time (lower=faster), so map with
`-z(anchor)`. The blend must IMPROVE ordering, verified by the acceptance
measurement (a sign error would DROP sign-acc — caught immediately).

## Config (rulings 3,4,8)

- Runtime-only post-process (no retrain). Config lives in the runtime/stage
  config, carried in the sampled-runtime manifest, read in `_run_stage` (mirrors
  `stage.fusion`). Chain: `configs/evo/gold_defaults.toml` → `gold_cycle/config.py`
  → manifest echo → `pipeline_manifest_v4` stage config → `_run_stage`.
- Two keys, names that cannot collide with fusion-net keys (sister #375):
  `quali_anchor_enabled` (bool) and `quali_anchor_alpha` (float). Namespaced to
  avoid collision (final names decided at plan; prefix `quali_pace_anchor_*`).
- alpha default = measured 0.5 unless a train-season fit with OOS validation
  clearly beats it (fit only on 2018-2024 train years; NEVER on eval seasons).
- DEFAULT ON once acceptance reproduces — UNLESS downstream assessment (ruling 6)
  says ship OFF until a retrain; that overrides and is pre-authorized.

## Downstream impact (ruling 6 — required findings section)

Consumers of quali race_weekend `pi`: fusion precision-weighting
(`fuse_module_fields_ordered` uses pi AND sigma_pi), gap-scale, calibration,
gold artifacts — all trained/fit against the UN-anchored pi distribution. The
z-standardize step in the blend ALSO changes pi's MAGNITUDE/SCALE (not just
ordering), which fusion's precision weighting is sensitive to. Must assess:
what shifts, whether retrain is indicated, and the safe activation story. This
assessment decides default ON vs OFF. Do NOT run a gold retrain.

## Acceptance evidence (ruling 5 — the issue's core)

Re-run the same-pairs diagnostic THROUGH THE PRODUCTION blend (production
`qs_theoretical_best` anchor, production attach point), before/after, and show
the §7.6.3 improvement reproduces within reasonable tolerance. Quantify and
EXPLAIN any delta vs the record-replay prototype (different lap population, same
signal). If production CANNOT reproduce → STOP, report as a verdict.

## Hard boundaries

- QUALI ONLY; race/race_start heads untouched.
- alpha = GLOBAL weight only (per-context is #375).
- Do NOT touch: `fusion.py`, `fusion_training/`, `scripts/fusion_replay/`,
  `docs/evo/fusion_rework_findings.md` (sister #375 owns these).
- I own: quali-head/latent_power race_weekend path, practice-evidence plumbing,
  config keys, tests, and §7.6.4 in `prediction_ceiling_and_priorities.md`.
- Production tests must NOT depend on generated records — synthetic/fixture only.

## Authority / ratification

Pre-ruled by the admiral brief (8 rulings) and user-ratified at fleet #372
checkpoint 2 (2026-06-06, "BOTH-STAGED", recorded in §7.6.3 + the issue body).
Commander cannot reach the human this run (background job); the ratification +
rulings ARE the user-decision for understand/plan. Any ruling override is logged
with justification (ruling 6 pre-authorizes a default-OFF override).
```
