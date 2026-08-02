# Evidence Integration: Gate 1 — Sprint Collection

**Date:** 2026-05-26  
**Gate:** 1  
**Verdict:** CLOSED ✓

## Evidence

| Session | laps | distinct_compounds |
|---------|------|-------------------|
| 2021 Great Britain S | 339 | 2 |
| 2021 Italy S | 343 | 2 |
| 2021 Brazil S | 480 | 2 |

Total 2021 laps in DB after collection: 60,244  
Session type distribution post-collection: FP1:22, FP2:22, FP3:19, Q:22, R:22, S:3 (exactly 3 sprint weekends)

No existing data disrupted. Script created at `scripts/collect_2021_sprints.py`.

## Gate Close Decision

All 3 done criteria met:
- [x] Session row in `sessions` table for each
- [x] At least 1 lap in `lap_times` for each
- [x] Compound data present (2 distinct dry compounds each sprint)

Gate 1 CLOSED. Proceed to Gate 2.
