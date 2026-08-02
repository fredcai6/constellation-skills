## cmdr-451 localization verdict — (a) feature representation

**Verdict: the standalone `race_weekend` quali head under-extracts because of FEATURE REPRESENTATION (a).** The cross-channel min-sector "who is generally fast" pace ordering — the signal whose data ceiling is 0.806 — is not present in (nor linearly recoverable from) the head's 23-dim `qs_*/short_run_*_adj` input vector. Three converging probes on the §7.6.2 same-pairs harness (single-module ablation retrains, no gold cycle, no Piece-2):

| probe | result | conclusion |
|---|---|---|
| Walk-forward linear readout of the head's OWN 23 features (LOSO) | **0.6513** (≈ trained head 0.6711; ~15pp < ceiling 0.8061) | pace ordering is **not linearly present** in the features |
| +PACE retrain: add `min(qs_best_raw, lr_best_raw)` as a 24th INPUT feature (OOS-2025) | 0.5868 → **0.7700** (+0.183, ≈ ceiling 0.7643) | supplying it as an input closes the gap → **(a) confirmed** |
| 3× wider net (`hidden_dim` 128→384), same 23 features (OOS-2025) | **0.5880** (≈ control 0.5868) | **(c) capacity excluded** — net is not starved |

**(b) training signal excluded as the lever:** prior art #387 proved the retro quali ordering labels are a perfect transitive tournament (retro `pi` disagrees with observed Q order on 0 / 65,266 directed pairs), so the head trains toward the *correct* ordering and still under-extracts — not retro-delta weighting. §7.6.3 C3 independently shows sign-accuracy is invariant to any monotone rescale, so calibration/weighting cannot move it; only a new ordering signal can. The lever is **information in the input representation**.

**Recommendation:** **no fix shipped** (a clean representation fix touches a promoted default — beyond the small-fix-only scope; floated to Admiral). The verdict directly **validates #425's framing**: feed an explicit all-FP min-sector practice-pace feature as a head **INPUT** (what the #420 anchor currently supplies post-hoc via blending). Design note for #425: add a companion `{name}_missing` indicator (the probe used a bare 0.0 NaN fallback) and consider a within-event-standardised variant. #394/#395 (form re-encodings) are orthogonal to this deficit — the missing signal is cross-channel pace, not form.

**Magnitude note (honest):** measured on the live promoted bundle `gold_cycle_260608_043414` (anchor-active retrain), the standalone deficit is already narrower than §7.6.2's headline — ~14pp headline / ~5pp OOS, vs 19pp/20pp in the original pre-anchor bundle — because #420 banks part of the gap in-bundle. The §7.6.2 records dir was gitignored/not preserved and the original bundle is gone, so records were regenerated from the live bundle (flagged; rh 0.7786 / ceiling 0.8061 / 23862 pairs reproduced exactly, rw deviation explained by the anchor-active retrain).

**Map impact:** §7.6.5 added to `docs/evo/prediction_ceiling_and_priorities.md` (localization verdict) + architecture reconciliation trail entry. No structural/code change (diagnostic only). **Triage (not filed, routed to Admiral):** TC1 #425 design input; TC2 §7.6.2 live-bundle number reconciliation; TC3 persist training seed in module manifest.

Leakage discipline: every probe respects walk-forward as-of cutoffs (eval years held out; pace feature is pre-Q FP-derived); the harness was run unmodified; control vs +pace/wide differ only by the one variable; reviewers independently verified each gate (no defects). Full evidence: `.agent-work/453/findings/cmdr-451.md` on branch `issue-451-quali-under-extraction`.
