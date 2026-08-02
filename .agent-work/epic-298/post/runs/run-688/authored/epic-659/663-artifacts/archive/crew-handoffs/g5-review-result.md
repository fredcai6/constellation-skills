# Review Result — g5-review (GATING acceptance gate, issue #663, SECOND of two)

## Assigned Gate
`g5-implement` reviewed for `g5-review` — synthetic parameter-recovery / identifiability GATING harness, `tests/unit/physics/layer2/test_grip_synthetic_recovery.py`.

## Result
**APPROVE**

## Independent determination: is the SPLIT result (recovery-passes-hollowly / separability-fails) a sound, real finding?
**YES — sound and real.** The harness is trustworthy, the numbers reproduce byte-identically, and the SNR calibration survives an independent real-data spot-check. The two halves of the split are exactly what they claim to be:
- **Recovery PASSES only hollowly.** The 94.4% pooled rate is carried by low-SNR replicates where the fit honestly reports enormous sigmas (asy_sigma up to 1e7–1e8 s), so its 2σ interval trivially covers the truth. The ONE genuinely-confident regime (highSNR/modBend) drops to 66.7% recovery / 66.7% asymptote-coverage — the moment the sigmas are tight, aliasing bias escapes the interval. "Recovery passes" therefore means "the error bars are honestly wide," NOT "the estimates are accurate." Correctly and prominently flagged by the implementer.
- **Separability FAILS decisively and intrinsically.** 31.9% pooled (threshold 90%), median |offset↔asymptote corr| 0.835, 49/72 replicates at/past the 0.8 wall, 23/72 pinned in [0.95,1.0]. It fails even in the estimator's cleanest possible case — data drawn exactly from G's own model, high SNR, fully-bending curve — at median |corr| 0.939 (only 33% clear 0.8). This is a functional-form defect, reproduced on known-truth synthetic data, that **independently confirms g4's real-data diagnosis**.

Both GATING gates for #663 now point at the same defect from opposite directions (g4: real data; g5: synthetic known-truth): G's saturating curve+offset parameterization aliases offset against asymptote on realistic F1 session shapes.

## Per-criterion findings (all 7 close criteria)

**1. Real fit genuinely called, not reimplemented — PASS.** L78 imports `fit_grip_baseline_from_laps` + `_saturating` from the production module; L210 calls it once per replicate on the synthetic lap frame; recovered params, sigmas, and `curve_offset_correlation` are all read off the production `GripEstimateRecord` (L217–221). No fit is reimplemented — a private re-fit would prove nothing about G, and there is none.

**2. Synthetic-data realism (SNR spot-check) — PASS (INDEPENDENTLY VERIFIED).** I fitted five real 2023 FP2 sessions myself with the worktree `grip_baseline` (asserted `__file__` inside the worktree to dodge the editable-install `.pth` trap). Measured **field-pooled residual RMS = 12.2–14.5 s** (Spain 14.5, Canada 13.1, Saudi 12.2, Netherlands 13.9, Vegas 12.8) vs the implementer's claimed ~14–17 s — same scale, honest. The harness's low-SNR "real" tier uses `noise_sigma=11.0` (~11 s residual), i.e. if anything **marginally EASIER than reality**, so it *understates* the problem rather than manufacturing it. Real physical rubber-evolution amplitude ~1.5 s under a ~13 s residual gives real SNR ≈ 0.11–0.13, landing right on the harness low band (0.136). My real fits also reproduced g4's degeneracy (Netherlands fitted asymptote 8040 s, Vegas −7870 s), confirming that large fitted asymptotes are aliasing artefacts, not genuine amplitude. **Decisive robustness point:** separability fails even at the cleanest high-SNR/high-bend tier, so the finding does not hinge on getting the SNR tier exactly right. The "realistic" tier is calibrated honestly (neither too easy nor too hard; marginally conservative).

