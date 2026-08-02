# Reviewer Handoff — G2 acceptance reproduction (issue #420)

Repo root: `C:\Programs\f1Brainz\.claude\worktrees\agent-aedb2af1326073fec`.
Branch `constellation/issue-420-quali-anchor-production`. Python `py`.
ALWAYS `PYTHONIOENCODING=utf-8` (shell + child subprocess env). Read
`docs/agents/CREW_CONTEXT.md` + `GLOSSARY.md`. You are an INDEPENDENT reviewer:
RE-RUN the harness and re-derive the numbers yourself; do not trust the report.

## Gate
`g2` — the acceptance VERDICT gate (the issue's core).

## What Was Measured
Whether the PRODUCTION pace-anchor path reproduces the §7.6.3 measured
improvement. The harness `scripts/accept_quali_anchor_420.py`:
- builds production `RaceFeatures` per event (`build_sampled_runtime_features`),
- runs the real race_weekend quali module inference on the committed gold bundle
  `gold_cycle_260603_173742_2018thru2024` to get per-event `pi`,
- builds the PRODUCTION anchor = `_nanmin2(qs_best_raw, lr_best_raw)` (min-sector
  pace across BOTH practice buckets — the same construction as the production
  `_anchor_quali_field` in `sampled_runtime.py`), imported from production,
- applies the PRODUCTION `blend_quali_pace_anchor`,
- scores sign-acc on the IDENTICAL shared non-tie pair set as §7.6.2/§7.6.3
  (importing `diagnose_quali_same_pairs` + `diagnose_quali_evidence` primitives),
- sweeps alpha, reports overall + EASY(gap>=9) before/after vs ceiling for
  headline 2018-2024 + OOS 2025, recovered-fraction, and delta vs §7.6.3.

Reported verdict: **REPRODUCES**. Headline α=0.5 = 0.7492 overall / 0.8742 EASY
(§7.6.3 ref 0.7452/0.8691, delta +0.004/+0.005); OOS α=0.5 = 0.7076/0.8417
(ref 0.7097/0.8451); α=0 baseline = 0.6153/0.6901 (ref 0.6153/0.6926).

## How to Inspect
```bash
git status --short
git diff scripts/accept_quali_anchor_420.py   # NEW file (untracked) — read it directly
```
Read `scripts/accept_quali_anchor_420.py` fully. Read the captured output
`.agent-work/issue-420-quali-anchor-production/g2_accept_output.txt` and JSON
`g2_accept_numbers.json`.

## RE-RUN (the core of this review)
```bash
# set PYTHONIOENCODING=utf-8 first
py scripts/accept_quali_anchor_420.py
```
This runs production inference over ~150 events; it may take several minutes.
Confirm it completes and the verdict + numbers MATCH the captured ones (small
nondeterminism should be ~0 since inference is deterministic).

## Close Criteria (each a check)
1. **α=0 reproduces baseline:** headline α=0 overall ≈ 0.6153 (within ~1pp) and
   EASY ≈ 0.6926. This is the control proving the pi source = the same trained
   race_weekend head as §7.6.2/§7.6.3. If α=0 does NOT reproduce, the whole
   measurement is suspect -> BLOCK.
2. **Production anchor is min-of-both-buckets:** the harness builds the anchor via
   `_nanmin2(d.qs_best_raw, d.lr_best_raw)` imported from
   `src.evo_predictor.sampled_runtime` (the SAME helper production uses), NOT
   qs_best_raw alone, NOT a forked reimplementation. Confirm by reading the code.
3. **Real production blend + inference:** uses `blend_quali_pace_anchor` (imported)
   and the real module inference (`build_pair_batch_for_module` + `run_module_field`)
   on the committed bundle `gold_cycle_260603_173742_2018thru2024`. Not a
   re-implementation of the blend math.
4. **Same-pairs population:** the shared non-tie pair set is built via the imported
   `diagnose_quali_same_pairs` primitives (`_shared_nontie_pairs`, `_acc_on_pairs`,
   `_stratified_pairwise`, `_restrict`) exactly as `scope_quali_anchor_414.py`
   does — NOT forked. Pair counts are in the same ballpark as §7.6.2 (headline
   ~24k; the +208 vs 23862 is from live-inference vs record event coverage, an
   acceptable/explained difference).
5. **Reproduction within tolerance:** headline α=0.5 overall within ±3pp of 0.7452
   and EASY within ±5pp of 0.8691; OOS α=0.5 reproduces the pattern. The reported
   deltas (+0.004 / +0.005 headline) are correct per your re-run.
6. **Delta-vs-prototype honestly explained:** the harness explains the production
   anchor = min across qs (short-stint) + lr (long-stint) buckets reconstructs the
   prototype's all-FP `best_across_fp` signal in-machinery; residual delta is
   bucket-split coverage. This explanation is accurate.
7. **Read-only / no production mutation:** the harness does not modify `src/`,
   params, or manifests; inference-only; no retrain. No forbidden files touched
   (fusion.py, fusion_training/, fusion_replay/, prediction_ceiling_and_priorities.md,
   scope_quali_anchor_414.py). (The harness imports diagnose_* scripts read-only.)
8. **No fork of the diagnostic primitives** (imports, not copies).

## Allowed Scope (what impl was permitted)
NEW `scripts/accept_quali_anchor_420.py` only; read-only elsewhere.

## Specific Exclusions (flag if touched)
src/ production code, params/manifests, fusion files,
prediction_ceiling_and_priorities.md, scope_quali_anchor_414.py.

## Suggested Model Tier
Stronger — this is the acceptance verdict; independent re-derivation is the point.

## Stop Conditions
BLOCK if: the harness cannot be re-run, α=0 does not reproduce the baseline, the
anchor is not the production min-of-buckets, the blend/inference/pairs are forked
rather than the real production+imported code, the reproduction is outside
tolerance, or a forbidden file was touched.

## Return Format
REVIEW_RESULT: verdict (APPROVE or BLOCK), per-check findings (1-8), YOUR re-run's
headline α=0 and α=0.5 numbers (to confirm reproducibility), blockers, out-of-scope
observations.
