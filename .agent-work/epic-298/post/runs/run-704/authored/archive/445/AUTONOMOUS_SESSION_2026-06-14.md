# Autonomous de-confounding/fingerprint session — consolidation (2026-06-14)

User AFK directive: "play around, recast natural units → normalized parameters under conditions to remove
confounds like compound degradation; keep pushing until you run out of clear paths." Ran the capability-
fingerprint + de-confounding + prediction thread to a decisive terminus. Sobering, honest result.

## The bottom line (read this)
The rich physics regime/character feature space — "which car is good in slow vs fast corners / at styles of
circuits" — **does not pan out as a usable predictor.** The character is physically REAL but predictively
INERT beyond overall pace. The physics's genuine, validated value-add over lap-times is **compound
degradation** (GRIP-3), nothing else surfaced. The original epic bet (richer physics feature space breaks
the lap-time quali ceiling) is, on this evidence, **mostly not supported via car-character**; it survives
only as the compound-degradation channel, which is still untested in the evo A/B harness.

## What was run (6 experiments, all LIGHT/anti-thrash, no thrash)
1. DC-1 (de-confound grip by GRIP-3 compound×track×load) — NULL. The compound+track confound is ~2% of grip
   vs the 25-30% cross-car spread; de-confounding changes nothing. The non-replication of FP-1/2 is intrinsic
   sampling noise on a thin slice, NOT modelled confounds. → de-confounding (the user's named lever) is not it.
2. FP-3 (decisive regime test: 18 races + robust 3-param curves, 400 splits) — NULL, ambiguity gone. Per-car
   overall-pace LEVEL replicates STRONGLY (lateral +0.72 [0.59,0.84], orders the grid correctly). The slow-vs-
   fast-corner SLOPE (downforce/fast-corner axis) replicates only +0.38 [0.22,0.54] — certainly real-but-faint,
   certainly below the 0.7 usable bar.
3. FP-4 (channel-balance: cornering-vs-power contrast) — borderline. corner_vs_power +0.65 [0.48,0.79]
   (strongest signal in the thread), PHYSICALLY CORRECT (straight-line: Haas/Williams/Sauber/Ferrari-23;
   cornering: Merc-22/RB/McLaren). Coarser question recovered signal (+0.38→+0.65) but still <0.7.
4. PRED-1 (supervised: does corner_vs_power × circuit-regime PREDICT per-circuit pace residual?) — NULL,
   decisive. Pipeline sanity PASS (LEVEL→quali pace r=−0.669, R²=0.45). The interaction: p=0.406, and held-out
   marginal skill NEGATIVE everywhere (adding it HURTS OOS prediction). Physically directionally-right but
   event noise swamps it. → the character does not beat just knowing who's fast.
(FP-1/FP-2 earlier: the original PCA nulls that started this.)

## What's RECOVERABLE / usable (the honest feature set)
- Per-car overall-pace LEVEL — replicable (+0.72), predicts quali pace (r=−0.67). BUT level = overall pace,
  obtainable from lap times directly. The physics doesn't beat lap-time pace here.
- Compound degradation — GRIP-3 global prior, held-out-race validated (χ²=0.15), supplants the incumbent
  compound estimation's degenerate γ. THE one genuine physics value-add. UNTESTED in the evo A/B harness.

## What's NOT recoverable (definitive nulls)
- Slow-vs-fast-corner regime fingerprint (FP-3: +0.38).
- Cornering-vs-straight-line car CHARACTER as a standalone feature (FP-4: +0.65, sub-bar) or as a
  circuit-specific predictor (PRED-1: predictively inert / negative held-out skill).

## Clear paths now exhausted; what remains (needs user)
- Untested: does the COMPOUND-DEGRADATION prior add skill in the evo A/B harness? (the epic done-bar; the one
  surviving physics feature; a committed build, not a play-around).
- Untested: the DRIVER axis (utilization replication/prediction) — but given the CAR character is predictively
  inert, low expected value; possible if driver skill is more stable than car-character.
- More circuits for PRED-1 — NOT worth it (held-out skill is negative, not merely insignificant).

## Recommendation for the user's return
The regime/character fingerprint is dead — stop building toward it. Two honest options: (a) test the
compound-degradation prior in the A/B harness (the one physics feature that survived; the actual done-bar),
(b) accept that the physics layer's prediction value over lap-times is thin (degradation only) and weigh
whether the epic's bet is bounded-here. The trajectory/force machinery is sound and validated; its
prediction payoff is narrower than the bet hoped.
