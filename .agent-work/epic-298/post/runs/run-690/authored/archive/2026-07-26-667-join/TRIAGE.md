# Triage recommendations — #667 the join

Issue-filing authority: per the epic-659 LATITUDE_CONTRACT, issue file/close is **Admiral-delegated**
— cmdr-667 does NOT file directly. All candidates below are **recommend-and-defer**: issue-ready,
surfaced to the Admiral in the closeout report for filing. None clears the fix-now ladder (all are
follow-on design/upgrade work, not bounded-adjacent-verifiable-no-arch).

---
## TC-1 — #670 join-vs-driver-overall baseline consistency
- **Labels:** unresolved decision, research hardening
- **What:** The pure join's "driver-overall mean" (T7-1 comparator) is the UNWEIGHTED mean of the k
  cell means. The fit-hierarchy driver-overall (`pool.grand_mean + team_effect[driver]`) is a
  DIFFERENT, support-weighted quantity. #670's "does the join beat the driver-overall prior?"
  diagnostic must fix ONE documented baseline, or it inherits this mismatch and could mis-size the
  join's value.
- **Evidence:** cold-critic MAJOR (plan-time); `fingerprint_bounded_validation.py:117` uses the
  fit-hierarchy driver-overall; the join uses the unweighted-cell-mean form (join.py + T7-1 test).
- **Acceptance:** #670 states which driver-overall baseline it compares against and why; the two
  forms are reconciled or the choice is justified.
- **Out of scope for #667:** the join is correct at the unit level regardless; this is a #670 sizing concern.
- **Disposition:** recommend-and-defer (Admiral-delegated filing; target issue #670).

## TC-2 — correlation-aware σ propagation (Build-2+ upgrade)
- **Labels:** research hardening, architecture weakness (mild)
- **What:** Build-1 propagates σ as INDEPENDENT cells (`Var = Σ w²σ²`, ~1/√k shrink), ignoring
  intra-driver cross-class correlation (same driver, same session — almost certainly correlated).
  A correlated, tight-corner driver gets a mildly overconfident prior. A later issue could carry a
  covariance floor / correlation-bearing propagation behind the SAME `join_weekend_prior` interface
  (the PRINCIPLED per-cell-PredictiveT + Welch–Satterthwaite candidate was the design-it-twice
  untaken road).
- **Evidence:** cold-critic MINOR; stated honestly in `join.py` module docstring as a Build-1
  simplification (not over-claimed).
- **Acceptance:** a follow-on issue evaluates whether cross-class correlation materially changes the
  prior's calibration and, if so, swaps in a covariance-aware propagation behind the same interface.
- **Out of scope for #667:** ruling 4 (lowest dimensionality) — the independent form is the Build-1 choice.
- **Disposition:** recommend-and-defer.

## TC-3 — fingerprint-cell fit-cutoff stamp (enforce, not just document, strictly-pre)
- **Labels:** missing structural node, research hardening
- **What:** `DriverFingerprintStore` records no per-cell fit cutoff (`as_of_round`). The join carries
  `as_of_round` for provenance but cannot independently re-verify a cell's strictly-pre status — it
  trusts the orchestration to have built the store slice under the right cutoff. A cutoff stamp on
  stored cells would let the join (and any consumer) ENFORCE the pre-quali guarantee, not just
  document it.
- **Evidence:** `store.py` schema (key = driver/era/vocab/channel/what_measure, no round);
  `fit.py::fit_driver_fingerprints` applies the cutoff at fit time but does not persist it.
- **Acceptance:** a follow-on adds a fit-cutoff column to the fingerprint cell store (additive
  migration) and the join asserts `cell_cutoff <= as_of_round`.
- **Out of scope for #667:** the store schema is #666's; #667 consumes it as-is.
- **Disposition:** recommend-and-defer.

---
## Also surfaced (not a code triage candidate — a scope decision for the Admiral)
- **3-circuit bounded-slice regeneration:** Monaco/Spain/Belgium reference_laps+observables are not on
  disk (swept at #666 closeout / never built by #664, which ran GB-only). Path A (GB-real + synthetic)
  was finalized within latitude. If the Admiral wants the full 4-circuit validation (path B), the
  3 circuits need per-circuit SegmentMap+physics-ideal-lap regeneration (heavy telemetry compute,
  Admiral-owned per the long-compute doctrine). The harness is season-ready. Floated twice; awaiting
  any B-ruling, else this is the documented gap.
