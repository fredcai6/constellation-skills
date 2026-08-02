# Issue #387 — Admiral ruling (user-ratified 2026-06-06)

This is the authority resolution of the `understand`-step blocker. The predecessor's measured
finding (FINDING.md) is accepted as the evidence base; option 1 is dead. Recorded verbatim as
the unblock; plan/execute resume from here.

## D1 — Option 2 ACCEPTED
External event-conditioned spread target derived from observed gaps. Retro ORDERING labels are
untouched. Option 1 (magnitude-preserving re-solve) is dead — do NOT modify the retro solve.
(Justified by FINDING.md: magnitude is removed at binarization, upstream of lambda; ordering is
invariant under any lambda — 0 sign flips / 65,266 quali pairs, CV stays ~0.001 at every ridge.)

## D2 — Build the artifact NOW in THIS issue
#387's acceptance requires a consumable spread target, not just a recommendation.

## D3 — Design (binding order sheet)

1. **Units / de-unitization:** all gaps expressed as fraction of the SAME field-median lap time
   the existing training features use — REUSE the #368/#369 median-relative normalization
   machinery; do NOT derive a parallel median; no seconds anywhere in the artifact. The exchange
   rate is dimensionless.
2. **Conceptual frame (code comments + doc):** per event, `expected_gap_ij ≈ s_event × (pi_i − pi_j)`.
   `s_event` (per-event exchange rate, fraction-of-median per unit power) IS the spread target.
   The spread target is a post-event LABEL (it sees the event's own laps, like retro-pi does);
   as-of discipline applies to the FEATURES that will later predict it, not to the label derivation.
3. **Race observable — two candidates, measured choice:**
   - PRIMARY candidate = integrated per-lap pace delta over ACTIONABLE laps ÷ number of actionable
     laps (actionable = green-flag, actually-completed).
   - BASELINE candidate = final finishing gap.
   Score BOTH for (a) discriminating power between known blowout vs packed events and (b)
   robustness on known late-caution races; choose with that evidence and record it.
4. **Actionable-lap determination:** first VERIFY whether per-lap track status (caution/yellow)
   exists in the DB. If not: use the field-median-spike proxy — a caution appears as the whole
   field's lap times spiking together; detect and exclude those laps from the integral. Do NOT
   extend data collection (rate-limited collector is out of scope) — the proxy is the approved
   fallback.
5. **Estimator (robust-first, floor-as-guardrail):** per-event `s_e = MEDIAN` over pairs of
   `(pace_gap_ij / (pi_i − pi_j))` — robust to the minority of pace-vs-finish sign-inverted pairs.
   Then a positive floor as guardrail only: clamp degenerate/non-positive estimates to a small
   positive value and FLAG those events in the artifact.
6. **Companion statistic (do NOT blend into s_e):** per-event pace-vs-finish sign-disagreement
   RATE, recorded as its own field — this is pace→finish conversion noise for Thrust B's σ work
   (#388/#389) to consume later. Preserved separately, NOT laundered into the scale.
7. **Quali spread target (clean path, #391's consumer):** from session-best (or theoretical-best)
   quali gaps, same units, same estimator — no caution machinery needed.
8. **Home:** DB-side derivation in the **evo** lane (not the generic latent_power solver), per the
   predecessor's accepted proposal. Artifact shape/storage is the reconciliation call
   (cheap/reversible — log it); it must be consumable by #386's σ work and #391.

## Lane (binding)
Label/target derivation only. Do NOT touch: the retro solve, the quali mean head (#391's lane),
or σ-floor/tail consumers (#388/#389).

## Done bar (for the run)
Spread-target artifact: per-event s_e (race + race_start as applicable), quali s_e, flags for
clamped events, companion disagreement rate; derivation script(s) + tests; candidate-selection
evidence (D3.3); append-shaped doc note in docs/evo/prediction_ceiling_and_priorities.md recording
the exchange-rate framing, the option-1 impossibility finding (cite FINDING.md numbers), and what
#391/#386 consume. Targeted tests green; pyright clean; branch pushed; PR opened (NOT merged).
