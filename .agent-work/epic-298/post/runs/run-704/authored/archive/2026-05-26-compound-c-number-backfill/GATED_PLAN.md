# Gated Plan: compound_c_number backfill + 2021 sprint collection

**Work ID:** `20260526-compound-c-number-backfill`  
**Intent:** Ensure 2018–2021 DBs have (a) complete session data and (b) correct `compound_c_number`
populated in `lap_times`, enabling the compound prior pipeline to generate priors for those years.

---

## Scope

**In scope:**
- Collect 3 missing 2021 sprint sessions (Great Britain S, Italy S, Brazil S)
- Fix `_compound_string_to_c_number` to handle 2018-era absolute compound names
- Write and run `scripts/backfill_compound_c_number.py` for 2018–2021 DBs (+ 2022 residual)
- Verify compound counts post-backfill

**Out of scope:**
- Running the compound prior pipeline (user does that separately)
- FastF1 re-collection for non-sprint sessions (data is complete)
- Naming normalization (Spain/Spanish) — triage candidate
- Fixing `get_weekend_sessions` for 2020 Emilia Romagna — triage candidate

---

## Gate 1 — Collect 3 missing 2021 Sprint sessions

**Goal:** DB has rows for Great Britain S, Italy S, Brazil S with lap_times populated.  
**Assignee:** Implementer Crew  
**Strength:** medium  

### Deliverables
1. Run `collect_session` (or collect_season with `--sessions S`) for each of the 3 events
2. Verify session rows + lap_times > 0 for all 3
3. Confirm sprint compound data is present (compound != NULL)

### Evidence required
- Session rows for (2021, Great Britain, S), (2021, Italy, S), (2021, Brazil, S) in DB
- `SELECT COUNT(*) FROM lap_times WHERE session_id = <id>` > 0 for each
- Lap count and compound distribution per sprint session

### Stop condition
All 3 sprint sessions collected with lap data. FastF1 rate limit is the only expected blocker.

---

## Gate 2 — Fix `_compound_string_to_c_number` + write backfill script

**Goal:** Code correctly handles 2018-era compound names; backfill script updates `compound_c_number`
in 2018–2022 DBs from existing `compound` column without FastF1 API calls.  
**Assignee:** Implementer Crew  
**Strength:** medium  
**Depends on:** Gate 1 complete (so sprint lap data is in 2021 DB before backfill)

### Code change: `src/data/collector.py` — `_compound_string_to_c_number`

Current behaviour:
- Maps HARD/MEDIUM/SOFT to `alloc.hard/medium/soft` (works for 2019+ relative naming)
- Returns None for SUPERSOFT/ULTRASOFT/HYPERSOFT (unmapped)
- Returns wrong value for 2018 races where SOFT is the hardest compound (alloc=[4,5,6] → SOFT→alloc.soft=6
  but correct is 4)

Required change: add `year: int = None` parameter; for year <= 2018, use absolute era mapping:
```
SUPERHARD=1, HARD=2, MEDIUM=3, SOFT=4, SUPERSOFT=5, ULTRASOFT=6, HYPERSOFT=7
```
For year >= 2019, keep existing alloc-based mapping.

### New script: `scripts/backfill_compound_c_number.py`

For each year 2018–2022 (and optionally all years):
1. Open the per-year DB
2. For each session with NULL compound_c_number rows, join sessions → get (year, gp_name)
3. Look up `get_compounds(year, gp_name)` from compounds.yaml
4. For each lap with compound != NULL and compound_c_number IS NULL:
   - Call `_compound_string_to_c_number(compound, alloc, year=year)` 
   - UPDATE `lap_times SET compound_c_number = ?` for that row
5. Log counts: rows updated, rows skipped (NULL compound / wet / unknown)

Script should:
- Accept `--years` arg (default 2018–2022)
- Accept `--dry-run` flag
- Print per-session summary
- Be idempotent (only updates NULL rows)

### Evidence required
- Before/after NULL counts per year
- 2018 spot-check: Austria (alloc=[4,5,6]) — SOFT should map to C4, SUPERSOFT to C5, ULTRASOFT to C6
- 2019 spot-check: Bahrain (alloc=[1,2,3]) — HARD→C1, MEDIUM→C2, SOFT→C3
- 0 rows updated for WET/INTERMEDIATE (correct: no C-number for wet)

---

## Gate 2 Review

**Reviewer checks:**
- `_compound_string_to_c_number` passes unit tests for all 2018-era compound names
- Backfill is idempotent (running twice gives same result)
- Wet/intermediate compounds correctly remain NULL
- compound_c_number NULL % drops to near-zero for 2018–2021 (residual only for wet compounds)

---

## Post-gates verification

```sql
-- Expected near-zero NULL for dry compound rows after backfill
SELECT year, COUNT(*) total, 
       SUM(CASE WHEN compound_c_number IS NULL AND 
           compound NOT IN ('WET','INTERMEDIATE','UNKNOWN','TEST_UNKNOWN','None','nan','') 
           THEN 1 ELSE 0 END) unexpected_nulls
FROM lap_times l JOIN sessions s ON l.session_id = s.id
GROUP BY year;
```

---

## Triage Candidates

1. **2020 Emilia Romagna FP2/FP3** — `get_weekend_sessions` returns FP2/FP3 but they never happened
   (compressed COVID format). Should be added to `KNOWN_UNAVAILABLE_SESSIONS`.

2. **Spain vs. Spanish naming** — 2018/2019 DBs have "Spain"; `F1_CALENDARS` has "Spanish".
   Causes false positives in `find_missing_sessions` / `is_session_complete`. Sessions exist.
