# Implementer Handoff — g3 (class-grain utilization observable + one-sided G band + energy)

## Gate
g3-implement (issue #664, epic #659, delegated). Worktree
`C:/Programs/f1brainz-wt/epic659-664`. Interpreter PIN:
`C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe` — NEVER bare `py`.

## Task
Deliver `src/physics/utilization/class_utilization_observable.py`: the per-driver,
per-CLASS utilization observable, plus extend the g2 store DB with a
`driver_class_observables` table. The observable is:
1. **Point deficit** — per-class ABSOLUTE transit-time (s) AND speed (m/s) deficit via g1
   `class_ledger.class_deficits(segment_map, distance_m, v_ideal, v_real)`. `v_ideal` is the
   driver's constructor `strictly_pre=True` ceiling simulated lap; `v_real` is the driver's
   real lap on the shared grid. (This point value is what G must NOT change — see below.)
2. **One-sided G uncertainty band** — a σ⁺ component wrapping module-G, per the binding
   pre-ruling.
3. **Energy channel** — RELATIVE deployment, descriptive/instrument this run (finding first).

## ⚠️ BINDING PRE-RULING — G is a ONE-SIDED directed uncertainty, NOT a point subtraction
- G is consumed as **μ=0, one-sided σ⁺, half/truncated Student-t on the "grip only improves"
  side**; circuit-agnostic; evolution shape = ramp-to-plateau (already the shape of #663's
  `offset + asymptote*(1-exp(-rate*x))`).
- **Do NOT subtract a point G.** The utilization POINT deficit is UNCHANGED by G. G ONLY adds
  a one-sided σ⁺ component to the deficit's uncertainty (the "grip could have flattered the
  real lap, so the true deficit could be LARGER" direction — one-sided). "G barely moves
  utilization" is the CORRECT, expected first-pass outcome, NOT a failure — state it honestly.
- **Consume, do NOT re-fit G.** Use `src/physics/layer2/grip_store.py`
  `get_grip_at(store, year, gp_name, session_type, cumulative_track_laps) -> (mu, sigma)`.
  Wrap it to the (μ=0, σ⁺) contract at THIS consumer boundary: use G's magnitude/`sigma` as
  the SCALE of the one-sided band; do NOT apply G's `mu` as a point shift. Sharpening G
  (moving μ off zero) is **#678, OUT OF SCOPE** — do not attempt it.
- Represent the band with the project's heavy-tailed machinery `src/common/student_t.py`
  (`predictive_t`, `DEFAULT_NU_LOSS`, `FormulaRule`) — a HALF/truncated Student-t, NOT a
  Gaussian (no baked-in normality). If the merged G module exposes only a point+sigma (it
  does), that is exactly the wrap point.

## ⚠️ ENERGY CHANNEL — finding FIRST, then build; relative-not-absolute; descriptive/instrument
- SEQUENCE: do the cheap **elevation-convention FINDING first** — does the deployment-focused
  channel need the total-mechanical-energy (½v²+g·h) convention on elevation circuits, or does
  relative deployment vs the car's own rolling baseline + phase structure + derate flags
  suffice? STATE your finding in the module docstring + the result. Let the finding decide
  single-vs-dual channel BEFORE building it (do not build both then rationalize).
- Energy is **RELATIVE deployment**, NEVER absolute SOC or kW (2026 rampdown → curved ramps,
  not cliffs). A thin, honest PROXY relative to the car's own rolling baseline (+ phase
  structure + derate flags) is acceptable — there is no ERS/SOC channel in the telemetry, so
  an absolute figure would be fabricated. State the proxy's honest scope explicitly.
- Energy is **DESCRIPTIVE / instrument this run** — it is NOT gated by the g4 jackknife
  (its pre-registered §7 comparison is downstream). Scope-note this in the module + result.
- Do NOT import the #682 energy-vocabulary work (separate epic).

