# notes-667 — the join (#667, epic #659 Wave 4a)

Working notes. NOT a report file. Fenced per LAUNCH_ORDER-667 (staged under
`.agent-work/`, never committed on the branch).

## Problem statement (reconciled against LAUNCH_ORDER-667 + DESIGN_SPEC §4/T7)

Build **the join**: compose the car-reference circuit fingerprint (#664) with the
driver-utilization fingerprint (#666) into a per-weekend, **quali-side** prediction prior,
for **both channels** (utilization/time-deficit AND energy), symmetric.

For each (driver, channel):

    prior = Σ_class  weight[class] × cell_mean[driver, class]

soft-membership-weighted, with **honest Student-t σ propagated** through the weighted
linear combination (thin cells → fat σ dominates). THE LINEAR JOIN *IS* THE PRIOR — no
sequence/bespoke/interaction escalation (that is #670).

### Inputs (consume as-is; do NOT re-derive)
- **Circuit per-class TIME-share composition** ← #664 `ReferenceUtilizationStore.get(...)`
  field-reference row: `ReferenceLapProduct.fingerprint` ({class_id: time_share}) +
  `.class_ids` order. **Sums to the CORNER share, NOT 1.0** (straights excluded — the
  confounded-negative-control ruling). Do NOT renormalize the composition to 1.0.
- **Fingerprint cells** ← #666 `DriverFingerprintStore.get_fingerprint(driver, era,
  vocabulary, channel, what_measure)` → exactly `k` `FingerprintCell`s in
  `vocabulary.class_ids` order; each carries (mean, sigma, support_n, status
  resolved/unresolved). Unresolved ⇒ mean=None, sigma=None. G's one-sided σ⁺ is already
  folded into cell σ — NO separate G handling at the join.
- **Student-t seam** ← `src/common/student_t.py` `predictive_t(mu, sigma, n_eff, nu_loss,
  rule)` → `PredictiveT`. Project ν default `DEFAULT_NU_LOSS=4.0`, `FormulaRule` tail rule.
- **Frozen constants** ← consume `FINGERPRINT_FROZEN` (#666) / layer2 `frozen_constants`
  (#660). Mint NO new literals; a needed-unfrozen threshold is a FLOAT to the Admiral.

### The 4 GATING invariants (spec T7 — the correctness gate; unit-test exactly)
1. **Uniform composition across classes ⇒ join returns exactly the driver-overall mean.**
2. **All cells identical ⇒ join returns that constant, regardless of the composition vector.**
3. **Single-class circuit ⇒ σ propagation collapses to that cell's σ.**
4. **Soft memberships flow through unchanged; composition sums to the corner share, not 1.0.**

### Load-bearing reconciliation — the join is a NORMALIZED weighted average (forced, not chosen)
Invariant 1 ("uniform composition ⇒ **exactly** the driver-overall mean") is an identity
ONLY if the weights applied to the cell means are the **normalized** soft memberships
`w_i = comp_i / Σ comp`. Proof: uniform comp `c_i = a` (Σ = corner share S = ka < 1) →
`w_i = 1/k` → prior = mean(cells) = driver-overall mean. An UN-normalized sum
`Σ c_i m_i = a·Σ m_i = S·mean(cells) ≠ mean(cells)` (since S≠1) would FAIL invariant 1.
So the normalized-weighted-average form is **forced by the spec's own gating invariant**,
not a free design choice. "Do not renormalize" (invariant 4 / pre-ruling) governs the
INPUT composition vector — it is consumed as-is, its corner-share sum preserved and
surfaced as provenance (distance-vs-time-share flag) — NOT the weighted-average
normalization, which is just how a weighted mean is formed. @grade: settled/inherited
(forced by DESIGN_SPEC line 132 + T7).

Invariants 2 & 3 also hold under the normalized-average form:
- (2) m_i = m ⇒ Σ w_i m = m·Σw_i = m (Σw_i = 1), any comp.
- (3) single nonzero class j ⇒ w_j = 1 ⇒ prior_mean = m_j, prior_var = w_j²σ_j² = σ_j².

### σ propagation (design choice — to settle in plan)
Independent-cell linear propagation: `prior_var = Σ w_i² σ_i²`, wrapped into a
`PredictiveT` via `predictive_t` with an honest combined `n_eff` (thin cell ⇒ small n_eff
⇒ fat tail). Exact `n_eff` combination + unresolved-cell fallback (mean+fat σ) are the two
open design points for the design-it-twice at plan.

### Thin/unresolved exposure — surfaced, never silently discounted (spec §4 line 93)
Output must carry `thin_classes` (classes leaning on unresolved/thin cells) and
`weight_on_thin` (their summed normalized weight). Thinness priced ONCE at fit time (σ
widening on resolved cells); the join propagates honestly and never re-filters.

### Constraints preserved
- **Pre-quali / as_of_round.** `fit_driver_fingerprints(..., as_of_round=...)` already
  applies the strictly-pre cutoff (`round_idx <= as_of_round`) at FIT time; cells in the
  store are already strictly-pre. The store key carries NO round, so the join cannot
  independently re-verify a cell's fit cutoff — the join accepts `as_of_round` for
  provenance and the season-capable orchestration is responsible for having built the
  store slice under that cutoff. (Map-impact / possible triage note.)
- **Consumer boundary.** The join is for the practice-update + fusion summaries ONLY;
  the race sim + instrument panel (#668) read un-aggregated cells directly — leave the
  cell store's direct-read API untouched.
- **Vocabulary version pinned** on every cross-boundary call; refuse a mismatch loudly.
- Both channels symmetric; own-DB (#632); no DB-blob commits; map fence.

### Scope
Build season-CAPABLE; validate on the BOUNDED slice (2023-Q, Monaco/Spain/GB/Belgium,
VER/PER/LEC/SAI, k=4), offline, reading #664 reference-lap time-shares + #666 fingerprint
store. NO full-season run (#670, HITL). Whether the join BEATS driver-overall is #670
(out of scope).

### Genuine gaps considered — none require an Admiral float at understand
- Unresolved-cell arithmetic + n_eff combination: design choices WITHIN latitude (lowest
  dimensionality, honest σ) — settle via design-it-twice at plan. If the fat-σ for a
  fully-unresolved cell needs a NEW frozen literal, that is an F12 FLOAT to the Admiral —
  will confirm at plan whether an existing constant suffices before minting.

## Plan-time rigor (design-it-twice + cold critic)

**Design-it-twice (σ propagation — the one load-bearing choice):** MIN (independent-cell
quadrature) vs PRINCIPLED (per-cell PredictiveT + Welch–Satterthwaite df). Converged to MIN
(lowest dimensionality, ruling 4); PRINCIPLED named as the untaken road (interface leaves room
to swap). Single-author in-context (bounded interface) — panel not warranted, surfaced as the
named choice.

**Cold plan critic (single critic — bounded single-module, not architecture-touching; surfaced
choice):** returned 1 BLOCKER + 3 MAJOR + 3 MINOR, ALL valid, ALL applied pre-freeze within
latitude (no new frozen literal):
- BLOCKER: MIN capped unresolved σ at max_resolved_σ and left nu on resolved support ⇒ an
  UNKNOWN class could not fatten the tail (defeats the honest-σ point). FIXED: σ_unres ≥
  cross-class mean-spread (can exceed resolved σ); n_eff folds in (1−weight_on_thin) so the
  tail fattens; quadrature combination pinned.
- MAJOR: "PLUS" ambiguous ⇒ pinned QUADRATURE.
- MAJOR: all 4 T7 cases degenerate ⇒ a comp↔cell mis-pairing/sign/ordering bug survives them.
  FIXED: added T7-5 non-degenerate general case (distinct shares × distinct means, hand-computed
  Σ w_i m_i, asserts a wrong normalization gives a different number).
- MAJOR: T7-1 comparator ⇒ documented driver-overall = UNWEIGHTED mean of the k cells at the
  pure-join level (distinct from the fit-hierarchy support-weighted driver-overall).
- MINORs: n_eff threshold ⇒ replaced with weight-aware effective count 1/Σ(w²/support) (no magic
  cutoff); thin test asserts numeric σ-widening now, not just metadata; independent-cell
  correlation assumption stated honestly in the docstring.

## Triage candidates (surface at triage step)
1. **#670 baseline consistency:** the join-level driver-overall (unweighted k-cell mean) differs
   from the fit-hierarchy driver-overall (pool.grand_mean + team_effect, support-weighted). #670's
   "join beats driver-overall" diagnostic must fix a single documented baseline to avoid inheriting
   this mismatch.
2. **Correlation-aware σ upgrade:** Build-1 propagates σ as independent cells (Var=Σw²σ²,
   ~1/√k shrink, ignores intra-driver cross-class correlation). A later issue could carry a
   correlation floor / covariance-bearing propagation behind the same interface.
3. **Join as_of_round provenance:** the fingerprint store records no per-cell fit cutoff, so the
   join carries as_of_round for provenance but cannot independently re-verify a cell's strictly-pre
   status. A cutoff-stamp on stored cells would let the join enforce, not just document, the pre-quali
   guarantee.

## g3 — honest-σ report on the real bounded slice (path A: GB-real + synthetic)

**Scope:** validated on the only real #664/#666 slice on disk — Great Britain 2023-Q (VER/PER/LEC/SAI,
k=4 severity classes), read offline from the archived #664 reference_utilization_run.db. Monaco/Spain/
Belgium are absent (their reference_laps rows were never built); the harness skipped them cleanly and
is season-ready for them (see triage). The 4 T7 invariants (the correctness gate) are proven
synthetically, deterministically, independent of any slice.

### The 4 T7 gating invariants + T7-5 (each pass/fail on pinned 3.14)
- T7-1 uniform composition ⇒ driver-overall (unweighted k-cell) mean — `test_t7_1_...` **PASS**
- T7-2 identical cells ⇒ that constant for any composition — `test_t7_2_...` **PASS**
- T7-3 single-class circuit ⇒ σ collapses to that cell's σ, mean = that cell — `test_t7_3_...` **PASS**
- T7-4 soft memberships unchanged; corner_share = Σ shares ≠ 1.0 — `test_t7_4_...` **PASS**
- T7-5 non-degenerate general case (distinct shares × distinct means, hand-computed Σw·m; ÷k and
  renormalize-to-1.0 bugs give different numbers) — `test_t7_5_...` **PASS**
- σ thin-widening (a class flipped unresolved ⇒ STRICTLY wider) **PASS**; σ monotonicity **PASS**;
  thin surfacing **PASS**; both-channels symmetric **PASS**; 6 loud refusals **PASS**; fully-thin **PASS**.
  Full suite: **18/18** (reviewer + commander both reproduced independently).

### Real GB honest-σ behavior (as_of_round=12, both channels — MEASURED, not dressed up)
corner_share = **0.4217** for every prior (the CORNER share — straight 0.445 + braking_zone 0.133
excluded — NOT renormalized to 1.0). All 4 severity cells resolve at this cutoff, so weight_on_thin=0.

| driver | channel     | corner_share | mean  | scale | nu  | weight_on_thin |
|--------|-------------|--------------|-------|-------|-----|----------------|
| VER    | utilization | 0.4217       | 2.693 | 1.368 | 4.0 | 0.00 |
| PER    | utilization | 0.4217       | 2.916 | 1.368 | 4.0 | 0.00 |
| LEC    | utilization | 0.4217       | 2.839 | 1.368 | 4.0 | 0.00 |
| SAI    | utilization | 0.4217       | 2.846 | 1.368 | 4.0 | 0.00 |
| VER    | energy      | 0.4217       | 0.199 | 0.090 | 4.0 | 0.00 |
| (PER/LEC/SAI energy ≈ 0.199–0.200, scale 0.090) | | | | | |

Both channels join symmetrically (identical machinery; different cell values). nu rides the
aleatoric floor DEFAULT_NU_LOSS=4.0 (data-rich after the season-pooled fit).

### Thin / fat-σ behavior — surfaced, honest
- **Thin-but-resolved:** c1 (severity:2023:v1:c1) is the thin cell — support ~**3.56** vs a much
  larger c0 — surfaced in `thin_resolved_cells_near_floor` for all 8 driver×channel priors. At
  as_of_round=12 (GB round 10 in cutoff) it clears the 1.0 unresolved floor, so it is resolved and
  weight_on_thin=0: a MEASURED outcome (matches #666's own bounded-validation finding), not a gap.
- **Fully-thin path (real data):** at as_of_round=9 (before GB's round 10, so ZERO in-cutoff data)
  all 8 priors are `fully_thin=True` — prior=None, mean=None, weight_on_thin=1.0, thin_classes=all 4.
  The loud honest absence, never a fabricated value.
- **Partial-unresolved fat-σ-dominates path** (weight_on_thin strictly between 0 and 1, σ_unres
  widening the prior beyond resolved dispersion) is proven by the g1 synthetic numeric thin-widening
  test — GB-only real data does not present a clean intermediate cutoff for it (GB is a single round).

### Both-channels-symmetric confirmation
CONFIRMED: the join runs identically for channel="utilization" and channel="energy" (g1
`test_both_channels_symmetric` + the 8 real GB priors span both channels with the same machinery).

### Map impact (fence respected — prose only, for the epic CLOSEOUT cartographer reconcile)
- NEW leaf `src/physics/fingerprint/join.py` (pure `join_weekend_prior` + `WeekendUtilizationPrior`)
  under the physics region — a new capability node `weekend-utilization-prior` composing #664
  reference_laps composition × #666 fingerprint cells. Consumer boundary: practice-update + fusion
  summaries only; the race sim + #668 panel read un-aggregated cells directly (unchanged).
- NEW `scripts/join_bounded_validation_667.py` + `tests/.../test_join_bounded_validation.py`.
- physics.md packet predates the #660–#666 fingerprint subtree; the join is another new leaf for the
  single epic-closeout reconcile. NO docs/architecture/* edits made (fence).

## g3 addendum — c1-UNRESOLVED demonstration (per Admiral binding conditions, ruling A)

**Admiral ruling A (2026-07-26):** accept GB-real + the synthetic invariants as the #667 validation
gate; decline path B (3-circuit regen = Admiral-owned long-compute, duplicates #670's season regen,
exercises no new code path). Binding conditions honored below. Cited rationale: the 4 T7 invariants are
the circuit-independent correctness gate; the real slice's job is honest σ + thin-cell surfacing, which
GB delivers.

**Condition 1 — c1 surfaced in thin_classes/weight_on_thin with fat σ, BOTH channels, symmetric.**
The strongest honest demonstration (condition 2, "at a cutoff where c1 is unresolved") IS reachable on
GB-only real data: as GB's single round-10 observation ages past the recency half-life (5 rounds), c1's
recency-weighted support decays below the 1.0 unresolved floor while the thick c0 stays resolved.
At **as_of_round=22** (a natural end-of-2023-season cutoff; 2023 = 22 rounds) all 8 priors
(VER/PER/LEC/SAI × utilization/energy) show:

| driver | channel     | mean  | scale | nu  | weight_on_thin | thin_classes |
|--------|-------------|-------|-------|-----|----------------|--------------|
| VER    | utilization | 2.651 | 1.524 | 4.0 | 0.0079         | [c1] |
| VER    | energy      | 0.200 | 0.097 | 4.0 | 0.0079         | [c1] |
| PER/LEC/SAI | (both)  | ...   | 1.524 / 0.097 | 4.0 | 0.0079     | [c1] |

- c1 is UNRESOLVED and surfaced in `thin_classes` with `weight_on_thin=0.0079` (= its normalized corner
  weight 0.0033/0.4217) — **identical on both channels ⇒ symmetric** (the fat-σ / thin-surfacing path
  is channel-agnostic, exactly as the join is built).
- **Fat σ dominates:** scale WIDENS vs the all-resolved round-12 baseline — utilization 1.368 → **1.524**
  (+11.4%), energy 0.090 → **0.097** (+7.8%) — the σ_unres = max(cross-class-mean-spread, max_resolved_σ)
  term doing real work. The unresolved class widens, never caps, the prior.

**Condition 2 — strictly-pre causal cutoff preserved.** Validated at as_of_round=22: the fit reads only
`round_idx <= 22`, and GB's sole observation is round 10 (<= 22) — no cell past the cutoff is ever read
(owner ruling #3, pre-quali, no leakage). The three cutoffs shown span the honest range: round 12
(all-resolved, c1 thin-but-resolved), round 22 (c1 unresolved via decay, c0 resolved — the partial fat-σ
path), round 9 (fully-thin, prior=None — before GB's round exists at all).

**Condition 3 — the 3-circuit gap, EXPLICITLY routed to #670.** Monaco/Spain/Belgium reference_laps +
observables are NOT on disk (#666 fp_slice swept at closeout; #664 ran GB-only). Cross-circuit breadth —
including the multi-circuit early-cutoff case where c1 is unresolved because a DIFFERENT circuit
(Monaco R6 / Spain R7) supplies c0/c2/c3 support — is #670's season-scale diagnostic, explicitly OUT of
#667 scope. The join + harness are season-ready for those circuits the moment their rows exist. Routed to
**#670** (Admiral is filing the triage note in parallel). This is a documented scope boundary, not a
silent gap.
