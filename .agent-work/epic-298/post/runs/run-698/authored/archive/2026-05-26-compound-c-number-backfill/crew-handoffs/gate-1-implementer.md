# Crew Handoff: Gate 1 — Collect 3 missing 2021 Sprint sessions

**Work ID:** 20260526-compound-c-number-backfill  
**Gate:** 1 of 2  
**Role:** Implementer  
**Repo path:** `C:\Programs\f1Brainz\.claude\worktrees\inspiring-kalam-e15259`  

---

## Task

Collect the 3 sprint sessions that are missing from `data/f1_data_2021.db`:

| Event | Session type | FastF1 identifier |
|-------|-------------|-------------------|
| Great Britain 2021 | S (Sprint race) | year=2021, round=10, session='Sprint' |
| Italy 2021 | S (Sprint race) | year=2021, round=14, session='Sprint' |
| Brazil 2021 | S (Sprint race) | year=2021, round=19, session='Sprint' |

These are genuine collection gaps — the sessions happened but were never collected. All other 2021 sessions
are present.

## Background

- Python: `py` (Python Launcher on Windows), not `python`
- Tests: `py -m pytest tests/...`
- DB path: `data/f1_data_2021.db` (relative to repo root)
- Collector: `src/data/collector.py` — `F1DataCollector.collect_session(year, gp_name, session_type)`
- 2021 sprint format: sessions are FP1, Q, FP2, S, R. The "S" session is the Sprint race.
  FastF1 calls it 'Sprint' in the API.

## How to collect

Use the existing `collect_season.py` script with a targeted flag, OR write a small inline script.

**Option A — targeted inline script (recommended):**
```python
# scripts/collect_2021_sprints.py  (create this file, then run once)
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from src.data.collector import F1DataCollector
from src.data.database import DatabaseManager
from src.utils.config import Config

db = DatabaseManager(db_path=Config.db_path_for_year(2021))
collector = F1DataCollector(db=db)

sprints = [
    (2021, 'Great Britain', 'S'),
    (2021, 'Italy', 'S'),
    (2021, 'Brazil', 'S'),
]
for year, gp, stype in sprints:
    print(f"Collecting {year} {gp} {stype}...")
    stats = collector.collect_session(year, gp, stype)
    print(f"  success={stats.success}, laps={stats.total_laps}, error={stats.error_message}")
```

Run: `py scripts/collect_2021_sprints.py`

**Option B — use collect_season.py:**
```
py scripts/collect_season.py --years 2021 --sessions S
```
But this may skip already-collected sessions. Use if Option A has issues.

## Verification (required evidence)

After collection, verify with:
```python
import sqlite3
conn = sqlite3.connect('data/f1_data_2021.db')
cur = conn.cursor()
for gp, stype in [('Great Britain','S'), ('Italy','S'), ('Brazil','S')]:
    cur.execute('''
        SELECT s.gp_name, s.session_type, COUNT(l.id) as lap_count,
               COUNT(DISTINCT l.compound) as distinct_compounds
        FROM sessions s LEFT JOIN lap_times l ON s.id=l.session_id
        WHERE s.year=2021 AND s.gp_name=? AND s.session_type=?
        GROUP BY s.id
    ''', (gp, stype))
    row = cur.fetchone()
    print(f"{gp} {stype}: {row}")
conn.close()
```

Expected: each sprint session has > 0 laps and > 0 distinct compounds.

## Authority / boundaries

- Only adds new session rows + lap_times; no modification of existing data
- Do NOT run full season recollection — only these 3 sessions
- Do NOT commit to git (Pilot decides commit strategy)
- If FastF1 returns a rate limit error, wait and retry rather than giving up

## Blockers

- FastF1 rate limit: if hit, wait 20 minutes and retry (the rate limit resets hourly)
- If FastF1 genuinely cannot find a sprint session for these events, report the error message exactly

## Done criteria

All 3 sprint sessions have a session row in `sessions` table AND at least 1 lap in `lap_times`.
