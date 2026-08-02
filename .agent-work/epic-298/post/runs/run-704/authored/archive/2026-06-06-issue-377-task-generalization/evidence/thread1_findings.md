# Thread 1 — Validate the redundancy/independence diagnosis PER TASK

All numbers traced to:
- **[SC]** = `.agent-work/archive/2026-06-06-issue-373-correlated-fusion/evidence/scorecard.json`
  (the #373 harness output, fixed unit-scale config, 173 events 2018–2025, per task).
- **[FD]** = `docs/evo/fusion_rework_findings.md` (#373 findings).
- **[CD]** = `docs/evo/prediction_ceiling_and_priorities.md`.
- Re-derivation snippet logged in commander transcript (decomposition recomputed from
  [SC] `variant_means`; matches [FD] decomposition table to the printed digits).

---

## 1A. Cross-module correlation structure per task (from [SC] R_estimated_offdiag)

Six off-diagonal blocks per task. Scope: C=constructor, D=driver. Evidence: rec=recent_history,
wk=race_weekend. Pair-type legend:
- **CD-same-ev** = constructor↔driver on the SAME evidence source (Crec↔Drec, Cwk↔Dwk) — the
  "driver↔constructor collinear" redundancy.
- **RW-same-scope** = recent↔weekend within the SAME scope (Drec↔Dwk, Crec↔Cwk) — the
  "recent↔weekend ~independent" pairs (the premise under test).
- **cross** = the two remaining mixed pairs (Crec↔Dwk, Drec↔Cwk).

| task | Crec↔Drec (CD-same-ev) | Cwk↔Dwk (CD-same-ev) | Drec↔Dwk (RW-same-scope) | Crec↔Cwk (RW-same-scope) | Crec↔Dwk (cross) | Drec↔Cwk (cross) |
|---|---|---|---|---|---|---|
| quali | 0.8689 | 0.8595 | 0.7313 | 0.7157 | 0.7120 | 0.7351 |
| race_start | 0.8334 | 0.8327 | 0.8949 | 0.8937 | 0.8300 | 0.8307 |
| race | 0.8418 | 0.8395 | 0.8736 | 0.8181 | 0.7887 | 0.8464 |

All from [SC] `tasks.<task>.R_diagnostics.R_estimated_offdiag` (λ=0.1 shrinkage).
Off-diagonal RANGE per task (matches [FD] table): quali 0.712–0.869; race_start 0.830–0.895;
race 0.789–0.874.

R condition number before→after shrink [SC]: quali 105.56→25.39; race_start 1187.33→34.57;
race 226.38→30.46. (race_start near-collinear before shrink — tightest co-movement.)

---

## 1B. Sub-question (a): does CONSTRUCTOR dominate MORE on race?

The brief's phrasing ("constructor dominate MORE on race, car/tyre-bound"). Two honest readings,
both answerable, and they point the SAME way: **NO — constructor↔driver collinearity does not
intensify on race; if anything it is flatter downstream.**

- **CD-same-evidence collinearity** (the redundancy the diagnosis named): quali **0.86–0.87** is
  the HIGHEST of the three tasks; race **0.84** and race_start **0.83** are slightly LOWER. So
  the "constructor field ≈ driver field" redundancy is strongest on QUALI, not race. [SC]
- **Constructor module sign-accuracy vs persistence** [CD §1.1]: grid→lap-3 constructor 0.919
  (driver 0.910); lap-3→finish constructor 0.740 (driver 0.791). On RACE (lap-3→finish) the
  constructor module is actually *weaker* than the driver module (0.740 < 0.791), the reverse of
  "constructor dominates more on race." On race_START the constructor edge is marginal (0.919 vs
  0.910). Both sit ~at the persistence ceiling either way.

**Verdict (a): the premise as stated is NOT supported.** The data does not show constructor
dominating more on race. The plausible intuition behind it (race order is car/tyre-bound) is real
in a *different* sense — race finishing order is ~persistence-bound and the recoverable part is
systematic team race-pace ([CD §1.2]: ~6.5% of movement is between-team) — but that is "the CAR
prior dominates the *outcome*," not "the constructor *module* dominates the *driver module* via
collinearity." The redundancy-correlation lens (what #373 measured) shows the opposite ranking.
*(Labelled: this reconciles two senses of "dominate"; the correlation/sign-acc numbers are
measured, the interpretation is mine.)*

---

## 1C. Sub-question (b): is recent↔weekend independence preserved downstream, or does it collapse?

This is the sharpest per-task result.

- On **QUALI**, RW-same-scope (0.716–0.731) is the LOWEST block — visibly below CD-same-ev
  (0.86–0.87). This is the only stage where "recent↔weekend relatively independent" reads true,
  and it matches [CD §1.4]'s quali figure (0.71–0.74). It is *relative* independence: 0.72 is
  still a strong correlation, but it is the loosest pair in the quali matrix.
- On **RACE_START**, RW-same-scope (0.894–0.895) is the HIGHEST block — recent and weekend are
  MORE redundant with each other than constructor is with driver (0.83). The quali ordering of
  blocks is INVERTED.
- On **RACE**, RW-same-scope is high and split: Drec↔Dwk 0.874 (≈ the top of the matrix) while
  Crec↔Cwk 0.818 (mid). Driver recent↔weekend has collapsed toward full redundancy; constructor
  recent↔weekend less so.

**Verdict (b): the independence does NOT survive downstream — it collapses, exactly as the
Thread-1 hypothesis anticipated.** Quali's relatively-independent recent↔weekend channel becomes
the *most* redundant pair by race_start. [SC, measured.]

**MECHANISM — labelled HYPOTHESIS, not measured here.** The brief asks whether independence
collapses "once you condition on the prior stage's order." The #373 harness estimates an
*unconditional* cross-module R, so it shows the collapse but does NOT isolate its cause. The
natural explanation: both downstream stages receive the prior stage's order as a handoff, and the
stack is persistence-dominated downstream ([CD §1.1]: grid→lap3 0.875, lap3→finish 0.776). When
both the recent-history and the race-weekend modules are largely re-expressing the same inherited
grid/quali order, they co-move strongly *because they share that handoff*, not because they
independently agree. Whether the residual recent↔weekend correlation *after partialling out the
prior-stage order* is small (independence preserved conditionally) or still large (genuinely
redundant) is **not answered by existing artifacts** and would need a partial-correlation /
conditioned-R probe. → recorded as a triage candidate; NOT built (WRITE-UP scope).

---

## 1D. Sub-question (c): does "A moves CALIBRATION not ORDERING" hold per task?

Re-derived the reformulation-vs-correlation decomposition from [SC] `variant_means`
(baseline → ablation_RI = per-entity REFORMULATION; ablation_RI → A = the CORRELATION component,
which is what #373 is about). Matches [FD] decomposition table.

| task | metric | baseline | R=I (ablation_RI) | A | Δreform (base→R=I) | Δcorr (R=I→A) | Δtotal (A−base) |
|---|---|---|---|---|---|---|---|
| quali | rank_mae | 3.3333 | 3.1555 | 3.3537 | −0.1779 | **+0.1982** | +0.0204 |
| quali | spearman | 0.6853 | 0.7118 | 0.6788 | +0.0265 | **−0.0330** | −0.0065 |
| quali | pairwise_ll | 0.6489 | 0.6456 | 0.6348 | −0.0032 | −0.0109 | −0.0141 |
| quali | cov80 | 0.0421 | 0.0539 | 0.0693 | +0.0119 | +0.0153 | +0.0272 |
| race_start | rank_mae | 2.4905 | 1.8116 | 1.8600 | −0.6789 | **+0.0484** | −0.6305 |
| race_start | spearman | 0.7569 | 0.8460 | 0.8424 | +0.0891 | **−0.0035** | +0.0855 |
| race_start | pairwise_ll | 0.6154 | 0.5981 | 0.5923 | −0.0173 | −0.0058 | −0.0231 |
| race_start | cov80 | 0.0202 | 0.0299 | 0.0483 | +0.0097 | +0.0184 | +0.0281 |
| race | rank_mae | 3.3348 | 2.8993 | 3.1678 | −0.4354 | **+0.2685** | −0.1670 |
| race | spearman | 0.6394 | 0.7036 | 0.6547 | +0.0642 | **−0.0489** | +0.0153 |
| race | pairwise_ll | 0.6400 | 0.6286 | 0.6279 | −0.0114 | −0.0007 | −0.0121 |
| race | cov80 | 0.0364 | 0.0399 | 0.0763 | +0.0034 | +0.0365 | +0.0399 |

**Verdict (c): "A moves calibration not ordering" HOLDS on every task — uniformly.**
- CORRELATION component on ordering (Δcorr): rank_mae **worse** on all three (+0.198 / +0.048 /
  +0.269); spearman **worse** on all three (−0.033 / −0.0035 / −0.049). The correlation correction
  never improves predicted order; it is flat-to-negative everywhere.
- CORRELATION component on calibration (Δcorr): cov80 toward nominal on all three (+0.015 /
  +0.018 / +0.037); pairwise-LL (calibration-sensitive) better on all three (−0.011 / −0.006 /
  −0.001).

**The per-task TEXTURE difference the brief flagged (race_start):** race_start's eye-catching
*total* ordering gain — rank_mae −0.63, spearman +0.086 — is almost entirely the per-entity
**REFORMULATION** (Δreform rank_mae −0.679, spearman +0.089), with the correlation adding ≈0
(Δcorr rank_mae +0.048, spearman −0.0035). Attributing race_start's improvement to "redundancy
handling" would be WRONG; it is the baseline→diagonal per-entity reformulation. This is the one
place the three tasks look different on the surface, and the decomposition shows the difference is
NOT in the #373 lever. cheap-B corroborates [FD]: its correlation component is flat-to-worse on
ordering for every task. [SC variant `cheapB` + `ablation_RI`; full cheap-B treatment in [FD].]

**Caveat (carried from [FD], applies to all three tasks):** absolute coverage is far below nominal
for every variant (cov80 ≈ 0.02–0.08 vs 0.80) because the fixed unit-scale config under-disperses
posteriors. The measurement isolates the *direction* of R's effect, not absolute calibration. The
ordering-vs-calibration split is the robust read; the absolute coverage level is not.

---

## 1E. Thread-1 one-line verdict

The quali-characterized diagnosis carries to race_start and race **with two corrections**:
(1) constructor↔driver collinearity does NOT intensify downstream (it is strongest on quali);
(2) recent↔weekend "independence" is a QUALI-ONLY property — it collapses to the most-redundant
block by race_start. The core #373 result — **the correlation correction moves calibration, not
ordering — generalizes cleanly and per-task.** The only surface difference (race_start's large
ordering gain) is reformulation, not redundancy handling, and so is not a counterexample.
