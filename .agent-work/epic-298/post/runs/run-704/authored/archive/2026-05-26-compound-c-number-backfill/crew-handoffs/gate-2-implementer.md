# Crew Handoff: Gate 2 — Fix compound_string_to_c_number + Backfill Script

**Work ID:** 20260526-compound-c-number-backfill  
**Gate:** 2 of 2  
**Role:** Implementer  
**Repo path:** `C:\Programs\f1Brainz\.claude\worktrees\inspiring-kalam-e15259`

---

## Context

The `compound_c_number` column in `lap_times` is NULL for nearly all 2018–2021 rows. The `compound`
column (raw string: SOFT/MEDIUM/HARD/SUPERSOFT/etc.) IS fully populated. The fix is a two-part change:

1. **Fix `_compound_string_to_c_number`** in `src/data/collector.py` to handle 2018-era absolute compound names
2. **Write `scripts/backfill_compound_c_number.py`** to update the DB from the existing `compound` column

---

## Part 1: Fix `_compound_string_to_c_number`

**File:** `src/data/collector.py`

**Current function (around line 44):**
```python
def _compound_string_to_c_number(
    compound: Any,
    alloc: Optional[CompoundAllocation],
) -> Optional[int]:
    """Map nominal compound label to C1-C5 using event allocation."""
    if alloc is None or compound is None or (isinstance(compound, float) and pd.isna(compound)):
        return None
    c = str(compound).strip().upper()
    if not c:
        return None
    if c in ("HARD", "HRD") or "HARD" in c:
        return alloc.hard
    if c in ("MEDIUM", "MED") or "MEDIUM" in c:
        return alloc.medium
    if c in ("SOFT", "SFT") or "SOFT" in c:
        return alloc.soft
    return None
```

**Problem:** In 2018, FastF1 stores **absolute** compound names (SOFT=C4, SUPERSOFT=C5, ULTRASOFT=C6,
HYPERSOFT=C7). The current function:
- Cannot map SUPERSOFT/ULTRASOFT/HYPERSOFT at all (returns None)
- Maps SOFT → alloc.soft which is WRONG for 2018 races where the allocation's soft is C5+ 
  (e.g. Austria 2018 alloc=[4,5,6]: SOFT should map to C4, not alloc.soft=6)

**Fix:** Add optional `year` parameter. For year <= 2018, use a direct absolute lookup table.

```python
# Fixed era mapping: 2018-era Pirelli compound names to absolute C-numbers
# These are fixed — SUPERSOFT is always C5, ULTRASOFT always C6, etc.
_ERA_2018_COMPOUND_TO_C: Dict[str, int] = {
    "SUPERHARD": 1,
    "HARD": 2,
    "MEDIUM": 3,
    "SOFT": 4,
    "SUPERSOFT": 5,
    "ULTRASOFT": 6,
    "HYPERSOFT": 7,
}


def _compound_string_to_c_number(
    compound: Any,
    alloc: Optional[CompoundAllocation],
    year: Optional[int] = None,
) -> Optional[int]:
    """Map nominal compound label to C1-C7 using event allocation or era lookup.

    For 2018 and earlier, FastF1 stores absolute compound names (SOFT=C4,
    SUPERSOFT=C5, ULTRASOFT=C6, HYPERSOFT=C7). For 2019+, it stores relative
    names (HARD/MEDIUM/SOFT) which map through the per-race allocation.
    """
    if compound is None or (isinstance(compound, float) and pd.isna(compound)):
        return None
    c = str(compound).strip().upper()
    if not c or c in ("NONE", "NAN", "UNKNOWN", "TEST_UNKNOWN"):
        return None

    # 2018 era: absolute compound names with fixed C-numbers
    if year is not None and year <= 2018:
        return _ERA_2018_COMPOUND_TO_C.get(c)

    # 2019+: relative names (HARD/MEDIUM/SOFT) mapped through per-race allocation
    if alloc is None:
        return None
    if c in ("HARD", "HRD") or "HARD" in c:
        return alloc.hard
    if c in ("MEDIUM", "MED") or "MEDIUM" in c:
        return alloc.medium
    if c in ("SOFT", "SFT") or "SOFT" in c:
        return alloc.soft
    return None
```

**Important:** The dict `_ERA_2018_COMPOUND_TO_C` should be defined at module level (above the function),
using the same import block. Add `Dict` to the typing import if not already there.

**All existing callers** of `_compound_string_to_c_number` must be updated to pass `year`:
- `collector.py` line ~566: `_compound_string_to_c_number(lap_dict.get('Compound'), compound_alloc)`
  → `_compound_string_to_c_number(lap_dict.get('Compound'), compound_alloc, year=year)`
  (The `year` variable is already in scope in `_extract_lap_times`)

---

## Part 2: Write `scripts/backfill_compound_c_number.py`

Create a new script that:
1. Iterates over per-year DBs (default 2018–2022)
2. For each session in the DB, joins to get (year, gp_name)
3. Looks up CompoundAllocation from compounds.yaml
4. For each lap with `compound_c_number IS NULL` and a non-empty `compound`:
   - Calls `_compound_string_to_c_number(compound, alloc, year=year)`
   - Batch-UPDATEs if result is not None

