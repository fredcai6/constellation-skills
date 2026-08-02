# Thread 3 — Ceiling-aware prioritization

Source: **fresh run of `scripts/diagnose_prediction_ceiling.py` in THIS worktree**, output
captured at `evidence/ceiling_diagnose_output.txt` (exit 0). Cross-checked against [CD]
(`prediction_ceiling_and_priorities.md`) and [SC] (#373 scorecard.json) where noted.

---

## 3A. Persistence baselines (re-derived this run — DURABLE)

| handoff | persistence sign-acc | flip rate | n |
|---|---|---|---|
| grid → lap-3 | **0.875** | 0.125 | 30763 |
| lap-3 → finish | **0.776** | 0.224 | 30763 |
| grid → finish (ref) | **0.753** | 0.247 | 32832 |

Matches the brief's quoted figures exactly. "Any downstream module must clear these to add ordinal
value" (script's own line).

Race-given-grid systematic team-pace fraction (re-derived): per-year 2.5%–10.1%, **MEAN 6.5%** ⇒
~94% of grid→finish movement is irreducible (and partly grid-regression-confounded, so the
genuinely learnable seam is smaller still).

Flip decomposition (current bundle, eval 2025): grid-PRESERVED pairs n=6496 model_acc 0.942;
grid-FLIPPED pairs n=1996 model_acc **0.298**. On the only recoverable pairs, the model is at a
coin-flip-minus.

---

## 3B. Module sign-accuracy vs ceiling (model-bound, eval 2025 — re-derived this run)

| module | sign_acc | persistence ceiling for its stage |
|---|---|---|
| driver_race_start_power_from_recent_history | 0.910 | 0.875 (grid→lap3) |
| constructor_race_start_power_from_recent_history | 0.919 | 0.875 |
| driver_race_power_from_recent_history | 0.791 | 0.776 (lap3→finish) |
| constructor_race_power_from_recent_history | 0.740 | 0.776 |
| driver_quali_power_from_recent_history | 0.745 | (quali has no persistence floor) |
| constructor_quali_power_from_recent_history | 0.769 | (quali has no persistence floor) |

Reading [matches CD §1.1]: race_start modules sit ABOVE the 0.875 handoff (0.910/0.919) — but note
that "edge over persistence" is what counts, and [CD §1.1] characterizes it as ~0; the modules are
essentially riding the very high handoff. Race modules straddle the 0.776 handoff (driver 0.791
just above, constructor 0.740 below). Quali modules (0.745/0.769) are the weakest in absolute
terms and have no persistence floor to lean on — all genuine ordinal skill originates here
[CD §1.1].

---

## 3C. Per-stage prioritization (where the fusion rework PAYS vs CAN'T)

The "rework" = the fusion-rework family (#373 correlated covariance, #374 interactions, #375
conditioned net). Ceiling logic applied per stage:

### race_start — PERSISTENCE-DOMINATED; ordering rework CANNOT pay
- grid→lap3 0.875 is the highest handoff; modules already at/above it; flip rate only 0.125.
- [SC] Thread-1: the #373 correlation component adds ≈0 to race_start ordering (Δcorr rank_mae
  +0.048, spearman −0.0035); the apparent ordering gain is reformulation, not redundancy handling.
- **Where the rework CAN'T pay:** any ORDERING-side fusion change on race_start. There is almost
  no headroom (0.125 flip rate, modules at ceiling), and #373 already showed the redundancy lever
  is neutral here.
- **Where a narrow win remains:** the UNCERTAINTY side — race_start has the highest pace→finish
  disagreement (~19%, [CD §9.5]) and a real event-conditioned spread (`s_e` CV 0.35), i.e. flip
  risk that a σ head could express. BUT [CD §1.3/§6] separately found NO statistically detectable
  race_start σ mis-level at n=24 (all |r|≤0.21 vs r_crit≈0.40). So even the σ win is bounded:
  the target exists (`s_e`), but there is no measured σ defect to correct in the current modules.
  **Net: race_start is the LOWEST-priority stage for the fusion rework.**

### race — MOST downstream headroom, but still SMALL and capped
- lap3→finish 0.776 is the lowest handoff (flip rate 0.224) ⇒ most ordering headroom of the
  downstream stages. BUT [CD §1.2] caps the *recoverable* part at ~6.5% systematic team-pace
  (mean, re-derived 3A), partly grid-regression. And the current model squanders it (29.8% on
  flip pairs).
- [SC] Thread-1: #373 correlation component on race ordering is the WORST of the three (Δcorr
  rank_mae +0.269, spearman −0.049) — redundancy discounting actively hurts race ordering. So the
  #373 lever specifically does not pay on race either.
- **Where the rework CAN pay (bounded):** the INTERACTION lever (#374) and the CONDITIONED net
  (#375) on the prior-order × race-pace-deviation term — this is the one place the ~6.5% lives and
  where the model has a measured failure (29.8% flip-pair accuracy, 3A). The ceiling is single-
  digit-percent of ordering, so expectations must be set accordingly [CD §4.5].
- **Where the rework pays MORE (uncertainty):** race `s_e` CV 0.31 + disagreement 16% give a real
  event-conditioned spread target for the σ/distribution work [CD §2 Thrust B] — consistent with
  the [FD] verdict that the fusion correction moves calibration, not ordering.
- **Net: race is the highest-headroom downstream stage, but the headroom is mostly on the
  UNCERTAINTY axis; the ordering gain available to #374/#375 is real-but-single-digit and is the
  prior-order×pace-deviation flip-pair slice.**

### quali — (not Thread 3's stages, but the anchor for the comparison)
All genuine ordinal skill originates here [CD §1.1]; modules weakest (0.745/0.769); no persistence
floor. The standalone `race_weekend` head sits ~19pp below its own data ceiling [CD §7.6.2], and a
cross-channel anchor recovers ~68–72% [CD §7.6.3]. This is where ORDERING rework pays — and it is
the stage the brief explicitly says the user will judge first ("let's see how quali goes").

---

## 3D. Thread-3 one-line prioritization statement

For the fusion rework: **ordering payoff is quali ≫ race > race_start ≈ 0**, and downstream the
payoff shifts axis — race_start has effectively no ordering headroom (0.875 handoff, #373 neutral)
and only a bounded, already-triaged σ story; race has the most downstream headroom but it is
~6.5%-capped on ordering (the prior-order×pace flip slice, where the model is at 29.8%) and is
mostly an UNCERTAINTY opportunity. The #373 redundancy lever specifically does not pay on ordering
for ANY task (Thread 1); the #374/#375 interaction/conditioning levers are where any downstream
ordering gain must come from, and they are ceiling-bounded to single digits on race and ~nil on
race_start.
