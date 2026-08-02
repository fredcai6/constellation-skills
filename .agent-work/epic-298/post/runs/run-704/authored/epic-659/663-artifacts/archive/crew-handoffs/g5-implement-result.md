# Implementation Result — g5-implement (GATING acceptance evidence, issue #663)

## Assigned gate
`g5-implement` — synthetic parameter-recovery / identifiability harness testing whether G's
actual fit recovers a KNOWN injected curve+offset and separates curve magnitude from offset,
on data where the ground truth is known.

## Return status
`complete` — harness built, driven through the engine to done (m0→m1→m2→m3, lease released as
the final journaled action), real numbers produced.
**Scientific outcome: SPLIT — recovery PASSES (94.4% ≥ 90%), separability FAILS decisively
(31.9% ≪ 90%, median |curve_offset_correlation| = 0.835). The separability null
INDEPENDENTLY CONFIRMS g4's real-data identifiability diagnosis on synthetic data with known
truth.** This is a complete, valid, reported deliverable per the Honest-Null Clause — not a
manufactured pass and not manufactured drama (recovery genuinely clears the bar).

## Completed slice
New pure-synthetic evaluation harness `tests/unit/physics/layer2/test_grip_synthetic_recovery.py`.
Per replicate it (1) generates a field-pooled synthetic session with a KNOWN saturating curve
`offset + asymptote*(1-exp(-rate*x))` + per-driver pace spread + i.i.d. noise, over a realistic
`cumulative_track_laps` axis with realistic stints (within-stint x rises with tyre_life — the
real wear/evolution confound); (2) calls the REAL `fit_grip_baseline_from_laps`; (3) scores
parameter-recovery (all three params inside the fit's OWN 2σ predictive-t interval of the
injected truth) and separability (`|curve_offset_correlation| < 0.8`). 72 replicates over a
6-cell factorial sweep of the two physically-meaningful identifiability axes (SNR × curve-bend).
Reports both pooled rates with the frozen 90% threshold as a PRINTED verdict + a per-regime
breakdown + a |corr| histogram; writes `.agent-work/663-grip-g/g5-synthetic-results.json`. Exits
0 regardless of the scientific outcome.

## Scope
**Files changed:**
- `tests/unit/physics/layer2/test_grip_synthetic_recovery.py` (new; `git check-ignore` exit 1 → committable)
- `.agent-work/663-grip-g/g5-synthetic-results.json` (new; local-only, untracked, NOT staged)
- `.agent-work/663-grip-g/g5-implement-plan.json` (+ `.journal`) (engine plan, local-only)

**Specific exclusions touched:** `no` — `grip_baseline.py`, `grip_store.py`, `grip_batch.py`,
`tyre_supplant.py`, and the g4 test file were all read-only/imported, never modified. (They show
as untracked `??` in `git status` because the entire g1–g4 `physics/layer2` module is uncommitted
on this branch — not because I touched them; confirmed the only tree write is the new test file.)
I did NOT attempt to fix the identifiability problem (out of scope — a g6/commander decision).

## Behavior changed
`no` — test-only addition; no production code path altered.

## The real rates + diagnostic detail (load-bearing)

Deterministic (fixed `BASE_SEED=663`, byte-reproducible across process runs — verified twice
identical). Recovery = all of (asymptote, rate, offset) inside the fit's OWN 2σ predictive-t
interval of the injected truth. Separability = `|curve_offset_correlation| < 0.8`.

| regime | SNR | bend | n | recov% | sep% | covOff | covAsy | covRate | med\|corr\| |
|---|---|---|---|---|---|---|---|---|---|
| highSNR/highBend | 5.00 | 0.90 | 12 | 100.0 | 33.3 | 100.0 | 100.0 | 100.0 | 0.939 |
| highSNR/modBend | 5.00 | 0.50 | 12 | 66.7 | 33.3 | 91.7 | 66.7 | 100.0 | 0.824 |
| medSNR/highBend | 1.00 | 0.90 | 12 | 100.0 | 41.7 | 100.0 | 100.0 | 100.0 | 0.886 |
| medSNR/modBend | 1.00 | 0.50 | 12 | 100.0 | 41.7 | 100.0 | 100.0 | 100.0 | 0.811 |
| lowSNR(real)/highBend | 0.14 | 0.90 | 12 | 100.0 | 16.7 | 100.0 | 100.0 | 100.0 | 0.828 |
| lowSNR(real)/modBend | 0.14 | 0.50 | 12 | 100.0 | 25.0 | 100.0 | 100.0 | 100.0 | 0.849 |

**POOLED recovery rate = 94.4% (threshold 90%) → PASS**
**POOLED separability rate = 31.9% (threshold 90%) → FAIL**
**median |curve_offset_correlation| across all 72 replicates = 0.835**