```python
#!/usr/bin/env python
"""
Backfill compound_c_number in lap_times from existing compound column.

No FastF1 API calls needed — derives C-numbers from the compound string
already stored in the DB using compounds.yaml allocations.

Usage:
    py scripts/backfill_compound_c_number.py [--years 2018 2019 2020 2021] [--dry-run]
"""
from __future__ import annotations

import argparse
import sqlite3
import sys
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data.collector import _compound_string_to_c_number
from src.evo_predictor.compound_adapter import get_compounds
from src.utils.config import Config


def backfill_year(year: int, dry_run: bool = False) -> dict:
    db_path = Config.db_path_for_year(year)
    if not db_path.exists():
        print(f"  [{year}] DB not found: {db_path}")
        return {"year": year, "skipped": True}

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # Get all sessions for this year
    cur.execute(
        "SELECT id, gp_name FROM sessions WHERE year = ?",
        (year,),
    )
    sessions = cur.fetchall()

    updated_total = 0
    skipped_total = 0

    for session in sessions:
        session_id = session["id"]
        gp_name = session["gp_name"]

        alloc = get_compounds(year, gp_name)

        # Fetch laps where compound_c_number is NULL
        cur.execute(
            """
            SELECT id, compound FROM lap_times
            WHERE session_id = ? AND compound_c_number IS NULL
            """,
            (session_id,),
        )
        laps = cur.fetchall()

        updates = []
        for lap in laps:
            c_number = _compound_string_to_c_number(
                lap["compound"], alloc, year=year
            )
            if c_number is not None:
                updates.append((c_number, lap["id"]))
            else:
                skipped_total += 1

        if updates and not dry_run:
            conn.executemany(
                "UPDATE lap_times SET compound_c_number = ? WHERE id = ?",
                updates,
            )
            conn.commit()

        updated_total += len(updates)
        if updates:
            print(
                f"  [{year}] {gp_name:25s}: {len(updates):4d} updated"
                + (" (dry-run)" if dry_run else "")
            )

    conn.close()
    print(
        f"  [{year}] TOTAL: {updated_total} updated, {skipped_total} skipped (wet/unknown/null)"
    )
    return {"year": year, "updated": updated_total, "skipped": skipped_total}


def main():
    parser = argparse.ArgumentParser(description="Backfill compound_c_number in lap_times")
    parser.add_argument(
        "--years",
        nargs="+",
        type=int,
        default=[2018, 2019, 2020, 2021, 2022],
        help="Years to backfill (default: 2018-2022)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be updated without writing to DB",
    )
    args = parser.parse_args()

    print(f"Backfilling compound_c_number for years: {args.years}"
          + (" [DRY RUN]" if args.dry_run else ""))

    for year in args.years:
        print(f"\n--- {year} ---")
        backfill_year(year, dry_run=args.dry_run)

    print("\nDone.")


if __name__ == "__main__":
    main()
```

---

## Part 3: Run the backfill

First dry run (to verify counts without writing):
```
py scripts/backfill_compound_c_number.py --dry-run
```

Then live run:
```
py scripts/backfill_compound_c_number.py
```

---

## Verification (required evidence)

After running, verify with:
```python
import sqlite3

for year in [2018, 2019, 2020, 2021, 2022]:
    db = f'data/f1_data_{year}.db'
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    cur.execute('SELECT COUNT(*) FROM lap_times')
    total = cur.fetchone()[0]
    cur.execute('''
        SELECT COUNT(*) FROM lap_times
        WHERE compound_c_number IS NULL
          AND compound NOT IN (\'WET\',\'INTERMEDIATE\',\'UNKNOWN\',\'TEST_UNKNOWN\',\'None\',\'nan\',\'\')
          AND compound IS NOT NULL
    ''')
    unexpected = cur.fetchone()[0]
    cur.execute('SELECT COUNT(*) FROM lap_times WHERE compound_c_number IS NULL')
    null_total = cur.fetchone()[0]
    print(f'{year}: total={total}, still_null={null_total}, unexpected_null={unexpected}')
    conn.close()
```

**Expected:**
- `unexpected_null` = 0 for all years (only wet/unknown/None correctly remain NULL)
- `still_null` significantly reduced vs. before (mainly wet compound rows)

Also spot-check 2018 Austria (alloc=[4,5,6]):
```python
import sqlite3
conn = sqlite3.connect('data/f1_data_2018.db')
cur = conn.cursor()
cur.execute('''
    SELECT l.compound, l.compound_c_number, COUNT(*) as cnt
    FROM lap_times l JOIN sessions s ON l.session_id=s.id
    WHERE s.gp_name=\'Austria\' AND s.year=2018 AND s.session_type=\'R\'
    GROUP BY l.compound, l.compound_c_number
    ORDER BY l.compound
''')
for r in cur.fetchall():
    print(r)
conn.close()
```
Expected: SOFT→4, SUPERSOFT→5, ULTRASOFT→6 (not SOFT→6)

---

## Authority / boundaries

- Only UPDATEs rows where `compound_c_number IS NULL` — fully idempotent
- Does NOT modify `compound` column
- Does NOT re-collect from FastF1
- Does NOT commit to git

## Done criteria

- `unexpected_null` = 0 for all years 2018–2022
- 2018 Austria spot-check shows SOFT→4, SUPERSOFT→5, ULTRASOFT→6
