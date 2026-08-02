# P5 — Per-segment kinetic-energy bookkeeping from raw telemetry, no ERS channels

**Question:** what does per-segment kinetic-energy bookkeeping from raw stored telemetry
look like on one power-sensitive circuit, and is any deployment/derate signature visible
without ERS channels?

**Headline:** yes, a clean and repeatable signature is visible — d(KE)/ds along a
full-throttle straight decays smoothly and monotonically from a few thousand N-equivalent
near corner exit toward ~0 (occasionally slightly negative) as the car approaches its
gear/power-limited terminal speed, consistent across all 4 drivers tested. DRS activation
shows a real, matched, immediate uptick in the derivative right at the activation point.
**What is NOT visible**: any discrete step/cliff consistent with an active MGU-K
deployment cutoff (battery depletion mid-straight) — the decay is smooth everywhere
tested, so this signature alone cannot distinguish "continuous full ICE+ERS the whole
straight" from "ICE-only with the same smooth shape." That distinction needs the ERS
channels (or ERS-informed physics) this spike was explicitly built to do without.

Circuit/session: **Monza (`gp_name="Italy"`), 2023 Q**, chosen for full-throttle fraction
over Baku/Spa (all three had full 20-driver coverage in the store; Monza used). Drivers:
VER, LEC, SAI, HAM (their single fastest Q lap each), plus a VER lap-to-lap comparison.

Data: `data/telemetry_store.db` + `data/telemetry_store_parquet/`, read via
`src.data.telemetry_store.TelemetryStore.read_session` (read-only). Scripts under
`.agent-work/explore-ref-utilization/excursions/scratch/P5/` (`ke_ledger.py`,
`ke_ledger2.py`, `ke_ledger3.py`) — throwaway, not productionized.

---

## 1. Method

- **Mass**: fixed `850 kg` for all drivers/laps (early-Q plausible figure per the ask —
  absolute scale is not load-bearing here, shape is). No fuel-burn or driver-mass
  correction applied; over a single ~80s Monza lap this is a second-order effect but it is
  an *assumption*, not measured.
- **Distance** `s`: cumulative trapezoidal integration of `speed_kmh/3.6` over
  `session_time_s` from the `car` stream, zeroed at each lap's start. Not cross-checked
  against the `pos` (X/Y/Z) stream in this spike — an easy follow-on, not done here.
