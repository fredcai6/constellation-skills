# Implementation Result — g4-implement (GATING acceptance evidence, issue #663)

## Assigned gate
`g4-implement` — held-out cross-session reconciliation harness proving (or honestly
disproving) that subtracting grip baseline G improves cross-session pace reconciliation.

## Return status
`complete` — harness built, driven through the engine to done, real numbers produced.
**Scientific outcome: measured NEGATIVE (Honest-Null Clause) — subtracting G does NOT
improve, it WORSENS, held-out cross-session reconciliation on 2023 practice data.**
This is a complete, valid, reported deliverable, not a defect hidden.

## Completed slice
New real-data evaluation harness `tests/unit/physics/layer2/test_grip_heldout.py` that,
per weekend session pair: splits the field 50/50 stratified-by-team (fixed seed 663,
disjoint asserted), fits G on the FIT-set drivers' laps only via the lap-frame seam
`fit_grip_baseline_from_laps`, stores it, then for the HELD-OUT drivers measures raw
cross-session pace reconciliation BEFORE vs AFTER subtracting each session's own G (via
`get_grip_at`). Exits 0 regardless of scientific outcome; prints the numbers and writes
`.agent-work/663-grip-g/g4-heldout-results.json`.

## Scope
**Files changed:**
- `tests/unit/physics/layer2/test_grip_heldout.py` (new; `git check-ignore` exit 1 → committable)
- `.agent-work/663-grip-g/g4-heldout-results.json` (new; local-only, untracked, NOT staged)
- `.agent-work/663-grip-g/g4-implement-plan.json` (engine plan, local-only)

**Specific exclusions touched:** `no` — `grip_baseline.py`, `grip_store.py`,
`grip_batch.py`, `tyre_supplant.py` all read-only/imported, never modified. g5 synthetic
gate not built.

## EXACT scope run (stated — NOT full-season; Budget latitude)
4 contrasting DRY circuits, one weekend session pair each, all `session_type` FP (dry,
rain flag 0 on every session used):

| circuit | pair | contrast | held-out cells |
|---|---|---|---|
| Monaco | FP2/FP3 | street / low-speed / high track-evolution | 10 |
| Spain (Barcelona) | FP1/FP2 | permanent / technical-aero | 15 |
| Netherlands (Zandvoort) | FP1/FP2 | permanent / banked-technical | 5 |
| Saudi Arabia (Jeddah) | FP1/FP2 | high-speed street | 7 |

DB: `C:/Programs/f1Brainz/data/f1_data_2023.db` (main checkout), path passed explicitly,
read-only. Chosen because each has the richest same-driver/same-compound cross-session
overlap for its circuit type and is dry on both sessions. Total 37 pooled held-out cells.

## Split scheme actually used
Frozen default was "50/50 stratified by team, else random with fixed seed"
(`decision:heldout-split-axis` graded **guess**). Used the stratified default unchanged:
10 teams × 2 drivers → hold out exactly one driver per team (seeded shuffle, seed 663),
the other fits. Genuinely disjoint by construction, asserted in-test per circuit. No
adjustment needed — team data fully populated in `session_classifications.team`.

## The real before/after reconciliation numbers (load-bearing)

Truth-side pace = median of a driver's **fastest 3 clean laps** per compound (the
low-fuel push-run pace — the genuinely comparable fuel/wear state across two FP sessions).
`before = pace_A − pace_B`; `after = (pace_A − G_A) − (pace_B − G_B)`. RMS in seconds,
lower = better.

| circuit | cells | before | after (full G) | evo (curve only) | swap (neg ctrl) |
|---|---|---|---|---|---|
| Monaco FP2/FP3 | 10 | 0.803 | 3.489 | 5.258 | 4.611 |
| Spain FP1/FP2 | 15 | 4.327 | 10.906 | 26.243 | 11.430 |
| Netherlands FP1/FP2 | 5 | 2.253 | 4.298 | 9.681 | 5.594 |
| Saudi Arabia FP1/FP2 | 7 | 1.875 | 5.399 | 45.501 | 7.725 |

**AGGREGATE (37 held-out cells, 4 circuits):**
- before : RMS = **3.019** s (MAE 1.958)
- after (subtract full G, prescribed) : RMS = **7.715** s (MAE 6.213)
- after_evo (subtract curve component only) : RMS = 26.287 s (MAE 21.363)
- after_swap (neg. control, wrong-session G) : RMS = 8.615 s (MAE 7.276)
- **Subtracting G changes reconciliation RMS by +155.5%; 0/4 circuits improved.**

### Why (diagnosed, not mysterious)
Per-session saturating-curve fits are **structurally unidentified on practice data** — the
offset↔asymptote correlation is at or near the ±1 degeneracy wall and the fitted params
are physically absurd:

