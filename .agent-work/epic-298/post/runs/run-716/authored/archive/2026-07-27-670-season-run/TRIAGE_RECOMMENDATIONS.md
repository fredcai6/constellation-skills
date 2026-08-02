# #670 Triage recommendations (5 candidates)

Delegated run: LAUNCH_ORDER-670 out-of-scope excludes Build-2/3 work and MAKING the allocation decisions, and
did NOT grant autonomous issue-filing latitude. Per delegated-triage doctrine, follow-ons are **recommend-and-defer**
(the deferral is recorded; the Admiral/owner decides filing). One candidate was resolved in-run.

---

## tc1 — consume vocabulary_divergent / vocabulary_guard.flagged_rounds downstream
- **Labels:** missing-consumer / bug-risk (detective guard left unread)
- **What:** the season runner's vocabulary guard is DETECTIVE (flags divergent-taxonomy rounds in season_results.json); downstream (G3/G5) must actually READ + surface flagged rounds, not leave them in JSON.
- **Disposition: FIXED-NOW (addressed in the season report).** The G5 report §1 surfaces the vocabulary-guard result explicitly ("Vocabulary guard: 0 divergent rounds"); the panel/diagnostic consume the covered-round set. This run had 0 flagged rounds, but the consumer path is honored. No separate issue needed.

## tc2 — rotating-block adjacent-partition correlation sensitivity
- **Labels:** research-hardening
- **What:** the K=n/2 rotating-block windows overlap (adjacent partitions correlated); worth a sensitivity check vs a wider deterministic balanced-partition family to confirm the averaged replication r is not artificially stabilized.
- **Importance:** low-moderate (the scheme is Admiral-endorsed as a read-adapter; this hardens confidence in the replication sizing).
- **Acceptance:** compare averaged r under the rotating-block family vs an alternative deterministic balanced family; report divergence.
- **Disposition: RECOMMEND-AND-DEFER** — no issue-filing authority this run; route to Admiral/owner.

## tc3 — export #668 private aggregation helpers for reuse
- **Labels:** cleanup / tooling / dependency-cleanup
- **What:** `run_season_panel_670.py` duplicates a few `instrument_panel_668_report.py` private helpers rather than importing them; export them to remove the duplication.
- **Importance:** low (maintenance).
- **Acceptance:** the corpus panel imports the shared helpers; no behavior change; tests still pass.
- **Disposition: RECOMMEND-AND-DEFER** (ineligible for fix-now: touches the committed #668 script, a reconcile-adjacent change; not this run's scope).

## tc4 — #666/#700 σ-calibration of the grip-term contribution
- **Labels:** research-hardening / performance-of-metric (ties to FOR-OWNER Decision 3)
- **What:** the landed #666 fit's predictive σ folds in `g_sigma_onesided` (~1e9, 20% of rows >1e6), inflating the held-out log-score to vacuity (coverage 1.0) and over-covering the panel calibration. Calibrate the grip-term contribution so the probabilistic score becomes informative.
- **Importance:** HIGH — it is the lever that makes the driver-term diagnostic informative; directly feeds owner Decision 3 (reference-lap/σ work before fingerprint work).
- **Acceptance:** predictive σ no longer dominated by the grip term; held-out log-score discriminates arms; panel coverage approaches nominal.
- **Disposition: RECOMMEND-AND-DEFER** — surfaced to the owner as evidence in the report FOR-OWNER block; filing is the owner's.

## tc5 — multi-season held-out variant to re-test whole-driver-term value
- **Labels:** research-hardening (ties to FOR-OWNER Decisions 1 & 2)
- **What:** the whole-driver-term value was thin/near-null vs the golf null on the bounded 2023 slice; re-test with deeper prior history per held-out weekend (multiple seasons) before allocating join weight to the driver axis.
- **Importance:** HIGH — determines whether the driver axis earns join weight (Decision 2) and Build-2 effort (Decision 1).
- **Acceptance:** the diagnostic runs over a multi-season slice with strictly-pre cutoffs; driver-term value re-sized against the golf null.
- **Disposition: RECOMMEND-AND-DEFER** — depends on backfill (out of scope per the launch order) + owner allocation decisions; route to Admiral/owner.
