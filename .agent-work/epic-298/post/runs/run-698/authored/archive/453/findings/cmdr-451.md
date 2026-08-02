# cmdr-451 — Localize the race_weekend quali-channel under-extraction (~19pp)

Issue #451 (epic #453, Wave 1). Sole writer: cmdr-451. Status: IN PROGRESS.

## Consolidated problem statement (ratified by Admiral launch order LO-451)

The standalone `race_weekend` quali latent-power head scores **0.6149** pairwise sign
accuracy on the §7.6.2 shared-pairs harness (headline 2018–2024; OOS-2025 reproduces:
0.5656), against a **data-only evidence ceiling of 0.8061** (OOS 0.7643) reachable from the
*same* FP1/2/3 laps it ingests. The sibling `recent_history` head reaches 0.7803 — within
~2.6pp of ceiling — so the evidence supports ~0.80; the `race_weekend` module fails to
extract it. #414/#420 banked ~70% of the gap with a one-feature cross-channel min-sector
pace anchor blend, proving the missing ingredient is **information routing, not calibration**
(§7.6.3 C3: pairwise sign-accuracy is invariant to any monotone rescale; only a new ordering
signal moves it).

**The question:** why can't the module itself learn what a one-feature blend recovers?
Localize to (a) feature representation, (b) training signal, or (c) capacity/architecture —
with numbers on the §7.6.2 same-pairs harness. Ship a fix only if small.

## Protected intent / hard constraints (from launch order + ORCHESTRATOR_CONTEXT)

- Scope fence: **single-module ablation retrains of the quali `race_weekend` module only.**
  NO full gold cycles. NO Piece-2 context-conditioned shared net. NO promoted-default changes
  unless the fix is genuinely small (one feature/encoding tweak in the module input path).
- All reported numbers on the §7.6.2 same-pairs harness (same pairs, same splits) or
  explicitly flagged off-harness.
- Walk-forward discipline: retrain probes respect as-of cutoffs; no leakage into scoring pairs.
- DB-only analysis; `py` not `python`; utf-8 child env on captured subprocesses.
- Honest null is a complete deliverable.

## Map-first context established at context step

- **Head input features (23-d):** `src/evo_predictor/quali_power_adapter.py` —
  `DRIVER_QUALI_POWER_FEATURE_NAMES`: all `qs_*` / `short_run_*` **adjusted** practice
  aggregates + missingness indicators + `qs_sector_available`. Fed as antisymmetric pairwise
  **differences** of per-driver vectors. **The raw `best_across_fp` min-sector pace ordering —
  the anchor signal whose ceiling is 0.8061 — is NOT among these features.**
- **Net (capacity):** `src/latent_power/network.py` `InnerNetwork` — 3 hidden layers
  (Linear+LayerNorm+act+dropout each), configurable `nn_hidden_dim`. Not capacity-starved for
  23 inputs → hypothesis (c) a priori weak.
- **Training signal:** `src/latent_power/modules.py` loss = `student_t_nll(pairwise, target_mu)`.
  `target_mu` = retro-solved `power_diff_ij` (`src/latent_power/retro_loader.py`
  `load_target_mu_for_event`).
- **Prior art #387 (retro-label-magnitude, archived):** every retro quali event is a *perfectly
  clean transitive binary tournament* — retro pi order disagrees with observed Q order on
  **0 / 65,266 directed quali pairs**; `start_bias=0` everywhere; magnitude was binarized away.
  So the head's supervision **ordering target is perfect** (= the true Q order), only its
  per-event spread is constant. This reframes hypothesis (b): the labels do NOT mis-order or
  down-weight the ceiling-scored pairs — the head is trained toward the *correct* Q ordering and
  still under-extracts. That pushes the weight of evidence toward **(a) representation**: the
  pace-ordering information the ceiling uses is not present in (or not linearly recoverable from)
  the `qs_*/short_run_*_adj` feature vector the head receives.

## Harness reproduction constraint

The §7.6.2 records dir (`.agent-work/issue-381-same-pairs/records/`) was gitignored and is NOT
preserved in the archive — only `same_pairs_numbers.json` survived (baseline reproduced from it:
rw 0.6149 / rh 0.7803 / ceiling 0.8061 / 23862 pairs ✓). The original bundle
`gold_cycle_260603_173742` is gone. Records must be **regenerated** via
`run.py backtest-latent-power-module --emit-module-record` on the committed promoted bundle
`gold_cycle_260608_043414_2018thru2024` (in worktree at `params/gold/runtime_bundles/`). NOTE:
that bundle was trained with the #420 anchor active, so its raw `pi` may differ from the §7.6.2
baseline — reproduction must be validated and any deviation flagged.

## Probe results

### G1 — reproduce scoreboard + read-only linear representation probe (no retrain)

| metric | §7.6.2 anchor | reproduced (this run) | status |
|---|---|---|---|
| rw (race_weekend) headline | 0.6149 | **0.6711** | FLAGGED (+0.056) |
| rh (recent_history) headline | 0.7803 | 0.7786 | reproduced |
| ceiling (best_across_fp) | 0.8061 | 0.8061 | reproduced exactly |
| pairs | 23862 | 23862 | reproduced exactly |
| rw OOS-2025 | 0.5656 | **0.7127** | FLAGGED (ceiling 0.7643) |
| **linear probe of rw head's OWN features (LOSO)** | — | **0.6513** | — |

**Why rw deviates:** the committed promoted bundle `gold_cycle_260608_043414` was retrained (#335
regen) with the #420 cross-channel pace anchor active. That anchor already lifted the in-bundle rw
head, so the standalone-head deficit measured here is **~14pp headline (0.6711 vs 0.8061)** and only
**~5pp OOS (0.7127 vs 0.7643)** — narrower than §7.6.2's 19pp/20pp because part of the gap is already
banked in this bundle. The localization question is unchanged; the magnitude is smaller in the live bundle.