## Store extension
Extend the g2 own-DB (`reference_utilization_store.py`'s DB, or a sibling table in the same
own db — your choice, document it) with a `driver_class_observables` table that MIRRORS the
existing `driver_utility_observables` schema
(`scripts/build_driver_utility_observables.py:65-84`: year, session_type, gp_name, round_idx,
constructor, driver, ...) PLUS: `class` (the g1 `(2+k)` class label), `map_version`, the
energy channel column(s), and the ONE-SIDED `g_sigma_onesided` column. Escalation columns
DORMANT from day one (present-but-unused — a launch-order-blessed exception to
lowest-dimensionality; note it). `INSERT OR REPLACE` idempotent; additive migrate; own-db;
tests temp-DB only.

## Test Mode
Test-after allowed; SYNTHETIC data + temp DB only (#656). The live end-to-end is g4.

## Close Criteria
- G moves ONLY the one-sided σ⁺; the point deficit is byte-identical with and without the G
  wrap (a unit test asserts `point_with_G == point_without_G` and `sigma_plus >= 0`, one-sided).
- The band is heavy-tailed (Student-t via `src.common.student_t`), not Gaussian.
- G is consumed via `get_grip_at` (grep: no re-fit / no call into `grip_baseline.fit_*`).
- Energy channel is RELATIVE (a unit test asserts it is invariant to an absolute-SOC/kW offset
  — i.e. it references the car's own rolling baseline, not an absolute scale); the
  elevation-convention finding is STATED.
- `driver_class_observables` mirrors `driver_utility_observables` + `class` + `map_version` +
  energy + `g_sigma_onesided`; escalation columns present-but-dormant; store round-trips;
  idempotent rerun; own-db; temp-DB tests.
- Per-class deficits use g1 `class_deficits` (absolute, no ratio).
- Run: `pytest tests/unit/physics/test_class_utilization_observable.py -q`.

## Allowed Scope
- CREATE `src/physics/utilization/class_utilization_observable.py`,
  `tests/unit/physics/test_class_utilization_observable.py`.
- EDIT (additive only) `src/physics/utilization/reference_utilization_store.py` to add the
  `driver_class_observables` table + its read/write (mirror the existing store conventions);
  do NOT change the existing `reference_laps` table behavior.
- READ-ONLY: `src/physics/utilization/class_ledger.py` (g1 `class_deficits`),
  `src/physics/layer2/grip_store.py` (`get_grip_at`), `src/physics/layer2/grip_baseline.py`
  (`GripEstimateRecord` shape — do NOT call its fit), `src/common/student_t.py`
  (`predictive_t`, `DEFAULT_NU_LOSS`, `FormulaRule`),
  `scripts/build_driver_utility_observables.py` (the schema to mirror),
  `src/physics/utilization/driver_utility_observable.py` (the #628 absolute-deficit sibling).

## Specific Exclusions
- NO subtraction of a point G; NO re-fit of G; NO moving G's μ off zero (#678).
- NO absolute SOC/kW; NO ERS inference.
- NO CLI / season-run / validation (g4).
- NO race-side observables (Build 2); this is quali-side only (no race-outcome leakage).
- Do NOT touch `segment_map/*`, `car_prior`, `physics_simulator`, or the `reference_laps`
  table's existing behavior.
- Mint NO new physical threshold literal (a float-hygiene tolerance is fine; a
  deficit-significance or energy threshold is a STOP-and-return float).

## Constraints
- `get_grip_at` returns `(mu, sigma)`; use `sigma` (and/or `mu` magnitude) as the σ⁺ SCALE
  only — the observable's point deficit is NEVER shifted by G.
- Deficit sign: positive = real lap slower than ideal. The one-sided band extends toward
  LARGER deficit (grip could have flattered the real lap).
- No baked-in normality: any distributional form is Student-t / heavy-tailed.
- Legacy pre-#627 `_sigma` rows soft-degrade (narrower widths) — document as honest scope,
  never crash (this is a NOTED, non-blocking degrade per the launch order).

## Map Anchors (inbound)
- **Structural:** `struct:physics.utilization` — new `class_utilization_observable.py`;
  additive extend `reference_utilization_store.py`; consumes g1 `class_ledger`,
  `struct:physics.layer2.grip_store`.
- **Capability:** per-driver per-class utilization observable (absolute deficit + one-sided G
  band + relative energy channel).
- **Constraints:** frozen-constants (no new literals); no-normality (Student-t); own-db;
  pre-quali (no race leakage).
- **Decision anchors:**
  - G one-sided wrap (μ=0, σ⁺, half-t). `@grade: settled/inherited · leans g3-implement`
    (a contradiction here is a float to the Admiral, NOT yours to revise — it is a binding
    epic-owner pre-ruling).
  - `decision:c1_driver_utilization_design` — absolute deficit, strictly_pre. `@grade:
    settled/human`
- **Evidence expectations:** `claim:G-band-one-sided` (point unchanged, σ one-sided);
  `claim:anti-circular`; energy-relative-not-absolute.
- **Map confidence flags:** #646 legacy `_sigma` soft-degrade — document, do not block.

## Deliverable Path Check
- **Committed** — `class_utilization_observable.py`, its test, and the additive edit to
  `reference_utilization_store.py`; confirm `git check-ignore` exits 1 for the new files.
- **Local-only** — the own db file (already gitignored).

## Required Evidence
- LOAD-BEARING: (1) point-deficit-unchanged-by-G unit test; (2) band is one-sided (σ⁺≥0,
  extends toward larger deficit) + heavy-tailed (Student-t) test; (3) energy-relative
  (invariant to an absolute offset) test; (4) store round-trip + idempotent rerun on temp DB.
- CONFIRMATORY: grep no G re-fit; escalation columns present-but-dormant; the
  elevation-convention finding is stated in the docstring.
- Run: `pytest tests/unit/physics/test_class_utilization_observable.py -q` — paste the tail.

## Verification Commands
```bash
C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/unit/physics/test_class_utilization_observable.py -q
git check-ignore src/physics/utilization/class_utilization_observable.py tests/unit/physics/test_class_utilization_observable.py; echo "exit $? (expect 1)"
```

## Suggested Model Tier
Stronger — the one-sided-G contract and the energy scope are the subtlest modeling decisions
in the epic; the point-unchanged and relative-not-absolute invariants are load-bearing.

## Authority
DECIDED (do not re-open, they are epic-owner pre-rulings): G = one-sided σ⁺, μ=0, no
subtraction, no re-fit; energy = relative-not-absolute, descriptive/instrument. You DECIDE:
the exact σ⁺-from-G mapping, the energy-deployment proxy design, the single-vs-dual channel
(from your finding), the store column names, function names. You must NOT decide alone: any
new physical/deficit/energy threshold (STOP + return — a float to the Admiral); any change to
G's μ; any change to the g2 `reference_laps` table.

## Stop Conditions
Stop and return IMPLEMENTER_RESULT if: you would need a new physical threshold; wrapping G
one-sided is not expressible from `get_grip_at`'s (mu,sigma) (report the exact gap); the
energy proxy cannot be built relative-only without an absolute channel (state it — a thin
scope-noted proxy or an honest "deployment channel deferred, finding: X" is acceptable); or an
allowed-scope boundary must be crossed.

## Return Format
Return IMPLEMENTER_RESULT: completed slice, files changed, test mode, evidence (pytest tail +
check-ignore), the ENERGY elevation-convention FINDING (explicit), assumptions, stop
conditions, out-of-scope observations, Workflow Feedback. WRITE it to
`.agent-work/664-reference-laps/crew-results/g3-implement-result.md` AND return a tight pointer
summary (incl. the energy finding) as your final message.
