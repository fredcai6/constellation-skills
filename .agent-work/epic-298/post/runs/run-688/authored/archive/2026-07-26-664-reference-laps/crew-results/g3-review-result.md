# Review Result

## Assigned Gate
`g3-review` — issue #664, epic #659 (class utilization observable + one-sided G band + relative energy)

## Result
`APPROVE`

## Handoff compliance
Delivered exactly the assigned scope: the two new files
(`src/physics/utilization/class_utilization_observable.py`,
`tests/unit/physics/test_class_utilization_observable.py`) plus the additive
`driver_class_observables` code in `reference_utilization_store.py`. All eight Close
Criteria were independently REPRODUCED (not read from the report), each a binding
epic-owner pre-ruling:

1. **G moves ONLY the one-sided σ⁺; point deficit byte-identical.** Reproduced: with
   `grip=(0.30,0.05)` vs `grip=None`, `speed_deficit_by_class`, `time_deficit_by_class`,
   and `lap_time_deficit_s` are `array_equal`/`==`. `g_sigma_onesided` is `0.0` without G,
   `>0` with G. Every band's `point_deficit == time_deficit` (μ never a point shift). Band
   is one-sided upward (`upper_bound(0.9) ≥ loc`), collapses to the point at zero scale.
2. **Heavy-tailed, not Gaussian.** `DEFAULT_NU_LOSS = 4.0`; half-t `upper_bound(0.99)=4.60`
   > Gaussian folded `2.58`. Built from `src.common.student_t.PredictiveT`.
