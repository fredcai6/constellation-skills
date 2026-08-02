# Season prior on the DRAG/POWER channel — architecture validation (2026-06-14 night)

Thread C of the overnight run. Goal: validate the human's "chase a prior through
the season" idea on the channel we TRUST (drag), with ground truth the grip channel
can't offer. Code: `.agent-work/445/envelope/drag_prior.py`; per-race fits cached
`drag_prior_fits.json`; raw `drag_prior.out`.

## Method
- Per race (all 22 of 2023, quali), per constructor (teammates pooled), full-throttle
  joint fit a = P/(mv) − ½ρ·CdA·v²/m → (P, CdA_closed/open) with SEs. Raw car_data,
  no Kalman smoothing → whole season is seconds of compute.
- Forward 1-D Bayesian filter (causal prior-chasing) per constructor on the
  RELATIVE-to-field quantity (car − field mean per race), which removes the per-track
  ERS-deploy / straight-geometry common-mode. Process noise allows slow drift
  (upgrades); obs variance = the per-race fit SE (thin/twisty races → wide → prior
  dominates).

## Result 1 — ARCHITECTURE WORKS (the headline)
The filter tamed per-race noise and converged to stable, season-consistent per-car
values. Thin-power-track taming (widest-SE races pulled toward the prior, σ
tightened): FER Dutch raw 525±14 → filtered 559±7; MERC São Paulo 532±8 → 547±6.
Filtered σ (±4–7 kW) < per-race σ (±5–14) — the season prior genuinely adds
information. This is the mechanism Monza-grip needs.

## Result 2 — DRAG CHARACTER recovered = known 2023 truth (validation PASS)
Filtered relative CdA (m², − = low drag):
  RBR −0.033 (LOW) · WIL −0.013 (LOW) · FER +0.016 (HIGH) · MERC +0.032 (HIGH)
Exactly the known character: Red Bull efficient + Williams low-downforce/low-drag
(FW45 = top-speed car) slippery; Mercedes (draggy W14) + Ferrari draggy. Matches the
cross_circuit drag finding. The RBR-vs-MERC gap is ~2σ at this (conservative) filter
setting — directionally clean, sign pattern perfect; an RTS smoother would tighten it.

## Result 3 — ENGINE POWER fails, but it's OBSERVABILITY not architecture
Filtered relative power: RBR −13.2 < MERC −1.4 < FER +5.9 < WIL +9.7 kW. The
same-engine pair MERC/WIL (both Mercedes PU) is NOT closest (11.1 kW apart; FER-WIL
3.8, MERC-FER 7.3 are closer) → engine-clustering ground truth did NOT come out.
Cause: P↔CdA / ERS-deploy entanglement — Williams' class-leading top speed is
mis-attributed to engine power when it's really low drag + deploy. On-track accel
cannot cleanly separate ~equal engines from aero. The filter faithfully filtered a
CONTAMINATED observable; it can't create separability that isn't in the data.

## Lesson (for Prong A and the program)
Prior-chasing delivers exactly when the per-race observable is clean:
- CLEAN observable (drag character / relative CdA) → recovers known truth, tames thin
  races, tight season-stable uncertainty. **Architecture validated.**
- NON-observable (engine power, P↔aero degeneracy) → filter can't manufacture signal.
Implication: the grip downforce B from the quali frontier IS a clean observable, so a
season grip filter (Prong A) should behave like the drag-character filter — and that
is the right fix for thin-corner tracks (Monza), far better than a fresh per-race solve.
Do NOT try to filter engine power from accel alone without an independent power source.
