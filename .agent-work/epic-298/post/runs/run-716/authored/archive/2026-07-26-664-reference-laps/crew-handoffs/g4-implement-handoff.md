# Implementer Handoff — g4 (season-capable build CLI + BOUNDED validation + jackknife)

## Gate
g4-implement (issue #664, epic #659, delegated). Worktree
`C:/Programs/f1brainz-wt/epic659-664`. Interpreter PIN:
`C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe` — NEVER bare `py`.

## Task
1. **Deliver `scripts/build_class_utilization_observables.py`** — a resumable, idempotent,
   SEASON-CAPABLE CLI that composes g1/g2/g3 to persist reference-lap products +
   per-driver per-class observables to the OWN db. MIRROR the structure of the working #628
   script `scripts/build_driver_utility_observables.py` (same load_store_df → per-round →
   per-constructor `build_car_ceiling(strictly_pre=True)` → `simulate_lap` → compose/persist
   pattern; timestamped output; idempotent skip of already-present rows; error rows never
   crash the batch). Season-capable = it accepts `--year --session-type --rounds --drivers`
   (or all) and could run the season; you only RUN a bounded slice (below).
2. **RUN a BOUNDED validation slice** — 2023 Q, ONE-to-TWO circuits, both constructors'
   drivers, one session each. NOT the full season (that is #670/Wave 6, HITL). Run it
   FOREGROUND / IN-TURN — do NOT background it; if it would exceed ~10 min, SHRINK the slice
   (fewer circuits) rather than detaching. Budget the op-count BEFORE running.
3. **GATING attribution-robustness check** — a DELETE-d / BLOCK JACKKNIFE (see below) →
   write `.agent-work/664-reference-laps/artifacts/jackknife_attribution.json` (+ a short
   `.md`).
4. **Author `tests/unit/physics/test_build_class_utilization_observables.py`** — a CLI SMOKE
   test on SYNTHETIC fixtures + temp DB only; it also asserts the jackknife artifact
   contract (real numbers + a fired positive control) against a synthetic fixture.

## Real-data paths (READ-ONLY, absolute — this worktree has no local data/)
- EstimateStore: `C:/Programs/f1Brainz/data/physics_estimates.db` (2023 Q = 220 estimates,
  full coverage — confirmed).
- Telemetry (session loads via `session_fit.load_quali_session` / `reference_lap_from_store`):
  `C:/Programs/f1Brainz/data/telemetry_store.db` (its own default — do not pass FastF1).
- Era severity mixture (`fit_era_severity_mixture` inside `derive_segment_map`):
  `C:/Programs/f1Brainz/data/damage_integrals.db` (`grip_bin_obs`, 612,615 rows).
- **Grip G store is UNPOPULATED** — the #663 `grip_estimates` table does NOT exist on disk
  (only the #625 `grip_bin_obs` substrate does). So the G one-sided band SOFT-DEGRADES on this
  slice: when `get_grip_at` raises / the store is absent, set the G σ⁺ contribution to 0
  (band omitted) and DOCUMENT it as an honest soft-degrade. Do NOT run `grip_batch` / re-fit G
  (consume-not-refit; #687/#688 out of scope). "G barely moves utilization" holds trivially
  here — the POINT observable and the GATING attribution robustness do NOT depend on G.

## ⚠️ JACKKNIFE (the SUBSTANTIVE gate) — delete-d block, boundary jitter, positive control
- **Delete-d / BLOCK jackknife, NOT drop-one.** Drop-one over a ~200-lap pool has near-zero
  boundary leverage. Per replicate, drop a DRIVER-block or a random LAP-block from the pooled
  derivation laps; FIXED replicate budget **B in [20, 50]** (state the exact B).
- **Perturbation under test = SegmentMap BOUNDARY jitter.** Re-derive the segment boundaries
  IN-MEMORY from the reduced lap pool (rebuild the reference lap via `build_reference_lap` on
  the retained per-lap arrays; re-tile), then RE-ATTRIBUTE per-class deficits against the SAME
  fixed `v_ideal`/`v_real` profiles (do NOT reload sessions, do NOT re-simulate the ceiling).
  Report per-class deficit STABILITY across replicates (e.g. the spread / IQR of each class's
  deficit).
- **INSTRUMENT, not a hard gate** (allocation-not-gating; "2σ is a reference not a gate").
  REPORT the stability numbers. Anchor any comparison to the EXISTING frozen boundary-drift
  scale `MAP_STABILITY_DRIFT_M` (= 10 m, `frozen_constants.py`). Mint NO new literal
  acceptance band. (If a hard band is ever truly needed, that is a FLOAT to the Admiral for a
  new F12 set — STOP and return, do NOT inline a literal.)
- **REQUIRED POSITIVE CONTROL.** Inject a synthetic lap with a KNOWN misattributed deficit
  (a corner deficit deliberately shifted into a straight class) and confirm the robustness
  statistic FLAGS it (its instability/mis-share exceeds the reported band). A measured-null /
  weak-attribution result is a COMPLETE deliverable ONLY if the positive control FIRED (proves
  the instrument can detect the failure it exists to detect). Record the positive-control
  result in the artifact.
- **Anti-circularity note to RECORD in the artifact:** the SCORING ceiling is the
  `strictly_pre=True` car prior (excludes the target round); the field reference lap only
  PLACES boundaries — it does not score. So the jackknife perturbs attribution, not the
  ceiling.
- deficits-sum-to-lap is a CONSTRUCTION check — label it construction, not validation.

## Protected Intent
- Build season-CAPABLE, RUN bounded. No full-season run (#670).
- Own-db (#632); pre-quali (no race-outcome leakage — 2023 Q only).
- Commander/crew must NOT run multi-hour compute; keep the run foreground + small.
- No frame-kill: a measured-null (with a fired positive control) is a COMPLETE deliverable.

## Test Mode
CLI smoke = SYNTHETIC + temp DB (#656). The REAL bounded run is a one-off validation, its
output is the `.json`/`.md` artifact (NOT a committed DB). The unit test does NOT run the real
slice.

## Close Criteria
- `scripts/build_class_utilization_observables.py` runs season-capably (mirrors #628),
  idempotent, own-db, pinned-interpreter-safe, timestamped.
- The bounded run produced the artifact `.agent-work/664-reference-laps/artifacts/
  jackknife_attribution.json` with: per-class deficit stability numbers (real), B (the
  replicate budget), the positive-control result (FIRED), the `MAP_STABILITY_DRIFT_M` anchor,
  the G soft-degrade note, and the anti-circularity note. A short companion `.md` summarizes.
- The jackknife is delete-d/block (leveraged), boundary-jitter, in-memory (no session reload
  per replicate), NOT self-weighted (out-of-sample).
- `tests/unit/physics/test_build_class_utilization_observables.py` passes (CLI smoke on
  synthetic + temp DB; asserts the artifact contract on a synthetic fixture incl. positive
  control).
- Honest reporting: the signal size is stated as an instrument reading, not a pass/fail.

## Allowed Scope
- CREATE `scripts/build_class_utilization_observables.py`,
  `tests/unit/physics/test_build_class_utilization_observables.py`, and the artifact files
  under `.agent-work/664-reference-laps/artifacts/`.
- You MAY add a small pure jackknife/validation helper module under
  `src/physics/utilization/` (e.g. `class_utilization_validation.py`) if it keeps the math
  unit-testable — your choice; document it.
- READ-ONLY: g1 `class_ledger`, g2 `reference_lap_product`/`reference_utilization_store`, g3
  `class_utilization_observable`, `car_prior`, `physics_simulator`, `segment_map/derivation/*`
  (`derive_segment_map`, `reference_lap_from_store`, `build_reference_lap`, `tile_reference_lap`),
  `frozen_constants` (`MAP_STABILITY_DRIFT_M`), `scripts/build_driver_utility_observables.py`
  (the pattern to mirror).

## Specific Exclusions
- NO full-season run (#670). NO backgrounding the validation run. NO grip re-fit / grip_batch.
- NO new literal acceptance band (STOP + return — a float). NO absolute SOC/kW.
- NO SegmentMap seeded/supersede write path. NO race-side observables.
- Do NOT write any real f1_data DB; the own-db output of the bounded run is a local artifact,
  not committed.

## Constraints
- Interpreter PIN throughout. Pinned pytest for the smoke test.
- If the bounded run cannot complete foreground in ~10 min, SHRINK the slice and note it —
  do NOT detach (harness-tracked bg workers die on subagent idle).
- Mirror the #628 script's error-row discipline (a failed round/driver is recorded, never
  crashes the batch).

## Map Anchors (inbound)
- **Structural:** `scripts/build_class_utilization_observables.py` (new CLI); composes g1/g2/g3
  + `struct:physics.segment_map.derivation`.
- **Capability:** season-capable utilization pipeline + bounded validation instrument.
- **Constraints:** own-db; pre-quali; build-capable-run-bounded.
- **Decision anchors:** build-season-capable-run-bounded `@grade: settled/human`;
  `decision:class-attribution-membership-faithful` (the jackknife's meaningfulness rests on
  the g1 soft-attribution) `@grade: settled/measured`.
- **Evidence expectations:** `claim:attribution-robust` (GATING jackknife stability +
  positive control); `claim:deficits-sum-to-lap` (construction).
- **Map confidence flags:** grip store empty → G soft-degrade (documented); long-run reap
  risk (#650/#648) → foreground + small.

## Deliverable Path Check
- **Committed** — `scripts/build_class_utilization_observables.py`,
  `tests/unit/physics/test_build_class_utilization_observables.py`, and (if created) the
  validation helper module; confirm `git check-ignore` exits 1 for each.
- **Local-only** — the jackknife artifact under `.agent-work/...` (intentionally NOT
  committed — it is under the gitignored `.agent-work/`), and the own-db output of the run.

## Required Evidence
- LOAD-BEARING: (1) the jackknife artifact with REAL per-class stability numbers + a FIRED
  positive control; (2) the CLI smoke test green (synthetic + temp DB); (3) the run completed
  foreground within the time bound (state wall-clock).
- CONFIRMATORY: idempotent rerun of the CLI (no dup rows); G soft-degrade documented;
  op-count budget stated.
- Run: `pytest tests/unit/physics/test_build_class_utilization_observables.py -q` — tail; and
  the bounded-run console tail.

## Verification Commands
```bash
C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/unit/physics/test_build_class_utilization_observables.py -q
# the bounded validation run (example — pick the exact circuit set that loads cleanly, keep it 1-2 circuits):
C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe scripts/build_class_utilization_observables.py --year 2023 --session-type Q --rounds <r> --drivers <...> --db <temp-own-db> --validate --jackknife-b 30
ls -la .agent-work/664-reference-laps/artifacts/jackknife_attribution.json
```

## Suggested Model Tier
Stronger — this is the epic's substantive GATING gate; the jackknife leverage + positive
control + report-not-literal discipline are load-bearing and subtle.

## Authority
DECIDED (do not re-open): build-capable-run-bounded; delete-d/block jackknife with positive
control; instrument-not-hard-gate anchored to `MAP_STABILITY_DRIFT_M`; G soft-degrade
(consume-not-refit). You DECIDE: the exact bounded circuit set (pick what loads cleanly), the
replicate budget B in [20,50], the block-drop unit (driver vs lap-block), the stability
statistic, CLI flag names, and whether to factor a pure validation helper. You must NOT decide
alone: any new literal acceptance band (STOP + return — a float); a full-season run; running
grip_batch.

## Stop Conditions
Stop and return IMPLEMENTER_RESULT if: the bounded run cannot complete foreground within the
time bound even after shrinking to one circuit (report the wall-clock + where it spent time);
a needed literal threshold/band surfaces (float); the required real data is missing for every
candidate circuit (report which); or an allowed-scope boundary must be crossed. A measured-null
with a FIRED positive control is NOT a stop condition — it is a complete deliverable.

## Return Format
Return IMPLEMENTER_RESULT: completed slice, files changed, test mode, evidence (pytest tail +
bounded-run tail + wall-clock + the jackknife stability numbers + positive-control result),
the G soft-degrade note, assumptions, stop conditions, out-of-scope observations, Workflow
Feedback. WRITE it to
`.agent-work/664-reference-laps/crew-results/g4-implement-result.md` AND return a tight pointer
summary (incl. the headline jackknife stability numbers + positive-control fired) as your final
message.
