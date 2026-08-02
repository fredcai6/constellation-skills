# Implementer Handoff

## Gate
g4-implement (GATING acceptance evidence — issue #663's first of two falsifiable gates)

## Task
Build a held-out reconciliation evaluation harness at `tests/unit/physics/layer2/test_grip_heldout.py` proving (or honestly disproving) that subtracting G improves cross-session pace reconciliation, using a genuinely disjoint driver split — **NOT in-sample self-scoring** (explicitly rejected by the frozen decision `decision:held-out-not-in-sample`).

**Mechanics (frozen at `understand`, interrogation q4):**
1. Pick a REPRESENTATIVE SLICE of the 2023 DB: 3-5 contrasting circuits (e.g. mix of a street circuit, a high-speed circuit, a technical circuit — your choice, state which and why). State the exact scope you ran — this is NOT required to be the full 22-event season (Budget latitude).
2. For each session in scope: split drivers ~50/50 (stratified by team via `session_classifications.team` where available, else random with a FIXED seed for reproducibility).
3. Fit G (call `src/physics/layer2/grip_baseline.py`'s `fit_grip_baseline_from_laps` — the lap-frame seam, NOT `run_grip_batch`) using ONLY the fit-set drivers' laps for that session.
4. For the HELD-OUT drivers only: compute a same-driver/compound/similar-fuel-state cross-session reconciliation error — i.e. take the same held-out driver's laps in a DIFFERENT session of the same weekend (e.g. FP2 vs FP3, or FP-vs-Q if both have usable laps), on the same compound, at a comparable fuel state, and compute how well the two sessions' pace reconciles BEFORE subtracting G (raw pace difference) vs AFTER subtracting each session's own G value (via `get_grip_at`) from each side.
5. G passes the gate if subtracting it REDUCES the held-out reconciliation error relative to not subtracting it. Report the actual numbers (before/after, aggregate + per-circuit) plainly — a measured null is a complete, valid, reportable deliverable (Honest-Null Clause), not a defect to hide.

**LEAKAGE DISCIPLINE (critical — read before writing the truth-side comparison logic):** the "truth channel" you use to define same-compound/similar-fuel comparability across sessions must NOT be drawn from the exact same signal family as G's own fit correction in a way that would make the pass spuriously easy. Concretely: if your reconciliation "truth" correction ALSO uses `race_degradation_slopes`-style compound/tyre-age/fuel regression on the SAME underlying laps G was fit from, you risk near-total collinearity between "G's correction" and "the truth's correction," which would make ANY G look like it improves reconciliation — not because G is right, but because both sides share the same nuisance-removal machinery. Before trusting a near-perfect result (loosely, anything that reads like P>=0.95-clean), explicitly check: is the truth-side pace comparison's own correction (if you apply one) full-rank and NOT collinear with G's own within-stint tyre_life/fuel terms? The launch order names the specific mechanism: "within-stint fixed-effects + tyre_life are collinear since lap_number = offset + tyre_life within a stint — use driver or race fixed-effects for the fuel term, not stint fixed-effects, on the truth side." If your reconciliation comparison uses ANY OLS/regression step of its own (beyond simple same-compound/similar-fuel-bucket filtering), verify and report its rank explicitly. The simplest way to avoid the leakage risk entirely: do NOT re-run a regression-based correction on the truth side at all — just bucket by compound + a coarse fuel-state proxy (e.g. lap-number quantile within the stint, or tyre_life quantile) and compare RAW held-out pace within matched buckets before/after subtracting G. State clearly which approach you took.

**HONEST-NULL OPERATIONALIZATION (do not skip this — a prior gate in this run was BLOCKed for a smaller mistake in the same spirit):** the pytest command must exit 0 whenever the harness RUNS CORRECTLY and REPORTS A RESULT — whether that result is "G improves reconciliation" or "G does not improve reconciliation." Do NOT write `assert reconciliation_error_after < reconciliation_error_before` as a pytest assertion — that turns a genuine scientific null into a test FAILURE, which is exactly the trap this gate must avoid. Instead: assert the harness ran to completion, the split was genuinely disjoint (assert `set(fit_drivers) & set(heldout_drivers) == set()`), a numeric result was computed for each circuit in scope, and the rank/leakage check passed — then LOG/PRINT/RETURN the actual before/after numbers as the test's real output (a test that logs a clear PASS/NULL verdict string is fine; a test whose exit code encodes the scientific outcome is not).

## Protected Intent
This is one of TWO GATING acceptance criteria for the whole issue #663. It must produce REAL evidence from REAL 2023 data, not a synthetic-only or self-referential check. The Honest-Null Clause means a negative result here is still a complete, valuable deliverable — do not manufacture a positive result or quietly narrow the test until it passes.

## Test Mode
Real-data evaluation harness (not TDD) — must produce actual numbers, not just pass/fail.

## Close Criteria
- Harness at `tests/unit/physics/layer2/test_grip_heldout.py` (exact path, hardcoded in g4-integrate's postcondition).
- Real run against `data/f1Brainz/data/f1_data_2023.db` — wait, the correct path is `C:/Programs/f1Brainz/data/f1_data_2023.db` (main checkout, NOT this worktree — pass it explicitly as an absolute path; the worktree does not carry `data/`).
- 3-5 contrasting circuits, explicitly named and justified.
- Driver split genuinely disjoint, asserted in the test itself.
- Leakage/rank discipline addressed (either avoided by design — bucket-based comparison — or explicitly checked and reported if a regression is used on the truth side).
- Pytest exits 0 regardless of scientific outcome; the actual before/after numbers are reported as real output (printed/logged, and ideally also written to a small results artifact file for the reviewer/commander to inspect, e.g. `.agent-work/663-grip-g/g4-heldout-results.json`).
- `simplification_limits` clean (self-check before returning).

## Allowed Scope
- New file: `tests/unit/physics/layer2/test_grip_heldout.py`.
- Optionally a small results artifact under `.agent-work/663-grip-g/` (this is local-only, not committed to the mission branch — fine to write, do not add to git).
- Read-only: `grip_baseline.py`, `grip_store.py`, `grip_batch.py`, `session_classifications` table, `data/f1_data_2023.db`.

## Specific Exclusions
Do not modify `grip_baseline.py`, `grip_store.py`, `grip_batch.py`, or `tyre_supplant.py`. Do not build the synthetic-recovery gate (g5) — that is separate.

## Constraints
- DB-only analysis: `C:/Programs/f1Brainz/data/f1_data_2023.db` (main checkout), path passed explicitly — never live FastF1/Jolpica.
- State the exact circuit/session scope run — do not silently claim full-season coverage.
- A null result must be reported with full rigor, not papered over.
- Test assertions must not fail merely because the scientific result is a null.
- Bound the runtime — if a full 3-5 circuit fit proves long (the #650 thread-cap tax roughly doubles fit wall-time), consider narrowing to fewer circuits and STATE that you did so and why, rather than running unboundedly. If you must run something long, detach it (`Start-Process -WindowStyle Hidden` from PowerShell, or an equivalent OS-level detach) with a state note, and poll for completion in your own turn — do NOT idle waiting on it.

## Map Anchors (inbound)
- **Structural:** `struct:physics.layer2`.
- **Capability:** G's held-out acceptance evidence.
- **Constraints/assumptions:** `constraint:db-only-analysis`.
- **Decision anchors:**
  - `decision:held-out-not-in-sample` @grade: settled/human · leans g4-implement,g4-review
  - `decision:heldout-split-axis` @grade: guess · leans g4-implement · settle: run on the real slice, adjust split scheme if it proves too coarse
- **Evidence expectations:** none new.
- **Map confidence flags:** none.

## Deliverable Path Check
- **Committed** — `tests/unit/physics/layer2/test_grip_heldout.py`; verify `git check-ignore` exit 1.
- **Local-only** — any results JSON under `.agent-work/663-grip-g/` — do not stage/commit it (this run's `.agent-work/` work area is not committed on the mission branch, per this run's own doctrine).

## Required Evidence
- The actual before/after reconciliation error numbers, per circuit AND aggregate (load-bearing — this IS the acceptance evidence).
- The leakage/rank check result (load-bearing).
- `pytest tests/unit/physics/layer2/test_grip_heldout.py -q` full output, exit 0 regardless of scientific outcome.
- `simplification_limits` clean.
- Explicit statement of scope (which circuits/sessions, why).
- Explicit statement of the split scheme actually used, and whether it matched the frozen 50/50-stratified default or had to be adjusted (with reasoning if adjusted — this decision is graded "guess," so a reasoned adjustment is sanctioned).

## Verification Commands
```bash
cd /c/Programs/f1brainz-wt/epic659-663
"/c/Users/fredc/AppData/Local/Microsoft/WindowsApps/py.exe" -m pytest tests/unit/physics/layer2/test_grip_heldout.py -q -s
"/c/Users/fredc/AppData/Local/Microsoft/WindowsApps/py.exe" -m src.utils.simplification_limits --paths tests/unit/physics/layer2/test_grip_heldout.py
```
(`-s` so printed diagnostic output isn't swallowed.) Use this exact launcher path — plain `py` resolves to a broken shim.

## Suggested Model Tier
Stronger — reason: this is the core scientific/statistical acceptance evidence for the whole issue, real-data leakage discipline is genuinely subtle, and a wrong call here (spurious pass or a broken harness) undermines the entire deliverable.

## Authority
The mechanics above (split axis, leakage-avoidance-by-bucketing recommendation, honest-null operationalization) are decided; the exact circuits chosen, the exact fuel/compound bucketing scheme, and whether to use a regression or a simple bucket comparison on the truth side are yours to choose within the stated constraints — state your choices and reasoning.

## Stop Conditions
Stop and return if: the 2023 DB lacks enough same-driver/same-compound cross-session laps to run a meaningful reconciliation at all (state this explicitly rather than fabricating a comparison), the fit proves prohibitively long even after narrowing scope, or a decision outside this authority is needed.

## Return Format
Return IMPLEMENTER_RESULT (write to `.agent-work/663-grip-g/crew-handoffs/g4-implement-result.md`, and return as final message text): completed slice, files changed, EXACT scope run, the real before/after numbers, leakage/rank check result, evidence produced (paste outputs), assumptions used, stop conditions hit, out-of-scope observations, workflow feedback.
