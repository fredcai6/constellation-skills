# Review Result

Status values follow `skills/workbench/references/status-model.md`.

## Assigned Gate
G1 — Field reference lap builder (issue #662, epic #659)

## Result
`APPROVE`

## Handoff compliance
Implements the task statement exactly: a POOLED field reference lap (curvature/speed/brake on one
shared grid) built from the durable store-first telemetry path, reusing `build_ribbon` for geometry.
New files only: `src/physics/segment_map/derivation/__init__.py`, `reference_lap.py`
(`ReferenceLap`, `build_reference_lap`, `reference_lap_from_store`), plus
`tests/unit/physics/segment_map/derivation/__init__.py`, `test_reference_lap.py` (7 tests). All 5
reviewer FOCUS points confirmed by direct source inspection (see Evidence below).

## Scope drift
None. `git status --porcelain` (full repo) shows only the two new untracked directories for this
gate (plus unrelated sibling `.agent-work/` workbench scaffolding). No existing
`src/physics/segment_map/*.py` runtime file (`runtime.py`, `store.py`, `identity.py`,
`from_mixture.py`, `protocols.py`, `__init__.py`) was touched; no `docs/architecture/*` file was
touched. Both specific exclusions from the handoff honored.

## Evidence verdict
Both Required Evidence commands reproduced independently on the pinned interpreter
(`C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe`):

```
cd C:/Programs/f1brainz-wt/epic659-662
.../python.exe -m pytest tests/unit/physics/segment_map/derivation/test_reference_lap.py -q
====================== 7 passed in 0.80s ======================

.../python.exe -m src.utils.simplification_limits --paths src/physics/segment_map/derivation/reference_lap.py
PASS (1 files checked)
```

Went beyond the handoff's evidence and ran the CREW_CONTEXT-mandated focused physics-region suite
for a regression check:

```
.../python.exe -m pytest tests/unit/physics/ -q
========== 2223 passed, 54 skipped, 0 failed, 11 warnings in 844.11s (0:14:04) ==========
```

No regressions anywhere in the physics region from the new subpackage.

Grid-alignment confirmation (from reading the pooling code): `build_reference_lap` resamples each
lap's speed/brake onto `u_grid = np.linspace(0.0, 1.0, n_grid)` using that lap's own
`u = s / s[-1]` progress (`_per_lap_progress`, `reference_lap.py:108-124`) — the **identical**
formula and identical `u_grid` construction that `ribbon.py`'s `_resample_laps_to_grid`
(`ribbon.py:163-196`) uses to build the pooled XY/curvature geometry. Both channel families are
therefore indexed by the same fractional-progress grid, and `ReferenceLap.__post_init__` enforces
`len(arr) == n_grid` for every channel and `distance_m` strictly increasing.

```bash
$ grep -n "fastf1\|build_session_ribbon" src/physics/segment_map/derivation/reference_lap.py
15:    ``ribbon.build_session_ribbon``.
327:    cache otherwise -- this function never imports/calls ``fastf1`` and never
328:    uses ``ribbon.build_session_ribbon``). Pools EVERY driver's clean flying
```
Both hits are docstring prose disclaiming their use; no import/call statement present. Confirmed
`fastf1`-free and `build_session_ribbon`-free.

## Code/doc quality
Minimal, well-scoped, project-rule compliant. `docs/agents/CREW_CONTEXT.md` and `GLOSSARY.md`
checked against the diff:
- **DB-only** (`r4a-db-only`): `reference_lap_from_store`'s only data-fetch is
  `session_fit.load_quali_session`, which tries the durable SQLite store
  (`telemetry_session.load_db_session`) first and falls back through the single approved
  preprocessing seam (`loaders.load_session`) — never `fastf1` directly. Confirmed at source.
- **Truth-anchored physics evidence** (`r4b-truth-anchored`): the module introduces no new physical
  law — geometry is delegated to `build_ribbon` verbatim (byte-exact parity asserted in
  `TestCurvatureMatchesRibbon`, effectively L4 parity with an already-tested reference); the
  genuinely new logic (median/mean-fraction pooling) has L2 known-answer tests
  (`TestSpeedMedianPooling` distinguishes median from mean on a skewed set;
  `TestBrakeFractionPooling` asserts an exact 0.6/0.0 split).
- **Structure/state** (`r4c-structure-state`): module-level state is one immutable float constant
  and a type alias; no impure caching, no module-level session/DB singleton — sessions are created
  per-call inside `reference_lap_from_store`.
- **No invented frozen constant**: `_MIN_LAP_TIME_S = 50.0` is a verified byte-identical reuse of
  the literal `50` `session_fit.py` already applies in three places (`fit_driver`'s clean-lap
  floor), not a new threshold.

### Fowler refactoring pass (`r6-fowler`)
Recorded to `.agent-work/662-segment-map/g1-review/fowler_pass.json`, cleared
`verify_fowler_pass.py` (12/12 baseline smells visited). Two non-blocking observations, one logged
override:
- **duplicated-code (flagged)** — `reference_lap.py`'s `_per_lap_progress` (lines 108-124)
  duplicates the arc-length parameterisation formula already inline in `ribbon.py`'s
  `_resample_laps_to_grid` (lines ~181-189): same `dX/dY/ds/s/u=s/s[-1]` math, different variable
  names. Separately, `_MIN_LAP_TIME_S=50.0` duplicates `session_fit.py`'s existing `50` literal as
  an independent copy rather than an imported shared constant — a future threshold change needs
  synchronized edits with no compiler/test tie between the copies. Both are correct today; worth a
  follow-up extraction (a shared `_arc_length_progress(X, Y)` helper and a shared
  `MIN_CLEAN_LAP_TIME_S` constant), not a blocker.
- **long-parameter-list (flagged)** — `reference_lap_from_store` has 9 total parameters (3
  positional + 6 keyword-only-with-defaults). Defensible today as a thin wrapper forwarding to two
  lower-level signatures, but worth a `**kwargs`/options object if either callee grows further.
- **data-clumps (overridden)** — `laps_xy`/`laps_speed`/`laps_brake` travel as three parallel
  sequences (a textbook clump), but `docs/agents/CREW_CONTEXT.md`'s "one canonical representation
  per concept at a boundary" already establishes bare per-lap array tuples as the sole
  representation for per-lap telemetry in this package (`ribbon.build_ribbon`'s `laps_xy`,
  `ribbon.drs_zone_mask`'s `laps_drs`); wrapping only this new function's version would create a
  second, competing representation for the identical concept in the same file.
- Remaining 9 baseline smells (long-method, large-class, feature-envy, primitive-obsession,
  shotgun-surgery, divergent-change, message-chains, speculative-generality,
  comments-as-deodorant): **absent**.

## Map impact verdict
- **Evidence supports claimed change:** yes — the 246-pooled-lap real-store run and the 7/7 test
  suite genuinely back the claimed pooled-reference-lap capability.
- **Constraints not violated:** yes — `constraint:db-only-analysis` honored (verified at source,
  not just by grep).
- **Notes match the diff:** yes — structural anchors (`build_ribbon`, `load_quali_session`) are
  reused unmodified as claimed; new capability `segment_map_derivation` is real; both inbound
  decisions (`decision:reference-lap-pooled-not-per-lap`, `decision:derivation-subpackage-placement`)
  implemented as specified.
- **Decision candidates surfaced:** yes — the implementer surfaced a new, ungraded candidate (the
  parallel-array contract for `laps_speed[i]`/`laps_brake[i]`) that future gates calling
  `build_reference_lap` directly need to know.
- **Durable context routed:** yes — formally routed via `flag-candidate` (see
  `triage_candidates` in `g1-review/review.json`, id `tc1`) so it reaches Cartographer/Commander
  at reconcile rather than being dropped.

## Reconciliation check
No divergence from recorded architecture requiring immediate reconciliation; `docs/architecture/*`
correctly untouched at this gate. One un-graded decision candidate flagged above for Commander/
Cartographer to grade at the next reconcile — not a G1 blocker.

## Blockers
- none

## Out-of-scope observations
- Fowler: duplicated arc-length formula + duplicated clean-lap-time literal across
  `reference_lap.py`/`ribbon.py`/`session_fit.py` — candidate for a small shared-helper extraction
  in a later gate (see Fowler pass above).
- Fowler: `reference_lap_from_store`'s 9-parameter forwarding signature — watch if it grows further.
- Un-graded decision candidate `decision:reference-lap-parallel-array-contract` (routed via
  `flag-candidate`, `tc1`) — needs a `@grade:` tag before G2+ can rely on the contract without
  re-litigating it.
- Implementer's own forward-looking note (not a defect, restated for visibility): `DBSession.laps`
  has no `PitInTime`/`PitOutTime` columns, so a future gate reusing `ribbon.py`'s private
  `_get_clean_laps` helper against a `DBSession` would silently skip the pit-lap filter rather than
  erroring — worth a docstring note on `telemetry_session.py` for whoever next touches that helper.

## Workflow Feedback
- **Handoff gaps:** none of substance. The handoff's Close Criteria phrasing ("by that lap's
  normalized arc-length u=s/s[-1]") was ambiguous enough that the implementer had to pick between
  two defensible readings (parallel-sampled vs. independently-timed-then-resampled) and documented
  the choice; this reviewer independently verified the chosen reading is the one that makes
  "arc-length" literally true and matches `build_ribbon`'s own internal convention, so no rework was
  needed — but the ambiguity itself is real and is exactly the kind of thing a future handoff
  referencing `build_reference_lap` directly should pin down explicitly (as the implementer already
  flagged).
- **Context rediscovered:** none beyond what the implementer already surfaced (the
  abbreviation-vs-driver-number `pick_drivers` keying quirk was already documented in
  `g1-impl-result.md` and verified again here by reading `reference_lap_from_store`'s fallback
  path).
- **Instructions improvised around:** the reviewer skill's survey template ships 7 base items; the
  `r4-quality` "append a check per rule" instruction was followed by appending three siblings
  (`r4a-db-only`, `r4b-truth-anchored`, `r4c-structure-state`) — the engine placed them at the end
  of the item queue (after `r6-fowler`) rather than immediately after `r4-quality`, which is a minor
  ordering surprise worth knowing about but did not block anything (`current` still walked me to
  each one before consolidation).
- **What would have made this easier:** none — the handoff's Required Evidence commands and Map
  Anchors were sufficient to drive the whole review without additional lookups beyond the cited
  reused seams.

## Return status
`complete`
