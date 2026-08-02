# Implementation Result

Status values follow `skills/workbench/references/status-model.md`.

## Assigned gate
`g6 (issue #662, epic #659) — GATING acceptance: the substantive falsification + verdict`

## Completed slice
Two SEPARATELY-NAMED GATING tests (`claim:map-stable`, `claim:typing-correct`) built on a
new validation harness, run against REAL 2023 data, with a written verdict — plus the
one pre-authorized minimal `drivers=` filter on `reference_lap_from_store` needed to make
the split-half stability proxy runnable.

## Scope
**Files changed:**
- `src/physics/segment_map/derivation/reference_lap.py` — added `drivers: Sequence[str] |
  None = None` to `reference_lap_from_store` (pre-authorized, minimal, backward-compatible;
  `None` path byte-unchanged).
- `tests/unit/physics/segment_map/derivation/test_reference_lap.py` — added
  `TestReferenceLapFromStoreDriversFilter` (real-data, guarded skip-if-absent).
- `scripts/validate_segment_map_662.py` (NEW) — the validation harness: scoped-null check,
  split-half derivation + circular boundary-drift matching, physical-corner-run merging +
  apex-distance computation, map corner-distance-share, `regime_rollup` cross-check, and a
  `main()` that runs everything against Bahrain + Austria 2023 Q and prints every number.
- `tests/unit/physics/segment_map/derivation/test_segment_map_gating.py` (NEW) — the two
  separately-named GATING tests, wired to the validation harness's functions.
- `.agent-work/662-segment-map/VERDICT.md` (NEW, local-only, not committed) — the verdict
  with real numbers.

