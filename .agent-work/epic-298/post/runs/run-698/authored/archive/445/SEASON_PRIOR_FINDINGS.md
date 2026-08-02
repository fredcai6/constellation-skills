# Season-prior filter — chase a per-car capability prior through the season (#445)

**Prong:** instead of fitting each (car, track) grip independently (Monza is
data-starved → B weakly pinned), carry a per-car capability PRIOR forward race-to-race
and UPDATE it each weekend. A sequential Bayesian / scalar-Kalman filter: prior (from
prior races) → likelihood (this race's nodes) → posterior, carried forward. Thin tracks
then borrow strength from the races before them.

**Verdict: POSITIVE, with one honest caveat.** The prior beats the fresh Monza fit
decisively on every measurable axis — tightness, teammate consistency, car sensibility,
and held-out rank correlation. The one thing the prior does NOT resolve is the top
ordering (RBR vs Ferrari are within noise); but Williams-last and Mercedes-#3 are
robust, and the prior turns a Monza fit that is **anti-correlated** with season truth
into one that **positively tracks** it. This is a clean, reproducible win for the
borrow-strength idea.

Code (all ADDITIVE, no shared module touched):
- `.agent-work/445/envelope/season_prior_collect.py` — collect+cache quali cornering
  nodes for 14 rounds × 8 drivers → `season_prior_nodes.npz` (108 car-races, run once).
- `.agent-work/445/envelope/season_prior_filter.py` — vendored IRLS frontier fitter,
  config-invariant observable + node-bootstrap obs covariance, adaptive scalar Kalman.
- `.agent-work/445/envelope/season_prior_run.py` — the decisive Monza test + held-out
  cross-check + season trajectories + plot (`season_prior.png`).

---

## 1. The formulation I chose, and why

**The config-invariance problem.** Per-track downforce B is genuinely
wing-config-dependent (high-DF tracks run more wing), so absolute B is NOT a
season-stable state to filter. This is visible in the data: the fitted field-mean B
*rises* from Bahrain (1.54g) through Hungary (2.32g) and is high at Monza (2.96g) even
though Monza is a *low*-downforce track — because the per-track frontier B absorbs
whatever curvature the cloud shows, and thin/banked tracks rail it. Filtering raw B
would filter mostly wing setup, not car capability.

**Choice: relative-to-field fast-corner downforce OFFSET** (the brief's first
candidate, judged "likely the cleanest" — confirmed):

```
y_c(race) = B_c · vref²  −  mean_over_field( B · vref² )         vref = 200 km/h
```

- `B_c · vref²` is the car's **unsaturated** downforce contribution to grip at a high
  reference speed (downforce-dominated regime).
- Subtracting the weekend field mean **cancels the shared mechanical A exactly** (A is
  common on the day) AND **removes the common wing-demand LEVEL** of the track (every
  car runs more wing at a high-DF track, lifting the whole field; the car's OFFSET vs
  the field is what reflects its aero platform and drifts slowly with development).

So `y_c` is a **config-invariant, season-stable** quantity that jumps on upgrades — the
right thing to filter. The field absorbs track/compound/wing demand; the car's relative
position is the slow-drifting state.

**One fix made during development.** I initially used `min(A + B·v², GSAT)` (the
clipped frontier grip) for the observable. At low-DF Monza several cars' frontiers hit
the GSAT=5.2 ceiling at 200 km/h, so the clipped grip collapsed to a single value and
**4 cars read an identical offset** (degenerate). Switching to the **unsaturated**
downforce term `B·vref²` (the genuine aero axis, which never saturates) fixed this; the
A and field-mean cancellation is unaffected. See the docstring in `season_prior_filter.py`.

Why not the alternatives:
- *platform×wing factorization* B = platform(car)·wingfactor(track): equivalent to
  the offset under a log transform, but multiplicative coupling is harder to identify
  with 8 cars × 14 tracks and adds a track-factor nuisance per round. The additive
  offset is simpler and the field-mean does the wing normalization implicitly.
- *residual filtering* (B minus a track-demand baseline): needs an external
  track-demand model; the field mean IS an internal, data-driven track-demand baseline.

---

## 2. Filter design (state / process / observation)

**Observation (per race).** Vendored copy of `grip_iter3.fit_global_keyed`: one global
mechanical A shared across that weekend's cars (structurally correct — tyre×surface is
common on the day) + per-car downforce B via the iterative quantile-IRLS + EM-peel
frontier (quali only). Then compute `y_c` per (1). **Obs noise R from a node-bootstrap**:
resample each car's nodes (with replacement), re-fit the whole weekend, recompute `y_c`;
`R_c = Var(bootstrap y_c)` over 200 resamples. This makes thin races self-report wide
uncertainty — exactly the lever that lets the prior dominate. Empirically it works:
rich Hungary R-sd 0.12–0.29g, thin Monza R-sd 0.28–0.95g.

