# Reviewer Handoff — G3 (cumulative_track_laps unlock)

## What was implemented
`EstimateRecord.cumulative_track_laps: Optional[int]=None` (self-heals via `_migrate_missing_columns`);
`session_race.session_cumulative_track_laps(...)` (FIELD laps before the constructor's fastest clean
lap, reusing `compute_cumulative_track_laps`); `record_from_estimate(..., cumulative_track_laps=None)`;
`estimate_store.populate_cumulative_track_laps_for_demo(...)`. Result:
`.agent-work/513-fp-fits/result-g3-implement.md`.

## How to inspect
`git diff -- src/physics/layer2/estimate_store.py src/physics/layer2/session_race.py` + the tests
`tests/unit/physics/layer2/test_estimate_store.py`, `tests/unit/physics/layer2/test_session_race.py`.

## Close criteria to verify
- Column added next to `mass_kg_assumed`; a legacy store WITHOUT the column self-heals via the existing
  additive `_migrate_missing_columns` ALTER (test opens a copy lacking the column → self-heal → NULL).
- `session_cumulative_track_laps` counts FIELD laps (ALL cars) before the constructor's fastest clean
  (`valid_lap=1`) lap, using the `lap_number < anchor` convention, reusing `compute_cumulative_track_laps`
  (that function BYTE-UNCHANGED). Returns None on no clean lap / missing session.
- `record_from_estimate` default-arg path byte-identical (backward compatible).
- Demo populate does UPDATE over existing rows only (no inserts, no real backfill / #646).

## Constraints to verify
- physics-region: no evo/latent_power/compound_prior/fastf1 imports.
- NO real `data/*.db` read/modify in tests; `git status --short data/` clean.
- `compute_cumulative_track_laps` unchanged (diff it).

## Evidence produced
`py -m pytest tests/unit/physics/layer2/test_estimate_store.py tests/unit/physics/layer2/test_session_race.py -q` → 125 passed (reproduce). Self-heal-on-legacy-store test present.

## Verification commands
```bash
cd /c/Programs/f1-513 && PYTHONPATH=/c/Programs/f1-513 py -m pytest tests/unit/physics -q && git status --short data/
```

## Return format
REVIEW_RESULT: verdict APPROVE or BLOCK + findings (severity, defect, location). BLOCK on: any change to
`compute_cumulative_track_laps`, any non-additive migration, any real-DB read in tests, any real backfill,
or any backward-incompatible `record_from_estimate` default. NOTE: the estimate_batch-vs-new constructor
resolution mismatch is ALREADY logged as triage candidate tc2 — do not re-block on it, note if seen.
Write REVIEW_RESULT to `.agent-work/513-fp-fits/result-g3-review.md` AND SendMessage to "ShipI-513".
