# Implementer Handoff — G1 (issue #420)

Repo root: `C:\Programs\f1Brainz\.claude\worktrees\agent-aedb2af1326073fec`.
Branch: `constellation/issue-420-quali-anchor-production` (already checked out).
Python is `py`. Tests: `py -m pytest tests/...`. Set `PYTHONIOENCODING=utf-8`.
Read `docs/agents/CREW_CONTEXT.md` + `docs/agents/GLOSSARY.md` before non-trivial work.

## Gate
`g1`

## Task
Productionize a cross-channel pace anchor for the race_weekend quali head: at
inference, blend the head's latent field `pi` with a within-event z-standardized
practice-pace ordering, behind a config key (DEFAULT OFF in this gate). Three
pieces: (a) a pure blend function + tests; (b) two runtime config keys threaded
end-to-end; (c) wire the blend into the runtime stage loop, gated to the quali
race_weekend driver head only.

## Protected Intent
The race_weekend quali head currently mis-orders coarse far-apart driver pairs
because it lacks a general-pace anchor (measured: §7.6.2/§7.6.3). Injecting the
practice min-sector pace as an ordering anchor recovers most of that gap. Must
NOT change race/race_start behavior, must NOT change anything when disabled
(default OFF), and `alpha=0` must be an EXACT ordering no-op.

## Test Mode
TDD required. Write failing unit tests first for the blend function, then
implement. Tests use SYNTHETIC arrays only — they must NOT depend on any
generated module records or DBs.

## Background: the exact math (from #414 §7.6.3, measured & ratified)

Per event, in `pi`-space where higher `pi` = faster/ahead (confirmed:
`src/latent_power/field_solve.py` solves `M pi = A^T W mu`; GLOSSARY: higher pi
ranks ahead; the §7.6.3 prototype uses `-pi` as a lower-better source):

```
z(x)   = (x - mean(x)) / std(x)         # within-event standardize; std==0 -> zeros
pi'_i  = (1 - alpha) * z(pi)_i + alpha * z(-anchor)_i
```

`anchor` is a per-driver practice min-sector pace as a TIME-like quantity where
LOWER = faster. Negating (`-anchor`) makes faster -> higher, matching `pi`.
- `alpha = 0`  -> `pi' = z(pi)`: a strictly-monotone (order-preserving) rescale
  of `pi`. Pairwise ordering is identical to the input `pi`. This is the
  no-op invariant (pairwise sign-acc unchanged).
- `alpha = 1`  -> `pi' = z(-anchor)`: pure anchor ordering.

The §7.6.3 prototype is `scripts/scope_quali_anchor_414.py` (read it for the
reference implementation of the z-blend; note it works in lower-better space
`s=(1-a)z(-pi)+a z(-best_across_fp)` which is order-equivalent to the pi-space
form above). DO NOT modify that script.

## Piece (a): the blend function — `src/evo_predictor/quali_pace_anchor.py` (NEW)

Pure stdlib + numpy. No domain imports beyond numpy. Signature (adjust names
sensibly, keep it pure and testable):

```python
def blend_quali_pace_anchor(
    pi: np.ndarray,            # shape (N,), the head's latent field (higher=faster)
    anchor: np.ndarray,        # shape (N,), per-driver practice min-sector pace
                               #   (lower=faster); np.nan = missing for that driver
    alpha: float,              # global blend weight in [0, 1]
) -> np.ndarray:               # shape (N,), blended pi'
```

Required behavior (each an explicit test):
1. `alpha == 0.0`: return `pi` UNCHANGED bit-for-bit (early return; do NOT even
   z-rescale — the production consumer must see the original pi when alpha=0 so
   it is a true no-op for magnitude AND ordering). Document this choice.
   (Rationale: the §7.6.3 "alpha=0" is order-equivalent to pi; returning pi
   itself is the strongest no-op and avoids perturbing downstream magnitude.)
2. Fewer than 2 drivers with a VALID (non-nan, finite) anchor: return `pi`
   unchanged (cannot standardize an anchor with <2 points; no signal to add).
3. Missing-anchor drivers (nan/non-finite): EXCLUDE them from the anchor
   z-standardization statistics, and for those drivers keep their z(pi)
   contribution only (anchor term = 0 for them). They must NOT pull the anchor
   mean/std and must NOT be dropped from the output array (output stays shape N,
   aligned to input). No silent imputation to 0 or any value — represent the
   missingness by giving them no anchor term. Document this policy in the
   docstring (canon: missingness explicit).
4. `std == 0` for pi or for the valid anchor subset: that z-term is all zeros
   (guard division by zero). If anchor std==0 there is no anchor ordering signal
   -> effectively returns z(pi) ordering (still fine).
