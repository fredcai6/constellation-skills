# Implementation Result — g4 (issue #664, epic #659)

Status values follow `skills/workbench/references/status-model.md`.

## Assigned gate
`g4-implement` — season-capable build CLI composing g1/g2/g3 + segment_map derivation,
a bounded 2023-Q validation slice, and the GATING attribution-robustness jackknife.

## Completed slice
Delivered the season-CAPABLE build CLI, a pure jackknife/validation helper, a synthetic
smoke test, and RAN the bounded real slice + gating jackknife foreground. Measured result:
**per-class attribution is ROBUST** to boundary jitter and the **required positive control
FIRED**.

## Scope
**Files changed (committed path — `git check-ignore` exits 1 for all three):**
- `scripts/build_class_utilization_observables.py` (new) — resumable, idempotent, own-db,
  season-capable CLI. Mirrors #628: `load_store_df` → per-round → derive SegmentMap live
  (one session load, pooled-once era mixture reused across rounds) → per-constructor
  `build_car_ceiling(strictly_pre=True)` + `simulate_lap` on the reference-lap grid →
  compose g2 `ReferenceLapProduct` + g3 `ClassUtilizationObservable` → persist via
  `ReferenceUtilizationStore`. Error rows never crash the batch; timestamped output;
  pinned-interpreter-safe; grip G soft-degrades (`grip=None` when the store is absent).
- `src/physics/utilization/class_utilization_validation.py` (new) — PURE jackknife math:
  `make_delete_d_blocks` (delete-d/block schedule), `attribute_deficits` (g1 soft-W wrapper),
  `boundary_set_drift_m` (symmetric nearest-neighbour drift, anchored to
  `MAP_STABILITY_DRIFT_M`), `per_class_stability`, and `positive_control` (planted
  corner-edge deficit; literal-free within-experiment contrast).
- `tests/unit/physics/test_build_class_utilization_observables.py` (new) — 8 synthetic +
  temp-DB tests (no real data / no session load).
- `.gitignore` (edit) — added `.agent-work/**/*.db` so the bounded-run own-db byproduct is
  never accidentally committed (matches the existing agent-work scratch-binary block).

**Local-only artifacts (under `.agent-work/`, intentionally not committed):**
- `.agent-work/664-reference-laps/artifacts/jackknife_attribution.json` + `.md` — the gating
  evidence.
- `.agent-work/664-reference-laps/artifacts/reference_utilization_run.db` — the own-db output
  (now gitignored).

**Specific exclusions touched:** no — no full-season run, no backgrounding, no grip re-fit /
`grip_batch`, no new literal acceptance band, no f1_data DB writes, no seeded/supersede write
path, no race-side observables.

## Behavior changed
Yes — a new season-capable pipeline persists per-driver per-class utilization observables to an
own DB, plus a one-off attribution-robustness instrument. No existing behavior altered (all g1/g2/g3
cores + derivation consumed read-only).

## Map Impact
- **Structural anchors touched:** `scripts/build_class_utilization_observables.py` (new CLI) —
  composes g1 `class_ledger` + g2 `reference_lap_product`/`reference_utilization_store` + g3
  `class_utilization_observable` + `struct:physics.segment_map.derivation`
  (`reference_lap_from_store`→`build_reference_lap`, `tile_reference_lap`, `derive_sector_lines`,
  `fit_era_severity_mixture`, `assemble_segment_map`). New pure module
  `src/physics/utilization/class_utilization_validation.py`.
- **Capabilities added:** season-capable utilization pipeline (build-capable) + bounded
  validation instrument (delete-d/block boundary-jitter jackknife + positive control).
- **Constraints honored:** own-db (#632); pre-quali `strictly_pre=True` (no race-outcome
  leakage); build-capable-run-bounded; consume-not-refit for G.
- **Decision anchors exercised:** `build-season-capable-run-bounded` (settled/human);
  `decision:class-attribution-membership-faithful` (soft-W attribution, not argmax — the
  jackknife's meaningfulness rests on it, settled/measured — REINFORCED: the measured stability
  below is under the soft-W path).
- **Claims/evidence produced:** `claim:attribution-robust` — CONFIRMED as an instrument reading
  (per-class deficit IQR ≤ 0.017 s / ≤ 0.057 m/s across 30 boundary-jitter replicates; boundary
  drift 0.74 m mean / 1.15 m max ≪ 10 m frozen anchor) with a FIRED positive control.
  `claim:deficits-sum-to-lap` — CONSTRUCTION check confirmed (Σ per-class time deficit
  = 5.62 s ≈ VER whole-lap deficit +5.625 s).
- **Trust limitations:** grip G store unpopulated → G band SOFT-DEGRADES to σ⁺=0 (documented);
  the deficit MAGNITUDES (5.6–8.8 s absolute vs the physics ceiling) are an instrument reading,
  not validated here — the jackknife tests ATTRIBUTION robustness, not ceiling calibration.

