# Review Result

Status values follow `skills/workbench/references/status-model.md`.

## Assigned Gate
g6 (issue #662, epic #659) — GATING acceptance: the substantive falsification + verdict

## Result
APPROVE

## Handoff compliance
Fully satisfied. Two SEPARATELY-NAMED test classes (`TestGating1MapStability` -> `claim:map-stable`,
`TestGating2TypingCorrect` -> `claim:typing-correct`) were built on a new validation harness
(`scripts/validate_segment_map_662.py`), run against real 2023 data, plus the one pre-authorized minimal
`drivers=` filter on `reference_lap_from_store` needed for the split-half proxy. `VERDICT.md` records the
numbers and the honest scoped-null statement. All Required Evidence commands were re-run independently and
reproduced exactly (see Evidence verdict).

## Scope drift
None beyond what was pre-authorized. Only `src/physics/segment_map/derivation/reference_lap.py` (the
pre-authorized additive `drivers=` filter) plus its test were touched among existing files; the two new
files (`validate_segment_map_662.py`, `test_segment_map_gating.py`) are within Allowed Scope; `VERDICT.md`
is a local work-area file. Specific Exclusions honored: no edits to `docs/architecture/*`,
`frozen_constants.py`, or any other segment_map runtime/store/identity file (confirmed via `git status`/
`git diff` — only `reference_lap.py` modified in that area). `git check-ignore` exits 1 (not ignored) for
both new committable files, matching the handoff's own Deliverable Path Check.

Two non-blocking hygiene observations (not part of this gate's diff, not blockers):
- `data/f1_data_2023.db` shows a same-size binary diff in `git status`, but its mtime (14:40) did not
  change even after this review re-ran the full validate script and both test suites — confirmed
  pre-existing, not caused by g6 (matches the implementer's own disclosure).
- `.agent-work/663-grip-g/` (g4/g5-heldout/synthetic-results JSON) is untracked clutter unrelated to
  issue #662, likely leftover from a different concurrent gate sharing this worktree — flagged for
  Commander/workbench hygiene, not a g6 defect.

## Evidence verdict
All four Required Evidence commands were independently re-run on the pinned interpreter
(`C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe`) and reproduced exactly:

- `pytest tests/unit/physics/segment_map/derivation/test_segment_map_gating.py -q` -> **6 passed** (no skips
  fired; matches impl-result's 6/6).
- `pytest tests/unit/physics/segment_map/derivation/test_reference_lap.py -q` -> **8 passed** (matches
  impl-result's 8/8 — confirms the `drivers=` default path is backward-compatible).
- `py -m src.utils.simplification_limits --paths scripts/validate_segment_map_662.py` -> **PASS (1 files
  checked)**.
- `py scripts/validate_segment_map_662.py` -> exit 0, stdout matched `VERDICT.md`/`g6-impl-result.md`
  **byte-for-byte**:
  - GATING-1 scoped null: `year=2023 n_circuits=22 has_repeat_circuit=False`
  - Bahrain split-half: `n_boundaries a/b=32/34 median_drift_m=2.178 max_drift_m=15.739`
  - Austria split-half: `n_boundaries a/b=25/25 median_drift_m=3.479 max_drift_m=80.676`
  - Bahrain physical corner count: `12` (P4 range [11,17]), apex distances identical to VERDICT.md
  - Bahrain corner distance-share: `map=0.3080 regime_rollup=0.5226`
  - Austria: `physical_corner_count=10 official_turn_count=10`

No claim in the impl-result or VERDICT.md failed to reproduce.

## Code/doc quality
Meets project rules (`docs/agents/CREW_CONTEXT.md`): DB-only (grep confirms zero `fastf1` references in
the new/changed files — all data access via `session_fit.load_quali_session` store-first path and
`DatabaseManager`); fail-visibly (every "UNAVAILABLE" branch prints/skips with the causing exception,
never fabricates a number); `MAP_STABILITY_DRIFT_M` imported, never a literal, and `CORNER_CURVATURE_THRESHOLD`
untouched (`frozen_constants.py` has no diff); validation messages name field/expectation/actual; no mutable
module-level state introduced; region verification (physics) run and green.

**Verified specifically:**
- **Physical-corner merge is correct, no double-count.** `sector_nesting._split_at_lines` implements
  split-not-snap by inserting the sector line and duplicating the straddled segment's *own* `seg_type` on
  both new pieces (`reference_lap.py`/`sector_nesting.py:166-169`). A sector-split corner therefore surfaces
  in the final `seg_type_code` array as two *adjacent, same-type* `CORNER` segments, which
  `physical_corner_runs`'s ordinary contiguous-run grouping merges back into exactly one physical corner —
  no sector-line-aware special case is needed, and none was added. This was verified by reading the merge
  logic directly, not just trusting the docstring's claim.
- **`drivers=` filter is genuinely backward-compatible.** The diff shows `driver_pool = session.drivers if
  drivers is None else [...]`, then `for driver_num in driver_pool:` — when `drivers=None` the loop target
  is the identical `session.drivers` object used before this parameter existed. The full pre-existing
  `test_reference_lap.py` suite (8 tests) still passes unchanged, confirming no behavior regression on the
  default path.
- **Split-half is a genuine disjoint-subset derivation**, not a synthetic/fabricated comparison: two real
  `ReferenceLap`/`Tiling` pairs are built from actual even/odd driver-number partitions of the same
  session's real laps, and boundaries are matched via a documented circular nearest-neighbor method (not a
  symmetric optimal assignment, explicitly documented as such).
- **Scoped null is honest, not silently green.** `ScopedNullResult.tested = False` is a distinct field from
  "gate passed"; the 2023 no-repeat-circuit fact is mechanically confirmed
  (`len(calendar) == len(set(calendar))`), never asserted as if cross-weekend stability had actually been
  tested.
- **Distance-share divergence rationale is sound.** `regime_rollup`'s `CORNER_GATE_MS2 = 3.0` m/s² lateral-g
  gate is confirmed (by reading `regime_rollup.py`) to be a materially looser corner criterion than this
  map's curvature-radius threshold, so the map's smaller share (0.3080 < 0.5226) is the expected direction,
  not an unexplained mismatch — and the test only asserts the *directional* inequality, not a numeric-
  closeness bound.
- **No frozen constant was retuned.** `git diff`/`git status` confirm `frozen_constants.py` has zero
  changes; `MAP_STABILITY_DRIFT_M` and `CORNER_CURVATURE_THRESHOLD` are both imported, never redefined or
  hardcoded as literals in the new files.

**Fowler refactoring pass** (`.agent-work/662-segment-map/g6-review/fowler_pass.json`, verified via
`verify_fowler_pass.py` exit 0): all 12 baseline smells received a verdict — 8 absent, 4 overridden with a
logged standard + reason (long-method for `main()`, cited against the heavier `validate_refine_505.py`
217-line precedent; duplicated-code/data-clumps/primitive-obsession, each citing the same subpackage
conventions g5-review already ruled on for this exact derivation package). Zero flagged.

## Map impact verdict
- **Evidence supports claimed change:** yes — every claim in the impl-result's Map Impact section was
  independently reproduced (see Evidence verdict).
- **Constraints not violated:** yes — `MAP_STABILITY_DRIFT_M` imported and honored; no frozen constant
  retuned; DB-only; no existing segment_map runtime/store/identity file edited.
- **Notes match the diff:** yes — structural anchors, capability change (`drivers=` filter enabling
  subset derivation), and constraint notes all match what the diff actually touched.
- **Decision candidates surfaced:** yes — `decision:stability-scoped-null-split-half` (confirmed present in
  `execute.json:1133` and `MISSION_FRAME.md:81`, currently graded `guess`) is correctly recommended for
  regrade to `settled/measured` now that its `settle:` experiment (calendar enumeration) has actually run —
  surfaced as a recommendation, not silently self-regraded, which is within the implementer's authority
  either way.
- **Durable context routed:** yes — three triage candidates (braking-onset boundary instability, low-end
  Bahrain corner count vs BIC's 15, apex visual cross-check) are routed as out-of-scope observations for a
  future gate/reviewer, not silently dropped or acted on outside scope.

## Reconciliation check
No unreconciled architecture divergence. The one open reconciliation item (regrading
`decision:stability-scoped-null-split-half` to `settled/measured` in `execute.json`/`MISSION_FRAME.md`) is
Commander/closeout's action item, already correctly surfaced by the implementer rather than silently
resolved or ignored.

## Blockers
- none

## Out-of-scope observations
- `.agent-work/663-grip-g/` untracked JSON files in this worktree are unrelated to issue #662 — workbench
  hygiene item for Commander, not a g6 defect.
- `decision:stability-scoped-null-split-half` regrade to `settled/measured` — action item for
  Commander/closeout on `execute.json`/`MISSION_FRAME.md`.
- The three triage candidates already named in the impl-result (braking-onset boundary instability at a
  handful of specific boundaries; Bahrain's physical corner count sitting at the low end of the P4 range
  vs BIC's 15; apex locations not independently checked against a real track map/diagram) — carry forward
  as-is, no new candidates found by this review.

## Workflow Feedback

- **Handoff gaps:** None material. The one genuine ambiguity ("assert the boundary drift (median, and
  report max) is < MAP_STABILITY_DRIFT_M") was already flagged by the implementer and resolved reasonably
  (median-only assertion); this review agrees with that reading given the max is traced to a specific,
  understood noise source (p10 braking-onset quantile over a half-field subsample), not general
  instability.
- **Context rediscovered:** None beyond what the implementer already documented (the
  `DEFAULT_STORE_PATH` absolute-path resolution). This review did not need to rediscover anything new to
  verify the claims — the handoff's "How to inspect" section and the impl-result's Evidence section were
  sufficient to reproduce every number directly.
- **Instructions improvised around:** none — none of the skill's engine verbs, the handoff's structure, or
  the FOWLER_PASS template needed improvisation for this review. One judgment call: for `duplicated-code`,
  `data-clumps`, and `primitive-obsession` this review re-verified (rather than blindly copying) that
  g5-review's prior override reasoning still applies to *this* diff's specific functions before reusing it
  — worth noting since a future reviewer should not assume a sibling gate's Fowler override automatically
  carries over without re-checking the specific code in front of them.
- **What would have made this easier:** none — the handoff's "Reviewer FOCUS" list mapped cleanly onto
  the survey's checks and the exact numbers to reproduce were stated up front, which made independent
  verification fast and unambiguous.

## Return status
complete
