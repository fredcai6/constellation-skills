# Reviewer Handoff

## Gate
g1-implement (reviewing for g1-review)

## Survey State Location
`.agent-work/663-grip-g/g1-review/review.json`

## What Was Implemented
`src/physics/layer2/grip_store.py`: a `GripEstimateRecord` frozen dataclass (PK session-level `(year, gp_name, session_type)`) + `GripStore` class (standalone SQLite, additive-only migration, has/upsert/load) + `error_record()` free function — the artifact-storage half of the grip-baseline module G (issue #663). Mirrors `src/physics/layer2/estimate_store.py`'s shape.

## How to Inspect the Diff
This is an UNCOMMITTED working tree in a linked worktree at `C:/Programs/f1brainz-wt/epic659-663` (branch `epic659/663-grip-g`). Inspect with:
```bash
cd /c/Programs/f1brainz-wt/epic659-663
git status --porcelain
git diff -- src/physics/layer2/grip_store.py tests/unit/physics/layer2/test_grip_store.py
```
(Both files are new/untracked — `git diff` on an untracked path shows nothing; use `cat`/Read on the files directly to inspect content, and `git status --porcelain` to confirm they're the only changes.)

## Task Statement
Create `src/physics/layer2/grip_store.py` mirroring `estimate_store.py`'s exact shape: `GripEstimateRecord` dataclass + `GripStore` class with additive-only migration, following the repo's precedented estimate-store pattern (design-it-twice explicitly skipped per issue #663).

## Close Criteria
- `GripEstimateRecord` is a frozen dataclass, PK `(year, gp_name, session_type)` — session-level, NOT per-constructor.
- Exact field list per the implement handoff (`.agent-work/663-grip-g/crew-handoffs/g1-implement-handoff.md`): year, gp_name, session_type, session_id, curve_asymptote(+sigma), curve_rate(+sigma), session_offset(+sigma), curve_offset_correlation, n_stints_used, n_drivers_used, n_laps_used, fit_status, fallback_reason, cumulative_track_laps_max, rain_flag, fitted_at, error.
- `GripStore`: own standalone SQLite DB, `has()/upsert()/load()`, additive-only migration mirroring `estimate_store.py:400-412` EXACTLY (PRAGMA table_info + ALTER TABLE ADD COLUMN, never drop/rename).
- `error_record()` free function, never-lose-a-failure pattern.
- Tests at `tests/unit/physics/layer2/test_grip_store.py` covering has/upsert/load round-trip AND the additive migration (a real test that adds a column to an existing table and confirms old data survives — not just a fresh-table happy path).

## Allowed Scope
New files only: `src/physics/layer2/grip_store.py`, `tests/unit/physics/layer2/test_grip_store.py`.

## Specific Exclusions
Must NOT modify `estimate_store.py` or any other existing `src/physics/layer2/` file. Must NOT contain fit logic (g2) or batch driver (g3) — check this wasn't scope-crept in.

## Constraints the Implementation Must Respect
- Follows `estimate_store.py`'s exact pattern (no novel design).
- Standard library `sqlite3` + `pandas` only, no new third-party dependency.
- Additive-only migration — verify by reading the migration code AND confirming a test actually exercises it (adds a column to a pre-existing table, checks old rows survive), not just asserted in prose.

## Map Anchors (inbound)
- **Structural:** `struct:physics.layer2` — new sibling module.
- **Capability:** new — grip-baseline artifact storage + query surface.
- **Constraints/assumptions:** `assumption:additive-only-migration`.
- **Decision anchors:** decision pressure — session-level PK vs EstimateRecord's per-constructor PK. Not yet graded (pending Cartographer at reconcile); confirm the implementation matches the PK exactly as specified, this is not the implementer's or your call to revise.
- **Evidence expectations:** `claim:cumulative-track-laps-reuse` — field names carry the `cumulative_track_laps` convention (check `cumulative_track_laps_max` field name specifically).
- **Map confidence flags:** none.

## Evidence Produced
IMPLEMENTER_RESULT at `.agent-work/663-grip-g/crew-handoffs/g1-implement-result.md` — 9/9 tests passing (pasted output), `git check-ignore` exit=1 for both new files. **IMPORTANT ENVIRONMENT NOTE:** the implementer found that plain `py` on this Bash-tool sandbox's PATH resolves to a codex-runtime shim lacking scipy/fastf1 (pre-existing repo-wide issue, not caused by this change) — re-run tests using the real launcher: `"/c/Users/fredc/AppData/Local/Microsoft/WindowsApps/py.exe" -m pytest tests/unit/physics/layer2/test_grip_store.py -q`. This evidence targets `g1-integrate.c1` (test-pass postcondition, already corrected to use this launcher path via engine `amend`) and `g1-review.c1` (this review's own `review-result` artifact).

## Suggested Model Tier
Simple bounded — small, precedented-pattern review.

## Stop Conditions
Stop and return BLOCK if: the diff cannot be accessed, evidence is absent or unverifiable (re-run it yourself using the corrected launcher path above), or the additive-migration test is missing/tautological.

## Return Format
Return REVIEW_RESULT: verdict (APPROVE or BLOCK), per-check findings, blockers, out-of-scope observations, workflow feedback. Write it to `.agent-work/663-grip-g/crew-handoffs/g1-review-result.md` AND return it as your final message text (you are a synchronous subagent).
