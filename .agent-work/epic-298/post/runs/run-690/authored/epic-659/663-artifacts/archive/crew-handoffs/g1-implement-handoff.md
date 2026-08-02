# Implementer Handoff

## Gate
g1-implement

## Task
Create `src/physics/layer2/grip_store.py`: a `GripEstimateRecord` frozen dataclass + `GripStore` class implementing the artifact-family half of the grip-baseline module G (issue #663, epic #659). This is a NEW file, mirroring the existing `src/physics/layer2/estimate_store.py`'s shape exactly (that file is your primary reference — read it in full before writing anything).

## Protected Intent
G must be a single canonical store every future consumer subtracts identically. The record shape frozen here is load-bearing for every later gate (g2 fit logic, g3 batch driver, g4/g5 acceptance harnesses) — do not under-scope the fields.

## Test Mode
Test-after allowed (store/round-trip tests, not TDD) — brief reason: the shape is precedented (estimate_store.py already proves this pattern works), so tests-after on a known-good pattern is appropriate; still required before this gate closes.

## Close Criteria
- `GripEstimateRecord` is a frozen dataclass with PK `(year, gp_name, session_type)` — session-level, NOT per-constructor (G is field-pooled across all cars in a session, unlike `EstimateRecord`'s per-constructor PK).
- Fields (exact names): `year: int, gp_name: str, session_type: str, session_id: int, curve_asymptote: float, curve_asymptote_sigma: float, curve_rate: float, curve_rate_sigma: float, session_offset: float, session_offset_sigma: float, curve_offset_correlation: float, n_stints_used: int, n_drivers_used: int, n_laps_used: int, fit_status: str` (one of `"ok"|"thin_fallback"|"error"`), `fallback_reason: Optional[str], cumulative_track_laps_max: int, rain_flag: bool, fitted_at: str, error: Optional[str] = None`. All the `_sigma`/float fields should default to `None`/`Optional[float]` where a record with `fit_status="error"` would not have them populated (mirror `estimate_store.py`'s own optional-field conventions for its error-record path — see `error_record()` there).
- `GripStore` class: own standalone SQLite database (its own file, own `sqlite3` connection — NOT the canonical season DB), one table (e.g. `grip_estimates`).
  - `__init__(self, db_path: str, *, must_exist: bool = False)`
  - `has(self, year: int, gp_name: str, session_type: str) -> bool`
  - `upsert(self, record: GripEstimateRecord) -> None` — `INSERT OR REPLACE` keyed on the PK tuple (idempotent).
  - `load(self, year: Optional[int] = None, session_type: Optional[str] = None, status: Optional[str] = "ok") -> pandas.DataFrame` — builds a `WHERE` clause from whichever args are non-`None`.
- **Additive-only schema migration**: a `_migrate_missing_columns` helper that does `PRAGMA table_info` then `ALTER TABLE ADD COLUMN` for any dataclass field missing from an existing table — mirror `estimate_store.py:400-412` EXACTLY (same approach, same never-drop/never-rename guarantee).
- An `error_record(year, gp_name, session_type, *, session_id, error, fitted_at=None) -> GripEstimateRecord` free function mirroring `estimate_store.py`'s never-lose-a-failure `error_record()` pattern.

## Allowed Scope
- New file: `src/physics/layer2/grip_store.py`.
- New file: `tests/unit/physics/layer2/test_grip_store.py`.
- Read-only reference: `src/physics/layer2/estimate_store.py` (do not modify it).

## Specific Exclusions
- Do NOT modify `src/physics/layer2/estimate_store.py` or any other existing file in `src/physics/layer2/` in this gate.
- Do NOT write the fit logic (curve/offset estimation) here — that is g2's job. This gate is the artifact shape + storage only; fields exist but nothing computes their values yet (tests populate them with synthetic fixture values).
- Do NOT write `grip_batch.py` — that is g3's job.

## Constraints
- Follow `estimate_store.py`'s exact shape/pattern — design-it-twice is deliberately skipped for this per issue #663 (the interface shape is precedented, not novel). Do not invent a different persistence approach.
- Standard library `sqlite3` + `pandas` only (matching `estimate_store.py`'s own dependencies) — no new third-party dependency.

## Map Anchors (inbound)
- **Structural:** `struct:physics.layer2` — `src/physics/layer2/`, component level. New sibling module.
- **Capability:** new capability — grip-baseline artifact storage + query surface (does not exist yet).
- **Constraints/assumptions:** `assumption:additive-only-migration` — the estimate-store convention never drops/renames columns.
- **Decision anchors:** decision pressure (not yet a graded decision) — PK is session-level `(year,gp_name,session_type)` not per-constructor, since G is field-pooled. This is a deliberate, already-made choice for this gate (not open for the implementer to revisit) — flagged for a future Cartographer decision-anchor recording at the run's reconcile step, not something to resolve here.
- **Evidence expectations:** field names must carry the `cumulative_track_laps` convention (see `session_race.py:268` `compute_cumulative_track_laps` and the existing `cumulative_track_laps` bridge column on `EstimateRecord` in `estimate_store.py`) — do not invent a differently-named axis.
- **Map confidence flags:** none.

## Deliverable Path Check
- **Committed** — `src/physics/layer2/grip_store.py`; new file, will appear in `git status` (untracked until staged) — not gitignored (verify with `git check-ignore src/physics/layer2/grip_store.py` before you finish; expect exit 1 = not ignored).
- **Committed** — `tests/unit/physics/layer2/test_grip_store.py`; same as above, verify not ignored.

## Required Evidence
- `git check-ignore src/physics/layer2/grip_store.py; echo $?` and same for the test file — both must print `1` (not ignored). Load-bearing: paste both outputs.
- `py -m pytest tests/unit/physics/layer2/test_grip_store.py -q` — full output pasted, all tests passing. Load-bearing.
- A one-paragraph confirmation that the additive-migration helper was modeled on `estimate_store.py`'s exact approach (cite the line range you read it from). Confirmatory — a spot-check is fine, no need to paste code diff-by-diff.

## Verification Commands
```bash
cd /c/Programs/f1brainz-wt/epic659-663
py -m pytest tests/unit/physics/layer2/test_grip_store.py -q
git status --porcelain src/physics/layer2/grip_store.py tests/unit/physics/layer2/test_grip_store.py
git check-ignore src/physics/layer2/grip_store.py; echo "exit=$?"
```

## Suggested Model Tier
Simple bounded — reason: precedented shape (mirrors an existing, working file almost line-for-line); low ambiguity, low risk.

## Authority
The record's field list and PK shape above are ALREADY DECIDED (from the run's `understand`/`plan` steps) — do not redesign them. If you find the field list is missing something g2/g3 will clearly need (based on reading estimate_store.py's own field list for comparison), you may ADD a field with a stated one-line reason in your IMPLEMENTER_RESULT, but do not remove or rename any listed field.

## Stop Conditions
Stop and return if: the additive-migration pattern in `estimate_store.py` turns out to be structured differently than described here (in which case describe what you actually found and how you adapted), or a decision outside this authority is needed.

## Return Format
Return IMPLEMENTER_RESULT: completed slice, files changed, test mode satisfied, evidence produced (paste command outputs), assumptions used, stop conditions hit, out-of-scope observations, workflow feedback.

**Write your IMPLEMENTER_RESULT to `.agent-work/663-grip-g/crew-handoffs/g1-implement-result.md` AND return it as your final message text** (you are running as a synchronous subagent — your final message is read directly by the dispatching commander).
