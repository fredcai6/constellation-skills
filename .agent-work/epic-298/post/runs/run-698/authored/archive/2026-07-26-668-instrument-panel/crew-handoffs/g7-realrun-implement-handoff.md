# Implementer Handoff — g7-realrun-implement

## Gate
g7-realrun-implement (#668 instrument panel) — the real-data culmination. Worktree
`C:/Programs/f1brainz-wt/epic659-668`, branch `epic659/668-instrument-panel`. PINNED interpreter
`C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe` — NEVER bare `py`.
**Editable-.pth trap:** this is a BARE SCRIPT, not pytest — `src.*` resolves to MAIN's checkout
(lacks the unmerged instrument_panel code) → ModuleNotFoundError. Add at the top of the script:
`import sys, pathlib; _REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]; sys.path.insert(0, str(_REPO_ROOT))`.
Verify `import fastf1` succeeds first (env sanity per launch order — the panel itself is DB-only,
no FastF1 calls).

## Task
Run ALL FOUR built instruments on the CROSS-CIRCUIT slice and emit a WRITTEN, VERSIONED report.
Deliverables:
- `scripts/instrument_panel_668_report.py` — the runnable report generator (reads the slice,
  runs the four instruments with the FROZEN signed thresholds, writes the report + a machine-
  readable JSON). Mirror the shape of `scripts/fingerprint_class_coverage_675.py`.
- `docs/physics/instrument_panel_668_gb2023q_report.md` — the versioned report (the script's
  markdown output, committed).
- `tests/unit/physics/instrument_panel/test_panel_report.py` — reproduces / no-leakback / bounded-
  scope checks (the g7-integrate test).

## Data (READ-ONLY; on-disk; NO FastF1 online)
- **Observables + reference_laps (cross-circuit slice)**:
  `C:/Programs/f1Brainz/.agent-work/archive/2026-07-26-666-driver-fingerprint/artifacts/fp_slice_2023Q.db`
  — tables `driver_class_observables` (per driver/class/circuit: `time_deficit_s`,
  `deployment_share`, `n_points`, `g_sigma_onesided`, `sigma_lapsampling`) and `reference_laps`
  (car-reference per constructor/class). Circuits: Belgium/GB/Monaco/Spain Q; drivers LEC/PER/SAI/VER.
- **Official FIA sector times**: `data/f1_data_2023.db` `lap_times.sector{1,2,3}_time` via
  `DatabaseManager.get_lap_times` (GB-Q = session_id 559 / round 10; the other three circuits'
  Q sessions similarly). READ-ONLY — **DB-BLOB GUARD: never stage/commit `data/f1_data_*.db`;
  `git checkout -- data/f1_data_2023.db` if it shows Modified after a read.**

## The four instruments on the real slice
1. **Variance decomposition** (`variance_decomposition.decompose_segment_time_variance`): size the
   car-reference / driver-utilization (FLOOR) / residual shares of the observed segment-time signal
   across the cross-circuit driver×class grid. Report the driver-utilization FLOOR plainly.
2. **Golf-corrected split-half replication + σ-honesty** (`replication.py`, DOUBLE-CENTERING):
   split-half unit = **CROSS-CIRCUIT 2-vs-2** over the 4 circuits — enumerate all 3 distinct 2v2
   partitions, average the split-half r. Use `frozen_replication_thresholds()` (the SIGNED set).
   σ-honesty OUT-OF-SAMPLE, carrying the refinement-2 main-effect margin uncertainty; surface thin
   classes (c1 excluded by MIN_SUPPORT_N=15).
3. **Channel comparison**: run replication in BOTH channels (utilization=time_deficit_s,
   energy=deployment_share); report per-class the winner / tie→utilization / unresolved, per the
   signed decision rule.
4. **Composed-sector scorecard** (`sector_scorecard.py`): compose the available per-segment/per-class
   predictions into FIA sectors (via `sector_nesting`) and validate against official sector times.
   Report (a) position-sum construction identity and (b) distribution calibration (central +
   Student-t coverage) with the gross-miscalib gate (consume `SECTOR_CALIB_GROSS_MISCALIB_BOUND`).
   **If the on-disk slice does not carry enough per-segment granularity to compose a full sector
   prediction, do NOT fabricate one** — report the construction check + whatever calibration IS
   computable and state the limitation explicitly (no-frame-kill; route the gap to #670). STOP and
   return to the commander if the scorecard cannot run at all, so I can decide.

## Report contents (the versioned .md)
- Header: issue #668, date, slice identity (4 circuits × 4 drivers), the exact FROZEN constants
  used (values), and a "SIZING panel — never gates Build 2/3" banner.
- Instrument 1: the three variance shares + the driver-utilization FLOOR, stated plainly.
- Instrument 2: golf-corrected (double-centered) split-half replication per class per channel + the
  σ-honesty verdict (coverage vs nominal, out-of-sample) + surfaced thin classes.
- Instrument 3: the channel-comparison winners (which channel earns join weight per class).
- Instrument 4: the sector scorecard — position-sum construction result + distribution-calibration
  central + coverage vs official + the gross-miscalib gate result (or the honest limitation).
- **Small signal is EXPECTED and is a COMPLETE result** (4 drivers × ~2-3 resolvable classes) —
  say the size plainly, no-frame-kill.
- **Bounded-scope note**: cross-circuit on the 4-circuit on-disk slice; full-season / broader-
  circuit breadth → #670 (HITL). State it explicitly.

## Allowed Scope
CREATE `scripts/instrument_panel_668_report.py`, `docs/physics/instrument_panel_668_gb2023q_report.md`,
`tests/unit/physics/instrument_panel/test_panel_report.py`. READ-ONLY: the two DBs above, the four
instrument_panel modules, `frozen_constants.py`, `sector_nesting.py`, `DatabaseManager`.

## Specific Exclusions
- Do NOT pull FastF1 online. Do NOT stage/commit any `data/f1_data_*.db` (#632 / DB-BLOB GUARD).
- Do NOT alter any signed frozen value or any instrument module's logic (wire/consume only; a small
  read-adapter in the script is fine). Do NOT let an official sector time enter a prediction
  (leakback). Do NOT touch #660/#664/#666/#667 producers. Do NOT touch `docs/architecture/*`.
- Do NOT run the full season (that's #670, HITL) — only the 4-circuit slice.

## Constraints
- Strictly-pre: thread `as_of_round` so predictions are pre-quali; official sectors are the post-hoc
  target only. Student-t coverage (no Gaussian). Consume frozen constants (no inline literals).
- Deterministic report (seed any RNG). pyright-0. Existing 49 instrument_panel tests stay green.

## Map Anchors (inbound)
- **Structural:** `src/physics/instrument_panel/` (all four); the two DBs; `sector_nesting.py`; `frozen_constants.py`.
- **Capability:** driver-utilization measurement (the exit instrument); composed-sector validation.
- **Constraints:** constraint:no-frame-kill; constraint:strictly-pre; constraint:db-only; constraint:own-db (#632).
- **Decision anchors:** decision:split-half-unit — CROSS-CIRCUIT 2v2 (owner-ruled).
  `@grade: settled/human · leans g7`
- **Evidence:** report reproduces; no leakback; bounded-scope honest; small size stated plainly.

## Deliverable Path Check
- **Committed** — `scripts/instrument_panel_668_report.py`,
  `docs/physics/instrument_panel_668_gb2023q_report.md`,
  `tests/unit/physics/instrument_panel/test_panel_report.py`; `git check-ignore` exits 1.
- The report JSON (if you also emit one) may be committed under docs/physics/ OR left local — state which.

## Required Evidence
- LOAD-BEARING: the report generator runs on the pinned interpreter and produces the .md + numbers;
  paste the four instruments' headline results.
- LOAD-BEARING: `test_panel_report.py` passes (report reproduces deterministically; a no-leakback
  assertion; the bounded-scope note present).
- LOAD-BEARING: pyright-0 on the new script; `git status --porcelain data/` clean at the end.
- Confirmatory: full `tests/unit/physics/instrument_panel/` suite green.

## Verification Commands
```bash
C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe -c "import fastf1; print('env ok')"
C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe scripts/instrument_panel_668_report.py
C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/unit/physics/instrument_panel/test_panel_report.py -q
git status --porcelain data/
```

## Suggested Model Tier
stronger — real-data wiring across four instruments + honest no-frame-kill reporting + the scorecard
composability judgment.

## Authority
The cross-circuit 2v2 split unit, the signed frozen values, and no-frame-kill honest sizing are
DECIDED (owner/Admiral). The scorecard's composability on the real slice is a JUDGMENT — if it
can't compose a full sector prediction, report the limitation honestly and STOP-and-return rather
than fabricating. Do NOT alter a signed value or an instrument's logic.

## Stop Conditions
Stop and return if: the scorecard cannot run at all on the slice; a signed value seems wrong; a real
DB must be written; FastF1 online seems required; or leakback cannot be avoided.

## Return Format
Return IMPLEMENTER_RESULT (slice, files, the four instruments' results, evidence, assumptions, stops,
out-of-scope, workflow feedback). WRITE it to
`.agent-work/668-instrument-panel/crew-results/g7-realrun-implement-result.md` before ending your
turn — that file IS the deliverable.
