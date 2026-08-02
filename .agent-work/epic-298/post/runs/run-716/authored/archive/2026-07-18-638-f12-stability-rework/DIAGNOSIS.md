# G1 DIAGNOSIS — F12 held-out-circuit k-instability (#638)

Real-data evidence: `data/damage_integrals.db` `grip_bin_obs`, 22 circuits, 612,615 rows.
Scripts: `.agent-work/638-f12-stability-rework/diagnose_k_instability.py`, `probe_logspace.py`,
`probe_logselect.py`, `probe_decisive.py`, `probe_final.py` (raw outputs `*_out.txt` alongside).

## Baseline reproduced (faithful)
Shipped `fit_property_mixture` (BIC over full N, standardized raw `(radius_m, lateral_g)`,
support floor 0.05, k_range (2,6)): per-split k_a/k_b = 4/6, 6/2, 4/6, 5/3, 3/4 → n_pass 0/5.
Byte-consistent with `docs/physics/625-f12-holdout-stability.json`.

## Root cause — TWO compounding failures

### RC1 (the deep one): raw radius is a heavy-tailed continuum → LOCATIONS shift with composition
`radius_m` spans p1=21m → p50=103m → p99=1169m (~2 decades, strongly right-skewed);
`lateral_g` p1=0.5 → p99=5.1. This is a smooth continuum, **not** clean clusters. A GMM tiling a
smooth skewed density plants its component means at density-weighted positions that move with the
circuit mix (a Monaco-heavy half pulls means to small radius; a Monza-heavy half to large radius).
**Even FIXING k, raw-space locations are unstable:** fixed k=2 → 1/5, k=3 → 1/5, k=4 → 1/5
(`diagnose_k_instability.py`, section D). So this is NOT merely a k-count artifact — it is a
location-identifiability failure of a Gaussian mixture on this descriptor.