**Linear-probe finding (decisive early signal for hypothesis (a)):** a walk-forward (LOSO) logistic
readout of the rw head's *own 23-dim input feature differences* scores **0.6513** on the same 23862
shared pairs — i.e. *at or below the trained head (0.6711)* and **~15pp below the 0.8061 ceiling**. A
linear model is an upper bound on "what ordering is linearly present in these features." It cannot reach
the ceiling. So the cross-channel min-sector pace ordering the ceiling exploits is **not linearly
recoverable from the head's feature vector** — the information is impoverished in the *representation*,
not merely under-weighted by the net. Reviewer independently re-ran the probe: 0.6513, deterministic.
G1 reviewed APPROVE, no defects.

### G2 — feature-ablation retrain (DECISIVE): add min-sector pace as one head input feature

Single-module retrains of `driver_quali_power_from_race_weekend`, seed 0, scored on the §7.6.2
harness. CONTROL = production 23 features. +PACE = 24th input feature = NaN-safe
`min(qs_best_raw, lr_best_raw)` (the #420 cross-channel pace anchor, supplied as an INPUT instead of
a post-hoc output blend). `feature_dim` auto-propagates; edit was a reversible probe (now reverted).

| split | condition | rw | ceiling | gap | pairs |
|---|---|---|---|---|---|
| headline (eval 2024) | CONTROL | 0.6560 | 0.8061 | 0.150 | 23862 |
| headline (eval 2024) | +PACE | 0.6792 | 0.8061 | 0.127 | 23862 |
| **OOS (eval 2025)** | **CONTROL** | **0.5868** | 0.7643 | 0.178 | 3352 |
| **OOS (eval 2025)** | **+PACE** | **0.7700** | 0.7643 | **-0.006** | 3352 |

The clean read is OOS-2025 (the full eval year is freshly retrained per condition). **+PACE lifts rw
0.5868 → 0.7700 (+0.183), essentially reaching the ceiling 0.7643.** The head, given the min-pace
ordering as an INPUT, *learns* what the #420 anchor bolts on post-hoc. The headline split shows only
+0.023 because it pools 2018-2024 records but only the eval-2024 year was retrained per condition
(2018-2023 records are the shared G1 gold bundle, identical across conditions) — so the headline
contrast is diluted and understates the effect; it is flagged as a single-held-out-year reading, not
the full LOSO headline. G2 reviewed APPROVE; reviewer confirmed via manifests that the contrast is
seed-0-clean (only feature_dim 23→24 differs), leakage-free, identical ceiling/pairs across conditions.

### G3 — capacity control: 3x wider net on the same 23 features

As-is (23-feature) retrain, OOS split, seed 0, `hidden_dim 384` (3x the default 128).

| condition | rw OOS | ceiling | pairs |
|---|---|---|---|
| G2 control (hidden_dim 128) | 0.5868 | 0.7643 | 3352 |
| **G3 wide (hidden_dim 384)** | **0.5880** | 0.7643 | 3352 |

**+0.0012 — capacity does nothing.** Extra capacity cannot extract signal that is not in the feature
vector. Hypothesis (c) capacity is EXCLUDED. G3 reviewed APPROVE; reviewer confirmed hidden_dim=384,
feature_dim=23, clean contrast, harness re-read reproduces 0.5880.

---

## VERDICT — Hypothesis (a) FEATURE REPRESENTATION, confirmed on the §7.6.2 same-pairs harness

The standalone `race_weekend` quali head under-extracts because **the cross-channel "who is generally
fast" min-sector pace ordering — the signal whose data ceiling is 0.806 — is not present in (nor
linearly recoverable from) the `qs_*/short_run_*_adj` feature vector the head ingests.** Three
converging probes:

| probe | result | what it rules in/out |
|---|---|---|
| G1 linear readout of the head's OWN 23 features (LOSO) | 0.6513 (≈ head 0.6711, ~15pp < ceiling 0.8061) | the pace ordering is NOT linearly present in the features |
| G2 +PACE input feature, OOS retrain | 0.5868 → 0.7700 (+0.183, ≈ ceiling) | supplying the missing ordering as an INPUT closes the gap → **(a) representation** |
| G3 3x-wider net, same features, OOS | 0.5880 (≈ control 0.5868) | **(c) capacity EXCLUDED** — net is not starved; signal is simply absent |

**Why not (b) training signal:** prior art #387 (archived, measured) established the retro quali
ordering labels are a *perfect transitive tournament* — retro `pi` order disagrees with the observed Q
order on **0 / 65,266 directed pairs**, `start_bias=0` everywhere. The head is therefore trained
toward the *correct* Q ordering and still under-extracts; the deficit is not retro-delta weighting
down-weighting the ceiling-scored pairs (the lever named in the issue's option (b)). The §7.6.3 C3
result independently shows pairwise sign-accuracy is invariant to any monotone rescale — so a
calibration/weighting change cannot move it; only a new ordering signal can. (b) is excluded as the
lever; the corrective lever is information in the input representation.

**Magnitude note (honest):** on the live promoted bundle `gold_cycle_260608_043414` (anchor-active
retrain), the standalone deficit is already narrower than §7.6.2's headline — ~14pp headline / ~5pp
OOS, vs 19pp/20pp in the original pre-anchor bundle — because the #420 anchor banks part of the gap
in-bundle. The localization is unchanged; the residual the module itself leaves is smaller in the live
bundle than the §7.6.2 headline implies.