- **KE** = `0.5 * m * v²` (translational only; no rotational/wheel inertia term, no
  elevation/gravity term even though Monza has some elevation change through Parabolica —
  the store's `pos.z_dm` was available but unused this pass).
- **Segments** = contiguous runs of `throttle >= 99 & brake == 0`, filtered to
  `duration ≥ 2.5s` and `length ≥ 150m`. This reliably found **7 full-throttle segments per
  lap**, consistent in count, order, and rough length across all 4 drivers — a good sign
  the heuristic is finding real straights, not noise.
- **d(KE)/ds** via `np.gradient` over the segment's `(s, KE)` samples (~40-50 samples per
  long segment at the store's native rate, no additional smoothing applied). Per the
  brief's framing, this is what's reported as the "deployment signature" — but to be
  precise about units: `d(KE)/ds` is a **net longitudinal force** (propulsive minus
  drag/rolling, in N-equivalent given the mass assumption), not power. `d(KE)/dt` (also
  computed, see §4 ledger `avg_net_power_kW`) is the power-dimensioned quantity. Both are
  reported below; they carry the same qualitative shape since `v` is monotonically
  increasing on these segments.

## 2. The core shape (all 4 drivers, both long straights, decile-of-distance profile)

Example, VER fastest lap (80.307s), longest straight (954m, 161→320 km/h), dKE/ds by
distance decile (N):

```
9131  5384  3963  2890  1887  1750  1028   789   109     8
```

Same pattern for LEC/SAI/HAM on their equivalent straights (see script output) — high
(4000-10000 N-equiv) near corner exit at moderate speed, decaying smoothly through the
straight, bottoming near 0 (sometimes slightly negative, e.g. VER -192, HAM -575 on the
last decile) right before the braking zone. This is the textbook shape of a car
approaching power-limited terminal velocity (`P = F·v`, drag ~`v²`, so net force → 0 as
`v` → the gear/power ceiling) — **not by itself evidence of an active deployment
strategy**, since a pure-ICE car under constant full throttle produces the same
qualitative decay. The value of this spike is confirming the raw telemetry supports
extracting this shape cleanly and repeatably per segment, and characterizing what it does
and doesn't distinguish.

**No discrete cliffs.** Across all 8 (driver × longest-straight) profiles inspected, the
decay is monotonic-ish with sampling noise, never a sudden vertical drop mid-straight.
If MGU-K deployment were being cut off part-way down these ~1km straights (battery
depleted), a plausible signature would be a step-like change in the decay rate at the cut
point; none was seen. Scoped claim: **no such cutoff signature is visible on these
particular Monza straights for these 4 drivers' fastest Q laps** — cannot generalize
further without ERS state or a larger sample.

## 3. DRS correlation (matched, on the actual DRS-zone segments)

The two *longest* straights (950-1040m) turned out to **not** be where DRS opens (drs
stayed at the "eligible" code `8` throughout, never `≥10`/active) — DRS activates on two
*other*, slightly shorter full-throttle segments (711-928m), consistent across all 4
drivers. Isolating those segments and splitting at the DRS-activation sample:

| Driver | Segment | v at DRS-open | pre-open mean dKE/ds | post-open mean dKE/ds | first 3 post-open samples |
|---|---|---|---|---|---|
| VER | 2859-3770m | 264 km/h | 6283 N | 1909 N | 4200, 5109, 3933 |
| LEC | 2858-3775m | 267 km/h | 6856 N | 2063 N | 6313, 4173, 4168 |
| SAI | 2873-3800m | 259 km/h | 6609 N | 2238 N | 4954, 5903, 5126 |
| HAM | 2888-3778m | 265 km/h | 6568 N | 1980 N | 3933, 4713, 5296 |

The **post-open mean is lower** than pre-open for all 4 drivers — but that's confounded by
speed already rising through the segment (net force naturally decays with speed
regardless of DRS). The cleaner tell is the **first few samples right at activation**:
they sit noticeably above the immediately-preceding trend in 3 of 4 cases (VER
1840/1849 vs a pre-open run that was already decaying toward ~1000 N; similar for LEC/SAI)
— i.e. a small transient bump consistent with the drag-reduction benefit, then resumed
decay as speed keeps climbing. This is a real but modest signature, and disentangling it
cleanly from the speed-driven decay would need a matched-speed comparison (DRS-open vs
DRS-closed samples at the *same* v), which this spike didn't build.

## 4. Segment energy ledger (VER fastest lap, all 7 straights)

| seg | dist (m) | dur (s) | v_in→v_out (km/h) | KE_in (kJ) | KE_out (kJ) | ΔKE (kJ) | avg net power (kW) |
|---|---|---|---|---|---|---|---|
| 0 | 714.1 | 7.68 | 318→342 | 3316.2 | 3835.6 | 519.4 | 67.6 |
| 1 | 954.3 | 12.24 | 161→320 | 850.0 | 3358.0 | 2508.0 | 204.9 |
| 2 | 219.0 | 3.72 | 146→256 | 699.0 | 2149.1 | 1450.1 | 389.8 |
| 3 | 195.8 | 2.96 | 206→264 | 1391.6 | 2285.6 | 893.9 | 302.0 |
| 4 | 911.6 | 11.12 | 200→335 | 1311.7 | 3680.2 | 2368.5 | 213.0 |
| 5 | 1040.4 | 12.88 | 205→323 | 1378.1 | 3421.3 | 2043.1 | 158.6 |
| 6 | 551.7 | 7.20 | 223→313 | 1630.8 | 3212.7 | 1581.9 | 219.7 |

Row semantics: `KE_in`/`KE_out` = kinetic energy (mass-assumption-scaled) at segment
boundaries; `ΔKE` = net mechanical work done on the car over the segment; `avg net power`
= `ΔKE / duration`. **This is as far as the ledger can honestly go from speed alone**: it
gives net work/power, not a propulsion/drag split. Decomposing further (inferred
propulsive work vs. inferred drag+rolling losses, separately) needs a drag model (CdA) —
the project already has per-session CdA fitting machinery (`density-cda-fix`,
`physics-2023q-estimate-pipeline` in prior work) that isn't wired into this spike. The
250-390 kW average-net-power range (segments 2/3, short high-acceleration bursts at
moderate speed) is in a physically sane ballpark against a modern F1 PU's combined
ICE+MGU-K peak output (~560-750 kW at the wheels net of losses), which is a soft sanity
check, not a validation.

## 5. Lap-to-lap (same driver, same straight)

VER fastest lap (80.307s) vs. a slower-but-still-representative push lap (81.573s, lap 5),
both on the same longest non-DRS straight:

```
fast (80.307s): dKE/ds early/mid/late = 4120 / 1904 / 350 N   (v 205→323 km/h)
push (81.573s): dKE/ds early/mid/late = 4755 / 1854 / 507 N   (v 208→327 km/h)
```

The shapes are close — mid/late thirds nearly identical, early third modestly higher on
the slower lap (4755 vs 4120 N, despite near-identical entry speed). This is a **single
driver, two laps, one straight** comparison — not enough to claim a real deployment
difference; it's consistent with "no obvious energetic difference between these two Q push
laps," which is itself a useful (if modest) scoped null: nothing jumped out that would
motivate chasing lap-to-lap ERS strategy differences from this shape alone without a
bigger sample.

## 6. Honesty bar — what's measured vs. what's assumed

**Directly measured from telemetry** (no assumption beyond store fidelity): speed,
throttle, brake, gear, DRS state, and everything derived purely from their *shape*
(segment boundaries, decay monotonicity, DRS-activation timing/speed).

**Assumption-dependent** (would shift with a different choice, though shape claims are
robust to it): absolute KE/power magnitudes (mass=850kg fixed, no fuel-burn correction);
"net force"/"net power" language (correct only up to the translational-KE-only,
no-elevation approximation — Monza's mild elevation change through Parabolica is ignored);
any propulsion-vs-drag split (not attempted — would need a CdA/drag model this spike
didn't invoke).

**Explicitly not resolved** (needs ERS channels or an ERS-informed model, which this spike
was scoped to work around): whether the observed smooth full-throttle decay reflects
continuous full ICE+MGU-K deployment the whole straight, a graduated deployment taper, or
effectively ICE-only late in the straight. The absence of a discrete cliff argues against
an abrupt mid-straight cutoff on these particular laps/straights, but that's a negative
result about *cliffs*, not a positive claim about deployment strategy.

## 7. What a fuller version would need

- Cross-check distance integration against the `pos` X/Y/Z stream (redundant distance
  estimate, would also unlock elevation/gravity correction).
- A CdA/drag-force model (already exists elsewhere in the project, per prior physics
  work) to split ΔKE into propulsive-work vs. drag-loss rows, making the ledger a true
  energy *bookkeeping* table rather than a net-work table.
- A larger driver/lap sample (more than 4 drivers × 1 lap) before drawing any lap-to-lap
  or DRS-magnitude conclusion beyond "shape is qualitatively sane and repeatable."