5. Validate inputs: `pi` and `anchor` same length, `alpha` finite in [0,1];
   raise ValueError naming the field, expectation, and actual value on violation
   (canon: validate meaningful inputs).

Keep it small (well under simplification limits). Add a module docstring stating
it is the production form of the #414 §7.6.3 anchor, sign convention, and the
missingness policy.

## Piece (b): config keys threaded end-to-end

Two RUNTIME-stage keys (this is an inference post-process; no retrain):
- `quali_pace_anchor_enabled` : bool, DEFAULT `false`
- `quali_pace_anchor_alpha`   : float, DEFAULT `0.5`

Names MUST keep the `quali_pace_anchor_` prefix (a sister effort #375 adds
fusion-net keys to the same files; no collision).

Thread them following the SAME pattern as the optional runtime keys
`emit_module_record` (#371) and `qs_compound_beta_regime` (#380). Trace those
two for the exact idiom. The chain:

1. `configs/evo/gold_defaults.toml`: add the two keys. Decide the section: these
   are runtime/inference knobs -> put under a runtime-appropriate section
   consistent with how the manifest stage config is sourced. Keep the edit
   MINIMAL and localized (sister #375 also edits this file).
2. `src/evo_predictor/gold_cycle/config.py`: add to the matching dataclass
   (mirror `qs_compound_beta_regime` at lines ~26-34, ~191-205, ~369-370,
   ~415-416) with validation (alpha finite in [0,1]; enabled is bool).
3. Manifest echo: `src/evo_predictor/sampled_runtime_manifest_assembly.py`
   `assemble_sampled_runtime_manifest` builds each stage dict (lines ~82-85 add
   `modules`+`fusion`). Add an optional `quali_pace_anchor` block to the QUALI
   stage dict only (e.g. `{"enabled": ..., "alpha": ...}`), sourced from config.
4. `src/evo_predictor/pipeline_manifest_v4.py`: add an OPTIONAL anchor config to
   `RuntimeStageConfig` (NEW small frozen dataclass, e.g. `QualiPaceAnchorConfig`,
   defined HERE — do NOT put it in fusion.py). Parse it in `_stage_from_dict`
   (~line 194-202) with a SAFE DEFAULT when the `quali_pace_anchor` key is
   ABSENT (old committed manifests have no key -> must default to disabled).
   Validate alpha in [0,1].

CRITICAL: existing committed manifests (`params/gold/.../pipeline_manifest.json`,
runtime bundle manifests) do NOT have this key. The parse path MUST treat
absent-key as `enabled=False` so old manifests keep working unchanged. This is
the load-bearing back-compat requirement; add a test for "stage dict with no
quali_pace_anchor key parses to disabled".

## Piece (c): wire into the runtime stage loop

`src/evo_predictor/sampled_runtime.py`, function `_run_stage` (around line
331-365). The module loop appends each `run_module_field(loaded, pair_batch)` to
`fields` (line 358). Insert the anchor there:

- Only when `task == "quali"` AND the stage's anchor config is `enabled` AND
  `module_name == "driver_quali_power_from_race_weekend"`.
  (The module-name constant: check `src/latent_power/modules.py` —
  `DRIVER_QUALI_POWER_FROM_RACE_WEEKEND`. Import/compare the constant, do not
  hardcode the string loosely.)
- Build the per-driver anchor array aligned to the just-produced
  `ModuleFieldResult.entity_ids` ordering, reading `qs_theoretical_best` from
  `features.drivers` keyed by `driver_id` (build a `{driver_id:
  qs_theoretical_best}` map from `features.drivers`; `features` is a `_run_stage`
  param). `qs_theoretical_best` is `DriverFeatures.qs_theoretical_best`
  (models/_features.py:44). If a driver in `entity_ids` is absent from the map,
  use `np.nan` (handled by the blend's missingness policy).
- Call `blend_quali_pace_anchor(result.pi, anchor_array, alpha)`; replace the
  field via `dataclasses.replace(result, pi=blended_pi)`. Record a small
  diagnostic (e.g. into `result.diagnostics`) noting anchor applied + alpha +
  n_valid_anchor for observability (optional but encouraged; keep it in the
  replaced object's diagnostics).
- `sigma_pi` handling: KEEP `sigma_pi` UNCHANGED in this gate, and document in a
  code comment that the blend changes the `pi` ORDERING/magnitude while sigma_pi
  (the head's posterior covariance) is left as-is; the downstream-magnitude/
  fusion-precision implications are assessed in G3's downstream-impact statement.
  Do NOT attempt to recompute sigma here. (Conservative: ordering is the
  measured lever; touching sigma is out of this gate's measured basis.)

This must be the ONLY behavioral change to inference, and a no-op when disabled.

## Close Criteria
- `blend_quali_pace_anchor` exists, pure, with all behaviors above; unit tests
  (synthetic) prove: alpha=0 returns pi unchanged; alpha=1 equals z(-anchor)
  ordering; a known 2-3 driver case where the anchor flips a mis-ordered pair
  (sign-acc improves) at alpha=0.5; <2 valid anchors -> unchanged; nan drivers
  excluded from stats and kept in output; std==0 guarded; bad inputs raise
  ValueError. All green.
- Config keys present in `gold_defaults.toml`, validated in `gold_cycle/config.py`,
  echoed into the quali stage of the assembled manifest, parsed in
  `pipeline_manifest_v4` with absent-key -> disabled (tested).
- `_run_stage` applies the blend ONLY for quali + driver_quali_power_from_race_weekend
  + enabled; no-op otherwise; race/race_start untouched.
- DEFAULT OFF (gold_defaults `quali_pace_anchor_enabled=false`).
- `py -m src.utils.simplification_limits` clean on every touched src/ + tests/ path.
- Existing evo unit tests still green (no regression from the additive change).

## Allowed Scope
- NEW: `src/evo_predictor/quali_pace_anchor.py`, `tests/unit/evo_predictor/test_quali_pace_anchor.py`.
- EDIT: `src/evo_predictor/sampled_runtime.py`, `src/evo_predictor/pipeline_manifest_v4.py`,
  `src/evo_predictor/sampled_runtime_manifest_assembly.py`,
  `src/evo_predictor/gold_cycle/config.py`, `configs/evo/gold_defaults.toml`.
- May add tests to existing test modules for the manifest-parse back-compat case
  (e.g. `tests/unit/evo_predictor/test_pipeline_manifest_v4.py` if it exists).

## Specific Exclusions (OFF-LIMITS — sister effort #375 owns these)
- `src/evo_predictor/fusion.py`, `src/evo_predictor/fusion_training/**`,
  `scripts/fusion_replay/**`, `docs/evo/fusion_rework_findings.md`.
- Do NOT define the new anchor config dataclass inside `fusion.py`.
- Do NOT modify `scripts/scope_quali_anchor_414.py` or its test.
- Do NOT change race/race_start stage behavior.
- Do NOT run a gold retrain or mutate any committed params/manifest artifact.
- Do NOT touch `docs/evo/prediction_ceiling_and_priorities.md` (Commander writes §7.6.4 in G3).

## Constraints
- DB-only canon: anchor comes from an existing feature already in `RaceFeatures`;
  no new DB read, no FastF1.
- Missingness explicit; no silent impute/zero.
- One canonical path; no compat shims beyond the REQUIRED absent-manifest-key
  default (which is back-compat for generated artifacts, expected).
- Validate inputs with messages naming field/expectation/actual.
- Tunable weight (alpha) lives in config, not inlined.

## Required Evidence
- `py -m pytest tests/unit/evo_predictor/test_quali_pace_anchor.py -q` output (green).
- The manifest back-compat parse test output (green).
- `py -m src.utils.simplification_limits <each touched path>` output (clean).
- A short note: exact files changed, the config section chosen in gold_defaults.toml,
  the module-name constant used, and the sigma_pi decision.

## Verification Commands
```bash
py -m pytest tests/unit/evo_predictor/test_quali_pace_anchor.py -q
py -m pytest tests/unit/evo_predictor/ -k "manifest or quali_pace or anchor" -q
py -m src.utils.simplification_limits src/evo_predictor/quali_pace_anchor.py src/evo_predictor/sampled_runtime.py src/evo_predictor/pipeline_manifest_v4.py src/evo_predictor/sampled_runtime_manifest_assembly.py src/evo_predictor/gold_cycle/config.py tests/unit/evo_predictor/test_quali_pace_anchor.py
```

## Suggested Model Tier
Stronger — multi-file config threading with a load-bearing back-compat
requirement and a sign-convention correctness risk.

## Authority
Decided (do not re-litigate): attach point (sampled_runtime `_run_stage`),
anchor source (`qs_theoretical_best`), default OFF this gate, sigma_pi unchanged
this gate, config key names (`quali_pace_anchor_*`), the blend math + sign. You
decide: the gold_defaults.toml section, the exact dataclass/field names, internal
test structure, diagnostics shape.

## Stop Conditions
Stop and return if: an allowed-scope file must be exceeded, a specific exclusion
must be touched, the anchor (`qs_theoretical_best`) turns out NOT to be reachable
in `_run_stage` from `features`, the module-name constant differs from
`DRIVER_QUALI_POWER_FROM_RACE_WEEKEND`, or a decision outside the above authority
is needed.

## Return Format
Return IMPLEMENTER_RESULT: completed slice, files changed, test mode satisfied,
evidence (paste key test + simplification output), assumptions used, stop
conditions hit, out-of-scope observations.