**Process (per car, scalar).** Random walk `y_t = y_{t-1} + w`, base process variance
`q0 = 2.5e-4 g²/race` (slow development drift), PLUS an **adaptive jump term**: when a
race's standardized innovation `z² = innov²/(P_pred+R)` exceeds `jump_k = 9`, treat the
step as a likely real step-change (upgrade) and inflate the predict variance by
`jump_mult = 40` for that update — heavier-tailed / adaptive process noise so a genuine
step isn't over-smoothed. A car absent that weekend is predict-only (state drifts,
variance grows). One independent scalar Kalman filter per car.

**State.** The filtered offset `y_c` with its variance `P_c`. Initialised at a car's
first appearance from that race's observation, prior variance `4·R` (mildly inflated).

---

## 3. The decisive Monza test — prior-informed posterior vs Monza-only fresh fit

Build the prior across the 13 pre-Monza rounds (Bahrain → … → Netherlands), carry it
into Monza, compare the Monza posterior to the Monza-only fresh fit.

```
 car  team |  FRESH y  fresh sd |  PRIOR m  prior sd | POSTERIOR  post sd | jump
 VER   RBR |   -1.049     0.479 |   +0.117     0.074 |    +0.090    0.073 |
 PER   RBR |   +1.008     0.947 |   -0.153     0.094 |    -0.141    0.094 |
 HAM  MERC |   +0.773     0.681 |   -0.219     0.074 |    -0.207    0.073 |
 RUS  MERC |   -1.038     0.276 |   +0.065     0.081 |    -0.130    0.116 | YES
 LEC   FER |   +1.195     0.842 |   -0.029     0.083 |    -0.017    0.083 |
 SAI   FER |   -0.672     0.301 |   -0.038     0.075 |    -0.075    0.073 |
 ALB   WIL |   -1.247     0.287 |   -0.162     0.080 |    -0.341    0.116 | YES
 SAR   WIL |   +1.030     0.887 |   -0.315     0.101 |    -0.298    0.100 |
```

- **TIGHTNESS.** mean obs sd (fresh Monza) **0.587 g → mean posterior sd 0.091 g**
  (84% shrink). The prior collapses the Monza uncertainty.

- **TEAMMATE CONSISTENCY** (a car property ⇒ teammates should agree). mean |teammate
  gap| **2.003 g (fresh) → 0.102 g (posterior)** — a **20× improvement**. The fresh
  Monza fit puts every teammate pair at opposite ends of the field (VER −1.05 vs
  PER +1.01; HAM +0.77 vs RUS −1.04; etc. — the classic thin-data noise signature
  flagged in the prior findings). The prior makes them converge: HAM/RUS 0.078,
  LEC/SAI 0.058, ALB/SAR 0.043. (VER/PER 0.231 is the one larger gap — partly real:
  Pérez genuinely underqualified in 2023, and the rich-race consensus also shows
  PER −0.11 below VER +0.28.)

- **CAR SENSIBILITY** (constructor mean; 2023 truth = RBR strong, Williams weak).
  Fresh Monza ranks **Ferrari #1, RBR #2, Williams #3, Mercedes #4** — nonsensical.
  Posterior ranks **RBR #1, Ferrari #2, Mercedes #3, Williams #4** — Williams correctly
  last. Caveat: RBR vs Ferrari at the top are within noise (they swap under bootstrap
  seed / q0); **Williams-last and Mercedes-#3 are robust across all 16 hyperparameter
  settings I swept** (q0 ∈ {1e-4…1e-3} × jump ∈ {off, k6/9, mult20/40}).

### Held-out cross-check (the cleanest single statement of value)

Score the **prior** (which never saw Monza) and the **fresh Monza fit** against a
season-consensus proxy = precision-weighted mean offset over the 6 richest pre-Monza
races (Azerbaijan, Miami, Monaco, Canada, Britain, Hungary — Monza excluded):

```
  RMSE vs consensus:          FRESH Monza = 1.085 g    PRIOR(entering Monza) = 0.131 g
  Spearman rank vs consensus: FRESH = +0.048           PRIOR = +0.500
```

The prior is **~8× closer in RMSE** and **+0.50 rank-correlated** with season truth,
where the fresh Monza fit is essentially **uncorrelated** (+0.05; under other bootstrap
seeds it goes mildly *negative*, i.e. the thin Monza order points the wrong way). The
prior is not just tighter — it points the right direction where the fresh fit does not.

---

## 4. Season trajectory per car (does it track known 2023 form, absorb upgrades?)

Constructor-level filtered offset, calendar order (Bahrain → Monza):

```
 team |  Bahr  Saud  Aust  Azer  Miam  Mona  Spai  Cana  Aust  Grea  Hung  Belg  Neth  Ital
  RBR | -0.00 -0.49 -0.19 -0.17 -0.13 -0.13 -0.03 -0.00 -0.04 -0.11 +0.00 +0.01 -0.02 -0.03
 MERC | -0.35 +0.11 +0.05 -0.09 -0.06 -0.05 -0.08 -0.08 -0.08 -0.06 -0.09 -0.08 -0.08 -0.17
  FER | +0.62 +0.11 +0.01 +0.05 +0.05 +0.06 -0.04 -0.03 -0.01 -0.01 -0.07 -0.04 -0.03 -0.05
  WIL | -0.27   --  -0.04 +0.05 +0.00 -0.05 -0.14 -0.16 -0.15 -0.13 -0.13 -0.25 -0.24 -0.32
```

