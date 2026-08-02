# Triage Recommendation: Learned as-of feature→s_e head for the quali gap scale

## Classification
feature, research hardening

## Source checklist/artifact
- review finding (g2-review, engine triage_candidate tc1)
- evidence: `.agent-work/issue-391-quali-gap-scale/evidence/quali_gap_scale_numbers.json`

## Structural anchor
struct:evo (`src/evo_predictor/quali_gap_scale.py`)

## Cartographer mismatch class
none (future work, not a current-map defect)

## Problem
#391 shipped a quali gap-magnitude expression (`expected_gap_ij = s·(π_i−π_j)`) and chose its
prediction-time scale `ŝ_e` from cheap carry-forward heuristics. The OOS-2025 measurement is an
HONEST NULL: neither carry-forward variant beats a global-constant baseline, so the shipped
default `ŝ_e` is the global constant. But the label-side event-conditioned ceiling sits ~40%
below every prediction-time source, so substantial exploitable event-to-event spread structure
exists that no cheap carry-forward captures. A learned, as-of feature→`s_e` predictor could
close that headroom.

## Current truth
- `src/evo_predictor/quali_gap_scale.py` exposes `expected_gap_ij`/`expected_gaps` + three
  `ŝ_e` providers (CF1 carry-forward, CF2 same-circuit prior-year, global-constant baseline).
- Shipped default `ŝ_e` = global constant (median of train-pool quali `s_e`) — it won by OOS
  midfield gap-MAE.
- `s_e` is a post-event LABEL produced by `spread_target.py` (committed at
  `params/spread_target/<y>/<r>/quali.json`).
- No as-of feature→`s_e` map exists; it was explicitly DEFERRED from #391 as #375-shaped.

## Desired/future concern
A predictive head that estimates `s_e` from pre-event (as-of) features, wired so the quali mean
head expresses gaps with a feature-conditioned `ŝ_e` instead of the global constant — IF it
beats the global-constant baseline on OOS midfield gap-MAE.

## Evidence
- OOS-2025 midfield gap-MAE: event (label ceiling) 0.001949; cf1 0.003258; cf2 0.003825;
  global_const 0.003255 (`quali_gap_scale_numbers.json`).
- Honest-null: `cf1_beats_global_constant=false`, `cf2_beats_global_constant=false`.
- Quali `s_e` cross-event CV ≈ 0.80 (§9.5) — genuinely event-conditioned; the structure is real.
- Calibration: the `event` (label) source has slope ≈ 1.0 / r² ≈ 0.84; all prediction-time
  sources have slope < 0.77 / r² < 0.54 — the cheap sources are under-dispersed and noisy.

## Impact
This is the lever that would make the quali mean head's gap magnitude trustworthy enough for
#386 (Thrust B) to measure "excess flip risk beyond the gap" against a PREDICTIVE (not just
label) gap. Without it, the deployed gap scale is a single constant — correct on average but
blind to track/session structure.

## Suggested scope
- Define an as-of feature contract for `s_e` (pre-event features only; explicit as-of cutoff;
  no leakage of the event's own laps — the project's as-of discipline).
- Fit a bounded predictor (e.g. ridge / small GBM / a small head) of `s_e` from those features.
- Reuse the existing measurement harness (`scripts/diagnose_quali_gap_scale.py`) to score the
  learned `ŝ_e` against the global-constant baseline on OOS midfield gap-MAE.
- Honest-null clause applies: ship the learned head ONLY if it beats the baseline.

## Non-goals
- No pi-semantics change; no ordering/rank work (that is #375).
- No σ-floor/tail or disagreement_rate work (#386/#388/#389).
- No change to `spread_target.py`'s label derivation.

## Acceptance criteria
- [ ] As-of feature contract for quali `s_e` defined and documented (no same-event leakage).
- [ ] A bounded learned `ŝ_e` predictor fit on the train pool, evaluated OOS 2025.
- [ ] OOS midfield gap-MAE of the learned `ŝ_e` reported vs the global-constant baseline via the
      existing harness; ship-or-null decision recorded.
- [ ] If shipped: `quali_gap_scale.py`/its caller use the learned `ŝ_e` as the default, behind a
      default-preserving switch; ordering output byte-identical.

## Recommended priority
medium

**Reason:** Clear, measured ~40% headroom and a real downstream consumer (#386), but the honest
null means the current global-constant default is acceptable in the interim; not blocking.

## Related artifacts
- `docs/evo/prediction_ceiling_and_priorities.md` §9.6 (the deferral + measurement)
- `docs/architecture/packets/evo_predictor.md` (`quali_gap_scale.py` entry)
- `src/evo_predictor/quali_gap_scale.py`, `scripts/diagnose_quali_gap_scale.py`
- Related issues: #391 (this work), #375 (context-conditioned net step), #386 (Thrust B epic)

## Issue creation authority
create issue directly (project ground rule: autonomous issue creation for non-trivial tasks;
Admiral order: drive to DONE incl. the deferred feature→s_e head triage text)