## Test mode
**Required:** test-after / inspection (CLI smoke on synthetic + temp DB; #656).
**Satisfied:** yes — 8 tests green under the pinned interpreter; the real bounded slice is a
one-off whose output is the `.json`/`.md` artifact (not a committed DB, not the unit test).

## Evidence

```bash
C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/unit/physics/test_build_class_utilization_observables.py -q
# -> 8 passed in 0.44s

C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe scripts/build_class_utilization_observables.py \
  --year 2023 --session-type Q --rounds 10 --drivers VER,PER,LEC,SAI \
  --db .agent-work/664-reference-laps/artifacts/reference_utilization_run.db --validate --jackknife-b 30 --jackknife-block driver
# -> done in 62.1s; 24 class rows (0 errors); g2 product 3 rows; positive control FIRED=True
```

**Result:** pass.

**Bounded-run headline (2023 Q, round 10 Great Britain / Silverstone, VER+PER+LEC+SAI):**
- Wall-clock: **62.1 s** foreground (op-count budgeted first: `load_weekend_inputs` timed at
  4.7 s; the full run stayed far under the 10-min bound — ONE circuit was sufficient, no shrink
  needed).
- Jackknife: **delete-d / driver-block, B=30, all 30 replicates re-derived cleanly**
  (boundary-jitter: reference lap rebuilt in-memory from each reduced pool, re-tiled,
  re-attributed against the SAME fixed v_ideal/v_real — no session reload, no ceiling re-sim).
- **Boundary-set drift: mean 0.74 m, max 1.15 m — well within `MAP_STABILITY_DRIFT_M`=10 m
  (within_anchor=True).**
- **Per-class deficit stability (across 30 replicates):** time-deficit IQR 0.0015–0.017 s,
  speed-deficit IQR 0.009–0.057 m/s — tiny relative to the deficits themselves (e.g. corner
  class c0 median 3.49 s / 6.04 m/s). Attribution is measured ROBUST.
- **Positive control FIRED = True** (injected corner deficit at a corner/straight edge:
  leaked straight-class spread 0.159 m/s vs clean baseline 0.0 — the instrument detects the
  misattribution it exists to detect).
- G soft-degrade: σ⁺ = 0 on every band (grip store absent); point deficits byte-identical
  with/without G. `grip_batch` NOT run.
- Idempotent rerun: all 4 drivers skipped ("already present"), 24 class rows / 3 product rows
  stable, no duplicates (6.0 s).

## TDD evidence, if required
Test-after/inspection mode. Failing-then-passing not applicable; a collection error (module
`__module__` unresolved for dataclass KW_ONLY probe when loading a non-package script) was
observed and fixed by registering the module in `sys.modules` before `exec_module`. Final: 8
passed.

## Docs/contracts touched
- `.gitignore` (added `.agent-work/**/*.db`). No API/contract changes to g1/g2/g3 or derivation
  (all consumed read-only).

## Assumptions
- Chose round 10 (Silverstone) — full causal history (rounds 1–9) for `strictly_pre=True`, both
  target constructors present, clean telemetry + sector data.
- B=30, driver-block, delete-~10%-of-pool per replicate (the leverage knob `_BLOCK_FRACTION`,
  documented as instrument design, not an acceptance band).
- Field fingerprint composed over the requested drivers' two constructors (field basis n=2), not
  the whole grid — consistent with the #628 driver-slice scoping; a full-season run (#670) would
  widen the basis.
- v_ideal/v_real/boundaries all evaluated on the reference-lap distance grid (the coordinate the
  SegmentMap boundaries live in) so attribution stays coherent.

## Stop conditions hit
- None. A measured-null was NOT the outcome — attribution measured robust with a FIRED positive
  control (a complete deliverable either way per the handoff).

## Out-of-scope observations
- The absolute per-lap deficit magnitude vs the physics ceiling (5.6–8.8 s) is large; whether
  that reflects an optimistic reference-lap-grid ideal sim vs the #628 ribbon-grid path is a
  calibration question for a later gate — not attribution robustness (triage candidate).
- The energy-deployment channel is persisted (descriptive/instrument) but not exercised by the
  jackknife (its pre-registered comparison is downstream, as g3 documented).

## Workflow Feedback
- **Handoff gaps:** The Deliverable Path Check asserted the artifact lives "under the gitignored
  `.agent-work/`", but `.agent-work/` is only partially gitignored in this repo (`*.pkl/*.npz/
  scratch/…` — NOT `*.db`). The own-db byproduct would have been committable. I added
  `.agent-work/**/*.db` to the ignore block; flagging so the handoff's path-check wording matches
  reality.
- **Context rediscovered:** the reference-lap grid vs the #628 ribbon grid coordinate question
  (which grid the SegmentMap boundaries live in) was load-bearing for coherent attribution and
  wasn't called out in the handoff — I resolved it to the reference-lap grid.
- **Instructions improvised around:** the checklist-engine reference path in the implementer
  SKILL (`skills/workbench/references/checklist-engine.md`) does not exist under the implementer
  skill dir; the engine + reference live under `constellation-workbench/`. Used the workbench copy.
- **What would have made this easier:** a one-line handoff note that the era severity mixture fit
  is cheap (~sub-second on the 2023 grip_bin_obs slice) and should be fit ONCE and threaded across
  rounds — I inferred this from `derive_segment_map`'s own `mixture`/`vocabulary` reuse contract.

## Return status
`complete`
