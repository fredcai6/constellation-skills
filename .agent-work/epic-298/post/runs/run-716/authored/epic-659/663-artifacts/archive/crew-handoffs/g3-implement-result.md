# IMPLEMENTER_RESULT — g3-implement (issue #663, module G batch driver + consumer query)

## Assigned gate
`g3-implement` — the grip-baseline season batch driver (`grip_batch.py`) + the
consumer-facing `get_grip_at` query function (additive to `grip_store.py`).

## Completed slice
Created `src/physics/layer2/grip_batch.py` with `run_grip_batch`, mirroring
`estimate_batch.py`'s injectable-`Callable`-default seam pattern exactly (loop
seasons -> GPs via `calendar_fn` -> session types via an injectable
`fit_fn`/`record_fn`, idempotent skip-unless-force, per-unit failure
isolation). Added `get_grip_at` (+ a new `GripRecordNotFoundError` exception)
to `grip_store.py`, additively. Created
`tests/unit/physics/layer2/test_grip_batch.py` (13 tests) covering both.

## Scope
**Files changed:**
- `src/physics/layer2/grip_batch.py` (new)
- `tests/unit/physics/layer2/test_grip_batch.py` (new)
- `src/physics/layer2/grip_store.py` (additive edit — see below)

**Specific exclusions touched:** No. `grip_baseline.py` (g2) and
`estimate_batch.py`/`estimate_store.py` were read but not modified. No g4/g5
acceptance-harness work was done.

## Behavior changed
Yes — new capability: a season/GP/session-type batch driver that populates
`GripStore` from g2's fit function, and the canonical consumer query
(`get_grip_at`) every future "subtract G" caller uses.

## `grip_store.py` additive-edit confirmation
Exactly two `Edit` tool calls were made against the file, each matching exact
pre-existing text (so neither could have touched anything else):
1. Inserted `import math` alongside the existing `import sqlite3` block.
2. Appended `GripRecordNotFoundError` (new exception class) and `get_grip_at`
   (new function) immediately after the existing `error_record()` function —
   nothing before that point was altered.

`grip_store.py` is still **untracked** in git (g1/g2 were never committed to
this worktree), so there is no tracked baseline to `git diff` against —
`git status --porcelain` shows only `?? src/physics/layer2/grip_store.py`
(a new/untracked file, not a tracked-modified one). The additive guarantee
here rests on the two `Edit` calls' exact-match preconditions, not a diff;
noting this as a workflow-feedback point below since the handoff assumed a
diff would be available.

## `run_grip_batch` design notes (Authority-scoped decision)
The handoff's signature lists `record_fn=...` as an injectable collaborator,
mirroring `estimate_batch.py`. But `estimate_batch.py` needs `record_fn`
because its `estimate_fn` returns a raw view object that must be *transformed*
into a storable `EstimateRecord`; g2's `fit_fn`
(`fit_session_grip_baseline`) is different — it already **returns a fully
populated `GripEstimateRecord`** on success (`fit_status` ok/thin_fallback),
or `None` when the session is absent from the DB, or (internally) its own
`error_record` when ITS internal try/except catches a failure. There is no
separate "estimate then transform" step for grip.

