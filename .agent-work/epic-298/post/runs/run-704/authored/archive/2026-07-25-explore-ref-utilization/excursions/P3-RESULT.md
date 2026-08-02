# P3 — Apex-speed fingerprint smoke test (2023 Q, split-half)

**Question:** do per-driver, radius-binned apex-speed curves built from 2023 Q `session_fits.apex_obs`
show ANY split-half cross-weekend structure — raw, and within-team normalized?

**Verdict (scoped to this exact setup):** Yes, marginally, in one radius band. RAW curves correlate
split-half as expected (car-quality baseline). After subtracting the teammate (cheap car control), the
correlation collapses to noise in most radius bins — but **one mid-radius bin (50–80m) keeps a
statistically-suggestive positive split-half correlation in BOTH `v_apex` (r=0.46, p=0.036) and `a_lat`
(r=0.59, p=0.004)**, and a second, tighter-radius bin (20–32m) shows the same for `a_lat` alone (r=0.59,
p=0.005) but not for `v_apex` (r=0.18, p=0.44). Everywhere else post-normalization correlation is weak,
inconsistent in sign, or goes mildly negative. This is a thin, bin-specific signal, not a broad
driver-level apex-speed fingerprint — see caveats below before reading anything stronger into it.

## Setup

- **Data:** `data/physics_fits.db`, table `session_fits`, column `apex_obs` (JSON list per row of
  `{v_apex, radius_m, a_lat, on_limit}`). Verified schema via `PRAGMA table_info` + sample row.
- **Scope:** year=2023, session_type='Q', fit_status='ok', apex_obs not null → **436 driver-weekend rows**
  (out of 440 Q rows; 4 dropped for missing/failed fits), 22 rounds, 22 drivers across 11 constructors.
  Coverage is uneven for mid-season swap seats (AlphaTauri: DEV 9 weekends, RIC 7, LAW 5 — LAW gets
  dropped from the split entirely below, min-weekends-per-half gate).
- **Radius bins:** the brief suggested log-spaced bins spanning ~30–500m. Checked empirically first —
  actual 2023-Q `radius_m` in this store ranges **8m to 200m** (p99 = 197.6m), nothing near 500m. Used
  **5 log-spaced bins from 20m to 200m** instead (`np.geomspace(20, 200, 6)`): 20–32, 32–50, 50–80,
  80–126, 126–200m. Raw-observation counts per bin across the full 2023-Q set: 3.7k / 6.3k / 7.5k / 6.1k
  / 7.8k — no bin is thin.
- **Per-weekend aggregate:** for each (driver, round, bin), median of `v_apex` (and separately `a_lat`)
  over raw apex observations falling in that bin that weekend.
- **Split:** rounds 1,3,5,…21 = "odd" half; 2,4,…22 = "even" half (calendar order, not randomized).
- **Half aggregate:** per driver per bin, median across weekends within the half (`nanmedian`, drivers
  with <3 weekends in either half excluded — drops LAW; DEV and RIC clear the gate at 5/4 and 3/4).
- **Team normalization:** for each (round, bin), where exactly two drivers ran for a constructor that
  round, `normalized = driver_value − teammate_value` (both directions). Rounds with a lone entrant for a
  team that round (swap gaps) are excluded from the normalized set, not backfilled.
- **Correlation:** Pearson r between half-1 and half-2 per-driver bin values, across drivers, per bin,
  with `scipy.stats.pearsonr` p-value. n=21 drivers per bin throughout (22 minus LAW).

## Results

### RAW `v_apex` (car-quality baseline — expected to correlate)

| bin | n | r | p |
|---|---|---|---|
| 20–32m | 21 | 0.483 | 0.027 |
| 32–50m | 21 | 0.145 | 0.531 |
| 50–80m | 21 | 0.578 | 0.006 |
| 80–126m | 21 | 0.371 | 0.098 |
| 126–200m | 21 | 0.104 | 0.653 |

### TEAM-NORMALIZED `v_apex` (driver − teammate)

