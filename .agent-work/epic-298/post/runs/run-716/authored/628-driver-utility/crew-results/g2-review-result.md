# Review Result

## Assigned Gate
`g2-review` (#628 Phase 3b, driver-utility latent + explicit-unknown status + artifact)

## Result
`APPROVE`

## verdict: APPROVE

## Handoff compliance
All close criteria met, independently re-verified (not just re-reading the implementer's evidence):

- `estimate_driver_utility(rows_df) -> DataFrame` returns exactly one row per `(year, driver,
  constructor, axis)` with columns `delta, sigma, status, tau, n_sessions, n_points,
  effective_sigma`.
- δ estimation reuses `pool_random_effects` unmodified (grep-confirmed import at
  `driver_utility.py:68`, no reimplementation; `git diff --stat` on `pooling.py` is empty). The
  well-supported-driver test asserts exact equality against an independently-computed
  `pool_random_effects` call.
- **Load-bearing check (OWNER-HARD explicit-unknown contract), independently reproduced from
  scratch** — beyond re-running the delivered tests, I wrote two standalone scripts that call
  `estimate_driver_utility`/`effective_axis_sigma` directly with fresh inputs the implementer
  never constructed:
  1. A thin (1-session) driver/axis row with `delta` **exactly 0.0** and a tiny own `sigma=0.001`
     → `status="unresolved"`, `effective_sigma=1.432` — far above the reserved floor (0.1) and
     far above `sigma * 10`.
  2. A direct comparison of `effective_axis_sigma(value=delta, ...)` (the handoff's literally
     prescribed call form) vs `effective_axis_sigma(value=None, ...)` (the shipped fix), both fed
     `delta=0.0`: `value=delta` returns `0.001` (sigma unchanged — **the reserved-sigma contract
     is defeated**); `value=None` returns `1.43` (**contract honored**). This independently
     confirms the implementer's self-reported "bug found and fixed mid-build" is a real defect
     they actually fixed, not merely asserted in prose — the fix is present in shipped code at
     `driver_utility.py:183`: `value=(delta if status == "resolved" else None)`.
- **Nothing dropped**, independently confirmed: re-ran the delivered `TestNothingDropped`
  scenario plus my own zero-valid-observation case (all `g_deficit` null for a driver/axis) —
  exactly one `unresolved` row is emitted, `delta`/`sigma` are `NaN`, `effective_sigma=0.1`
  (synthesized purely from the axis `reference_value`). An axis-null error row (whole round
  failed) correctly produces **no** phantom output row.
- **Resolved path**, independently confirmed: a 5-session group → `status="resolved"`, `delta`
  matches an independently-computed `pool_random_effects` call, `effective_sigma == sigma`
  (unchanged passthrough).
- `write_driver_utility_db` writes to an **untracked** SQLite DB; `git status data/` shows only
  G1's pre-existing untracked scratch DB — `data/driver_utility.db` does not exist on disk (only
  written under pytest `tmp_path`, matching the handoff's "G5 runs the real batch" scoping).

## Scope drift
None. `git diff --stat HEAD -- src/physics/layer2/pooling.py src/physics/layer2/estimate_store_fields.py`
is empty (zero modification to either reused seam). Full `git status --porcelain` shows only the
2 new files (`src/physics/utilization/driver_utility.py`, `tests/unit/physics/test_driver_utility.py`)
plus `.agent-work/` scratch and G1's pre-existing untracked DB. No G3 (held-out gate) or G5 (real
batch) logic present, matching the handoff's specific exclusions.

## Evidence verdict
Required evidence present and independently reproduced:

```
$ py -m pytest tests/unit/physics/test_driver_utility.py -q
============================= test session starts =============================
platform win32 -- Python 3.14.3, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Programs\f1-628
configfile: pyproject.toml
plugins: anyio-4.13.0, hypothesis-6.152.9, cov-7.1.0, mock-3.15.1
collected 8 items

tests\unit\physics\test_driver_utility.py ........                       [100%]

============================== 8 passed in 1.23s ==============================
```

```
$ py -m src.utils.simplification_limits --paths src/physics/utilization/driver_utility.py
PASS (1 files checked)
```

```
$ git check-ignore -v src/physics/utilization/driver_utility.py tests/unit/physics/test_driver_utility.py
(exit 1 -- neither path is gitignored)

$ git status --porcelain data/
?? data/driver_utility_observables.db     (G1's pre-existing untracked scratch DB, untouched)
```

Independent load-bearing-check scripts (not part of the delivered test suite), re-run fresh in
this review:

```
$ py verify_g2.py
PER row: {..., 'delta': 0.0, 'sigma': 0.001, 'status': 'unresolved', 'effective_sigma': 1.4324803663575985}
PASS: delta==0.0 exactly, unresolved status, effective_sigma is WIDE: 1.4324803663575985
ALO zero-obs row: {..., 'status': 'unresolved', 'delta': nan, 'effective_sigma': 0.1}
PASS: zero-observation group emits a row, status unresolved, effective_sigma synthesized: 0.1

$ py verify_g2_bug.py
buggy (value=delta literal handoff form): 0.001
fixed (value=None, as implemented): 1.43
CONFIRMED: the handoff's literal call form defeats the reserved-sigma contract when delta==0;
the implemented value=None fix restores it.
```

## Code/doc quality
Meets CREW_CONTEXT.md rules, checked independently: no FastF1 import (grep exit 1); input
validation names field/expectation/actual (`"rows_df: missing required columns {sorted(missing)},
got {sorted(rows_df.columns)}"`); missingness is represented intentionally (zero-observation group
→ explicit `None`/`NaN`, not zeroed/imputed); module scope holds only 5 immutable constants, zero
mutable state, zero `DatabaseManager` singleton, zero stray `print()`; tunable thresholds
(`MIN_RESOLVED_SESSIONS`, `REFERENCE_VALUE_FLOOR_MS`) are named constants with docstring
rationale; reuse discipline is real (imports, not copy-paste, confirmed via `git diff --stat`).

**Fowler refactoring pass** (`r6-fowler`, required): 12/12 baseline smells visited, all `absent`,
record at `.agent-work/628-driver-utility/g2-fowler-pass.json`,
`verify_fowler_pass.py` exits 0 (`smells=12, flagged=[], overridden=[]`). The module is small,
single-purpose, has no copy-pasted logic vs. its sibling `driver_utility_observable.py` (different
domains — telemetry arrays vs. pooled session rows), uses a named `_GROUP_KEYS` constant instead
of scattered tuples, and its one substantial inline comment documents a genuinely non-obvious
cross-module precedence trap in the reused seam rather than compensating for locally confusing
code.

## Map impact verdict
- **Evidence supports claimed change:** yes — the delta/status/effective_sigma/nothing-dropped
  claims are all independently reproduced above, including a genuinely novel test I constructed
  beyond the delivered suite.
- **Constraints not violated:** yes — the OWNER-HARD explicit-unknown contract is honored; `data/
  driver_utility.db` stays untracked; `pool_random_effects`/`effective_axis_sigma` are reused
  unmodified.
- **Notes match the diff:** yes — the Map Impact section's claimed structural/capability/
  constraint impact matches what the diff actually contains; no overstatement.
- **Decision candidates surfaced:** n/a — no new decision required; `decision:c1_driver_utilization_design`
  is followed, not re-opened.
- **Durable context routed:** yes — one triage candidate flagged (tc1, below) for the
  `effective_axis_sigma` docstring trap; G3/G5 correctly identified as the natural next gates.

## Reconciliation check
No architecture divergence requiring Commander reconciliation. `struct:physics.utilization` is
already mapped (`docs/architecture/packets/physics.md` lines 44, 1217-1220, path
`src/physics/utilization/`); `driver_utility.py` is a natural additive file within that
already-mapped path. `decision:c1_driver_utilization_design` is cited and followed (the decision's
four design choices concern G1's car-prior/frontier construction; G2 builds on top of that output
without altering any of them) — not re-opened or contradicted. The map does not yet name
`driver_utility.py` by name — expected content drift for Cartographer's next pass on a
multi-gate build (G3/G5 still pending), not a review-blocking gap.

## Blockers
- none

## Out-of-scope observations
- (tc1, flagged to triage_candidates in the survey) `effective_axis_sigma` (`src/physics/layer2/
  estimate_store_fields.py:139-168`) prioritizes `value` over `reference_value` whenever `value is
  not None` — a real, independently-reproduced caller trap for any metric that can be genuinely
  ~0 while unresolved. The implementer already fixed their own call site (`value=None` when
  `status != "resolved"`) and flagged this in their result; I independently re-confirmed the trap
  is real (script comparison above) and recommend a docstring note on `effective_axis_sigma`
  itself stating the precedence rule explicitly, so a future caller (G3, G5, or another
  axis-status consumer) does not have to rediscover it from first principles.

## Workflow Feedback
- **Handoff gaps:** none — confirmed after review: the handoff's "Exact seam signatures" section
  and Close Criteria were sufficient to independently re-derive and re-test the load-bearing
  contract without needing anything not in the handoff or the cited source files.
- **Context rediscovered:** none — confirmed after review: the implementer's result file already
  named the exact bug/fix and file/line, so no rediscovery was needed beyond reading the seam
  source directly (which the handoff already pointed at via "Exact seam signatures").
- **Instructions improvised around:** none — confirmed after review: the reviewer skill's survey
  items, the handoff's close criteria, and the required-evidence list mapped cleanly onto this
  gate; no ambiguity required improvisation.
- **What would have made this easier:** none — confirmed after review: the handoff already named
  the load-bearing check precisely enough (including the implementer's self-reported bug) that
  independent reproduction was straightforward with two short standalone scripts.

## Return status
`complete`