`|corr|` histogram (all 72 ok replicates): `[0,.2) 0 · [.2,.4) 3 · [.4,.6) 3 · [.6,.8) 17 ·
[.8,.95) 26 · [.95,.99) 14 · [.99,1] 9`. So 49/72 (68%) sit at or past the 0.8 aliasing wall,
with 23/72 pinned in [0.95, 1.0] — the same degeneracy g4 observed on real fits (corr ≈ ±1).

### Why (diagnosed, not mysterious)
- **Separability failure is INTRINSIC to the fit's functional form, not a data artifact.** Even
  in the estimator's cleanest possible case — data generated exactly from the model, high SNR
  (5), curve fully bending (bend 0.9) — the offset↔asymptote correlation still sits at median
  **0.939** and only 33% of replicates clear 0.8. `offset` (the x→0 intercept) and `asymptote`
  (the total rise) are structurally anti-correlated whenever the curve does not saturate
  *within* the observed window with abundant low-x anchoring; on realistic F1 session shapes
  it never does cleanly. This is exactly the T2 separability defect `curve_offset_correlation`
  was built to surface, reproduced here with known truth.
- **It worsens toward the real regime.** As SNR falls to ~0.14 (the real ~15 s field-pooled
  residual scale vs the ~1.5 s track-evolution amplitude), separability collapses to 16–25%
  and |corr| drifts toward the ±1 wall — matching g4's real Monaco/Netherlands/Saudi fits
  (corr −1.000 / −0.995 / +0.78).
- **Recovery PASSES but the pass is soft and mechanism-revealing, not reassuring.** At low SNR
  the fit honestly reports enormous sigmas (the #560-correct "don't be falsely confident"
  behavior), so its 2σ interval trivially covers the truth → 100% coverage. The pass is thus
  "the error bars are wide enough to be honest," NOT "the estimate is useful." The one regime
  that dips (highSNR/modBend, recovery 66.7%, covAsy 66.7%) is the tell: when SNR is high the
  sigmas are tight, and then the aliasing-induced *bias* along the degenerate offset↔asymptote
  direction pushes the point estimate outside its own (now narrow) interval. So recovery only
  survives by the sigma widening — the moment the fit is confident, the aliasing breaks
  coverage.

**Scope of the null (scoped-nulls doctrine — what was and was NOT tested):**
- Tested: the exact `fit_grip_baseline_from_laps` object, data drawn FROM its own model
  (no misspecification), 6 regimes spanning SNR {5, 1, 0.14} × bend {0.9, 0.5}, 12 seeds each,
  ~20 drivers, 1–3 stints, 5–9 laps/stint, 3 dry compounds (real wear path exercised).
- NOT tested: injected-asymptote magnitude was fixed at −1.5 s (SNR varied via noise, not
  amplitude); no injected *fuel* confound (i.i.d. noise only — which is the BENIGN case, so
  the real structured-fuel degeneracy is if anything worse than measured); driver/stint counts
  not swept; only the FP-like shape (no Q/R stint regimes). A dead separability result here is
  "this fit form, on these realistic shapes, cannot separate curve from offset" — NOT "grip
  baselines are impossible." Natural next variant (out of scope, g6): constrain/regularize the
  fit (bound asymptote, fix/prior the rate) and re-run this exact harness to see whether
  separability recovers.

## The frozen `decision:synthetic-criterion` (0.8 threshold) — settled, not moved
Graded `guess` with settle-instruction "adjust the 0.8 threshold with recorded reasoning if it
proves miscalibrated." I ran the harness and judged 0.8 **well-calibrated, left unchanged**: the
estimator's *best case* (clean model, high SNR) sits right at median |corr| ≈ 0.82–0.94, i.e. the
threshold lands exactly on the boundary the fit form can achieve, and realistic regimes blow
through it to ≈1. Moving it up would whitewash an intrinsic aliasing; moving it down would make
even the degenerate real fits "pass." 0.8 is the informative cut, so I regrade it
`settled/measured` (settled by running the harness; reasoning recorded here).

## Test mode
**Required:** `evidence-only` (real synthetic-data evaluation harness, not TDD).
**Satisfied:** `yes` — harness runs the full 72 replicates, computes+reports both rates, writes
the artifact, exits 0 under the null. No `assert recovery_rate>=0.90` / `assert
separability_rate>=0.90`; the only asserts are harness-validity (≥50 replicates ran, ≥90% reached
the real curve-fit path, all finite, both rates in [0,1], SNR genuinely varied).

## Evidence (pasted)