3. **G consumed, not re-fit; μ on zero.** Grep confirms `get_grip_at` is imported/called;
   no `grip_baseline`, no `.fit_`. μ stays zero (band loc unshifted; #678 not attempted).
4. **σ⁺-from-G units — see explicit judgement below.** Coherent.
5. **Energy RELATIVE.** Reproduced invariance to a +1234.5 additive specific-energy offset
   (shares, phase fraction, total all identical). No absolute SOC/kW (reads `np.diff` of
   specific energy only). Elevation-convention FINDING stated in the docstring (single KE
   channel suffices; `g·h` common-mode cancels). Scope-noted DESCRIPTIVE/instrument, not gated.
6. **Store.** `driver_class_observables` faithfully mirrors the sibling
   `driver_utility_observables` schema (`year, session_type, gp_name, round_idx,
   constructor, driver`), replaces `axis`→`class` and `g_deficit`→`speed_deficit`, adds
   `map_version, time_deficit_s, g_sigma_onesided, deployment_share,
   deployment_phase_fraction`; escalation columns present-but-DORMANT (verified NULL);
   `INSERT OR REPLACE` idempotent; additive `_migrate_missing_class_columns`; own-db
   (`data/reference_utilization.db`); temp-DB tests. `reference_laps` UNCHANGED — its 8 g2
   tests still green and both tables coexist.
7. **Deficits use g1 `class_deficits` (absolute, no ratio)** — returned verbatim; a direct
   `class_deficits` call equals the observable's fields.
8. **`pytest ... -q` → 23 passed in 0.51s.** Reproduced.

## Scope drift
No exclusions touched. No point-G subtraction (byte-identical proven); no G re-fit (grep
clean); μ never off zero; no absolute SOC/kW; no ERS inference; no race-side observable
(uses `strictly_pre` ideal); `reference_laps` untouched; no new physical/threshold literal
minted (`derate_flag` deliberately left dormant); `simplification_limits` PASS on both files.

## Evidence verdict
Every IMPLEMENTER_RESULT claim reproduced from the **worktree** copy (confirmed
`mod.__file__` resolves into the worktree, avoiding the editable-install `.pth` trap), via
an independent script + the test suite. Truth-anchored per CREW_CONTEXT physics levels:
L1 analytical (`hypot(0.3,0.4)=0.5`), L2 invariants (offset-invariance, sign-insensitivity),
L3 degenerate (zero-scale band collapse). Evidence is sufficient and genuinely demonstrates
the behavior.

## σ⁺-units question — explicit judgement (COHERENT, not a blocker)
`get_grip_at` returns `(mu, sigma)` where `mu` is the fitted grip **pace level in seconds**
and `sigma` its propagated uncertainty (same units). `onesided_sigma_from_grip` computes
`σ⁺ = hypot(mu, sigma)` → a band **width in seconds**.

The band is attached **only** to the per-class **time deficit** (`time_deficit_by_class`,
seconds). Verified empirically: every band's `point_deficit` equals a time-deficit value,
and **no** band equals any `speed_deficit` value; the observable exposes `speed_deficit_by_class`
as a plain array with **no** associated band. So σ⁺ (seconds) attaches to a seconds quantity
— **dimensionally coherent**. The feared failure mode ("a second-scaled σ⁺ silently attached
to an m/s speed deficit without conversion") **does NOT occur** — the speed deficit carries
no band at all. The docstring documents this ("wrapping the per-class TIME deficit").

One honest nuance (already routed to triage by the implementer, not a defect): `mu` is a
**whole-session lap-pace** grip level while `time_deficit_s` is a **per-class transit-time**
deficit — both seconds, but at different aggregation grains, so combining them yields a
conservatively WIDE one-sided envelope at the per-class grain. That is a magnitude/scale
modeling generosity, not a units incoherence, and it wants an explicit scale-reconciliation
ruling. Flagged as a triage candidate, not a blocker.

## Code/doc quality
Minimal, cohesive, well-tested. Docstrings explain WHY (binding pre-rulings, the
elevation-convention finding) per the project convention, not deodorant. Fowler pass driven
over all 12 baseline smells (`verify_fowler_pass.py` EXIT=0):
- **flagged (observation):** `duplicated-code` — `_migrate_missing_columns` /
  `_migrate_missing_class_columns` are near-identical 4-line additive-heal loops, and the
  write/get/has/count method pairs mirror between the two tables; parameterizable to a shared
  `_migrate(con, table, cols)`. LOW severity, rule-of-three not yet crossed — not a blocker.
- **overridden (logged):** `large-class` + `divergent-change` (own-db one-store-per-DB
  convention #632 / estimate_store mirror); `data-clumps` (established store method-signature
  convention); `speculative-generality` (launch-order-blessed dormant escalation columns).
- All other smells absent.

## Map impact verdict
- **Evidence supports claimed change:** yes — reproduced.
- **Constraints not violated:** frozen-constants, no-normality, own-db, tests-clean-real-dbs,
  pre-quali, anti-circularity all honored.
- **Notes match the diff:** yes — one new module + one additive sibling table; `reference_laps`
  untouched; consumes g1 `class_ledger`, `grip_store.get_grip_at`, `src.common.student_t` as
  anchored.
- **Decision candidates surfaced:** yes — no contradiction of the settled/inherited G
  one-sided wrap or `decision:c1_driver_utilization_design` (settled/human); no FLOAT needed.
- **Durable context routed:** two triage candidates recorded (below).

## Reconciliation check
No divergence from recorded architecture requiring reconcile. Aligns with
`struct:physics.utilization`. Escalation columns are a documented, launch-order-blessed
dormant exception.

## Blockers
- None.

## Out-of-scope observations
- **Triage candidate 1 (G pace-unit reconciliation):** `g_sigma_onesided` is a whole-session
  lap-pace grip width applied as the per-class transit-time band width — coherent (seconds on
  seconds) but grain-mismatched, yielding a conservatively wide envelope. Wants an explicit
  scale-reconciliation ruling. (Implementer already flagged.)
- **Triage candidate 2 (real derate_flag):** the dormant `derate_flag`/`escalation_*` columns
  need an energy-threshold ruling before a computed derate can be activated (would mint a new
  physical threshold). Owner decision required.
- **Minor (duplicated-code):** consider a shared `_migrate(con, table, cols)` helper if a
  third table joins this store.

## Workflow Feedback
- **Handoff gaps:** The "Allowed Scope / Read-only" list names
  `build_driver_utility_observables.py` and `driver_utility_observable.py`; the first does not
  exist under `src/physics/utilization/` (the actual sibling-schema source is
  `src/physics/utilization/driver_utility.py`, whose docstring documents the persisted schema,
  and `scripts/build_driver_utility_observables.py`). Minor — I located the real schema by
  grep — but the read-only pointer was mis-pathed.
- **Context rediscovered:** Had to open `grip_store.get_grip_at` to confirm `mu` is a
  pace-*second* level (the handoff asserted "grip PACE-seconds" but the σ⁺-units check is
  load-bearing, so the unit had to be confirmed at source). Worth carrying the `get_grip_at`
  return-unit citation in the handoff's σ⁺-units bullet.
- **Instructions improvised around:** None — the reviewer skill, engine, and Fowler rail
  covered the workflow cleanly.
- **What would have made this easier:** Fix the read-only file path
  (`driver_utility.py`, not `build_driver_utility_observables.py`) and cite `get_grip_at`'s
  return units inline.

## Return status
`complete`
