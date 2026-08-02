# Reviewer Handoff

## Gate
g1 — pace-gap history provider (issue #369, work area `.agent-work/issue-369-pace-gap-form/`)

## What Was Implemented
Data layer for quali pace-gap history: (a) `get_quali_best_valid_laps_batch(year, round_nums)` on the DB metadata mixin returning `{round_num: {driver_id: best_valid_lap_seconds}}` for Q sessions; (b) new pure provider `src/evo_predictor/quali_pace_gap_history.py` — `compute_pace_gaps` (per-event `(t − field_median)/field_median`) and `build_quali_pace_gap_history(db, year, round_num)` returning per-driver gap lists aligned to rounds `1..round_num-1` with `nan` for missing; (c) two new unit test files (14 + 21 tests). Pure addition; no existing behavior modified.

## How to Inspect the Diff
Uncommitted working tree on branch `constellation/issue-369-pace-gap-form`:
```bash
git -C C:\Programs\f1Brainz status
git -C C:\Programs\f1Brainz diff -- src/data/database/_metadata.py
```
New (untracked) files — read directly:
- `src/evo_predictor/quali_pace_gap_history.py`
- `tests/unit/data/test_quali_best_laps_query.py`
- `tests/unit/evo_predictor/test_quali_pace_gap_history.py`

## Task Statement
The full implementer handoff (task, frozen formula, alignment contract, filters): `.agent-work/issue-369-pace-gap-form/crew-handoffs/G1_IMPLEMENTER_HANDOFF.md`. Summary: batch query for best valid non-pit Q laps (filters frozen: `valid_lap = 1`, `pit_in_time IS NULL`, `pit_out_time IS NULL`, `lap_time IS NOT NULL`, session_type 'Q', no track_status filter), MIN per (round, driver), mirroring `get_session_classifications_batch`/`get_practice_lap_times` patterns; plus pure gap provider with `quali_history_full`-style alignment (`src/evo_predictor/data_adapter/_assemble.py:138` is the reference contract).

## Close Criteria
- Query correctness: joins/filters exactly as frozen; MIN per (round_num, driver_id); per-year DB usage via `self.db_path`; empty `round_nums` → `{}`; requested-but-absent rounds present as empty dicts; sqlite error → `DatabaseError`, mirroring sibling methods.
- Gap math: median computed over drivers **with** a valid best lap that event (missing excluded from median); gap `(t − median)/median`; slower → positive; single driver → 0.0; empty event → no gaps; raw values — no clipping.
- Alignment contract: list index `i` = round `i+1`; rounds `1..round_num-1` only (as-of, no current-round leakage); `round_num <= 1` → `{}`; all-missing prior round stays in alignment as nan; driver universe = union over prior rounds.
- Missingness honesty: `nan` only, never imputed, never silently dropped.
- Test quality: the new tests actually pin the above (filters individually exercised, alignment indices asserted, nan placement asserted); fixture DB matches real schema (`src/data/schema.sql`).
- Simplification limits pass on touched paths.
- No FastF1/Jolpica imports anywhere in the new code.

## Allowed Scope
- `src/data/database/_metadata.py` (one method added)
- `src/evo_predictor/quali_pace_gap_history.py` (new)
- `tests/unit/data/test_quali_best_laps_query.py` (new)
- `tests/unit/evo_predictor/test_quali_pace_gap_history.py` (new)

## Specific Exclusions
`src/evo_predictor/models/`, all adapters, `data_adapter/`, `run.py`, gold config, `module_adapters/`, `src/data/schema.sql`, `collector.py`, `load_fastf1.py`. Flag if touched.

## Constraints the Implementation Must Respect
- DB-only (no FastF1), `py` not `python`.
- Gap formula and validity filters are frozen by the human-approved plan — any deviation is a BLOCK.
- Implementer compacted docstrings/SQL in `_metadata.py` to fit the 999-line file ceiling — verify the compaction did not change logic or degrade the docstring below sibling-method standard.
- Type hints consistent with file (repo runs pyright).

## Evidence Produced
From IMPLEMENTER_RESULT (status: complete, TDD satisfied — failing-first observed):
- `py -m pytest tests/unit/data/test_quali_best_laps_query.py tests/unit/evo_predictor/test_quali_pace_gap_history.py -q` → 35 passed in 2.05s
- `py -m pytest tests/unit/data -q` → 77 passed in 6.12s
- `py -m src.utils.simplification_limits --paths <4 touched files>` → PASS (4 files checked)
- lap_time unit verified as seconds (schema.sql line 37 + collector `.dt.total_seconds()` convention)

Re-run any of these yourself; do not take the transcript on faith.

## Suggested Model Tier
simple bounded — small diff, frozen spec, but the alignment/median subtleties deserve a careful read.

## Stop Conditions
Stop and return BLOCK if: the diff cannot be accessed, evidence is absent or unverifiable, or a policy decision is required before a verdict is possible.

## Return Format
Return REVIEW_RESULT: verdict (APPROVE or BLOCK), per-check findings, blockers, out-of-scope observations.