I resolved this by re-mapping `record_fn`'s role to the one genuine gap: an
error record for a session whose `fit_fn` call **raises outright** (before
g2's own internal try/except could run, e.g. `_get_session_row`'s DB read is
not wrapped in g2's try). `record_fn` defaults to `grip_store.error_record`
and is called only on that outer-catch path, with a `session_id=-1` sentinel
(documented in-code) since no real session_id was ever resolved. This keeps
`record_fn` genuinely injectable/testable per the handoff's stated intent
("every collaborator is an injectable Callable parameter... lets tests inject
fakes") while fitting grip's actual data shape. Flagged explicitly here since
it's a plausible-alternative reading of the handoff, not the literal
`estimate_batch.py` split.

`session_type=None` fans out over `src.utils.constants.SESSION_TYPES`
(`['FP1','FP2','FP3','Q','R','S','SQ']`) — the one existing canonical
session-type list in the repo, matching g2's `decision:session-scope-uniform`
(fit runs uniformly across all session types).

`weekend_neighbors` (g2's thin-session cross-session extrapolation input) is
**NOT wired** by the batch driver — `fit_fn` is called as
`fit_fn(year, gp, session_type, db_path=db_path)`, leaving `weekend_neighbors`
at its default `None`. The handoff's exact signature
(`run_grip_batch(store, *, seasons, db_path, force=False, session_type=None,
fit_fn=..., calendar_fn=..., record_fn=..., log=print)`) does not mention
`weekend_neighbors`, and wiring it correctly needs an ordered second pass
(gather already-fitted normal sessions per GP before fitting a thin one),
which is materially more than "mirror `estimate_batch.py`'s pattern." Flagged
as a triage candidate below rather than improvised.

## `get_grip_at` sigma-propagation choice (Authority-scoped decision)
First-order/delta-method combination:
`var = sigma_offset^2 + (1-e^{-rate*x})^2*sigma_asymptote^2 +
(x*asymptote*e^{-rate*x})^2*sigma_rate^2 +
2*(1-e^{-rate*x})*curve_offset_correlation*sigma_offset*sigma_asymptote`.
The offset<->asymptote cross-term uses g2's stored `curve_offset_correlation`
(its own T2 separability diagnostic); rate<->offset and rate<->asymptote
cross-terms are dropped because g2 stores no such correlation — a documented
simplification, not an oversight (docstring states this explicitly). For a
`thin_fallback` record (no curve params fit), there's no curve term to
propagate, so `get_grip_at` returns `(session_offset, session_offset_sigma)`
directly — the handoff's own sanctioned conservative fallback, applied only
when curve params are genuinely absent (not as a general shortcut).

The exception (`GripRecordNotFoundError`) is raised both when no record
exists for the PK AND when a record exists but has no usable fit
(`session_offset is None`, i.e. `fit_status="error"`) — treating both as "no
usable answer" rather than letting an error-status record silently produce a
nonsense `(None, None)` or crash on a `float(None)`.

## Test mode
**Required:** test-after.
**Satisfied:** yes — 13 new tests (grip_batch.py) + 9 pre-existing
(grip_store.py) = 22, all green.

## Evidence

### Full new-file test run (load-bearing)
```
$ py.exe -m pytest tests/unit/physics/layer2/test_grip_batch.py -q
collected 13 items
tests\unit\physics\layer2\test_grip_batch.py .............               [100%]
13 passed in 0.53s
```

### Per-unit failure isolation (load-bearing — most important behavior in this gate)
```
$ py.exe -m pytest tests/unit/physics/layer2/test_grip_batch.py -q -k isolat
collected 13 items / 11 deselected / 2 selected
tests\unit\physics\layer2\test_grip_batch.py ..                          [100%]
2 passed in 0.06s
```
`test_batch_isolates_one_failing_session_and_continues`: a fit_fn that raises
for exactly ONE `(gp, session_type)` (Monaco/Q, `RuntimeError("curve_fit did
not converge")`) among several — asserts `counts["fitted"]==1`,
`counts["errors"]==1`, the failing session lands in the store with
`fit_status="error"` and the exact exception message, `session_id==-1`
(sentinel), and every other session (Bahrain) still gets fitted and stored as
`"ok"`. `test_batch_isolation_survives_failures_on_both_sides_of_a_good_session`:
two failing GPs bracketing one good one — exact counts, exact per-GP status
partition.

### get_grip_at (load-bearing)
```
$ py.exe -m pytest tests/unit/physics/layer2/test_grip_batch.py tests/unit/physics/layer2/test_grip_store.py -q -k get_grip_at
collected 22 items / 16 deselected / 6 selected
......                                                                    [100%]
6 passed in 0.11s
```

### Full suite together (grip_batch.py + grip_store.py)
```
$ py.exe -m pytest tests/unit/physics/layer2/test_grip_batch.py tests/unit/physics/layer2/test_grip_store.py -q
collected 22 items
tests\unit\physics\layer2\test_grip_batch.py .............               [ 59%]
tests\unit\physics\layer2\test_grip_store.py .........                   [100%]
22 passed in 0.61s
```

### simplification_limits (self-checked before returning)
```
$ py.exe -m src.utils.simplification_limits --paths src/physics/layer2/grip_batch.py src/physics/layer2/grip_store.py tests/unit/physics/layer2/test_grip_batch.py
PASS (3 files checked)
```

### git check-ignore (both new files committable)
```
$ git check-ignore src/physics/layer2/grip_batch.py; echo exit=$?
exit=1
$ git check-ignore tests/unit/physics/layer2/test_grip_batch.py; echo exit=$?
exit=1
$ git status --porcelain -- src/physics/layer2/grip_store.py src/physics/layer2/grip_batch.py tests/unit/physics/layer2/test_grip_batch.py
?? src/physics/layer2/grip_batch.py
?? src/physics/layer2/grip_store.py
?? tests/unit/physics/layer2/test_grip_batch.py
```

## Close-criteria coverage
- `run_grip_batch` mirrors `run_estimate_batch`'s injectable-fn seam (same
  style of `Callable` defaults; see the design-note above for the deliberate
  `record_fn` re-mapping) — ✅
- Per-unit failure isolation genuinely works: `test_batch_isolates_one_failing_session_and_continues`
  and its bracketing variant — ✅ (evidence pasted above)
- `get_grip_at` correctly evaluates the stored curve, returns `(mu, sigma)`,
  raises `GripRecordNotFoundError` on a missing OR unusable record — ✅
- Tests at exact path `tests/unit/physics/layer2/test_grip_batch.py` — ✅

## Assumptions used
- `record_fn`'s role is re-mapped to "build the error record for a session
  whose `fit_fn` raised outright" rather than a literal copy of
  `estimate_batch.py`'s estimate->record transform (see design note above).
- `weekend_neighbors` cross-session wiring is deliberately NOT implemented in
  the batch driver (out of the handoff's exact signature; flagged as triage).
- A `thin_fallback` record's `get_grip_at` sigma is exactly
  `session_offset_sigma` (no curve term exists to propagate) — the handoff's
  own explicitly sanctioned conservative option.
- `curve_offset_correlation` is the only stored cross-parameter correlation;
  rate<->offset/asymptote cross-terms are dropped from the delta-method sigma
  (documented in the `get_grip_at` docstring).
- `session_id=-1` is used as the sentinel for an outer-layer error record
  where `fit_fn` raised before resolving a real session_id (PK doesn't include
  `session_id`, so this cannot collide with or corrupt any stored row).

## Stop conditions hit
None. `estimate_batch.py`'s pattern mapped cleanly (with the documented
`record_fn` re-interpretation, which stayed within the handoff's stated
Authority — "the exact sigma-propagation method... is yours to choose" and
the general "mirror the seam style" instruction, not a literal line-for-line
copy requirement).

## Out-of-scope observations (triage candidates for Commander)
1. **`weekend_neighbors` wiring.** `run_grip_batch` never supplies g2's
   `weekend_neighbors` parameter, so every thin-session fallback in a real
   batch run degrades straight to the degenerate all-thin field-prior path
   rather than g2's richer nearest-normal-neighbour extrapolation. A future
   enhancement needs an ordered two-pass batch (fit normal sessions first per
   GP, then re-pass thin ones with the now-available neighbours) — real
   design work, not a drop-in.
2. **`GripStore.load()` scan cost in `get_grip_at`.** The current
   implementation calls `store.load(year=year, session_type=session_type,
   status=None)` (a full `SELECT *` for that year+session_type) and filters
   `gp_name` in pandas, rather than a single indexed point query. Fine at
   current data volumes; a hot-path consumer calling `get_grip_at` in a tight
   loop may want a dedicated single-row SQL query added to `GripStore` later.
3. **`session_id=-1` sentinel semantics.** If any future consumer of the
   `grip_estimates` table assumes `session_id` is always a valid FastF1/DB
   session id, the `-1` sentinel on this specific error path (outer-catch,
   `fit_fn` raised before resolving a session) would need documenting there
   too — currently only documented in `grip_batch.py`'s own module docstring
   and inline comment.

## Map Impact
- **Structural anchors touched:** `struct:physics.layer2` — new module
  `grip_batch.py` (module G's batch driver, sibling to `grip_baseline.py`/g2
  and `grip_store.py`/g1); `grip_store.py` grew a new consumer-facing function
  + exception (additive).
- **Capabilities added:** the module-G season/GP/session-type batch driver
  (`run_grip_batch`) and THE consumer query surface for subtracting G
  (`get_grip_at`) — the latter is explicitly the Protected Intent surface
  named in the handoff.
- **Constraints/assumptions relied on:** `decision:session-scope-uniform`
  (g2) — honored by fanning out over all `SESSION_TYPES` when unfiltered.
- **Decision candidates:** the `record_fn` re-mapping (design note above) is
  a plausible-alternative reading worth a Cartographer/Commander sanity check
  if a future gate (g4/g5) assumed the literal `estimate_batch.py` split.
- **Claims/evidence produced:** `claim:failure-isolation-batch-level` — a
  session whose `fit_fn` raises is isolated and recorded, never sinking the
  batch (2 dedicated tests). `claim:get-grip-at-honest-sigma` — `get_grip_at`
  never returns an implied `sigma=0`; both the normal-fit delta-method path
  and the thin-fallback path always return a positive, non-degenerate sigma
  (tested directly).
- **Trust limitations / drift found:** none new.
- **Triage candidates:** the three items above (weekend_neighbors wiring,
  `get_grip_at` query cost, `-1` sentinel documentation reach).

## Workflow Feedback
- **Handoff gaps:** The handoff's `record_fn=...` in the exact signature
  implicitly invites a literal mirror of `estimate_batch.py`'s
  estimate-then-transform split, but g2's `fit_fn` already returns the full
  record — there's no natural "transform" step for `record_fn` to do on the
  success path. A one-line note ("record_fn only applies to the outer-catch
  failure path, since fit_fn already returns a full record") would have saved
  the design-choice writeup above.
- **Context rediscovered:** Had to independently locate the repo's one
  canonical session-type list (`src.utils.constants.SESSION_TYPES`) since the
  handoff said "all types" without naming the source; a pointer would have
  saved a grep.
- **Instructions improvised around:** The Deliverable Path Check's
  `grip_store.py` diff expectation assumes the file is tracked; it's
  untracked (g1/g2 never committed in this worktree), so `git diff` shows
  nothing. Substituted a by-construction argument (two exact-match `Edit`
  calls) instead — worth noting for the next handoff in this same
  epic/worktree since the same will be true for g4/g5 unless g1-g3 get
  committed first.
- **What would have made this easier:** A one-line clarification of
  `record_fn`'s intended role given g2's single-function fit shape (vs.
  estimate_batch.py's two-step shape), and a note that `grip_store.py` is
  still untracked so diff-based additive-confirmation isn't available.

## Return status
`complete`