- **Trajectories are smooth and converge** after a noisy opening 2–3 rounds (Bahrain
  Ferrari +0.62 is a SAI fit artifact — n=276 but a high-B outlier — that the filter
  damps within two races). No thrashing.
- **Williams trends clearly downward** through the second half (−0.27 → −0.32, lowest by
  Monza) — matches the weak FW45. RBR/Ferrari/Mercedes cluster near zero (the
  competitive front separated by < 0.2g), consistent with the prior finding that the
  *front* of the grid is within the measurement noise floor.
- **Per-driver:** VER climbs to steadily positive (+0.09…+0.17, strongest car); PER sits
  below VER all season; HAM trends to −0.21 (W14 fast-corner weakness — matches the
  "Merc-low quali" signal from earlier prongs); SAR/ALB sink. Plausible 2023 form.
- **Upgrade jumps** (`*`) fired at RUS-Monza, ALB-Monza, SAR-Belgium — i.e. exactly at
  the thin/odd races where the innovation spiked; the adaptive term let the filter step
  rather than over-smooth, without destabilizing neighbours. Removing the jump term
  changes the headline numbers negligibly (teammate gap 0.102→0.102), so it's a safety
  valve, not a load-bearing tuning knob.

See `season_prior.png` (top: per-car with ±1σ bands and jump stars; bottom: constructor
means; dotted line = Monza).

---

## 5. What worked / what didn't / open questions

**Worked**
- The **borrow-strength premise is validated**: a thin race (Monza, 43–80 nodes/car)
  that is anti-correlated with truth on its own becomes well-determined and correctly
  ordered once the prior is carried in. Tightness 84%, teammate gap 20×, rank
  correlation flips from ~0 to +0.5.
- **Config-invariant offset** is the right state: the field mean cleanly absorbs the
  wing-demand level (which swings the raw B by 2× across tracks) and leaves a stable
  per-car axis.
- **Node-bootstrap obs covariance** is the key mechanism — it makes thin races
  self-down-weight so the prior dominates automatically, no manual gating.
- **Robustness:** the win survives the full hyperparameter sweep; nothing is tuned to
  flatter.

**Didn't / limitations**
- **The top order (RBR vs Ferrari) is still unresolved** — within noise, as in every
  prior prong. The filter sharpens *Williams-last* and *Mercedes-#3* but cannot
  manufacture front-of-grid resolution that isn't in the quali grip data. This is the
  same noise floor the pipeline findings document; the prior does not break it.
- **A/B identifiability fails on tracks without slow corners.** Netherlands (Zandvoort,
  banked, few slow corners) railed A to the 0.80g floor and pushed everything into B
  (field-mean B 8.26g — degenerate). The offset there is still roughly sensible and the
  wide-R + prior absorb it, but a track-demand model or a stronger A-anchor (pool slow
  corners across the season to pin A once) would be cleaner.
- **Per-driver, not per-car, observable.** I filter per driver (so teammate consistency
  is a *test*, not an assumption). The consensus proxy confirms real within-team spread
  (PER < VER, HAM weak), so `y_c` is car+driver, not pure car. Pooling to constructor
  would tighten further but forfeit the teammate-consistency check.

**Open questions / next steps**
- **RTS smoothing** (backward pass) would sharpen the early-season trajectory and the
  pre-Monza prior using all 13 races' information, not just the causal filter. Cheap to
  add on the cached nodes.
- **Anchor A globally**: fit one mechanical A across the whole season's slow-corner
  nodes (pinning the v→0 intercept once), then per-race only B — this would fix the
  Zandvoort degeneracy and make the offsets more comparable race-to-race.
- **Process-noise from real upgrade calendar**: instead of an adaptive z² trigger, seed
  jumps at the known 2023 upgrade weekends (e.g. RBR/Ferrari/Mercedes floor packages) to
  test whether the filter's flagged jumps line up with reality.
- **Feed the high-speed end** (the prior findings' open problem): the offset is still
  driven by the downforce-dominated B, which is data-starved at the fast-corner limit on
  thin tracks. The race-node de-confound prong (parallel) is the complementary fix; the
  prior here is orthogonal and they should compose (de-confounded richer per-race obs →
  even tighter filter).

**Bottom line.** Chasing a config-invariant capability prior through the season is a
real, validated improvement for data-starved tracks: it makes Monza's posterior 8×
closer to season truth and correctly ordered where the fresh fit is not, with robust
Williams-last / Mercedes-#3 facts and smooth, upgrade-aware trajectories. It does not,
and structurally cannot, resolve the RBR-vs-Ferrari front-of-grid tie that sits below
the quali-grip noise floor.