**Specific exclusions touched:** no — did not edit docs/architecture/*, any existing
segment_map runtime/store/identity file, or `frozen_constants.py`. `regime_rollup.py` and
`corner_attributes.py`/`derive.py`/`tiling.py`/`sector_nesting.py` were read, not edited.

## Behavior changed
Yes, narrowly: `reference_lap_from_store` gained an additive optional `drivers=` filter
(default `None` behavior is byte-unchanged — verified by the full pre-existing
`test_reference_lap.py` suite still passing, 8/8). No other production behavior changed;
everything else added is new test/validation-harness surface.

## Map Impact
- **Structural anchors touched:** `test_segment_map_gating.py`,
  `validate_segment_map_662.py` (both NEW, per the inbound Map Anchors); a minimal
  additive change to `reference_lap.py`'s public signature (`drivers=` kwarg, default
  preserves prior behavior).
- **Capabilities added/changed/affected:** the segment-map derivation pipeline can now be
  run over an arbitrary driver subset (`drivers=`), enabling split-half / partial-field
  stability analysis without touching the store or session layer.
- **Constraints/assumptions touched:** `frozen_constants.MAP_STABILITY_DRIFT_M` (imported,
  never a literal, per constraint) — honored, and its median-drift gate is now backed by
  real evidence for the first time (previously only a frozen number with no real-data
  stress test behind it).
- **Decision candidates / resolved decisions:**
  - `decision:stability-scoped-null-split-half` (inbound, already graded `guess · leans g6
    · settle: enumerate 2023 calendar`) — SETTLED by this gate: `get_calendar(2023)` has 22
    unique GPs, zero repeats, mechanically confirmed. Recommend regrading to
    `settled/measured`.
  - New candidate: the handoff's "assert the boundary drift (median, and report max) is <
    MAP_STABILITY_DRIFT_M" is grammatically ambiguous (assert median-only, or assert both?).
    I read it as "assert median, report max" (see VERDICT.md's own note) because the max is
    dominated by a specific known-noisy quantity (p10 braking-onset over a half-sized
    subsample), not general tiling instability — asserting on it would conflate two
    different failure modes. Flagging this reading as a within-authority judgment call, not
    a settled interpretation, in case Commander/Admiral wants it made explicit for future
    gates that reuse this proxy.
- **Claims/evidence produced:**
  - `claim:map-stable` — split-half median boundary drift PASSES for both Bahrain
    (2.178m) and Austria (3.479m) under `MAP_STABILITY_DRIFT_M=10.0m`.
  - `claim:typing-correct` — Bahrain physical corner count (12) is in the P4 plausible
    range [11,17]; Austria physical corner count (10) EXACTLY matches its official turn
    count (10); the map's corner distance-share (0.3080) is directionally consistent with
    (smaller than) `regime_rollup`'s looser-gated corner distance-share (0.5226).
- **Trust limitations / drift found:** the MAX split-half drift is large at a handful of
  boundaries (15.7m Bahrain, 80.7m Austria) — real, bounded instability at braking-zone
  onsets (and one Austria corner-exit boundary), reported not gated. If a downstream
  consumer ever needs braking-zone boundary precision specifically (not just corner
  typing), this is a genuine open risk worth a tighter follow-up.
- **Triage candidates:**
  1. The braking-zone-onset boundary instability (max drift far above the corner-boundary
     median) suggests the p10 quantile onset detector is the least field-size-robust part
     of the tiling — a future gate could investigate whether a larger p-quantile or a
     bootstrap-stabilized onset estimate reduces this without abandoning the "field
     envelope, not central tendency" design intent (frozen_constants.py's own rationale for
     p10).
  2. Bahrain's physical corner count (12) sits at the LOW end of the P4 range
     [11,17] and below BIC's cited 15 official turns — passes the gate as authored, but if
     a future gate wants tighter agreement with the official count, the
     `CORNER_CURVATURE_THRESHOLD` (inherited from #625, "NOT independently proven as the
     corner/straight gate" per its own frozen_constants.py docstring) is the candidate to
     scrutinize — NOT retuned here (frozen-constants discipline), just flagged per its own
     docstring's own invitation ("carried pending the map typing spot-checks").
  3. Apex locations were reported as distances but not independently checked turn-by-turn
     against a real Bahrain track map/diagram in this gate (out of scope, see below) — a
     natural follow-up for a reviewer with visual track-map access.

## Test mode
**Required:** `test-first / test-after (mixed, per item)` — TDD for the `drivers=` filter
(minimal, additive) was effectively test-after (the filter was added, then exercised via a
new guarded real-data test) since the change is a thin, low-risk addition to an already
G1-reviewed module; the two GATING tests themselves are evidence-only against real data
(no synthetic RED/GREEN cycle makes sense for a validation harness whose whole point is to
report real numbers).
**Satisfied:** yes — full evidence below.

## Evidence

```bash
cd C:/Programs/f1brainz-wt/epic659-662
C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/unit/physics/segment_map/derivation/test_reference_lap.py -q
# 8 passed in 2.81s

C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/unit/physics/segment_map/derivation/test_segment_map_gating.py -q
# 6 passed in 12.53s (no skips fired -- real data present)

C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe -m src.utils.simplification_limits --paths scripts/validate_segment_map_662.py
# PASS (1 files checked)

C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe scripts/validate_segment_map_662.py
# GATING-1: scoped null year=2023 n_circuits=22 has_repeat_circuit=False
# Bahrain: n_boundaries a/b=32/34 median_drift_m=2.178 max_drift_m=15.739
# Austria: n_boundaries a/b=25/25 median_drift_m=3.479 max_drift_m=80.676
# GATING-2: Bahrain physical_corner_count=12 (P4 range [11,17])
#   apex distances (m): [711.3, 790.4, 907.2, 1481.6, 1839.0, 1977.0, 2194.9,
#                         2652.3, 3366.5, 3805.0, 4037.9, 4824.8]
# Bahrain corner_distance_share map=0.3080 regime_rollup=0.5226
# Austria physical_corner_count=10 official_turn_count=10
# exit 0
```

**Result:** pass — all four commands green, re-run twice (once during m2/m3, once during
m4's verification pass) with identical numbers both times.

## TDD evidence, if required
- Failing test observed: N/A for the GATING tests (evidence-only against real data, per
  the handoff's own framing — "the numbers... reproduce when the script re-runs", not a
  RED/GREEN production-code cycle). For the `drivers=` filter: no formal RED was captured
  as a separate step (the parameter was added directly, mirroring how small,
  low-risk, additive kwargs are usually introduced in this codebase) — the GREEN evidence
  (8/8 passing, including the new filter test) is what's carried here; flagged in Workflow
  Feedback below.
- Passing test observed: `test_reference_lap.py` 8/8; `test_segment_map_gating.py` 6/6.
- Refactor while green: no refactor needed; both files were correct on first full run.

## Docs/contracts touched
- none — `docs/architecture/*` was explicitly excluded and not touched.

## Assumptions
- `regime_rollup.load_circuit_frame`'s lack of a year filter is a pre-existing (not a
  bug I'm fixing) property of that function; I filter the returned frame to `year==2023`
  in my own script rather than editing `regime_rollup.py` (read-only, per Allowed Scope).
- The split-half even/odd partition (sorted by `int(driver_num)`) is a within-authority
  choice ("You MAY decide the split") — documented in `split_half_drivers`'s docstring.
- Austria (Red Bull Ring) was chosen as the 2nd GATING-2 circuit specifically for its
  short, unambiguous, well-documented 10-turn layout (lower risk of corner-merging
  ambiguity at chicanes/hairpins than a higher-turn-count circuit); this is a
  within-authority choice, not a settled epic decision.
- The corner distance-share cross-check tolerance is directional (`map_share <
  regime_share`), not a numeric-closeness bound — justified by the two systems' genuinely
  different corner gates (curvature vs. lateral-g threshold), documented in both the
  script and VERDICT.md.
- P4-RESULT.md's plausible range [11, 17] and BIC's 15-turn official count are treated as
  given per the handoff (external references), not re-derived here.

## Stop conditions hit
- none — no real-data check required editing a reviewed module beyond the pre-authorized
  `drivers=` filter; the split-half ran without incident; no frozen threshold looked wrong
  enough to warrant a stop (the low-end P4 placement and the CORNER_CURVATURE_THRESHOLD's
  own "not independently proven" caveat are reported as triage candidates, not treated as
  a blocking anomaly — the count is still within the pre-authorized plausible range).

## Out-of-scope observations
- See Map Impact's "Triage candidates" above (braking-onset instability, low-end Bahrain
  corner count vs official 15, apex-location visual cross-check).
- `data/f1_data_2023.db` shows as modified in `git status` — this predates this gate's
  work (present at the start of this session before any file in this gate was touched);
  not investigated or touched here, flagged only so it isn't mistaken for this gate's
  output.

## Workflow Feedback
- **Handoff gaps:** the phrase "Assert the boundary drift (median, and report max) is <
  MAP_STABILITY_DRIFT_M" is genuinely ambiguous between "assert median only, report max
  for context" and "assert both." I resolved it toward the former (median-only assertion)
  because the real data showed the max is dominated by a specific, understood noise
  source (p10 braking-onset quantile over a half-field subsample) rather than general
  instability — asserting on it would have either forced a much looser threshold for max
  specifically (diluting the gate) or produced a spurious FAIL on a well-understood
  artifact. Naming this reading explicitly in the handoff would remove the ambiguity for
  a future re-run of this gate.
- **Context rediscovered:** had to independently discover that
  `src.data.telemetry_store.DEFAULT_STORE_PATH` is already an ABSOLUTE main-checkout path
  (`C:/Programs/f1Brainz/data/telemetry_store.db`), so `reference_lap_from_store`'s
  `store=None` default resolves correctly even from this worktree (whose own
  `data/telemetry_store.db` does not exist) without any override needed. This wasn't
  stated in the handoff and cost a few minutes of tracing through `session_fit.py` →
  `telemetry_session.py` → `telemetry_store.py` to confirm; worth a one-line anchor note
  for future crews touching `reference_lap_from_store`.
- **Instructions improvised around:** the handoff didn't specify HOW the test file should
  share computation with the validation script (import? duplicate?). I chose
  `import scripts.validate_segment_map_662 as validate` in the test file, matching an
  existing repo convention (`tests/unit/data/test_backfill_data_quality.py` and four
  siblings already `import scripts.<name>` without an `__init__.py` in `scripts/`) rather
  than inventing a new pattern.
- **What would have made this easier:** stating explicitly in the handoff whether the
  MAX split-half drift is meant to be asserted or only reported would have removed the
  one real judgment call in this gate.

## Return status
`complete`
