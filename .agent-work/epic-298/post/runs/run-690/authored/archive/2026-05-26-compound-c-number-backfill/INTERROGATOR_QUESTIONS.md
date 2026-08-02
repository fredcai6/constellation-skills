# Interrogator Questions: 20260526-compound-c-number-backfill

## Summary of findings from repo inspection

**Key discovery:** The `compound_c_number` NULL problem is _not_ a FastF1 data availability issue — it is a
collection-time gap. The `compound` column is **fully populated** in all 2018–2021 DBs. The C-numbers just
were never computed, likely because the compound→C-number logic was added after those seasons were originally
collected.

| Year | Total rows | compound_c_number NULL | compound NULL |
|------|-----------|----------------------|---------------|
| 2018 | 58,002    | 100%                 | 0%            |
| 2019 | 58,946    | 100%                 | 0%            |
| 2020 | 50,240    | 100%                 | 0%            |
| 2021 | 76,611    | 91.3%                | 1.1%          |
| 2022 | 58,947    | 10.9% (residual wet) | ~0%           |

**Implication:** We can backfill `compound_c_number` from the existing `compound` column — **no FastF1
re-collection needed** for compound data. This avoids API rate limits entirely.

**2018-specific wrinkle:** FastF1 stores absolute compound names for 2018 era:
`SOFT, MEDIUM, HARD, SUPERSOFT, ULTRASOFT, HYPERSOFT`. The current `_compound_string_to_c_number` only
handles `HARD/MEDIUM/SOFT` (relative names). Needs extension to handle era-specific absolute names.

---

## Session completeness audit results

**Genuine missing sessions** (need FastF1 collection):
- 2021 Great Britain S (Sprint race)
- 2021 Italy S (Sprint race)
- 2021 Brazil S (Sprint race)

**Not gaps — confirmed real non-events:**
- 2020 Emilia Romagna FP2/FP3 — Imola 2020 was a compressed COVID format (FP1+Q+R only)
  → NOT in `KNOWN_UNAVAILABLE_SESSIONS` (triage: should be added)
- Russia 2021 FP3 — officially cancelled due to heavy rain; already in `KNOWN_UNAVAILABLE_SESSIONS` ✓

**Naming inconsistency (data present, wrong key):**
- 2018 and 2019: sessions stored as "Spain" in DB, but `F1_CALENDARS` says "Spanish"
  → Sessions exist, naming mismatches cause false "missing" in audit (triage)

---

## Questions

### Q1: Prefer pure-DB backfill vs. FastF1 re-collection for compound_c_number?
**Status:** RESOLVED — user confirmed: "mostly focus on the db backfill, but we can use fastf1 to fill
any holes"  
**Answer:** DB backfill primary; FastF1 only for confirmed gaps

### Q2: Data collection first — collect 3 missing 2021 Sprint sessions?
**Status:** RESOLVED — user confirmed: "make data collection the first priority"  
**Answer:** Yes, Gate 1 = collect missing sprint sessions, Gate 2 = backfill compound_c_number

### Q3: How to handle 2018-era absolute compound names?
**Status:** RESOLVED by implication — fix `_compound_string_to_c_number` as part of Gate 2  
**Answer:** Extend function with fixed era-2018 mapping; pass year so SOFT→C4 for 2018 vs SOFT→alloc.soft
for 2019+

### Q4: Should compound prior pipeline run automatically after backfill?
**Status:** DEFERRED — out of scope for this work; user to run pipeline manually after
