# Capability fingerprint — multi-channel fusion (capstone, 2026-06-14 night)

Thread D of the overnight run: fuse the two season-filtered channels validated
tonight (Prong A grip/downforce + Thread C drag) into one per-car capability
fingerprint. Code: `.agent-work/445/envelope/fingerprint_fuse.py`.

## The motivation
EVERY single channel hits the same front-of-grid floor: grip/downforce cannot
separate Red Bull from Ferrari (both de-confound prongs AND the season grip filter
agree they tie within noise). But the cars differ on DIFFERENT axes, and each channel
is clean on a different axis. So fuse them.

## The result — all four constructors separate into correct, known-true quadrants
Season-filtered, quali, relative-to-field, z-scored across the 4 constructors:

```
                          downforce    drag-eff   character (KNOWN 2023, recovered)
  RBR  [high-DF, low-drag]   +0.99       +1.33    RB19 efficient benchmark        ✓
  FER  [high-DF, high-drag]  +0.78       -0.62    SF-23 draggy but grippy         ✓
  WIL  [low-DF,  low-drag]   -1.53       +0.53    FW45 slippery minnow            ✓
  MERC [low-DF,  high-drag]  -0.25       -1.25    W14 draggy WITHOUT downforce    ✓
```

**The RBR-vs-Ferrari tie BREAKS on the drag axis:**
- downforce gap |RBR−FER| = 0.21 σ  (TIED — the noise floor every prong hits)
- drag-eff  gap |RBR−FER| = 1.95 σ  (cleanly SEPARATED)
RBR = high-downforce + low-drag (efficient); Ferrari = high-downforce + high-drag
(draggy, drag-limited top speed). Single-channel grip can't tell them apart; the
drag axis does. Aero-efficiency composite (DF_z + drag-eff_z): RBR +2.33 (clear #1),
FER +0.16, WIL −1.00, MERC −1.49.

## Why this matters
This is the per-car capability fingerprint the whole physics program has chased. It
did NOT come from any one clever channel — each channel individually is noisy and
hits the front-of-grid floor. It came from the RIGHT RECIPE, established tonight:
  RELATIVE-to-field (cancels track/compound/wing common-mode)
  + QUALI (clean μ, no race confounds — Prong B proved race doesn't transfer)
  + SEASON-FILTERED (prior-chasing tames thin tracks — Prongs A & C validated)
  + MULTI-CHANNEL (fusion separates what single channels tie).

## Honest limitations
- Recovers CHARACTER (which is independently known), not a quantitative ranking, and
  NOT championship order — Mercedes was P2 in the 2023 WCC despite the "worst aero"
  quadrant, because pace also = engine + driver + reliability. The fingerprint is an
  aero-character descriptor, not a pace predictor (yet).
- n=4 constructors; downforce offsets are Prong A's Monza-entering season-filtered
  snapshot; drag is the season forward-filter. Front-of-grid RBR-vs-FER ordering
  within the downforce channel remains below the floor — fusion separates their
  CHARACTER (efficient vs draggy) but does not rank their absolute pace.
- Not yet shown to PREDICT out-of-sample (the program's north star). Generalization
  to all 10 constructors and a predictive test are the next steps.

## Bottom line
Per-car capability IS extractable from telemetry — as CHARACTER, via the validated
recipe (relative + quali + season-filtered + multi-channel). The fused fingerprint
recovers the full known 2023 four-constructor aero character map and breaks the
front-of-grid tie that defeated every single channel. This is the strongest
affirmative result of the physics program to date; productization (absolute pace
ranking, prediction) is not yet established.
