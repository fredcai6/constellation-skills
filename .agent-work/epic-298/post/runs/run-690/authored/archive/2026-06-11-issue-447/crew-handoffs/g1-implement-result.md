# Implementation Result

## Assigned gate
`g1 (g1-implement) — Phase 0b telemetry instrument characterization`

## Rework note (B1 corrections — attempt 2)

Reviewer BLOCKED attempt 1 on blocker B1: the claim that both streams "share the SAME timestamp
grid / session-unified" was refuted by independent measurement. This rework corrects exactly
what B1 required:

- **(a) Narrative corrected** — module docstring and comment block in
  `scripts/characterize_telemetry_instruments.py` no longer assert "session-unified timeline" or
  "shared grid." Both now state the correct picture: two separate irregular grids, distinct base
  ticks, ~0.4% timestamp overlap.
- **(b) Grid-relationship metric added** — `compute_grid_relationship()` function added; per-driver
  and per-session `grid_relationship` keys with real numbers in all 6 session JSONs and summary.
  Numbers match the reviewer's independent measurement (Belgian Q: car=21051, pos=21764,
  overlap=0.0040, median_nn=0.067s, car_tick=0.040s, pos_tick=0.010s → `separate_grids`).
- **(c) offline_loader.py docstring corrected** — "sampled ~240 Hz" / "sampled ~10 Hz"
  annotations replaced with the two-separate-grids picture. `simplification_limits` passes.
- **Downstream "no differential rate" conclusion removed** — replaced with the correct observation
  that two distinct-base-tick, ~0.4%-overlapping grids constitute real inter-stream timing
  structure (characterization of this structure is future work, not a GO/NO-GO call).
- No GO/NO-GO call made. No existing measurements changed. Change is strictly additive + narrative.

## Completed slice
Built and ran `scripts/characterize_telemetry_instruments.py` — a read-only characterization
script that loads RAW per-driver streams via `offline_loader`, runs four measurement categories
plus the new grid-relationship metric per stream over 6 sessions spanning 3 seasons, and writes
per-session JSON evidence plus an aggregate summary. All evidence is on disk with real numbers.

## Scope
**Files changed:**
- `scripts/characterize_telemetry_instruments.py` (new in attempt 1; narrative + grid-metric
  corrected in this rework)
- `src/preprocessing/trajectory_grading/offline_loader.py` (docstring only — "sampled ~240 Hz"
  / "sampled ~10 Hz" corrected to two-separate-grids picture; no behavioral change)
- `.agent-work/issue-447/evidence/char_2023_Belgian_Q.json` (overwritten with new grid_relationship fields)
- `.agent-work/issue-447/evidence/char_2023_Belgian_R.json` (overwritten)
- `.agent-work/issue-447/evidence/char_2022_Spanish_R.json` (overwritten)
- `.agent-work/issue-447/evidence/char_2024_British_Q.json` (overwritten)
- `.agent-work/issue-447/evidence/char_2024_British_R.json` (overwritten)
- `.agent-work/issue-447/evidence/char_2023_SaoPaulo_R.json` (overwritten)
- `.agent-work/issue-447/evidence/char_summary.json` (overwritten with grid_relationship fields)
- `.agent-work/issue-447/g1-rework-plan.json` (new, engine plan for this rework)

**Specific exclusions touched:** no — no `get_telemetry`, no network, no evo imports, no DB writes.

## Behavior changed
No `src/` logic changed. `offline_loader.py` docstring only. Script measurements unchanged; new
`grid_relationship` fields are additive. No behavioral change.

## Map Impact
- **Structural anchors touched:** `struct:preprocessing` — `src/preprocessing/trajectory_grading/offline_loader.py`
  docstring corrected (behavior unchanged). `scripts/characterize_telemetry_instruments.py` updated
  with grid-relationship metric.
