# Implementer Handoff — G1 (#675 diagnosis + frozen-constant pre-registration)

## Gate
g1-implement (epic659/666-driver-fingerprint; issue #666, epic #659 Wave 3)

## Task
Create the new `src/physics/fingerprint/` package's pre-registered frozen constants, plus a #675 class-axis
coverage diagnostic that reproduces the #665 coverage method on the REAL bounded driver×class slice, and
emit a per-channel verdict (does the class-axis `predictive_t` under-coverage generalize to real data?).

## Protected Intent
The #675 verdict gates whether the G3 fit applies a class-level `shared_floor`. It must rest on a POWERED,
well-defined coverage measurement — NOT a circular or under-powered one. Frozen constants must be
pre-registered (values fixed BEFORE this run) so nothing is tuned to observed numbers (Ruling F12).

## Test Mode
Test-after allowed for the diagnostic script (it is a research diagnostic, not promoted logic); the
frozen-constants test is a plain assertion test. The coverage script MUST be run and its verdict JSON pasted.

## Close Criteria
- `src/physics/fingerprint/__init__.py` exists (package marker).
- `src/physics/fingerprint/frozen_constants.py` defines a single pre-registered named set `FINGERPRINT_FROZEN`
  (a frozen dataclass or a module-level mapping) with EXACTLY these commander-pre-registered values, each with
  a one-line docstring/comment stating it is pre-registered before the first real-data run (Ruling F12):
  - `FINGERPRINT_NOMINAL_COVERAGE_LEVEL = 0.80`
  - `FINGERPRINT_UNDER_COVERAGE_BOUND = 0.60`  (class-axis empirical coverage below this = materially under-covered; aligned with #665 `CALIBRATION_COVERAGE_THRESHOLD`)
  - `FINGERPRINT_RECENCY_HALFLIFE_ROUNDS = 5.0`
  - `FINGERPRINT_UNRESOLVED_SUPPORT_FLOOR = 1.0`  (summed `n_points` below this → unresolved cell)
  Do NOT invent extra constants. Do NOT read/tune these from the slice.
- `scripts/fingerprint_class_coverage_675.py` runs offline and emits the verdict JSON (below).
- `tests/unit/physics/fingerprint/__init__.py` + `tests/unit/physics/fingerprint/test_frozen_constants.py`
  assert each `FINGERPRINT_FROZEN` value == the pre-registered value above, finite, non-negative.
- Verification commands below pass.

## The #675 coverage method — PIN THIS EXACTLY (load-bearing; the critic flagged circularity/underpower)
Reference the existing harness for the method: `scripts/pooling_imbalance_validation_665.py` (READ IT; do not
edit it). Reproduce its coverage measurement, adapted to real support structure:

**PRIMARY verdict = synthetic-recovery with KNOWN injected truth, driven by the REAL slice's per-cell support counts.**
1. Read the real slice DB (`--slice-db`, default `.agent-work/666-driver-fingerprint/artifacts/fp_slice_2023Q.db`),
   table `driver_class_observables`. Keep only the k=4 corner-severity classes (`class LIKE 'severity:%'`);
   EXCLUDE `straight` and `braking_zone`. Entities: drivers = {LEC, PER, SAI, VER}; classes = the 4 severity ids.
2. From the real rows, extract the per-(driver, class) SUPPORT COUNTS `n_points` (sum across the 4 circuits per
   driver×class cell) — this is the real imbalance the fit sees. (This mirrors #665's use of a real per-driver
   lap marginal × class shares, but uses the ACTUAL realized cell counts instead of a proxy profile.)
3. Generative model (as in #665): `y[d,c] = grand_mean + true_driver_effect[d] + true_class_effect[c] + N(0, obs_sigma)`,
   with `driver_sigma`, `class_sigma`, `obs_sigma` taken from #665's constants (driver_sigma=0.15,
   class_sigma=0.30, obs_sigma=1.0) for the TIME channel; for the ENERGY channel scale to that channel's own
   spread (fit the same structure on `deployment_share`-scaled effects; state the sigmas you use).
4. For `N_REPS >= 200` reps: draw true effects + per-cell observations at the real support counts, fit
   `fit_two_way(values, teams=drivers, circuits=classes)`, and for EACH axis wrap the shrunk axis effect in
   `predictive_t(eff, sem, n_eff, nu_loss=4.0, rule=FormulaRule())` where `sem` is the naive within-group
   standard error and **`n_eff` = the summed observation count backing that axis estimate (NOT the pooled
   `.n` group count)** — this is the exact subtlety #665 uses. Then `lo,hi = pt.interval(0.80)` and
   `hit = int(lo <= true_val <= hi)`. Accumulate hits over reps×entities per axis.
5. Empirical coverage = hits/n per axis, WITH a binomial 95% CI (so the generalizes flag doesn't flip on noise).
   Run this for BOTH channels (time, energy) and BOTH axes (driver, class).

**SECONDARY (descriptive only, flag as a DIFFERENT quantity):** a leave-one-out / held-out empirical coverage
on the REAL `time_deficit_s` values (predict each held-out cell from the rest, check the 0.80 interval covers
the held-out observation). Report it but state plainly it measures observation-level predictive coverage, not
the epistemic class-effect interval coverage the PRIMARY measures.

**Verdict JSON** → `.agent-work/666-driver-fingerprint/artifacts/coverage_675_verdict.json`:
- per (channel, axis): empirical coverage + binomial 95% CI + n_reps.
- `class_vs_driver`: the class-axis vs driver-axis coverage gap per channel.
- `generalizes` per channel: `true` iff class-axis empirical coverage's CI UPPER bound < `FINGERPRINT_UNDER_COVERAGE_BOUND` (0.60).
- `shared_floor_recommendation` per channel: if generalizes, a recommended additive σ floor for the class
  level (e.g. `sqrt(class_sigma_component)` — state your derivation; it is applied later in G3 via
  `pool_random_effects(shared_floor=...)`), else `0.0` / "no action needed".
- A short prose `interpretation`.

## Allowed Scope
CREATE: `src/physics/fingerprint/__init__.py`, `src/physics/fingerprint/frozen_constants.py`,
`scripts/fingerprint_class_coverage_675.py`, `tests/unit/physics/fingerprint/__init__.py`,
`tests/unit/physics/fingerprint/test_frozen_constants.py`. READ-ONLY: `scripts/pooling_imbalance_validation_665.py`,
`src/physics/layer2/pooling.py`, `src/common/student_t.py`, `src/physics/layer2/frozen_constants.py`, the slice DB.

## Specific Exclusions
Do NOT edit `pooling.py`, `student_t.py`, `driver_utility.py` (#675 forbids it — CONSUME them). Do NOT build the
store/vocabulary/fit (G2/G3). Do NOT run the full-season pipeline or any online FastF1 call. Do NOT regenerate
the slice — it is provided.

## Constraints
- Interpreter PIN `C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe`; NEVER bare `py`. Run
  everything from the worktree root with `PYTHONPATH=.` (editable-.pth trap: else you import MAIN-repo src/).
- No new inline literals — the 4 values live only in `FINGERPRINT_FROZEN`. Consume `#660`
  `src/physics/layer2/frozen_constants.py` if a value already exists there (none of these do).
- Do NOT stage/commit any `.agent-work/` path or any `data/` blob.
- `import` style is `from src.physics... import ...` / `from src.common.student_t import ...`.

## Map Anchors (inbound)
- **Structural:** `struct:physics.layer2` `pooling.fit_two_way` / `pool_random_effects` (shared_floor);
  `struct:common` `student_t.predictive_t`/`FormulaRule`; NEW `struct:physics.fingerprint frozen_constants`.
- **Capability:** #675 class-axis coverage investigation (gates the G3 class intervals).
- **Constraints:** frozen constants F12 (pre-register before first real fit).
- **Decision anchors:** `decision:pooled_sigma_shared_systematic_floor` — `shared_floor` is the class-axis lever.
  `@grade: settled/measured · leans g1-implement,g3-implement`
- **Evidence expectations:** `claim: #675-coverage` — real class-axis coverage measured vs level 0.80.

## Deliverable Path Check
- Committed: `src/physics/fingerprint/__init__.py`, `src/physics/fingerprint/frozen_constants.py`,
  `scripts/fingerprint_class_coverage_675.py`, `tests/unit/physics/fingerprint/__init__.py`,
  `tests/unit/physics/fingerprint/test_frozen_constants.py` — each `git check-ignore <path>` exits 1 (not ignored).
- Local-only (gitignored, NOT in diff): `.agent-work/666-driver-fingerprint/artifacts/coverage_675_verdict.json`
  and the read-only input `.agent-work/666-driver-fingerprint/artifacts/fp_slice_2023Q.db`.
- These are NEW files: `git diff` will not show them until staged; they appear in `git status`.

## Required Evidence
- LOAD-BEARING (prove rigorously): the coverage script's stdout + the verdict JSON contents (paste it);
  the frozen-constants test output.
- Confirmatory: `git check-ignore` exit codes; a `git status --porcelain` snapshot showing no data/.agent-work staged.

## Verification Commands
```bash
cd C:/Programs/f1brainz-wt/epic659-666
PYTHONPATH=. "C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe" scripts/fingerprint_class_coverage_675.py --slice-db .agent-work/666-driver-fingerprint/artifacts/fp_slice_2023Q.db
PYTHONPATH=. "C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe" -m pytest tests/unit/physics/fingerprint/test_frozen_constants.py -q
```

## Suggested Model Tier
Stronger reasoning — the coverage-method fidelity (n_eff semantics, injected-truth-over-real-support, binomial CI)
is subtle and load-bearing; a wrong harness poisons the #675 verdict.

## Authority
The 4 frozen values + the coverage METHOD are commander-decided (pre-registered) — do NOT change them. You MAY
choose the energy-channel injected sigmas and the exact shared_floor derivation formula — state them. You do NOT
decide the final apply/no-apply #675 disposition (the commander adjudicates at integrate from your numbers).

## Stop Conditions
Stop and return if: the slice DB is missing/malformed; the #665 method cannot be reproduced faithfully; a
constant would need a value other than the pre-registered ones; you would need to edit a forbidden file.

## Return Format
Return IMPLEMENTER_RESULT: completed slice, files changed, test mode satisfied, evidence produced (paste the
verdict JSON + test output), assumptions used (energy sigmas, shared_floor derivation), stop conditions hit,
out-of-scope observations, workflow feedback. Deliver the result via SendMessage to cmdr-666 before ending your turn.
