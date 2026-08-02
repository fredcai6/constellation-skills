# P4 — Sector composition check on the Bahrain ephemeris pilot

Question: how large is the composition/boundary error when the Bahrain ephemeris
pilot's per-segment transit times (`eph_residual.corner_json`) are summed and compared
against official timing (lap and sector)?

Read-only excursion over `C:\Programs\f1Brainz`. Scripts (throwaway) at
`.agent-work\explore-ref-utilization\excursions\scratch\P4\p4_explore.py` and
`p4_sectors.py`. Pinned interpreter, no network/FastF1 calls, all DB connections opened
`mode=ro`.

## Headline finding

**The premise doesn't hold as stated.** `corner_json` is not a full-lap tiling — it is a
**curvature-threshold segmentation that only covers "in-corner" arcs** (where
`|curvature| >= cfg.simulator_curvature_threshold`, see
`src/physics/ideal_lap/generator.py:555` `_corner_transit_times`, called with
`corners=True` from `residuals.py:859`). Straights are deliberately excluded. Summing
`transit_s` therefore recovers only **~35% of the lap** by design, not by error — the gap
is where the car isn't cornering, not a boundary/measurement mistake. This is documented
in the module's own "v1 limitations" docstring (`generator.py:75`, referenced again at
`generator.py:157-159`), so it's a known scope limit, not a bug I'm surfacing for the
first time.

Sector times **do exist on disk** (`data/f1_data_2023.db` → `lap_times.sector1_time` /
`sector2_time` / `sector3_time`), so the composed-sector comparison in part (2) of the
ask was runnable — but because of the corner-only coverage gap, its result is dominated
by the same missing-straights effect, not by segmentation/boundary error. Details below.

## (0) Does official per-lap sector timing exist on disk?

**Yes.** `data/f1_data_2023.db` → `lap_times` table has `sector1_time`, `sector2_time`,
`sector3_time` columns (`session_id=515` = 2023 Bahrain, `session_type='R'`). 1056 lap
rows for that session; 1035 have all three sector times populated (the 21 gaps are
mostly out-laps missing `sector1_time`). All 2471 `eph_residual` (driver, lap) rows for
2023 Bahrain R matched a `lap_times` row with complete sector data — no join gap.

`data/telemetry_store.db` → `tele_laps` was also checked: it carries only
`lap_time_s` / `lap_start_time_s` / `lap_end_time_s`, **no sector breakdown** — not a
usable source for this check.

As a free consistency check on the join key itself: `eph_residual.observed_lap_s`
matches `f1_data_2023.lap_times.lap_time` **exactly** for all 2471 rows (diff = 0.000000s
on every row) — confirms the ephemeris pilot's lap-time ground truth is the same official
timing data, not an independently-derived number.

## (1) Internal consistency: sum(`corner_json[].transit_s`) vs `observed_lap_s`

Over all 2471 driver-laps (2023 Bahrain R, all 20 drivers):

| stat | coverage ratio (Σtransit_s / observed_lap_s) |
|---|---|
| mean | 0.3493 |
| median | 0.3475 |
| stdev | 0.0161 |
| min | 0.3105 |
| max | 0.3863 |

Segments per lap: mean 14.13 (min 11, max 17) — plausible for Bahrain's corner count.
Max `end_m` seen across all segments: 5340.2m, consistent with the BIC GP layout's known
~5412m lap length (external knowledge — track length is **not itself stored** in either
DB queried; flagged as an assumption below, not read off disk).

**Reading:** the ratio is tight (1.6 percentage points of stdev) and well below 1 for
every single lap — i.e., this is a **stable, repeatable partial-coverage export**, not
noisy boundary error. The "residual" here isn't a composition error at all; it's the
straight-line time the export never included. Internally, the segmentation looks sound
(low lap-to-lap variance in what fraction of the lap is "in a corner").

## (2) Sector mapping (segments → 3 FIA sectors) and composition error

Sector boundary distances aren't stored anywhere on disk for this circuit/session, so
per the ask, I inferred them: grid search over boundary pairs `(b1, b2)` on
`[0, 5412m]` (50m step, assumed track length as above), assigning each segment to a
sector by its midpoint `(start_m+end_m)/2`, minimizing total squared error of
`(Σ segment transit_s in sector) − (official sector time)` summed over sectors and all
2471 laps.

**Best fit:** `b1=1850m`, `b2=4100m` → arc lengths S1=1850m, S2=2250m, S3=1312m.

Per-sector composition error (model − official), at the best-fit boundaries, all 2471
laps:

| sector | mean (s) | median (s) | stdev (s) | min (s) | max (s) |
|---|---|---|---|---|---|
| S1 | −21.171 | −21.224 | 0.627 | −23.438 | −19.397 |
| S2 | −22.685 | −22.678 | 1.002 | −26.072 | −20.386 |
| S3 | −20.295 | −20.326 | 0.664 | −18.663 | −22.293 |

Equivalently, coverage fraction (model/official) per sector: **S1 ≈ 32%, S2 ≈ 47%,
S3 ≈ 16%** of the official sector time is accounted for by corner segments; the rest is
straight-line time outside the export.

For comparison, naive equal-thirds-by-distance boundaries (1804m/3608m) give a *worse*
total SSE (3,595,092 vs 3,401,418 at the best fit) — the grid search does pull toward
better alignment — but the residual composition error stays of the same huge magnitude
(mean −14.4s to −26.9s per sector) either way.

**Reading:** the ~0.6–1.0s stdev per sector (out of a ~20–45s official sector time) means
the *shape* of the error is highly repeatable lap-to-lap — this is a fixed geometric
offset (how much of each sector's arc is corner vs straight), not measurement scatter.
But the **magnitude** (60–85% of each sector's time unaccounted for) means this
composed-sector check, run as literally specified, mostly just re-measures the
corner/straight split per sector rather than validating segment-level transit-time
accuracy. A best-fit boundary search can't fix that: total error across the 3 sectors is
constant regardless of `(b1, b2)` — it's fixed by the overall ~35% coverage — so the
search only ever redistributes a fixed shortfall between sectors, it can't shrink it.

## What this means for a real composed-sector validation

Not currently buildable from what's exported. Two ways forward, neither of which I've
started (out of scope for a read-only excursion):

1. **Export full-lap tiling from the ideal-lap generator**, not just curvature-threshold
   corner arcs — i.e. change `corners=True` in `_corner_transit_times` (or add a sibling
   mode) to emit contiguous coverage of the whole distance grid, corners and straights
   both. Then Σsegment transit_s per sector is a fair comparison against official sector
   times.
2. Alternatively, restrict the *official* side to corner-only ground truth (e.g. per-corner
   minisector timing if F1 ever exposes it) — but FIA sector splits inherently include
   straights, so this doesn't fit the data that exists on disk today.

## Scoped nulls

- Track length (5412m) is external knowledge (BIC GP layout), **not read from any DB
  queried** — flagged, not fabricated as a DB fact.
- Did not check other years/GPs in `eph_residual` — only `(2023, 'Bahrain', 'R')` exists
  in the table at all (single run family, 3 `eph_runs` rows, same year/gp/session).
- Did not inspect `eph_state` (mass/kappa) — out of scope for this composition question.
- Sector-boundary "best fit" is a least-squares fit to a fundamentally biased target (see
  above) — treat `b1=1850m, b2=4100m` as a fit artifact of this dataset, not a claim
  about where BIC's real FIA sector lines are.
