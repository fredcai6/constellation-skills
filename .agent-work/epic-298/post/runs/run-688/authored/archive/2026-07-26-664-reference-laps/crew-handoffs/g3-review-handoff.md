# Reviewer Handoff — g3 (class utilization observable + one-sided G band + energy)

## Gate
g3-review (issue #664, epic #659, delegated). Worktree
`C:/Programs/f1brainz-wt/epic659-664`. Interpreter PIN:
`C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe` — NEVER bare `py`.

## Survey State Location
`.agent-work/664-reference-laps/g3-review/review.json`.

## What Was Implemented
- `src/physics/utilization/class_utilization_observable.py` (NEW) — per-driver per-class
  observable: absolute time+speed deficit (via g1 `class_deficits`) + a ONE-SIDED G σ⁺ band
  (`σ⁺ = hypot(mu, sigma)` from `get_grip_at`; μ never a point shift; half/truncated
  Student-t at `DEFAULT_NU_LOSS`; extends toward LARGER deficit only) + a RELATIVE energy
  deployment channel.
- `src/physics/utilization/reference_utilization_store.py` (ADDITIVE edit) — new
  `driver_class_observables` table mirroring `driver_utility_observables` + `class` +
  `map_version` + `time_deficit_s` + `g_sigma_onesided` + energy columns; escalation columns
  (`derate_flag`/`escalation_tier`/`escalation_note`) present-but-dormant. `reference_laps`
  table untouched.
- `tests/unit/physics/test_class_utilization_observable.py` (NEW) — 15 tests; the 8 existing
  store tests still pass (23 total).

## How to Inspect the Diff
UNCOMMITTED working tree, linked worktree. `git status --porcelain`; the two new files are
untracked; `reference_utilization_store.py` was NEW in g2 (still untracked) — open it and read
the added `driver_class_observables` code (a `git diff` won't show it since the whole file is
untracked). `git diff --name-only` hides untracked files.

## Task Statement
Per the implementer handoff `.agent-work/664-reference-laps/crew-handoffs/g3-implement-handoff.md`:
the per-driver per-class utilization observable + one-sided G band + a relative energy channel,
extending the g2 own-DB store. G and energy are governed by BINDING epic-owner pre-rulings.

## Close Criteria (each a review check — REPRODUCE)
- **G moves ONLY the one-sided σ⁺; the point deficit is byte-unchanged.** Reproduce the
  `point_with_G == point_without_G` test. Confirm the band is ONE-SIDED (σ⁺≥0, toward larger
  deficit) and μ is NEVER applied as a point shift.
- **Heavy-tailed, not Gaussian.** Confirm the band uses `src.common.student_t`
  (`predictive_t`/`FormulaRule`), a half/truncated Student-t — reproduce the half-t-tail >
  Gaussian check.
- **G is consumed, NOT re-fit.** Grep the module: it calls `grip_store.get_grip_at`, never
  `grip_baseline.fit_*` / re-fits. μ is NOT moved off zero (#678 not attempted).
- **⚠️ SCRUTINIZE the σ⁺-from-G mapping units.** The implementer flagged a low-stakes
  reconciliation: G's `(mu, sigma)` are in grip PACE-seconds; `σ⁺ = hypot(mu, sigma)` is used
  as the band width. Confirm this is dimensionally coherent for the TIME-deficit (both
  seconds) and check how it is applied to the SPEED-deficit (m/s) — if the same second-scaled
  σ⁺ is attached to an m/s quantity without conversion, note it (a MODERATE finding if the
  units are mixed silently; not necessarily a BLOCK if the band is documented as a time-domain
  width — judge and report).
- **Energy is RELATIVE, never absolute SOC/kW.** Reproduce the
  `relative_invariant_to_absolute_offset` test (an absolute offset differentiates to zero).
  Confirm the elevation-convention FINDING is STATED in the docstring (finding: single KE
  channel suffices; `g·h` common-mode cancels; total-mechanical-energy not needed). Confirm
  energy is scope-noted DESCRIPTIVE/instrument, NOT gated.
- **Store:** `driver_class_observables` mirrors `driver_utility_observables` + `class` +
  `map_version` + energy + `g_sigma_onesided`; escalation columns present-but-DORMANT;
  `INSERT OR REPLACE` idempotent; additive migrate; own-db; temp-DB tests. The `reference_laps`
  table behavior is UNCHANGED (reproduce the 8 g2 store tests — still green).
- Deficits use g1 `class_deficits` (absolute, no ratio).
- Re-run `pytest tests/unit/physics/test_class_utilization_observable.py
  tests/unit/physics/test_reference_utilization_store.py -q` → confirm 23 green.

## Allowed Scope
The two new files + the additive edit to `reference_utilization_store.py`. Read-only:
`class_ledger.py`, `grip_store.py`, `grip_baseline.py`, `student_t.py`,
`build_driver_utility_observables.py`, `driver_utility_observable.py`.

## Specific Exclusions (flag if touched)
- NO point-G subtraction; NO G re-fit; NO μ off zero (#678).
- NO absolute SOC/kW; NO ERS inference; NO race-side observables.
- The `reference_laps` table must be UNCHANGED; g4/CLI not here.
- No new PHYSICAL/deficit/energy threshold literal (float-hygiene tolerance ok).

## Constraints the Implementation Must Respect
frozen-constants (no new literals); no-normality (Student-t); own-db (#632);
tests-clean-real-dbs (#656); pre-quali (no race leakage); anti-circularity (absolute deficit).

## Map Anchors (inbound)
- **Structural:** `struct:physics.utilization` — new `class_utilization_observable.py`;
  additive `reference_utilization_store.py`; consumes g1 `class_ledger`,
  `struct:physics.layer2.grip_store`, `src.common.student_t`.
- **Capability:** per-driver per-class observable (deficit + one-sided G band + relative
  energy).
- **Decision anchors:** G one-sided wrap (μ=0, σ⁺, half-t) `@grade: settled/inherited` (a
  contradiction is a FLOAT to the Admiral, not a local revision — binding pre-ruling);
  `decision:c1_driver_utilization_design` `@grade: settled/human`.
- **Evidence expectations:** `claim:G-band-one-sided`; energy-relative-not-absolute;
  `claim:anti-circular`.
- **Map confidence flags:** #646 legacy `_sigma` soft-degrade — documented, non-blocking.

## Evidence Produced
IMPLEMENTER_RESULT at `.agent-work/664-reference-laps/crew-results/g3-implement-result.md`:
`23 passed in 0.50s`; point-deficit byte-identical with/without G; σ⁺(0.3,0.4)=0.5; half-t
0.99 tail > Gaussian; energy invariant to absolute offset; deployment shares sum to 1;
round-trip + idempotent (2 rows). Energy FINDING: single KE channel suffices. Two triage
candidates flagged (real `derate_flag` needs an energy-threshold ruling; G pace-unit ↔
deficit-second reconciliation). The APPROVE `review-result` you return is matched at
`g3-integrate.c2`.

## Suggested Model Tier
Stronger — the one-sided-G contract and the energy relative-invariance are the subtlest
correctness properties in the epic.

## Stop Conditions
BLOCK if: G shifts the point deficit; G is re-fit or μ moved off zero; energy is absolute
(SOC/kW) or not relative-invariant; the band is Gaussian (baked-in normality); the
`reference_laps` table changed; a new physical threshold literal was minted; or evidence is
unverifiable.

## Return Format
Return REVIEW_RESULT (verdict APPROVE/BLOCK + per-check findings + blockers + workflow
feedback), INCLUDING your judgement on the σ⁺-units question. WRITE it to
`.agent-work/664-reference-laps/crew-results/g3-review-result.md` AND return a tight verdict
summary as your final message.
