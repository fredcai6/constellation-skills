# G1 Verdict — first layer-2 recursive parameter filter (2022 Spain R)

Layer-1: production `StintSmoother` via `fit_stint_hp`, dual pinned ell per regime
(grip=10, coast/drag=4.5; F5/F6), honest 2x2 posterior accel covariance rotated to
(a_long,a_lat). 6 drivers x 22 clean laps, ~76k samples each, all chi2_pos ~ 0.97-1.00.
auto-ell landed 1.4-2.3 (confirming F1/F6: chi2 blind to accel var -> ell MUST be pinned).
Production will use NSStintSmoother state-dependent ell (decided).

## (1) Sequential tightening — YES
Joint info-form posterior (7-param coupled state) tightens lap-by-lap; well-observed
params (theta_D, a_lat0) track ~1/sqrt(N); C_df shows a cliff when corner data first
enters (degeneracy break). corr(theta_D,C_df) settles at -0.39 (the coupling channel).

## (2) BOOTSTRAP headline — REAL mechanism, geometry-capped net (honest partial)
Controlled A/B/C on solo RUS:
  A coast-only (no df)              CdA 2.013 +- 0.062
  B coast + shared C_df, NO corners CdA 1.339 +- 0.914  (collinear df col inflates)
  C full bootstrap (corners pin Cdf)CdA 1.845 +- 0.068
- Corner-regime data pins C_df: sd 1.79e-3 -> 5.25e-5 (34x), and buys back **+92.6%**
  of the C_df-sharing inflation (B->C). The cross-regime information transfer
  grip(corner) -> C_df -> drag(coast) is demonstrated and large.
- BUT net vs the no-downforce drag model is **-8.8%** (slightly worse): coast drag and
  downforce-drag are both ~v^2 (collinear), so admitting downforce into coast cannot be
  fully resolved even with corner-pinned C_df. This is F2's geometry confound, quantified.
- KAPPA sweep: buyback saturates ~+94% for any kappa>0.1; net-vs-A degrades monotonically
  (-1% at 0.1 -> -52% at 0.8) as more of C_df lives in the (collinear) coast channel.
VERDICT: bootstrap MECHANISM real (information flows across regimes via the shared param);
as a CdA-tightener it is capped by coast drag/df collinearity -> honest partial, not a win.

## (3) Teammate pooling — tightens, but < independent-sqrt(2)
solo->pair mean car-param sd ratio: Merc 1.36, Ferrari 1.59, RBR 1.29 (C_df 1.34-1.53).
Ferrari ~1.59 > sqrt(2): teammate samples complementary regimes. Merc/RBR < sqrt(2):
correlated/overlapping coverage (less than 2 independent cars' worth).

## (4) FALSIFICATION — drift-audited, per-pair (the key discipline)
Naive per-car posteriors declared ALL pairs inconsistent (p~0, max|z| 5.9-7.5). AUDIT:
per-lap theta_D scatter vs formal SE gives red_chi2=6.8 -> filter overconfident by x2.6
(between-lap drift not in R; matches F2/F5 drift caveat). After inflating covariance by
the measured drift factor:
  - **Red Bull (VER+PER): SAME CAR within noise** (p=0.19, max|z|=2.3) -> pooling valid.
  - Mercedes (p=0.001) & Ferrari (p=0.000): still inconsistent but max|z| only 2.3-2.9 ->
    candidate "rare exception" (setup/tyre-phase/balance split between teammates), NOT a
    wild mismatch, and NOT to be silently pooled.
The naive "all inconsistent" was a covariance artifact; honest verdict is mixed/per-pair.

## (4b) Held-out + posterior-predictive — calibrated
Train on all-but-lap-53, predict its forces: posterior-predictive reduced chi2 = 1.46,
93% of held-out measurements within 2 sigma -> the accumulated params reproduce unseen
accelerations within (honest) covariance.

## ell reported
grip ell=10.0, coast ell=4.5 (pinned, per F5/F6). auto-ell 1.4-2.3 (rejected). Production
-> NSStintSmoother state-dependent ell.

## Evidence
g1_filter.json, g1_probe.json, g1_falsif_audit.json, g1_summary.png (this dir);
layer-1 checkpoints in ../ckpt/g1_2022_Spain_R_*.npz; scripts in worktree
scripts/experiments/g1_{harvest,filter,probe,plot,falsif_audit}.py (branch expt/448-g1).