| circuit | sess | fit_status | offset (s) | asymptote | offset↔asy corr |
|---|---|---|---|---|---|
| Monaco | FP2 | ok | 93.20 | −107640.29 | **−1.000** |
| Spain | FP2 | ok | **101.99** | −18.29 | −0.750 |
| Netherlands | FP1 | ok | 88.15 | 35.51 (positive!) | 0.742 |
| Saudi Arabia | FP1 | ok | 70.84 | 42.44 (positive!) | **−0.999** |
| Saudi Arabia | FP2 | ok | **111.17** | −20.87 | 0.654 |

(offsets of 102/111 s on ~77–90 s circuits; positive asymptotes mean the curve claims pace
*rises* with rubber — backwards.) So `G_A − G_B` is dominated by fit degeneracy + the
fuel-laden, cross-session-incomparable absolute offset (swings of −4 to −17 s) rather than
the real ~0.5–2 s low-fuel track-evolution shift. Subtracting it over-corrects.

**Robustness of the null (scoped-nulls doctrine — what else I tested):**
- **Not a split artifact.** I re-ran the FULL-FIELD fit (all 20 drivers) for the same 8
  sessions: it is equally or MORE degenerate (Monaco FP3 offset = −386129 s, corr −1.000;
  Spain FP1 corr −0.991; Netherlands FP2 asymptote +8042). The degeneracy is **G-intrinsic
  to practice-session data**, not induced by the 50/50 held-out split. (Diagnostic run,
  not committed to the test.)
- **Not just an offset-frame artifact.** The evolution-only variant (subtract the curve
  component with the free offset removed) is *even worse* (26 s) — the curve *shape* itself
  is degenerate, so the null survives the "you subtracted incompatible absolute levels"
  objection.
- **Not a metric artifact.** An earlier all-lap / coarse-tyre-bin median gave a nonsense
  ~12–16 s before-RMS (Monaco traffic laps dragging 2-lap medians); the fastest-3 push-pace
  proxy gives a physical ~0.8 s Monaco / 3.0 s pooled before-RMS, independently reproduced
  by a standalone probe. The negative holds under the *correct* (low-noise) metric.

## Leakage / rank check result (load-bearing)
**Approach taken: leakage-avoidance by design (the handoff's sanctioned simplest route).**
The truth side runs **NO regression** — held-out pace is a raw median of fastest-N clean
laps, pure filter + median, no OLS, no design matrix, no `race_degradation_slopes`. There
is therefore nothing on the truth side that can be collinear with G's within-stint
tyre_life/fuel terms; the ONLY correction being tested is G itself. No rank check on a
truth-side regression is needed because there is no truth-side regression (stated
explicitly, per the handoff). Reviewer can confirm by inspection: no `lstsq` /
`race_degradation_slopes` on the held-out pace path.

Two further guards make the (negative) result falsifiable rather than machinery:
1. **Disjoint split asserted** every circuit — G is out-of-sample for every held-out driver.
2. **Swapped-correspondence negative control** — subtract each session's WRONG G (same
   machinery, A↔B correspondence broken). It HURTS more than `before` (8.62 > 3.02), which
   confirms `G_A − G_B` carries a real DIRECTIONAL signal (not random subtraction noise) —
   it is just badly over-sized/degenerate, so even the correct correspondence worsens
   reconciliation. A pure machinery-tautology would have made the improvement symmetric
   under the swap; it is not.

## Honest-null operationalization (verified)
Pytest asserts ONLY harness validity: harness ran ≥3 circuits with cells; every split
disjoint; every circuit numeric; a pooled `before_rms > 0` (non-vacuous gap to explain);
truth side regression-free; negative control computed. There is **no**
`assert after < before`. The scientific verdict is printed + written to JSON, never encoded
in the exit code. `pytest … -q -s` → **1 passed, exit 0** under the NEGATIVE result.

## Evidence (pasted)

```
$ py -m pytest tests/unit/physics/layer2/test_grip_heldout.py -q -s
circuit       pair    contrast                         cells  before   after     evo    swap
Monaco        FP2/FP3 street / low-speed / high track-evolution    10   0.803   3.489   5.258   4.611  [null]
Spain         FP1/FP2 permanent / technical-aero          15   4.327  10.906  26.243  11.430  [null]
Netherlands   FP1/FP2 permanent / banked-technical         5   2.253   4.298   9.681   5.594  [null]
Saudi Arabia  FP1/FP2 high-speed street                    7   1.875   5.399  45.501   7.725  [null]
AGGREGATE (pooled 37 held-out cells over 4 circuits):
    before    : RMS=  3.019  MAE=  1.958 s
    after     : RMS=  7.715  MAE=  6.213 s   (subtract full G, prescribed)
    after_evo : RMS= 26.287  MAE= 21.363 s   (subtract curve only)
    after_swap: RMS=  8.615  MAE=  7.276 s   (neg. control: wrong-session G)
    subtracting G changes reconciliation RMS by +155.5%  (0/4 circuits improved)
LEAKAGE/RANK CHECK: truth side regression-free (no OLS/lstsq ...); split disjoint every
    circuit (asserted); negative-control swap HURTS more than before -> DIRECTIONAL/real.
VERDICT: NULL: subtracting G does NOT improve (it worsens) held-out reconciliation
.
1 passed in 0.64s

$ py -m src.utils.simplification_limits --paths tests/unit/physics/layer2/test_grip_heldout.py
PASS (1 files checked)
```

