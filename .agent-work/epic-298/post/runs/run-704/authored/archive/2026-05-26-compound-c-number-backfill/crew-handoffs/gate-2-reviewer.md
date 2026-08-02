# Crew Handoff: Gate 2 — Reviewer

**Work ID:** 20260526-compound-c-number-backfill  
**Gate:** 2 of 2  
**Role:** Reviewer  
**Repo path:** `C:\Programs\f1Brainz\.claude\worktrees\inspiring-kalam-e15259`

---

## What was implemented

1. **`src/data/collector.py`** — `_compound_string_to_c_number` extended:
   - Added `_ERA_2018_COMPOUND_TO_C` module-level dict (SUPERHARD=1..HYPERSOFT=7)
   - Added optional `year` param; year≤2018 uses direct dict lookup; 2019+ uses alloc-based logic
   - Caller in `_extract_lap_times` now passes `year=year`

2. **`scripts/backfill_compound_c_number.py`** (new) — pure-DB backfill that updates
   `compound_c_number` from existing `compound` column using compounds.yaml

---

## Review checklist

### Code correctness

**`_compound_string_to_c_number`:**
- [ ] `_ERA_2018_COMPOUND_TO_C` dict has correct C-number values (SOFT=4, SUPERSOFT=5, ULTRASOFT=6,
  HYPERSOFT=7, MEDIUM=3, HARD=2, SUPERHARD=1)
- [ ] Year branch: `year <= 2018` guard is correct (not `< 2018`, not `== 2018`)
- [ ] 2019+ path still functions correctly — alloc-based logic unchanged
- [ ] Guard for None/nan/UNKNOWN strings fires before dict lookup
- [ ] `year=None` (default) falls through to alloc path — backward compatible for existing callers
- [ ] Wet/Intermediate not in the dict — returns None correctly for those

**Caller update:**
- [ ] `_extract_lap_times` passes `year=year` to the function
- [ ] No other callers of `_compound_string_to_c_number` that should also pass year (check with grep)

**`backfill_compound_c_number.py`:**
- [ ] Only UPDATEs rows WHERE `compound_c_number IS NULL` — idempotent
- [ ] Does NOT modify the `compound` column
- [ ] Correct DB path lookup via `Config.db_path_for_year(year)`
- [ ] `--dry-run` flag works (prints without writing)
- [ ] Session join is correct (gets gp_name + year for allocation lookup)
- [ ] Skips rows where `_compound_string_to_c_number` returns None (wet/unknown)
- [ ] Commits after batch, not per-row

### Spot-check correctness
- [ ] Austria 2018 (alloc=[4,5,6]): SOFT→4, SUPERSOFT→5, ULTRASOFT→6 (verified by implementer —
  check the spot-check in evidence)
- [ ] 2019 Bahrain (alloc=[1,2,3]): HARD→1, MEDIUM→2, SOFT→3 — run this query:
  ```sql
  SELECT compound, compound_c_number, COUNT(*)
  FROM lap_times l JOIN sessions s ON l.session_id=s.id
  WHERE s.year=2019 AND s.gp_name='Bahrain' AND s.session_type='R'
  GROUP BY compound, compound_c_number ORDER BY compound;
  ```

### Evidence validation
- [ ] `unexpected_null = 0` for 2018, 2019, 2022 (confirmed by implementer)
- [ ] Orphaned-row explanation for 2020/2021 is credible — verify orphan claim:
  ```sql
  SELECT COUNT(*) FROM lap_times WHERE session_id NOT IN (SELECT id FROM sessions);
  ```
  Run against 2020 and 2021 DBs. Should match the reported 3,692 / 16,615 counts.

### Tests
- [ ] `py -m pytest tests/unit/evo_predictor/ -x -q` passes
- [ ] Run `py -m pytest tests/ -x -q --ignore=tests/integration` — confirm no new failures

---

## Report back

For each checklist item: pass / fail / concern.  
For any failures: exact error, file:line, severity (blocker vs. concern).  
Final verdict: APPROVE or REJECT with reason.
