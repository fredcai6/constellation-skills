# Evidence Integration: Gate 2 — Reviewer

**Date:** 2026-05-26  
**Gate:** 2  
**Reviewer verdict:** APPROVE  
**Gate status:** CLOSED ✓

## Checklist results (all pass or minor-concern)

| Check | Result |
|-------|--------|
| `_ERA_2018_COMPOUND_TO_C` dict values correct | PASS |
| Year guard is `<= 2018` (not `< 2018`) | PASS |
| 2019+ alloc-based path unchanged | PASS |
| None/nan/UNKNOWN guard fires before dict | PASS |
| `year=None` backward compatible | PASS |
| WET/INTERMEDIATE return None | PASS |
| `_extract_lap_times` passes `year=year` | PASS |
| No other stale callers | PASS |
| Backfill script idempotent (WHERE IS NULL) | PASS |
| Backfill doesn't touch `compound` column | PASS |
| `--dry-run` works | PASS |
| Skips None-result rows (wet/unknown) | PASS |
| Commits per batch (not per row) | PASS |
| Austria 2018 spot-check: SOFT→4, SUPERSOFT→5, ULTRASOFT→6 | PASS |
| 2019 Bahrain Race: HARD→1, MEDIUM→2, SOFT→3 | PASS |
| unexpected_null=0 for 2018, 2019, 2022 | PASS |
| Orphaned rows are pre-existing, irrelevant to compound priors | PASS |
| No new test failures | PASS (6 pre-existing schema failures unrelated) |

## Corrected orphan row counts

Reviewer live-queried actual counts (evidence doc had slight underestimates):

| Year | Orphaned rows (actual) | Evidence doc had | Impact |
|------|----------------------|------------------|--------|
| 2020 | 3,738 | 3,692 | None — qualitative conclusion correct |
| 2021 | 17,529 | 16,615 | None — all NULL totals match |

## Latent pre-existing note

Reviewer noted: 2019+ path uses `"SOFT" in c` which would match "SUPERSOFT". This pre-exists this
change; new `year <= 2018` gate ensures SUPERSOFT never reaches 2019+ path. Not a regression.

## Gate Close Decision

- [x] unexpected_null=0 for all years (excluding orphaned pre-existing rows)
- [x] Austria 2018 and Bahrain 2019 spot-checks pass
- [x] No new test failures
- [x] Reviewer approved

Gate 2 CLOSED. All gates complete.
