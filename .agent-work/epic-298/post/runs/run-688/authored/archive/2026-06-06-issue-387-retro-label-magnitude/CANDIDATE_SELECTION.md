# Issue #387 D3.3 — Race observable candidate selection (measured)

Two candidates scored over 68 real races (2022-2024, `get_race_lap_times`) via
`.agent-work/issue-387-retro-label-magnitude/probe_race_observable.py`:

- **PRIMARY** = `integrated_pace_gap`: per-lap pace delta to the field over ACTIONABLE
  (green-flag, completed) laps, averaged; fraction-of-median units.
- **BASELINE** = `finishing_gap`: total-race-time gap to the field median, fraction-of-median.

## CHOICE: PRIMARY (integrated green-flag pace gap)

### Criterion (a) — discriminating power (blowout vs packed)
| candidate | mean per-event dispersion | cross-event CV | blowout-vs-packed dynamic range |
|---|---|---|---|
| PRIMARY  | 0.00894 | 0.609 | **~13x** (packed 2023R20 0.0038 → blowout 2023R16 0.050) |
| BASELINE | 0.00565 | 0.669 | **~2x, collapsed** (all events clustered ~0.003-0.006) |

BASELINE's *CV* is marginally higher (0.67 vs 0.61), but that is the WRONG measure here:
its higher variance is spurious caution-noise, not blowout-vs-packed signal. The exemplar
table proves it — BASELINE assigns nearly identical dispersion to a Verstappen demolition
(2023R16 Monza, baseline 0.0056) and a genuinely packed race (2023R15, baseline 0.0057),
i.e. it CANNOT separate the two. PRIMARY separates them with a ~13x dynamic range and its
blowout exemplars are the real dominant races (2023R16 Monza, 2023R13 Spa, 2022R1 Bahrain,
2024R23). Discriminating power (the property the spread target actually needs — recall the
retro labels have CV ~0.001, FINDING.md) goes to PRIMARY.

### Criterion (b) — robustness on late-caution races (the decider)
Median BASELINE/PRIMARY dispersion ratio:
- high-caution races (caution_frac >= 0.20, n=7): **1.152**, but wildly unstable per-race
  (0.24 to 1.65).
- low-caution races (< 0.10, n=41): **0.709**, stable.

A late caution bunches the field nose-to-tail behind the safety car, so the finishing gap
is COMPRESSED or distorted unpredictably (ratio swings 0.24-1.65), while green-lap pace is
unaffected by construction (caution laps are excluded from PRIMARY's integral). BASELINE is
caution-fragile; PRIMARY is caution-robust. This is exactly the failure D3.3 asked us to
test for, and it lands against BASELINE.

## Conclusion
PRIMARY wins both criteria: a clean ~13x blowout-vs-packed dynamic range AND immunity to
caution compression. `spread_target` consumes `integrated_pace_gap` for the race / race_start
phases. BASELINE (`finishing_gap`) is retained in the module as a diagnostic/comparison only,
not used by the spread target.

Note: the module's actionable-lap filter uses per-lap `track_status` (verified populated
2021-2025 zero nulls; ~6% null in 2018); the field-median-spike proxy is the tested fallback
for laps/years without usable track_status.