```
$ py -m pytest tests/unit/physics/layer2/test_grip_synthetic_recovery.py -q -s
G SYNTHETIC PARAMETER-RECOVERY / IDENTIFIABILITY -- issue #663 gate g5
replicates=72 (ok fits=72)  |  real fit_grip_baseline_from_laps called per replicate
regime                       SNR  bend   n  recov%   sep%  covOff  covAsy covRate med|corr|
highSNR/highBend            5.00  0.90  12   100.0   33.3   100.0   100.0   100.0     0.939
highSNR/modBend             5.00  0.50  12    66.7   33.3    91.7    66.7   100.0     0.824
medSNR/highBend            1.00  0.90  12   100.0   41.7   100.0   100.0   100.0     0.886
medSNR/modBend             1.00  0.50  12   100.0   41.7   100.0   100.0   100.0     0.811
lowSNR(real)/highBend      0.14  0.90  12   100.0   16.7   100.0   100.0   100.0     0.828
lowSNR(real)/modBend       0.14  0.50  12   100.0   25.0   100.0   100.0   100.0     0.849
|curve_offset_correlation| histogram (all ok replicates):
    [0,.2)   0 · [.2,.4) 3 · [.4,.6) 3 · [.6,.8) 17 · [.8,.95) 26 · [.95,.99) 14 · [.99,1] 9
POOLED recovery rate     =   94.4%  (threshold 90%)  -> PASS
POOLED separability rate =   31.9%  (threshold 90%)  -> FAIL
median |corr| across all replicates = 0.835
VERDICT: NULL: G does NOT clear the 90% identifiability bar across the tested regimes
         (confirms g4's real-data diagnosis synthetically -- see per-regime breakdown)
results artifact -> ...\.agent-work\663-grip-g\g5-synthetic-results.json
1 passed in 1.88s   (exit 0; determinism re-verified: two runs identical rates)

$ py -m src.utils.simplification_limits --paths tests/unit/physics/layer2/test_grip_synthetic_recovery.py
PASS (1 files checked)
```

Confirmation the harness calls g2's real function (the whole point):
`from src.physics.layer2.grip_baseline import _saturating, fit_grip_baseline_from_laps` — the fit
is imported and invoked once per replicate; recovered params, sigmas, and
`curve_offset_correlation` all read off the production `GripEstimateRecord`. No fit reimplemented.

`predictive_t` — EXACT call cited (function `two_sigma_covers`):
`predictive_t(mu_hat, sigma_reported, n_eff=n_stints_used, nu_loss=DEFAULT_NU_LOSS,
rule=FormulaRule()).interval(0.9545)`. The record's `*_sigma` is already the module's predictive
scale, so re-passing it re-applies the tiny `sqrt(1+1/n_eff)` factor → a marginally WIDER
interval, biasing the coverage check toward PASS (so the separability FAIL and any recovery miss
are not too-tight-interval artifacts). `0.9545` = two-sided 2σ-equivalent probability mass.

Engine: plan `.agent-work/663-grip-g/g5-implement-plan.json` claimed (session g5-impl-cmdr663) →
m0-context / m1-calibrate / m2-harness / m3-simplify all advanced → `current` = "DONE: no open
items" → lease released (final journaled action).

## Assumptions
- Injected curve amplitude fixed at asymptote = −1.5 s (a physical green→rubbered pace gain);
  SNR is varied via noise, not amplitude, to keep the SNR axis interpretable.
- "Realistic noise" operationalized as a SWEEP, not a single number: per-lap i.i.d. σ ∈
  {0.30, 1.50, 11.0} s giving SNR {5, 1, 0.14}, where the low band reproduces the real ~14–17 s
  field-pooled residual scale I measured fitting five real 2023 FP sessions. Per-driver pace
  spread (σ 0.7 s) is injected separately as structured field noise, since the fit really pools
  the whole field into one curve.
- `cumulative_track_laps` axis: x_max = 500 (real ~460–610), within-stint step FIELD_CONC = 12
  (concurrent circulating cars), stint p_start spread over [0, x_max]. This reproduces the real
  within-stint collinearity of track-evolution x with tyre_life (and thus the wear confound).
- n_eff for the interval = the record's `n_stints_used` (the same n_eff the module uses for its
  own sigma).

## Stop conditions hit
None. `fit_grip_baseline_from_laps` accepted the synthetic lap frame with no signature change
(the calibration probe confirmed callability before scaling to 72 replicates). No decision beyond
the granted authority was required (the one graded `guess`, the 0.8 threshold, fell inside my
authority to settle by running the harness). Runtime ~2 s.

