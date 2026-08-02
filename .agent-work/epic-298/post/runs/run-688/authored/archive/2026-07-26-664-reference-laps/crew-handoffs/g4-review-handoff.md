# Reviewer Handoff — g4 (season-capable CLI + BOUNDED validation + jackknife)

## Gate
g4-review (issue #664, epic #659, delegated). THE SUBSTANTIVE gate. Worktree
`C:/Programs/f1brainz-wt/epic659-664`. Interpreter PIN:
`C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe` — NEVER bare `py`.

## Survey State Location
`.agent-work/664-reference-laps/g4-review/review.json`.

## What Was Implemented
- `scripts/build_class_utilization_observables.py` — season-capable, resumable, idempotent
  own-db CLI composing g1/g2/g3 + segment-map derivation (mirrors #628; G soft-degrades).
- `src/physics/utilization/class_utilization_validation.py` — pure jackknife math (delete-d
  block schedule, boundary drift vs `MAP_STABILITY_DRIFT_M`, per-class stability, positive
  control).
- `tests/unit/physics/test_build_class_utilization_observables.py` — 8 synthetic + temp-db
  tests (green).
- `.gitignore` — additive `.agent-work/**/*.db` (keeps the run own-db local).
- Bounded run artifact (local-only): `.agent-work/664-reference-laps/artifacts/
  jackknife_attribution.json` + `.md`.

## How to Inspect the Diff
UNCOMMITTED working tree. `git status --porcelain`; open the 3 new committable files + `git
diff .gitignore`. The artifact JSON is under `.agent-work/` (local-only, not committed — do
NOT flag as missing from the diff).

## Task Statement
Per `.agent-work/664-reference-laps/crew-handoffs/g4-implement-handoff.md`: a season-CAPABLE
build CLI + a BOUNDED validation run + the GATING delete-d/block jackknife with a positive
control, reported as an INSTRUMENT (no new literal band).

## Close Criteria (REPRODUCE — do not read-through)
- **BOUNDED run, not full-season.** Confirm the run was 1-2 circuits, foreground, within the
  time bound (artifact `wall_clock_s_to_here` = 62.1s; gp=Great Britain, round 10). NO
  full-season run.
- **⚠️ INDEPENDENTLY RECOMPUTE the robustness statistic from the persisted artifact**
  (`.agent-work/664-reference-laps/artifacts/jackknife_attribution.json`) — load it, and
  either re-derive the per-class stability summary from the replicate data it carries, OR
  re-run the pure `class_utilization_validation` math on the same inputs and confirm the
  reported per-class IQR/median + boundary-drift (mean 0.736 m / max 1.15 m) MATCH. Do NOT
  accept the numbers on a code read alone.
- **Jackknife is genuinely LEVERAGED + out-of-sample:** delete-d / driver-BLOCK (NOT
  zero-leverage drop-one), B=30, boundary jitter re-derived in-memory from the REDUCED pool
  against the SAME fixed v_ideal/v_real (no session reload, no ceiling re-sim). Confirm it is
  NOT self-weighted (lesson:loo-residual-diagnostic) — the scoring ceiling is `strictly_pre`
  (anti-circularity note in the artifact) and the field reference lap only places boundaries.
- **⚠️ POSITIVE CONTROL FIRED.** Confirm `jackknife.positive_control.fired == True` and that
  the mechanism is real (injected corner→straight-edge deficit; injected straight spread
  0.159 > baseline 0.0). **A measured result WITHOUT a fired positive control is a BLOCK** —
  the instrument would be unproven.
- **No new literal acceptance band.** Confirm the report ANCHORS to the frozen
  `MAP_STABILITY_DRIFT_M` (=10 m) and mints NO new literal threshold. `within_anchor=True`.
- **deficits-sum-to-lap labelled CONSTRUCTION**, not validation. Own-db (never f1_data).
  Pinned interpreter. G soft-degrade documented (grip store empty, σ⁺=0, grip_batch NOT run).
- **Honest reporting:** the attribution result is reported as an INSTRUMENT reading
  (allocation-not-gating), not a manufactured pass/fail. A measured-null would be reported
  honestly.
- **Import-graph-scoped regression** (NOT the full physics suite — lesson:
  scope-self-authored-regression-to-import-graph): run the touched-module tests +
  the sibling utilization/segment_map tests to confirm nothing broke:
  `pytest tests/unit/physics/test_class_ledger.py
  tests/unit/physics/test_reference_lap_product.py
  tests/unit/physics/test_reference_utilization_store.py
  tests/unit/physics/test_class_utilization_observable.py
  tests/unit/physics/test_build_class_utilization_observables.py
  tests/unit/physics/test_driver_utility_observable.py
  tests/unit/physics/test_regime_utilization.py tests/unit/physics/segment_map -q`.
  Report the count green.

## Allowed Scope
The 3 new committable files + the `.gitignore` line + the local artifact. Read-only
consumption of g1/g2/g3 modules + segment_map derivation + frozen_constants.

## Specific Exclusions (flag if touched)
- NO full-season run; NO grip re-fit (grip_batch); NO new literal band; NO absolute SOC/kW;
  NO seeded/supersede write path.
- The bounded run's own-db + the artifact are LOCAL-ONLY (under `.agent-work/`) — not a defect
  if absent from the committed diff.

## Constraints the Implementation Must Respect
build-capable-run-bounded; own-db (#632); tests-clean-real-dbs (#656); no new literal (F12);
no-frame-kill (measured result + fired positive control = complete); pinned interpreter.

## Map Anchors (inbound)
- **Structural:** `scripts/build_class_utilization_observables.py` +
  `class_utilization_validation.py`; composes g1/g2/g3 + segment_map derivation.
- **Capability:** season-capable pipeline + bounded validation instrument.
- **Decision anchors:** build-season-capable-run-bounded `@grade: settled/human`;
  `decision:class-attribution-membership-faithful` (jackknife meaningfulness rests on it)
  `@grade: settled/measured`.
- **Evidence expectations:** `claim:attribution-robust` (jackknife stability + FIRED positive
  control — RE-CONFIRM by recompute); `claim:deficits-sum-to-lap` (construction).
- **Map confidence flags:** grip store empty → G soft-degrade (documented); long-run reap →
  run was foreground/bounded (62s).

## Evidence Produced
IMPLEMENTER_RESULT `.agent-work/664-reference-laps/crew-results/g4-implement-result.md`:
smoke 8/8; bounded run GB round 10, 272 pool laps / 20 drivers, 62.1s; delete-d driver-block
B=30, 30/30 ok; boundary drift mean 0.736 / max 1.15 m ≪ 10 m; per-class IQRs 0.0015-0.017 s /
0.009-0.057 m/s; positive control FIRED (0.159 vs 0.0); G σ⁺=0 soft-degrade; deficits-sum-to-lap
5.62 s ≈ VER +5.625 s; idempotent rerun clean. The APPROVE `review-result` you return is
matched at `g4-integrate.c2`.

## Suggested Model Tier
Stronger — the substantive gate; the recompute + positive-control + no-literal-band checks are
load-bearing for whether the epic gated anything real.

## Stop Conditions
BLOCK if: the run was NOT bounded; the jackknife is drop-one/zero-leverage or self-weighted;
the positive control did NOT fire; a new literal band was minted; the recomputed statistic does
NOT match the artifact; a real DB was written; or the regression subset reveals a break.

## Return Format
Return REVIEW_RESULT (verdict APPROVE/BLOCK + per-check findings + the RECOMPUTED numbers you
independently derived + blockers + workflow feedback). WRITE it to
`.agent-work/664-reference-laps/crew-results/g4-review-result.md` AND return a tight verdict
summary as your final message.