**3. `predictive_t` exact call — PASS.** `two_sigma_covers` (L194–197) calls `predictive_t(mu_hat, sigma_reported, n_eff, nu_loss=DEFAULT_NU_LOSS, rule=FormulaRule()).interval(0.9545)` exactly as cited. Confirmed against `src/common/student_t.py`: `.interval(0.9545)` delegates to `scipy.stats.t(df=nu, loc, scale).interval(0.9545)` — the central interval holding 0.9545 probability mass, the correct two-sided 2σ-equivalent. The record's stored `*_sigma` is already a predictive scale, so re-passing it re-applies the `sqrt(1+1/n_eff)` epistemic factor → a marginally WIDER interval. This biases coverage **toward PASS**, so the 94.4% recovery is a *generous* pass; a tighter (exact-2-scale) interval would only lower recovery and strengthen the "recovery is hollow" story. The choice is conservative w.r.t. the finding and does not move the split.

**4. Recovery-passes-only-via-sigma-widening — PASS (materially qualifies the pass).** Verified from the per-regime table and raw replicates: all low-SNR regimes show 100% recovery with 100% asymptote-coverage but huge sigmas; the single confident regime (highSNR/modBend) drops to recovery 66.7% / covAsy 66.7%. A passing rate driven by honest uncertainty-inflation is a genuinely different finding from one driven by tight, accurate estimates — the implementer states this explicitly and it is correct.

**5. Honest-null operationalization — PASS.** Read every assert (L388–402): (1) ≥50 replicates ran; (2) ≥90% reached the real curve-fit path; (3) per-ok finite outputs; (4) both rates finite in [0,1]; (5) SNR genuinely varied. NONE encodes `recovery_rate>=0.90` or `separability_rate>=0.90`; the L403–405 comment states the omission is deliberate. The scientific verdict is printed + written to JSON, exit 0 under the null.

**6. `decision:synthetic-criterion` guess-graded adjustment — PASS.** The 0.8 threshold and ≥50 replicate count were kept unchanged; the regrade reasoning to `settled/measured` is genuinely RECORDED in the result doc (L104–112), not merely asserted. Defensible: the estimator's cleanest regime sits at median |corr| 0.82–0.94 (right at the 0.8 wall) and 49/72 replicates sit ≥0.8, so 0.8 is the informative identifiability cut — raise it and you whitewash an intrinsic aliasing the fit fails even in its best case. NOTE: the `@grade:` tag in `execute.json` (L869) still literally reads `guess`; flipping it to `settled/measured` is the commander's reconcile action, not a review defect.

**7. Diagnostic depth reproduces — PASS.** Re-ran `pytest -q -s`: output byte-identical to the pasted evidence (recovery 94.4% PASS, separability 31.9% FAIL, median |corr| 0.835, full per-regime table and |corr| histogram). Deterministic from fixed `BASE_SEED=663`. Not hand-summarized after the fact.

## Handoff compliance
Built exactly what the handoff asked: known-truth synthetic recovery + separability over a 6-cell SNR×bend factorial (72 replicates ≥ the frozen 50), calling g2's real fit, honest-null reporting, exit 0 under the null. Stop conditions: none hit. Compliant.

## Scope drift
New file only. `git status --porcelain` shows the whole `physics/layer2` module untracked on branch `epic659/663-grip-g` (g1–g4 uncommitted); the only g5 addition is `test_grip_synthetic_recovery.py` (`git check-ignore` exit 1 = committable). Decisive independent proof no fix was smuggled into `grip_baseline.py`: my real-session re-fits reproduced the SAME degenerate large-asymptote / near-±1-corr fits g4 saw — the estimator was not secretly constrained. Results JSON + engine plan untracked, not staged. No drift; exclusion honored.

## Evidence verdict
Required evidence present and independently reproducible: harness re-run identical; SNR-realism claim confirmed against real 2023 fits; `simplification_limits --paths` re-run PASS (exit 0). This synthetic known-truth harness is the L2/L3 truth-anchored evidence CREW_CONTEXT requires for a physics change.