## Out-of-scope observations (triage candidates for the commander)
1. **CONFIRMED (synthetic, known-truth): G's per-session curve+offset is structurally
   non-separable** — offset↔asymptote |corr| ≥ 0.8 in ~68% of replicates and pinned near ±1 at
   realistic SNR, EVEN when the data is generated exactly from G's own model. Combined with g4's
   real-data negative, this is now corroborated from both directions: G as currently fit is not a
   usable cross-session-subtractable baseline. The defect is in the *estimator/parameterization*,
   not merely the real data. Candidate fixes (for g6): reparameterize to an identifiable basis
   (e.g. fit the anchored initial value + a bounded total-gain instead of free offset+asymptote),
   bound/prior the asymptote to a physical range, fix or strongly-prior `rate`, or gate G to a
   flat session offset when `|corr|` is near 1 (the record already exposes it).
2. **Recovery "passes" only via honest sigma widening, not estimate quality.** The 94.4% is
   carried by low-SNR replicates where the fit reports huge sigmas; the one high-SNR/confident
   regime drops to 66.7% because aliasing bias then escapes the narrow interval. A downstream
   consumer that subtracts G's point estimate (as g4's prescribed reconciliation did) gets no
   protection from the wide sigma — reinforcing g4's out-of-scope note #2 that "subtract G"
   should be σ-gated downstream.
3. **The separability defect is functional-form-intrinsic**, so it will recur for ANY session
   shape short of one where the curve saturates within a well-anchored low-x window — unlikely on
   real F1 practice. Worth deciding at the epic level whether the field-pooled saturating-curve
   model is the right shape at all, vs a simpler monotone track-evolution offset.

## Map Impact
- **Structural anchors touched:** `struct:physics.layer2` — new test-only module
  `tests/unit/physics/layer2/test_grip_synthetic_recovery.py`; no production module changed.
- **Capabilities affected:** G's synthetic-identifiability acceptance evidence — produced; result
  is SPLIT (recovery PASS 94.4%, separability FAIL 31.9%).
- **Constraints/assumptions touched:** honored the exclusion set (no edits to
  grip_baseline/grip_store/grip_batch/tyre_supplant or the g4 test); relied on
  `fit_grip_baseline_from_laps`'s lap-frame seam and `predictive_t`'s public interface unchanged.
- **Decision candidates / resolved decisions:** `decision:synthetic-identifiability` — evidence
  produced. `decision:synthetic-criterion` (was `guess`) — settled `settled/measured`, 0.8
  threshold judged well-calibrated and left unchanged, reasoning recorded above.
- **Claims/evidence produced:** G's curve+offset fit is non-separable (offset↔asymptote |corr| ≥
  0.8, → ±1 at realistic SNR) on synthetic data drawn from G's own model — INDEPENDENTLY
  CONFIRMS g4's real-data diagnosis. Backed by the 72-replicate sweep + JSON artifact.
- **Trust limitations / drift found:** the aliasing is intrinsic to the fit's functional form
  (not a data-quality or split artifact) — a strong signal that the g1/g2 curve parameterization
  is the thing to revisit, not the data pipeline.
- **Triage candidates:** the three above (esp. #1 — reparameterize/constrain the fit).

## Workflow Feedback
- **Handoff gaps:** The handoff's item-3(a) says recovery checks whether params land "within the
  fit's OWN reported 2-sigma predictive interval (build this via `predictive_t(mu, sigma, n_eff)`)"
  but did not resolve the double-count subtlety: the record's stored `*_sigma` is ALREADY a
  `predictive_t` scale, so feeding it back through `predictive_t` re-applies the epistemic factor.
  It's negligible (n_eff large → sqrt(1+1/n_eff)≈1.01) and biases toward PASS, so I used it and
  documented the direction — but a one-line note ("the stored sigma is the predictive scale; use
  it as `sigma`") would have removed the ambiguity.
- **Context rediscovered:** The dominant real-fit residual is ~14–17 s and STRUCTURED (fuel +
  field spread), not i.i.d. — I had to fit five real sessions to learn this, and it's the single
  most important calibration fact (it's why real SNR ≈ 0.13 and why the fit degenerates). g4's
  result implied it but neither the handoff nor an anchor carried the residual scale. Carrying
  "real field-pooled residual ≈ 15 s, curve amplitude ≈ 1.5 s → SNR ≈ 0.1" into this handoff would
  have saved the calibration probe.
- **Instructions improvised around:** "Match real 2023 session shapes … realistic noise levels"
  under-determines the experiment when the honest answer is a SWEEP (the result depends strongly
  on SNR and bend). I improvised a 6-cell SNR×bend factorial and reported the dependence rather
  than pick one noise number and hide it — this also directly answers the handoff's "which regime
  fails?" ask. The template/handoff has no slot for "the deliverable is a regime map, not a single
  pass/fail," which is the right shape for an identifiability test.
- **What would have made this easier:** A one-line calibration anchor (real residual scale +
  curve amplitude → real SNR) and an explicit "report recovery/separability as a function of a
  stated regime sweep" instruction. Neither blocked the deliverable; recorded because I was the
  only one who saw the friction.

## Return status
`complete`
