# Commander decision — anchor field correction (issue #420)

## Trigger
G2 acceptance measured PARTIAL reproduction with the G1 anchor `qs_best_raw`:
headline α=0.5 = 0.6624 overall / 0.7486 EASY vs §7.6.3 0.7452 / 0.8691
(delta -0.083 / -0.121). Root cause: the production anchor `qs_best_raw`
(short-stint quali-sim laps only) has its own α=1 ceiling 0.6784, ~12.7pp BELOW
the prototype's `best_across_fp` ceiling 0.8053 on the identical shared pairs.
α=0 baseline reproduced (PASS), so the pi source is correct — the anchor was the
problem.

## Probe (Commander-level, read-only; probe_anchor_variants_420.py, years 2019/2022/2024, 10803 pairs)
| anchor | α=0.5 overall | α=0.5 EASY | α=1 overall (ceiling) | α=1 EASY |
|---|---|---|---|---|
| A `qs_best_raw` (current G1) | 0.6781 | 0.7737 | 0.6934 | 0.7917 |
| B `min(qs_best_raw, lr_best_raw)` | **0.7567** | **0.8825** | **0.8163** | **0.9485** |
| C `best_across_fp` (DB, all FP, prototype) | 0.7540 | 0.8795 | 0.8101 | 0.9430 |

B ≈ C (B slightly exceeds). `min(qs,lr)_best_raw` recovers the full §7.6.3
improvement using ONLY existing `DriverFeatures` fields (qs_best_raw +
lr_best_raw), both available at the attach point, no new DB read, no new feature,
no machinery bypass.

## Why B works
Prototype `best_across_fp` = min-sectors over ALL clean FP laps. Production splits
those laps into short-stint (`qs_*`) and long-stint (`lr_*`) buckets. The min
ACROSS both buckets recovers the all-laps min-sector ordering signal. `qs_best_raw`
alone discarded the long-run laps, which carry the general-pace anchor.

## Decision
Change the production anchor from `qs_best_raw` to `min(qs_best_raw, lr_best_raw)`
(per-driver, NaN-safe: if both missing -> NaN; if one missing -> use the other).
This is MANDATED by admiral ruling 1 ("compute the same best_across_fp min-sector
pace source through the real practice-evidence machinery") — the two practice
buckets ARE that machinery's representation of the all-FP min-sector pace. G1's
`qs_best_raw`-only choice (a crew assumption the Commander provisionally accepted)
was too narrow; this corrects it.

## Authority / logging
- This is a "gate proved the plan wrong" event (spine: surface to user). User is
  unreachable (background job); brief authorizes Commander decision with logged
  justification. Logged here.
- NOT scope creep: ruling 1 required matching best_across_fp; this achieves it
  in-machinery. The VERDICT flips from PARTIAL to (expected) FULL reproduction.
- Action: reopen G1 to change the anchor field + add the min-of-two-buckets helper
  + tests; then re-run G2 acceptance at full scale to confirm.