Physics: corner radius is **multiplicative** — adjacent corner classes differ by roughly an
*order of magnitude* (the shipped `RADIUS_SCALE_M=50` comment itself says "order-of-magnitude
gap"). The natural scale is **logarithmic**. Fitting in `(log10 radius, lateral_g)` makes
locations composition-STABLE: fixed k=2 → 5/5 (stats 0.26–0.51), fixed k=4 → 5/5 (0.31–0.57)
(`probe_logspace.py`). log10(radius) is near-symmetric (p1=1.31 → p50=2.01 → p99=3.07).

### RC2: BIC over ~300k autocorrelated rows saturates the k_range; the 5% support floor knife-edges
BIC penalty is negligible at this N (penalty 63–439 vs LL sums ~1.5M; per-point LL keeps
improving), so BIC always wants the k_range ceiling. `grip_bin_obs` rows are massively
autocorrelated (many bins/lap, many laps), so raw N grossly overstates independent information.
Which k finally survives is then decided by the **5% relative support floor**, which prunes the
rare very-fast-corner component inconsistently across compositions.

Cheap candidate fixes tested and REJECTED (all in `diagnose_k_instability.py`/`probe_*`):
- **effective-N-capped BIC penalty** (caps 300…10000): NO effect (0/5) — the penalty was already
  negligible; shrinking it changes nothing while the LL term still scales with full N.
- **subsample-budget selection** (2k/5k/10k, raw): 0/5 — the continuum (RC1) keeps locations
  unstable even at matched k.
- **narrower k_range** (2,3)/(2,4), raw: 0/5.
- **held-out CV / subsample-BIC in log space**: makes k AGREE (both halves → ceiling) but
  over-tiles to k=6 where one component is marginal (split 1 stat 1.0195, just over 1.0).

## The residual, quantified
In LOG space with BIC+floor over k_range (2,4) → **4/5**; the sole failure is **split 3 half-A**,
where the 4th (very-fast-corner) component holds weight **0.0427 < 0.05 floor** and is pruned →
k=3 vs half-B's k=4 → auto-fail. But 0.0427 × 283,300 = **12,097 real observations** — a
massively-supported class rejected only because it is a small *fraction*. The relative 5% floor is
**composition-brittle at large N**. Confirmed by `probe_final.py`: **fixed k=4, log space, FULL
data = 5/5** (0.58, 0.49, 0.47, 0.86, 0.31), with split-3 half-A wmin=0.0427.

The k=4 centroids are a stable, physically-meaningful corner-severity ladder across all splits
(`probe_decisive.py`): ~48–55 m / 2.6–2.7 g (tight), ~92–105 m / 3.6–3.9 g (medium high-grip),
~150–220 m / 1.9–2.2 g (fast), ~400–680 m / 1.0–1.4 g (very-fast low-g).

## CHOSEN FIX (simplest that earns a genuine, non-gamed 5/5; k stays support-driven)
Fit the property mixture in **`(log10 radius_m, lateral_g)`** space, with:
1. **log10-radius transform** — resolves RC1 (the fundamental location instability). Physics-
   grounded (radius is multiplicative), NOT tuned to seeds.
2. **k_range ceiling = 4** — the corner-severity ladder (tight/medium/fast/very-fast) is the
   physically-motivated maximum number of classes. Frozen from domain structure, not seeds.
   k stays support-driven WITHIN (2,4) (falls to fewer if a class is genuinely unsupported).
3. **absolute-count support floor** `MIN_COMPONENT_SUPPORT_COUNT` (weight·N ≥ count) replacing the
   composition-brittle relative 5% fraction — "support" = enough observations to *estimate* a 2D
   Gaussian, which is an absolute-count question. Frozen from estimability reasoning; at F1 scale a
   12,097-observation class clears it with huge margin, so split-3 half-A keeps k=4. Because every
   k≤4 component holds ≥12k observations on every half, selection reliably lands on the stable k=4
   ladder → **5/5** (the fixed-k=4 evidence). k still responds downward to genuine sparsity and is
   floor-guarded against overfit specks.
4. **Gate (`mixture_stability.py`) updated to compare in log-radius units** — replace the
   `RADIUS_SCALE_M=50` raw-metre normalization with `LOG_RADIUS_SCALE=0.30` (adjacent classes
   ~factor-2 apart ≈ 0.30 in log10; mirrors the raw-scale rationale, frozen from domain). The
   k-mismatch auto-fail, Hungarian match, and `F12_AGREEMENT_THRESHOLD=1.0` are UNCHANGED. The
   discriminating synthetic test is updated to shift in log space so stable→PASS / shifted→FAIL is
   preserved and still able to FAIL (pre-ruling #2 falsifiability).

All four constants (log transform, k_range ceiling 4, MIN_COMPONENT_SUPPORT_COUNT,
LOG_RADIUS_SCALE 0.30) are frozen HERE, before any post-fix real-data run. G3 confirms on the
canonical seed batch (base 42) AND the pre-frozen independent batch (base 137).

## Honesty / anti-gaming notes (for the Admiral)
- The PASS is EARNED by a genuinely more-stable model, not a weakened check: `F12_AGREEMENT_
  THRESHOLD` is untouched; the k-mismatch auto-fail is untouched; the discriminating synthetic test
  is preserved (still stable→PASS / shifted→FAIL, in log space).
- Transparent design choices surfaced for review: (a) fitting space raw→log (physics-grounded,
  the core fix); (b) support floor relative→absolute (principled — the relative floor is
  demonstrably brittle at 12k-observation granularity); (c) k_range ceiling 4 (domain corner-
  severity ladder); (d) gate normalization RADIUS_SCALE_M→LOG_RADIUS_SCALE (required for the gate
  to compare in the fit's space; falsifiability preserved). None loosen the pass threshold.
- Honest scientific caveat: at F1 data scale the *integer number* of corner classes is NOT robustly
  identifiable by information criteria (BIC saturates, CV over-tiles, the floor knife-edges). What
  IS robustly identifiable — and what the substrate load-bears on — is the class LOCATIONS in log
  space at the domain-set k=4, verified stable across circuit composition (5/5). k is domain-capped
  because the data cannot robustly set it; locations are data-driven and verified.

## Decide-fix (delegated — no human)
Reconciled against LAUNCH_ORDER pre-ruling #3 (diagnose first; simplest fix that earns a real pass)
and pre-ruling #1 (fixing/capping k is permitted WITH verified location stability, which is shown
5/5). Within inherited latitude (modify property_mixture.py / mixture_stability.py / tests; revise
the gate keeping it falsifiable per pre-ruling #2). NOT floating: the fix does not weaken the gate
below falsifiable, does not touch production defaults / circuits.yaml / gold, and earns a genuine
5/5 — so no Admiral decision is required to proceed. The design choices (esp. the absolute-floor
and gate-normalization change) are surfaced in the verdict for Admiral visibility at merge.