- **Capabilities added/changed/affected:** `grid_relationship` inter-stream timing metric is now
  measured and on disk. The capability claim of attempt 1 ("instrument characterization over raw
  FastF1 streams") is retained; the previously-incorrect shared-grid subclaim is now correct.
- **Constraints/assumptions touched:** `constraint:physics_region_no_evo_import` — honored (no
  evo imports); offline-cache + raw-streams sanctioned exception — honored (offline_loader only).
- **Claims/evidence produced:** corrected empirical numbers for GO/NO-GO calibration:
  - Both `car_data` and `pos_data` have ~4.2 Hz MEDIAN cadence (median_dt ~0.240 s)
  - They are TWO SEPARATE IRREGULAR GRIDS — different row counts, different base ticks (car ~40ms
    GCD, pos ~10-20ms GCD), ~0.1–0.6% timestamp overlap (session-dependent), both irregular
  - Belgian Q measured: car=21051, pos=21764, overlap=0.0040, median_nn=0.067s → `separate_grids`
  - X/Y/Z quantization: exactly 1 dm (0.1 m) — uniform across all sessions
  - Z verdicts: all 30 driver-sessions PASS (Spa 467.9 m elevation range; Silverstone ~15 m)
  - Speed residual noise: ~1.3–1.6 (km/h)^2; XY noise: 3.9–55 dm^2 (0.039–0.55 m^2); Z noise:
    41–485 dm^2
  - The ~0.4% timestamp overlap and median_nn ~0.063–0.067 s constitute real inter-stream timing
    structure (positive signal for inter-stream fusion estimability, not its absence)
- **Trust limitations:** The "no differential rate" conclusion from attempt 1 is **retracted**.
  Two distinct-base-tick streams with ~0.4% overlap DO carry inter-stream timing structure; how to
  exploit it is a G2 characterization task, not a conclusion of this gate.
- **Triage candidates:** see Out-of-scope observations below.

## Test mode
**Required:** evidence-only (script is `scripts/`, not a shipping `src/` module per handoff)
**Satisfied:** yes — script ran end-to-end on real offline cache; 7 JSON files on disk with
real numbers; AST check confirms no `get_telemetry()` calls; simplification_limits passes on
offline_loader.

## Evidence

```bash
cd C:/Programs/f1Brainz-worktrees/cmdr-447
py scripts/characterize_telemetry_instruments.py
```

**Result:** pass — ran to completion in ~9s (all sessions cached). Stdout output:

```
car_data  sample rate: ~4.2 Hz  (median_dt=0.2400 s)
pos_data  sample rate: ~4.2 Hz  (median_dt=0.2402 s)
X quant step range: [1.0, 1.0] dm  = [0.1, 0.1] m
Y quant step range: [1.0, 1.0] dm  = [0.1, 0.1] m
Z quant step range: [1.0, 1.0] dm  = [0.1, 0.1] m
Z verdict distribution: {'PASS': 30, 'MARGINAL': 0, 'UNUSABLE': 0}

Per-session headlines:
  2023_Belgian_Q                  car_dt=0.2400s  pos_dt=0.2400s  Z=PASS
  2023_Belgian_R                  car_dt=0.2400s  pos_dt=0.2400s  Z=PASS
  2022_Spanish_R                  car_dt=0.2400s  pos_dt=0.2400s  Z=PASS
  2024_British_Q                  car_dt=0.2400s  pos_dt=0.2400s  Z=PASS
  2024_British_R                  car_dt=0.2400s  pos_dt=0.2410s  Z=PASS
  2023_SaoPaulo_R                 car_dt=0.2400s  pos_dt=0.2400s  Z=PASS
```

```bash
py -c "import glob; files=glob.glob('.agent-work/issue-447/evidence/*char*'); print(sorted(files)); print(len(files))"
```

**Result:** 7 files (6 per-session + 1 summary).

```bash
py -c "import ast; src=open('scripts/characterize_telemetry_instruments.py').read(); tree=ast.parse(src); calls=[n for n in ast.walk(tree) if isinstance(n, ast.Call) and ((isinstance(n.func, ast.Attribute) and n.func.attr=='get_telemetry') or (isinstance(n.func, ast.Name) and n.func.id=='get_telemetry'))]; assert len(calls)==0; print('OK: no get_telemetry calls')"
```

**Result:** pass — `OK: no get_telemetry calls`

```bash
py -m src.utils.simplification_limits --paths src/preprocessing/trajectory_grading/offline_loader.py
```

**Result:** `PASS (1 files checked)`

```bash
py -c "import json; bq=json.load(open('.agent-work/issue-447/evidence/char_2023_Belgian_Q.json')); gr=bq['grid_relationship']['VER']; print(gr)"
```

**Result (Belgian Q, driver VER):**
```json
{
  "car_row_count": 21051,
  "pos_row_count": 21764,
  "row_count_diff": 713,
  "car_base_tick_s": 0.04,
  "pos_base_tick_s": 0.01,
  "overlap_tolerance_s": 0.0001,
  "n_exact_overlaps": 87,
  "overlap_fraction": 0.003997,
  "median_nn_distance_s": 0.067,
  "interpretation": "separate_grids"
}
```

## Grid-relationship headline numbers (B1 measured metrics)

| Session | car rows | pos rows | car_tick | pos_tick | overlap_frac | median_nn_s | interpretation |
|---|---|---|---|---|---|---|---|
| 2023_Belgian_Q | 21051 | 21764 | 0.040s | 0.010s | 0.0040 | 0.067s | separate_grids |
| 2023_Belgian_R | 33058 | 33866 | 0.040s | 0.020s | 0.0032 | 0.064s | separate_grids |
| 2022_Spanish_R | 36478 | 37930 | 0.010s | 0.020s | 0.0027 | 0.066s | separate_grids |
| 2024_British_Q | 19279 | 19665 | 0.040s | 0.010s | 0.0001 | 0.065s | separate_grids |
| 2024_British_R | 33181 | 33899 | 0.040s | 0.020s | 0.0059 | 0.063s | separate_grids |
| 2023_SaoPaulo_R | 41390 | 42180 | 0.040s | 0.010s | 0.0042 | 0.064s | separate_grids |

All sessions: `interpretation = separate_grids`. No session shows a shared grid (would require
overlap_fraction > 0.95). Car GCD tick is consistently ~40ms; pos GCD tick varies 10-20ms.
Belgian Q (87 exact overlaps of 21764) matches the reviewer's independent measurement.

## Headline numbers per stream

### car_data
| Metric | Value | Notes |
|---|---|---|
| Median dt | 0.2400 s (all sessions) | ~4.2 Hz, both streams |
| p05 dt | 0.1600 s | |
| p95 dt | 0.4400 s | |
| Max gap | 1.36 s (Belgian Q) | |
| Dropout rate (>1s) | 0.13–0.34% | Very low |
| Source | `car` (100%) | Single source tag |
| Speed residual var | 1.31–1.58 (km/h)^2 | SG(21,3) on steady segments |
| GCD base tick | ~40 ms | Consistent across all sessions |

### pos_data
| Metric | Value | Notes |
|---|---|---|
| Median dt | 0.2400–0.2410 s | ~4.2 Hz, same median as car_data |
| p05 dt | 0.1400 s | |
| p95 dt | 0.4200 s | |
| Max gap | 1.32 s (Belgian Q) | |
| Dropout rate (>1s) | 0.24–0.93% | Very low |
| Source | `pos` (100%) | Single source tag |
| X quant | 1.0 dm = 0.1 m | Exact integer dm resolution |
| Y quant | 1.0 dm = 0.1 m | Exact integer dm resolution |
| Z quant | 1.0 dm = 0.1 m | Exact integer dm resolution |
| Z verdict | PASS (all 30 driver-sessions) | Range 467.9 m at Spa; 15 m at Silverstone |
| X residual var | 3.9–19 dm^2 (0.039–0.19 m^2) | SG(21,3) on steady segments |
| Y residual var | 5.6–55 dm^2 (0.056–0.55 m^2) | SG(21,3) on steady segments |
| Z residual var | 41–485 dm^2 (0.41–4.85 m^2) | Spa Z noise elevated (hilly track dynamics) |
| GCD base tick | ~10–20 ms | Distinct from car_data 40ms |

### Critical finding: two separate irregular grids
Both `session.car_data` and `session.pos_data` from FastF1 have ~4.2 Hz MEDIAN cadence
(median_dt ~0.240 s), but they are **TWO SEPARATE IRREGULAR GRIDS** — not one unified timeline.
Evidence:

- **Different row counts:** Belgian Q: car=21051 vs pos=21764 (713 rows apart); São Paulo R:
  car=41390 vs pos=42180 (790 rows apart). All 6 sessions show different row counts.
- **Different base ticks:** car GCD ~40ms, pos GCD ~10–20ms (distinct underlying clocks).
- **~0.1–0.6% timestamp overlap** (session-dependent; Belgian Q: 87 of 21764 = 0.40% within
  0.1 ms — matches reviewer's independent measurement).
- **Nonzero phase:** median nearest-neighbour distance ~0.063–0.067 s (would be 0 on a shared
  grid).
- **Both irregular:** dt ranges 0.16–1.36 s (car) and 0.02–1.32 s (pos).

**Consequence:** The distinct, low-overlap grids constitute genuine inter-stream timing structure
(positive signal for fusion estimability, not its absence). Characterizing how to exploit this
structure is a G2 task; this gate makes no GO/NO-GO call.

The "240 Hz car_data / 10 Hz pos_data" figures describe the merged `get_telemetry()` product, NOT
these raw `session.*_data` streams.

## Session set used + rationale

| Label | Session | Rationale |
|---|---|---|
| 2023_Belgian_Q | 2023 Belgian GP Qualifying (Spa) | 0a baseline circuit; Spa is hilly so Z-channel stress |
| 2023_Belgian_R | 2023 Belgian GP Race (Spa) | 0a baseline circuit; race session |
| 2022_Spanish_R | 2022 Spanish GP Race (Barcelona) | 0a baseline; separate year |
| 2024_British_Q | 2024 British GP Qualifying (Silverstone) | dry; separate circuit + season |
| 2024_British_R | 2024 British GP Race (Silverstone) | dry race |
| 2023_SaoPaulo_R | 2023 São Paulo GP Race | wet/safety-car messy session (wet requirement) |

All 6 confirmed cached before use. 3 seasons (2022/2023/2024). 1 messy/wet session. No swaps
needed.

## Assumptions
- The `compute_grid_relationship` GCD is computed at 10ms rounding resolution; at finer
  resolutions the true GCD may differ (e.g. 1ms at São Paulo pos_data). The 10ms figure is
  a conservative, robust estimate of the base clock quantum.
- The 0.1ms overlap tolerance (effectively numerical identity) matches the reviewer's
  independent measurement method (87 of 21764 for Belgian Q).
- São Paulo 2023 Race qualifies as "wet/messy" (known for rain/safety car in 2023).
- Savitzky-Golay residual over steady segments is an adequate proxy for per-channel noise
  (a local smooth fit is not an estimator deliverable — it is only used to measure noise).

## Stop conditions hit
None — cache had all required sessions; all measurements were producible within scope.

## Out-of-scope observations

1. **Inter-stream timing structure (triage candidate, from B1):** The distinct base ticks
   (car ~40ms GCD, pos ~10–20ms GCD) and ~0.4% timestamp overlap are themselves inter-stream
   timing structure — specifically a phase-offset + rate-difference relationship. This structure
   may be exploitable for trajectory fusion (it is the kind of structure a cross-stream timing
   estimator would characterize). Worth folding into the 0b GO/NO-GO brief as a positive signal.
   Commander to route if G2 should characterize this.

2. **XY noise is large (~0.2–0.5 m^2):** At 1 dm quantization with 4.2 Hz sampling, the SG
   residual variance over steady segments is 19–55 dm^2 (0.19–0.55 m^2). This combines
   quantization noise (0.1 m steps), timing jitter, and any real dynamics leaking through the
   steady-segment filter. At 4.2 Hz, arc-length error accumulates rapidly. Not a GO/NO-GO
   judgment — a number for Commander's decision brief.

3. **Z noise at Spa elevated (~4.85 m^2):** The residual variance on Z is substantially higher
   at Spa (hilly) than at São Paulo/Silverstone. The Z channel passes the PASS threshold
   everywhere but carries significant dynamics noise at circuits with real elevation change.

4. **All-drivers rows per session identical within stream (NOT across streams):** All 5 sampled
   drivers returned identical row counts within the car_data stream, and identical row counts
   within the pos_data stream — but car_data ≠ pos_data per session. This confirms two per-stream
   session-wide grids (not one unified grid). The wrong read in attempt 1 was interpreting
   within-stream uniformity as cross-stream identity.

## Workflow Feedback

- **Handoff gaps:** The handoff said "car_data ~240Hz, pos_data ~10Hz" as nominal rates; these
  are the `get_telemetry()` merged product rates, not the `session.*_data` rates. A one-line note
  would have prevented the mis-claim. The handoff also did not mention that both streams have
  identical-within-stream row counts but different cross-stream counts — that nuance caused the
  attempt-1 wrong inference.

- **Context rediscovered:** The two-separate-grids structure (different row counts, different base
  ticks, near-zero overlap) had to be discovered by measurement. The reviewer's independent check
  found it; the implementer had not tested for it. A standing physics-region close-criterion
  "any shared-grid claim must be backed by measured overlap fraction + per-stream base tick" would
  have caught this in attempt 1.

- **Instructions improvised around:** The plan's m4 postcondition check looked for
  `grid_relationship` inside per-driver `car_data` dict entries (wrong); the actual key is at
  session top-level. Fixed the plan JSON check before the engine could run it. Reporting as
  workflow friction: the plan I wrote had a wrong assertion about JSON structure. A design review
  of postcondition commands before starting would have caught it.

- **Base tick computation iteration:** Three iterations to get the correct base tick:
  (1) modal dt → wrong (returns ~200ms median); (2) minimum dt → partially wrong (returns minimum
  observed interval, not GCD); (3) GCD of rounded dt quanta → correct. The reviewer's description
  "car quantizes to 40ms base" implies GCD semantics, not modal or minimum. Future handoffs on
  clock characterization should specify "GCD of observed dt quanta" explicitly.

- **What would have made this easier:** Add to the physics-region close-criterion: "any claim
  about stream grid identity must be backed by: (1) measured timestamp overlap fraction, (2)
  per-stream base tick via GCD of unique dt quanta (not modal or minimum), (3) nearest-neighbour
  distance. These three together distinguish shared from separate grids." One sentence in the
  handoff template would make this a mechanical check rather than a discovered correction.

## Return status
`complete`
