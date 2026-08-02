# Implementer Handoff — G2 (driver-utility latent estimator + explicit-unknown status + banked artifact)

## Gate
`g2-implement` (#628 Phase 3b). Worktree **C:/Programs/f1-628** ONLY. Bespoke scripts need
`PYTHONPATH=C:/Programs/f1-628`. Tests are cwd-safe. G1 is merged on this branch (the observable module +
CLI + row schema exist).

## Task
Build `src/physics/utilization/driver_utility.py`: a **partial-pooling driver-utility latent estimator** over
the G1 observable rows, with an **explicit resolved/unresolved status per axis** (reusing the estimate_store
sentinel machinery), producing a **banked artifact**.

## Protected Intent (OWNER HARD REQUIREMENT)
Every (driver, axis) carries an explicit resolved/unresolved status. Any axis with thin/insufficient support
becomes a **reserved high-uncertainty slot** (wide σ) — **NOTHING dropped silently**. Turn implicit wide-σ
into an explicit, testable "we don't know."

## Test Mode
TDD required (synthetic observable rows — do NOT need the real batch; G5 runs that).

## Close Criteria
- `estimate_driver_utility(rows_df) -> DataFrame` with one row per (year, driver, constructor, axis) and
  columns: `delta, sigma, status, tau, n_sessions, n_points, effective_sigma`.
- **δ estimation:** per (driver, axis), pool the per-session `g_deficit` values with per-session
  `sigma_lapsampling` via `pool_random_effects(values, sigmas)` → `delta = pooled.mu`, `sigma = pooled.sigma_mu`,
  `tau = pooled.tau`. This is the **teammate-relative** driver deficit (document that: δ is measured against a
  per-constructor both-teammate ceiling; within-constructor δ are mutually anchored).
- **Explicit-unknown status:** `status = "resolved"` iff `n_sessions >= MIN_RESOLVED_SESSIONS` (default 3)
  AND the axis has real support; else `status = "unresolved"`. For every row compute
  `effective_sigma = effective_axis_sigma(value=delta, sigma=sigma, status=status, reference_value=<per-axis
  deficit reference magnitude>)` — REUSED from `estimate_store_fields` (do NOT reimplement the sentinel).
  Because δ is a deficit that can be ≈0, you MUST pass a non-trivial `reference_value` = a per-axis reference
  magnitude (e.g. the population std of `g_deficit` on that axis across all drivers, floored to a small m/s
  constant) so an unresolved axis gets a genuinely WIDE reserved σ, not ≈0.
- **Nothing dropped:** every (driver, axis) that appears in the observable rows emits exactly one artifact row
  WITH a status — a driver/axis with too few sessions is emitted as `unresolved` + wide `effective_sigma`,
  never omitted.
- **Banked artifact:** `write_driver_utility_db(df, path)` persists the DataFrame to an **UNTRACKED** SQLite
  DB `data/driver_utility.db` (table `driver_utility`), idempotent (replace-on-rerun for the same slice).

## Allowed Scope
- NEW: `src/physics/utilization/driver_utility.py`, `tests/unit/physics/test_driver_utility.py`.
- READ-ONLY reuse: `src/physics/layer2/pooling.py::pool_random_effects` (+ `PooledParameter` fields
  `mu, sigma_mu, tau, k, i2, q, shrunk`), `src/physics/layer2/estimate_store_fields.py::{effective_axis_sigma,
  normalize_axis_status, UNRESOLVED_AXIS_SIGMA_FRAC}`. Do NOT modify these.

## Specific Exclusions
- Do NOT build the held-out gate (G3) or run the real batch (G5). No held-out split logic here — this gate is
  the estimator + status + artifact only, fit over whatever rows it is handed.
- Do NOT reinvent the sentinel/status machinery; reuse `estimate_store_fields`.

## Constraints
- `py` not `python`. Tests: `py -m pytest tests/unit/physics/test_driver_utility.py -q`.
- `data/driver_utility.db` is **UNTRACKED** — NEVER `git add` it.
- Respect `src.utils.simplification_limits` (complexity <=20, files <=... ; keep functions small — G1 hit this).

## Exact seam signatures (verified from source)
- `pool_random_effects(values, sigmas, *, sigma_floor=1e-9, shared_floor=0.0) -> PooledParameter`.
  `PooledParameter(mu, sigma_mu, tau, k, i2, q, shrunk)`. k==1 returns the single session's own (value, sigma).
- `effective_axis_sigma(value: Optional[float], sigma: Optional[float], status: Optional[str], *,
  reference_value: Optional[float]=None) -> Optional[float]`. `status=="resolved"` → sigma unchanged; else
  widens to `>= UNRESOLVED_AXIS_SIGMA_FRAC(=1.0) * abs(value or reference_value)`.
- `normalize_axis_status(status) -> str` (None → "unresolved").

## Map Anchors (inbound)
- **Structural:** `struct:physics.utilization` — new driver_utility.py; reuse pooling + estimate_store_fields.
- **Capability:** driver-utility latent (race-history prior), banked artifact.
- **Constraints:** OWNER HARD explicit resolved/unresolved status; reserved slots; nothing dropped silently.
- **Decision:** decision pressure — additive teammate-relative latent (surfaced at reconcile).
- **Evidence:** shrinkage of thin drivers; status-flip below support; full-axis coverage; artifact schema.

## Deliverable Path Check
- **Committed:** `src/physics/utilization/driver_utility.py`, `tests/unit/physics/test_driver_utility.py` —
  `git check-ignore` each, confirm exit 1.
- **Local-only (untracked):** `data/driver_utility.db`.

## Required Evidence
- `py -m pytest tests/unit/physics/test_driver_utility.py -q` full pass.
- A test proving: (a) a thin (1–2 session) driver's δ has status="unresolved" and `effective_sigma` widened to
  the reserved scale; (b) a well-supported driver has status="resolved" and δ ≈ the DL-pooled mean; (c) EVERY
  (driver,axis) in the input emits a row (nothing dropped); (d) shrinkage: a noisy thin driver's δ pulls
  toward the population/axis mean relative to its raw mean.

## Verification Commands
```bash
cd /c/Programs/f1-628 && py -m pytest tests/unit/physics/test_driver_utility.py -q
cd /c/Programs/f1-628 && py -m src.utils.simplification_limits src/physics/utilization/driver_utility.py
```

## Suggested Model Tier
simple bounded — pooling + sentinel are reused seams; the one subtlety is the `reference_value` for unresolved δ.

## Authority
Construction decided by the Commander (teammate-relative additive latent; reuse the sentinel). Do not re-open.
If `pool_random_effects`/`effective_axis_sigma` signatures differ from above, STOP and return.

## Stop Conditions
Stop and return if: allowed scope exceeded, a cited seam signature mismatches source, the explicit-unknown
contract cannot be satisfied by reusing `effective_axis_sigma`, or the artifact needs a tracked data file.

## Return Format
Return IMPLEMENTER_RESULT: completed slice, files changed, test mode satisfied, evidence (pytest +
simplification-limits output), assumptions, stop conditions hit, out-of-scope observations, workflow feedback.