Engine: plan `.agent-work/663-grip-g/g4-implement-plan.json` claimed → m0/m1/m2/m3 all
advanced → `current` = "DONE: no open items" → lease released (final journaled action).

## Assumptions used
- "Comparable fuel state" operationalized as the low-fuel push-run pace (median of fastest
  3 clean laps per driver/compound) — a well-defined comparable state present in both FP
  sessions, chosen after an all-lap/tyre-bin median proved swamped by traffic noise (~12 s
  vs ~0.8 s). Stated and justified in the file docstring.
- Residual fuel-load variation across different low-fuel runs is a small (~sub-second)
  residual confound, dwarfed by the multi-second G degeneracy; noted, not corrected.
- `_read_clean_session_laps` / `session_cumulative_track_laps_by_lap` / `_get_session_row`
  reused from `grip_baseline` (identical clean-lap filter, no reimplementation).

## Stop conditions hit
None. The DB had ample same-driver/same-compound cross-session laps (stop condition not
triggered). Runtime trivial (~0.65 s; targeted per-session curve fits, not `run_grip_batch`)
— no narrowing or OS-detach needed.

## Out-of-scope observations (triage candidates for Commander)
1. **G's saturating-curve fit is structurally unidentified on FP-session data**
   (offset↔asymptote corr ≈ ±1, physically absurd offsets/asymptotes), full-field AND
   split. This is the single most important finding: G as currently fit is **not usable as
   a cross-session subtractable baseline** on practice data. It is exactly the T2
   separability failure that `curve_offset_correlation` and the g5 gate target — g5 will
   likely also surface it. Candidate follow-ups: constrain the fit (bound the asymptote to
   a physical range, or fix/regularize `rate`), or restrict G to sessions with sufficient
   cumulative-track-laps spread to identify the curve, or fall back to a flat session
   offset when `|corr|` is near 1.
2. **`get_grip_at` returns an honest inflated sigma for these degenerate fits**, but this
   reconciliation subtracts only the point estimate `mu`. A sigma-weighted consumer would
   down-weight these degenerate corrections; the acceptance test as prescribed does not.
   Worth considering whether "subtract G" should be sigma-gated downstream.
3. The Race (`R`) session was not used for cross-session pairing (fuel/stint regime differs
   sharply from FP push laps); only FP-vs-FP pairs were tested. FP-vs-Q and involving R are
   untested variants.

## Map Impact
- **Structural anchors touched:** `struct:physics.layer2` — new test-only module
  `tests/unit/physics/layer2/test_grip_heldout.py`; no production module changed.
- **Capabilities affected:** G's held-out acceptance evidence — produced, result is
  NEGATIVE (subtracting G worsens held-out reconciliation on 2023 FP data).
- **Constraints honored:** `constraint:db-only-analysis` — read-only 2023 DB, explicit
  absolute path, no FastF1/Jolpica.
- **Decision anchors:** `decision:held-out-not-in-sample` honored (genuinely disjoint,
  out-of-sample split). `decision:heldout-split-axis` (guess) settled by running the real
  slice — the stratified 50/50 default worked, no adjustment.
- **Claims/evidence produced:** G's per-session curve is structurally unidentified on
  practice data (offset↔asy corr ≈ ±1), evidenced by the fit diagnostics AND the +155.5%
  reconciliation degradation; robust across full-field, curve-only, and negative-control
  variants.
- **Triage candidates:** the three above (esp. #1 — G fit identifiability).

## Workflow Feedback
- **Handoff gaps:** The handoff prescribed the before/after formula assuming G would be a
  clean subtractable level, but did not anticipate that G's fit is often **degenerate** on
  the very data the reconciliation runs on. It also didn't specify the "comparable fuel
  state" pace proxy concretely — the first defensible reading (tyre-age bins) produced a
  noise-swamped metric (~12 s) and had to be replaced with a fastest-N push-pace proxy.
  Naming a recommended pace proxy would have saved one iteration. Neither gap blocked the
  deliverable; both are recorded because I was the only one who saw them.
- **Context rediscovered:** That `fit_grip_baseline_from_laps` returns absurd offsets/
  asymptotes on thin-x FP data (the offset↔asy corr ≈ ±1 regime) — not surfaced in the
  handoff or anchors; discovered by inspecting fitted records. The g5 T2 diagnostic clearly
  exists for exactly this, so it's known upstream but wasn't carried into this handoff.
- **Instructions improvised around:** The "leakage/rank check must pass" assertion could be
  read as requiring a rank number; since I use no truth-side regression, I asserted the
  structural regression-free property + disjoint split + a falsifiable swap control instead,
  and stated so explicitly (the handoff's own "simplest way to avoid leakage entirely" text
  sanctions this).
- **What would have made this easier:** A one-line note in the handoff that G's fits may be
  ill-conditioned on practice data (so implementers expect and diagnose a possible negative
  rather than assume a harness bug), plus a suggested comparable-pace proxy.
