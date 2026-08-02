# Implementer Handoff — G3 (hierarchical Student-t shrinkage fit, both channels, strictly-pre)

## Gate
g3-implement (issue #666, epic #659)

## Task
Build `src/physics/fingerprint/fit.py` — the slow-offline-loop fit that reads #664's `driver_class_observables`,
runs hierarchical Student-t shrinkage (field → driver-overall → class cell + class-across-drivers parent,
recency-weighted, both channels, strictly-pre), and writes exactly-k cells into the G2 `DriverFingerprintStore`.

## Protected Intent
This fit is the keystone: a leaked future row, an under-priced σ, a double-priced σ, or a G-perturbed point value
all silently miscalibrate every downstream consumer. The strictly-pre cutoff and the once-priced σ are the crown
invariants — make them structural.

## Test Mode
TDD required — the acceptance invariants ARE the test surface. Tests in
`tests/unit/physics/fingerprint/test_fit.py`, TEMP/scratch DBs only (#656). You MAY build tiny synthetic
observable DBs in the tests (temp) to drive precise leak/idempotence/G assertions.

## Consume (do NOT edit): the #675 verdict + the primitives
- The commander-adjudicated **#675 verdict** (see `.agent-work/666-driver-fingerprint/notes-666.md`): class-axis
  under-coverage GENERALIZES on both channels → APPLY a class-level `shared_floor` PER CHANNEL, **derived from the
  real fit's own class-effect variance component: `shared_floor = sqrt(fit_two_way(...).var_circuit)`** (NOT the
  synthetic 0.30), applied EXACTLY ONCE via `pool_random_effects(shared_floor=...)`. Do NOT floor the
  driver-overall level (out of #675 scope — bounded-slice artifact).
- `src/physics/layer2/pooling.py`: `fit_two_way(values, teams, circuits) -> TwoWayPool` (grand_mean,
  team_effects, circuit_effects, var_team, **var_circuit**, var_resid, frac_*, predict(team,circuit)); and
  `pool_random_effects(values, sigmas, *, shared_floor=0.0) -> PooledParameter` (its k==1 branch returns
  `sigma_mu = hypot(sigma0, shared_floor)` — the single-cell floor you want). CONSUME both; do NOT edit them.
- `src/common/student_t.py`: `predictive_t(mu, sigma, n_eff, *, nu_loss, rule) -> PredictiveT`,
  `FormulaRule()`, `DEFAULT_NU_LOSS` (=4.0). CONSUME; do NOT edit.
- `src/physics/fingerprint/frozen_constants.py`: `FINGERPRINT_RECENCY_HALFLIFE_ROUNDS` (5.0),
  `FINGERPRINT_UNRESOLVED_SUPPORT_FLOOR` (1.0). `src/physics/fingerprint/{address,vocabulary,store}.py` (G2).

## Close Criteria (each proven by a test)
- `fit_driver_fingerprints(observables_db_path, store, *, as_of_round, era, vocabulary, season, ...)` —
  `as_of_round` is REQUIRED with NO default (a call omitting it is a TypeError).
- **STRICTLY-PRE CUTOFF over the ENTIRE input set:** the fit filters ALL `driver_class_observables` rows to
  `round_idx <= as_of_round` BEFORE any pooling — this cut applies to the target driver AND to the rows feeding
  the class-across-drivers parent AND the field mean (which pool OTHER drivers). No `round_idx > as_of_round` row
  may influence ANY cell via any pooling level.
- Keep only the k severity classes (`class LIKE 'severity:%'`); EXCLUDE `straight` and `braking_zone`. Refuse via
  `vocabulary.require_fittable()` unless PASS/override.
- **Hierarchy:** per channel, aggregate each (driver, class) cell over its rounds with RECENCY weighting
  `w = 0.5 ** (Δround / FINGERPRINT_RECENCY_HALFLIFE_ROUNDS)` (Δround = as_of_round − round_idx ≥ 0), giving a
  recency-weighted cell value + a recency-effective support `n_eff` (recency-weighted sum of `n_points`). Feed the
  per-(driver,class) values to `fit_two_way(values, teams=drivers, circuits=classes)`. Cell point =
  `grand_mean + driver_effect[driver] + class_effect[class]` (= `TwoWayPool.predict`). The class-across-drivers
  parent = `grand_mean + class_effect[class]`; driver-overall = `grand_mean + driver_effect[driver]`.
- **σ composition at a SINGLE structural site, each component added exactly ONCE:**
  `sigma_cell = sqrt(sigma0^2 + shared_floor^2 + g_sigma_onesided^2 + sigma_lapsampling^2)` where
  - `sigma0` = a principled base cell scale (e.g. the within-group naive SEM of the cell's recency-weighted
    observations, or the fit's residual scale — document your choice);
  - `shared_floor = sqrt(var_circuit)` for THIS channel (the #675 class-effect-variance floor), applied via
    `pool_random_effects(shared_floor=...)` — the SINGLE pricing site;
  - `g_sigma_onesided` = the #664 one-sided σ⁺ (0.0 in current data → soft-degrades, byte-identical point);
  - `sigma_lapsampling` = carried as a PRESENT-but-zero component (dormant NULL → 0), NOT dropped.
  Store `(mean=cell_point, sigma=sigma_cell, support_n=n_eff, status, shared_floor_applied=shared_floor)`.
  The predictive distribution is `predictive_t(mean, sigma_cell, n_eff, nu_loss=4.0, rule=FormulaRule())`
  (build it where consumed; store the (mean, sigma) pair).
- **Thin/unresolved:** a cell with recency-effective support < `FINGERPRINT_UNRESOLVED_SUPPORT_FLOOR` → written as
  `status="unresolved"` (never a missing row). Exactly k cells per (driver, era, channel) always.
- **BOTH channels:** time (`time_deficit_s`) and energy (`deployment_share`). Both written (channel dim).
- **Slow-offline mutation only; NO fit-on-read** — the fit is an explicit function a batch/offline caller runs;
  the store never invokes it on read (already structural in G2 — do not add a back-edge).

## Tests (test_fit.py, temp DBs) — the acceptance surface
- **Cutoff-leakage KEYSTONE** (cite #628's measured 14.6× materiality precedent in the test docstring): build a
  temp observables DB; fit with `as_of_round=R`; assert TWO poison forms leave the target cell (mean AND sigma)
  BYTE-IDENTICAL to the clean fit: (a) an added TARGET-driver row at `round_idx>R`, AND (b) an added NON-TARGET
  driver row at `round_idx>R` (proves the parent/field pooling is also cut). Both must be no-ops.
- **σ-widening priced ONCE:** (i) idempotence — re-invoking the pricing op on an already-floored σ == applying it
  once (no double-floor); (ii) single-site — the shared_floor enters at exactly one place (assert via a structural
  check, e.g. the fit calls the flooring site once per cell; a spy/count or a single-call design).
- **G σ⁺=0 byte-identical point:** fit with g_sigma_onesided=0 vs a nonzero value on a temp cell; assert the POINT
  (mean) is byte-identical (only σ differs).
- **sigma_lapsampling slot present-and-zero:** the σ composition includes the sigma_lapsampling component and it
  is 0 when NULL (assert the slot is present, not dropped).
- **Recency weighting:** a recent round outweighs an old one (a monotone assertion).
- **Both-channel fit:** time + energy cells both written for a (driver, era).
- **as_of_round required:** calling without it raises TypeError.
- **k-cells + unresolved:** a class with no in-cutoff support → unresolved row; exactly k cells returned.

## Allowed Scope
CREATE `src/physics/fingerprint/fit.py` + `tests/unit/physics/fingerprint/test_fit.py`. READ-ONLY: pooling.py,
student_t.py, the G2 fingerprint modules, frozen_constants.py, `reference_utilization_store.py` (to read the
observables schema — column names in the recon: `year, session_type, gp_name, round_idx, constructor, driver,
class, map_version, speed_deficit, time_deficit_s, n_points, sigma_lapsampling, g_sigma_onesided,
deployment_share, deployment_phase_fraction, ...`). You MAY read the real slice DB read-only to sanity-check, but
the tests must use temp synthetic DBs.

## Specific Exclusions
Do NOT edit pooling.py/student_t.py/driver_utility.py (#675). Do NOT floor the driver-overall level. Do NOT run
the full-season pipeline / any online call. Do NOT build the G4 end-to-end validation (that is G4). Do NOT change
the G2 store schema (additive migration only if truly needed — surface it first).

## Constraints
- Interpreter PIN + `PYTHONPATH=.`; `from src...` imports.
- as_of_round REQUIRED no default; cutoff over ENTIRE input set.
- σ priced once at a single site; byte-identical point under G σ⁺=0; sigma_lapsampling present-but-zero.
- No data/.agent-work blob staged.

## Map Anchors (inbound)
- **Structural:** NEW `struct:physics.fingerprint.fit`; `struct:physics.layer2` fit_two_way/pool_random_effects;
  `struct:common` predictive_t.
- **Decision anchors:** `decision:c1_driver_utilization_design` — strictly_pre load-bearing; 14.6× precedent.
  `@grade: settled/measured · leans g3-implement`
  `decision:pooled_sigma_shared_systematic_floor` — class-axis shared_floor. `@grade: settled/measured · leans g3-implement`
- **Constraints/assumptions:** as-of cutoff; no baked-in normality (predictive_t); no race-outcome leakage.
- **Evidence expectations:** `claim: cutoff-leakage` (keystone), `claim: sigma-priced-once`, `claim: G-byte-identical`.

## Deliverable Path Check
- Committed: `src/physics/fingerprint/fit.py`, `tests/unit/physics/fingerprint/test_fit.py` (check-ignore exits 1).
- Local-only: temp test DBs (pytest tmp_path).

## Required Evidence
- LOAD-BEARING (prove rigorously): the cutoff-leakage keystone (both poison forms), σ-priced-once (idempotence +
  single-site), G byte-identical — paste each test's pass. Full `tests/unit/physics/fingerprint/test_fit.py` green.
- Confirmatory: `simplification_limits --paths src/physics/fingerprint/fit.py tests/unit/physics/fingerprint/test_fit.py`; clean git status.

## Verification Commands
```bash
cd C:/Programs/f1brainz-wt/epic659-666
PYTHONPATH=. "C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe" -m pytest tests/unit/physics/fingerprint/test_fit.py -q
PYTHONPATH=. "C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe" -m src.utils.simplification_limits --paths src/physics/fingerprint/fit.py tests/unit/physics/fingerprint/test_fit.py
```

## Suggested Model Tier
Stronger — the fit is the invariant-dense heart; the parent-side cutoff and once-priced σ are subtle.

## Authority
The hierarchy shape, the #675 shared_floor derivation (sqrt(var_circuit) per channel), the cutoff semantics
(entire input set), and the σ-once rule are commander-decided. You MAY choose `sigma0`'s base definition + the
recency-aggregation mechanics — document them. Do NOT weaken any invariant.

## Stop Conditions
Stop and return if: an invariant cannot be made structural; fit_two_way's outputs don't support the hierarchy as
specified; the σ composition can't be priced at one site; you'd need to edit a forbidden file or change the G2 schema.

## Return Format
Return IMPLEMENTER_RESULT: completed slice, files changed, test-mode satisfied, evidence (paste the keystone +
σ-once + G tests and the full test_fit run + simplification_limits), assumptions (sigma0 base, recency mechanics),
stop conditions, out-of-scope, workflow feedback. Write to
`.agent-work/666-driver-fingerprint/crew-handoffs/g3-implement-result.md` AND SendMessage a concise summary to
`cmdr-666` before ending your turn.