| bin | n | r | p |
|---|---|---|---|
| 20–32m | 21 | 0.180 | 0.435 |
| 32–50m | 21 | 0.290 | 0.202 |
| **50–80m** | 21 | **0.459** | **0.036** |
| 80–126m | 21 | -0.111 | 0.631 |
| 126–200m | 21 | -0.125 | 0.590 |

### RAW `a_lat`

| bin | n | r | p |
|---|---|---|---|
| 20–32m | 21 | 0.228 | 0.320 |
| 32–50m | 21 | -0.039 | 0.868 |
| 50–80m | 21 | 0.695 | <0.001 |
| 80–126m | 21 | 0.275 | 0.228 |
| 126–200m | 21 | -0.349 | 0.121 |

### TEAM-NORMALIZED `a_lat` (driver − teammate)

| bin | n | r | p |
|---|---|---|---|
| **20–32m** | 21 | **0.590** | **0.005** |
| 32–50m | 21 | 0.235 | 0.304 |
| **50–80m** | 21 | **0.594** | **0.004** |
| 80–126m | 21 | -0.430 | 0.052 |
| 126–200m | 21 | -0.105 | 0.649 |

## Honest read

- The RAW tables behave as expected: `v_apex` and `a_lat` both correlate split-half in most bins because
  car pace is stable within a season — this is the baseline, not evidence of driver skill.
- After the teammate subtraction, correlation drops toward zero or flips sign in 3 of 5 bins for both
  metrics — the majority of the raw split-half correlation was car, not driver, as expected.
- **The 50–80m bin is the one place both metrics agree post-normalization**: `v_apex` r=0.459 (p=0.036),
  `a_lat` r=0.594 (p=0.004). That two different quantities computed from the same underlying observations
  point the same way in the same bin is a mild internal cross-check, not independent confirmation — they
  share the same corners and the same underlying physics.
- `a_lat` also shows a significant normalized correlation in the 20–32m (tightest-corner) bin (r=0.590,
  p=0.005) that `v_apex` does not (r=0.180, p=0.435) — the two metrics disagree there, which weakens
  confidence in that one specifically.
- 80–126m trends negative post-normalization for both metrics (v_apex -0.111, a_lat -0.430 at p=0.052)
  — if anything, teammates' apex behavior in that band anti-correlates within-team across halves, which
  is not something a "driver fingerprint" story predicts and is more likely a normalization artifact or
  small-n noise.
- No bin shows structure in both metrics AND is signed the same as the raw baseline direction with a
  comfortable margin — the strongest reading this run supports is "some non-zero within-team-normalized
  structure concentrated in mid-radius corners (50–80m), weaker or absent elsewhere."

## Scoped nulls / what this does NOT show

- This is 2023 Qualifying only, one year, one session type, 21 drivers, calendar-order odd/even split
  (not randomized) — not a general claim about driver fingerprints existing or not.
- No ceiling-normalization, no shrinkage/regularization, no multiple-comparison correction across the 20
  cells tested (5 bins × 2 metrics × raw/normalized) — the p≈0.03–0.05 cells would not all survive a
  Bonferroni-style correction; treat them as suggestive, not confirmatory.
- Teammate-subtraction is a cheap car control, not a full one — it does not remove circuit-specific setup
  choices, fuel/strategy differences within a qualifying weekend, or track-type clustering by parity of
  round number (odd/even rounds are fixed calendar slots, not a random draw, so if similar corner
  characters cluster on one parity that could bias any bin's correlation without being "driver skill").
- No causal or magnitude claim — this only tests whether split-half correlation is distinguishable from
  noise at all, not how large a true fingerprint effect would be or whether it would matter for
  prediction.
- `on_limit` flag (present in the schema) was not used to filter to on-limit-only observations; this run
  pooled all apex observations regardless of that flag.

## Artifacts

- Script (throwaway): `C:\Programs\f1Brainz\.agent-work\explore-ref-utilization\excursions\scratch\P3\apex_fingerprint_p3.py`
- DB accessed read-only via `file:...?mode=ro` URI; interpreter pinned to
  `C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe`.