## Code/doc quality
Small cohesive helpers; reuses the production fit rather than reimplementing it; explicit RNG (`np.random.default_rng`) with fixed seed, no global state; pure-synthetic (DB-free) so the DB-only rule is N/A. Fowler pass: `verify_fowler_pass.py` exit 0 (record at `.agent-work/663-grip-g/g5-review/fowler-pass.json`) — 10 smells absent; `data-clumps` overridden (the 3 per-param coverages are distinct identifiability axes reported separately by design — the per-axis breakdown IS the deliverable); `comments-as-deodorant` overridden (the dense docstring/comments carry the GATING scientific calibration rationale a reviewer must read, not deodorant masking unclear code). No refactor blocker.

## Map impact verdict
- **Evidence supports claimed change:** Yes — the reproduced numbers + my independent real-fit spot-check back the split-result claim.
- **Constraints not violated:** exclusion set honored (no edit to grip_baseline/grip_store/grip_batch/tyre_supplant or the g4 test); relied only on the unchanged `fit_grip_baseline_from_laps` seam and `predictive_t` public interface.
- **Notes match the diff:** Yes — test-only, `struct:physics.layer2`, no production module touched.
- **Decision candidates surfaced:** `decision:synthetic-identifiability` evidence produced; `decision:synthetic-criterion` regrade proposed with recorded reasoning (commander to formalize).
- **Durable context routed:** Yes — the cross-gate G-identifiability finding is routed as triage candidate `tc1` for the commander.

## Reconciliation check
No code-level divergence requiring reconcile. The one item for the Commander is a **verdict decision, not a defect** (explicitly out of this gate's scope per exclusions): with both GATING gates confirming the same non-separability defect, adjudicate reopen-g2-to-constrain-the-fit vs accept-the-honest-null as #663's deliverable, and formalize the `synthetic-criterion` regrade.

## Blockers
- None.

## Out-of-scope observations (triage candidates for the Commander)
1. **CONFIRMED cross-gate: G's saturating curve+offset is structurally non-separable** (offset↔asymptote |corr| near ±1; only 31.9% of synthetic replicates clear 0.8, median 0.939 even in the cleanest regime). Defect is in the estimator/parameterization, not the data. Candidate fixes: reparameterize to an identifiable basis (anchored initial value + bounded total-gain), bound/prior asymptote+rate, or flat-offset fallback when |corr|→1.
2. **"Subtract G" should be σ-gated downstream.** Recovery passes only via honest sigma-widening; a consumer subtracting G's point estimate gets no protection from the wide sigma (reinforces g4's observation #2).
3. **Functional-form question for the epic level:** whether the field-pooled saturating-curve model is the right shape at all vs a simpler monotone track-evolution offset, given the aliasing is intrinsic to the form on realistic F1 session shapes.

## Workflow Feedback
- **Handoff gaps:** Excellent, tractable handoff — the 7 enumerated criteria mapped cleanly onto independent checks and correctly directed me to *actually fit a real session* rather than trust the pasted calibration. One friction: criterion 3 asks whether a "different level should have been used and whether that would move the 94.4% materially," but the honest answer required reasoning about the *direction* of the sigma double-count (it widens → biases toward PASS) rather than a re-run at a different level; a one-line steer ("assess the direction of bias, not a re-run") would have been cleaner. Not blocking.
- **Context rediscovered:** The editable-install `.pth` worktree trap (ad-hoc probe scripts silently import MAIN `src/`) bit my independent real-fit — I had to `sys.path.insert(0, worktree)` and assert `grip_baseline.__file__`. This is the identical friction the g4 reviewer reported; it is now clearly a recurring cost for any #663 reviewer who writes an independent probe, and belongs in the handoff as a one-line note. The real field-pooled residual scale (~13 s) and physical curve amplitude (~1.5 s) that pin the real SNR were also not carried as an anchor — the g5-implement result flagged the same gap.
- **Instructions improvised around:** None material. The reviewer survey engine + Fowler rail accepted the two logged overrides cleanly; the `current`-alone survey cold-start caveat did not bite (single continuous session).
- **What would have made this easier:** Two one-line handoff anchors would have saved a cycle for both g4 and g5 reviewers: (a) the `.pth` worktree-import trap + the assert-`__file__` workaround; (b) the pre-measured real calibration numbers (field-pooled residual ~13 s, rubber-evolution amplitude ~1.5 s → real SNR ~0.12).

## Return status
`complete`
