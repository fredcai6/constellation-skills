# Review Result

Status values follow `skills/workbench/references/status-model.md`.

## Assigned Gate
`g1` — #629 Phase-5 feature-view store foundation

## Result
`APPROVE`

## Handoff compliance
All Close Criteria met and independently reproduced (not taken on the implementer's word):
- `src/physics/feature_view/{__init__,records,store}.py` exist; `grep -rn "evo_predictor\|evo\." src/physics/feature_view/` returns zero matches.
- `py -m pytest tests/unit/physics/feature_view -q` reproduced: **27 passed**, same test names/counts as the implementer's evidence.
- The three RESERVED fields (`process_noise_link`, `parc_ferme_step`, `unit_class_residuals`) were exercised directly (not just read) — each construction attempt with a non-`None` value raises `ValueError` for real.
- `git check-ignore src/physics/feature_view/store.py` reproduced: exit 1 (not ignored).
- `py -m src.utils.simplification_limits --paths src/physics/feature_view` reproduced: PASS (3 files).

## Scope drift
None. `git status --porcelain` shows only three untracked paths: `.agent-work/629-feature-view/` (workbench artifacts), `src/physics/feature_view/`, `tests/unit/physics/feature_view/`. No existing tracked file modified. Specific exclusions honored: `src/physics/layer2/` and `src/physics/weekend_state/` untouched; every test uses `tmp_path`, confirmed by reading all four test files — no writes to `data/physics_estimates.db` or any committed DB path.

## Evidence verdict
TDD evidence is credible (RED observed for `records.py`/`store.py` against real `ModuleNotFoundError`; the two protected gate tests were written against the by-then-built store per the handoff's explicit allowance, with both asserted to be real, not simulated). Both protected-gate claims were independently adversarially probed (see below) — this is the substantive part of this review.

### Adversarial bypass construction (append-only)
Two scratch scripts (`bypass_append_only.py`) constructed the two lazier implementations the Close Criteria name:
1. **`INSERT OR REPLACE` instead of plain `INSERT`** — reproduced: the second identical-key write no longer raises `sqlite3.IntegrityError`, so `test_duplicate_natural_key_and_model_version_raises_real_integrity_error`'s `pytest.raises(sqlite3.IntegrityError)` would correctly **fail to observe an exception and error out** — the gate test genuinely catches this regression, it does not pass it silently.
2. **UNIQUE key missing `model_version`** — reproduced: a legitimate new-model-version insert (test 1's own scenario, `v2` with a bumped `model_version`) is **wrongly rejected** by the lazier key, so `test_older_model_version_row_survives_a_newer_version_write_byte_identical` would itself error on this lazier implementation — again, genuinely caught, not silently passed.

Both of the Close Criteria's named lazier-implementation scenarios are confirmed to break the gate tests as designed. The real `sqlite3.IntegrityError` traceback in the implementer's evidence was independently re-triggered.

### Adversarial bypass construction (as-of leakage)
Three scratch probes (`bypass_as_of_leakage.py`), importing the real checker/regex live from the test module rather than reimplementing it:
1. **The handoff's named negative control** (`SELECT * FROM weekend_state_records WHERE constructor=?`, session-unfiltered) — confirmed `_all_statements_session_scoped` returns `False`: correctly rejected.
2. **A subtler attack not named in the handoff**: a WHERE-clause that carries `session_type IN (...)` syntactically but with the IN-list hardcoded to **all four sessions regardless of the as-of bound**. The text-only regex checker (`_SESSION_SCOPE_RE`) cannot distinguish this from a correctly-bound clause — confirmed it scores `True` (a real, if narrow, soundness gap in the SQL-shape check taken in isolation). However, I confirmed the co-located **row-content assertions** in the same tests (`len(result_a["weekend_state"]) == 1`, exact axis-value match, the FP3-excludes-Q check) independently catch this exact bug class — a hardcoded-all-sessions `load_as_of` returns 4 rows where the test asserts 1. The shipped test suite is sound end-to-end via this defense-in-depth (SQL-shape check + data-content check), even though the SQL-shape check alone has this narrow blind spot. See Out-of-scope observations.
3. Independently re-captured (fresh `sqlite3.connect` trace-callback wrap, not reusing the implementer's capture) the real `store.load_as_of("FP2")` SQL: binds literal `('FP1', 'FP2')` only — confirmed FP3/Q never appear.

No constructed bypass slipped through the shipped test suite.

## Code/doc quality
Fowler refactoring pass completed and recorded (`fowler_pass.json`, `verify_fowler_pass.py` exit 0). One non-blocking observation (`duplicated-code`: the four `load_*` methods share a near-identical body); three smells present but overridden against logged repo-standard reasons (`data-clumps` and `primitive-obsession` against the sibling `estimate_store.py`'s identical `_PK`/raw-str convention; `speculative-generality` against the handoff's own plan-level Authority section for the three reserved fields, converted from bare speculation to a guarded placeholder by the `__post_init__` checks). No blocking code smells.

Reuse constraint verified: `store.py` imports (does not reimplement) `effective_axis_sigma`/`UNRESOLVED_AXIS_SIGMA_FRAC`/`normalize_axis_status` from `estimate_store_fields` — confirmed by reading the import statement and by independently re-running the two identity tests (`test_effective_axis_sigma_for_row_reuses_layer2_helper_not_reimplemented`, `test_normalize_axis_status_is_the_real_layer2_function`).

Project-specific rules from `docs/agents/CREW_CONTEXT.md` checked: validation exceptions name field+expectation+actual (`session_ordinal`'s `ValueError` names the bad input and the known set); no undocumented input shapes (`load_as_of` has a single required shape, no default `as_of_session`); module-level state is immutable constants only (`SESSION_ORDER`, `DEFAULT_DB_PATH`, `_TABLES`) — no mutable singleton.

## Map impact verdict
- **Evidence supports claimed change:** yes — the store/records/tests exist exactly as the Map Impact notes describe, and both protected-gate claims independently reproduce.
- **Constraints not violated:** yes — `constraint:physics_region_no_evo_import` independently grep-confirmed clean.
- **Notes match the diff:** yes — `struct:physics.feature_view` created exactly as scoped; no file outside the new package/test directory touched.
- **Decision candidates surfaced:** the implementer's one flagged decision candidate (the `__post_init__` guard on reserved fields, in case G2+ wants to relax it) is reasonable and correctly flagged rather than silently baked in.
- **Durable context routed:** no new triage candidates beyond what the handoff already scoped to G2-G5; nothing dropped.

## Reconciliation check
No divergence from the recorded architecture. The new-component-vs-layer2-module-leaf decision was already resolved at plan and was not quietly revisited — `store.py`'s docstring justifies the standalone-DB choice by citing the `fit_store.py`/`wear/store.py` precedent rather than re-litigating it, and the store imports (does not reimplement) the three named layer2 helpers.

## Blockers
- none

## Out-of-scope observations
- **`duplicated-code` (non-blocking):** the four `load_weekend_state`/`load_car_basis_posteriors`/`load_lap_evidence`/`load_feature_view_rows` methods share a near-identical body (build `year`/`gp_name` clauses, call `self._load`); could collapse to one generic `load(table, year=, gp_name=)`, but the named per-table methods aid caller discoverability. Not worth blocking a G1 foundation gate over.
- **As-of leakage checker's SQL-shape regex has a narrow blind spot (non-blocking, worth a note for G2+):** `_SESSION_SCOPE_RE` (`session_type\s+IN\s*\(|session_ordinal\s*<=`) verifies an `IN (...)` clause is *present* in the WHERE text but cannot verify its *bound values* are actually the as-of subset rather than a hardcoded all-sessions list. In the current implementation this is a non-issue because `load_as_of`'s own `allowed_sessions` computation is correct (independently reproduced: literal `('FP1','FP2')` only for `as_of="FP2"`), and any future regression of this kind would still be caught by the tests' row-content assertions (`len == 1`, exact axis value, FP3-excludes-Q) — so today's test suite is sound end-to-end. But if a future gate (G2+) refactors `load_as_of` and the row-content assertions get weakened/removed while the SQL-shape check is kept as the sole guard, this blind spot becomes exploitable. Suggest (not blocking): a follow-up test asserting the actual *bound parameter values* of the `IN (...)` clause equal the expected as-of subset (available via the same `set_trace_callback` capture, since SQLite's trace callback substitutes literal values into the printed statement — confirmed during this review's probes), closing the gap between "shape present" and "shape correctly bound." Candidate for Triage against G2 (`load_as_of` is the surface any future L1-L4 wiring will call).
- **Broader physics-region suite not fully reproduced (non-blocking):** `CREW_CONTEXT.md`'s Verification-By-Region table names `py -m pytest tests/unit/physics/ -v` as the physics region's focused command (broader than just `feature_view`). I ran it as an extra diligence check; it did not finish inside a 300s budget (large suite, consistent with `TESTING.md`'s note that some physics suites run long) — inconclusive, not a failure. Not treated as a blocker: this gate touches zero existing files (confirmed under Scope drift), so no existing physics test can be affected by construction, and the handoff's own required command (`tests/unit/physics/feature_view` only) is what actually gates this new, isolated leaf package. Flagging so Commander/Cartographer knows the wider-region command wasn't exercised to completion this run, in case a future gate wants a full confirmed green run on record.

## Workflow Feedback
- **Handoff gaps:** none — confirmed after review: the handoff's Close Criteria named the exact two lazier-implementation scenarios worth adversarially constructing (`INSERT OR REPLACE`, UNIQUE key missing `model_version`) and the exact negative-control query to try (`SELECT * FROM weekend_state_records WHERE constructor=?`) — all three were directly actionable without guessing at what "bypass" meant.
- **Context rediscovered:** the correct interpreter (`py` resolving to `AppData/Local/Microsoft/WindowsApps/py.exe`, Python 3.14.3) needed the same `PATH` fix the implementer's Workflow Feedback already flagged (prepend that directory ahead of the POSIX-shell-default `py`) — confirms this is a standing session/box quirk worth carrying forward, not implementer error.
- **Instructions improvised around:** the reviewer skill's checklist-engine reference (`references/checklist-engine.md`) notes the `refresh-request` cold-start display (`DIGEST:`/`REFRESH REQUESTED:`) is `gated`-only and does not surface on a `survey` checklist's `current` — not hit this run (no refresh request was needed), but flagging that I read and accounted for this known gap per the reference doc, consistent with its documented workaround (read the survey JSON's `evidence` array directly if it were needed).
- **What would have made this easier:** none beyond the above — the handoff was unusually precise about exactly which adversarial constructions to attempt, which made the "actually try to construct a bypass" instruction concrete rather than open-ended.

## Return status
`complete`
