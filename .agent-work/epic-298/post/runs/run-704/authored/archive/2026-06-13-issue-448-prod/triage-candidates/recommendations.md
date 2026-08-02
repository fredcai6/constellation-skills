# Triage Recommendations — issue-448-prod

Three issue-ready recommendations. Per the spine triage step, these need human (Admiral) approval before filing.
The Commander did NOT file them; they are routed in the final return for the Admiral to approve each.

---

## TR-1 — Re-home the physics-characterization scripts against the new trajectory module
**Labels:** cleanup, tooling, dependency cleanup
**What:** Four scripts were validly deleted in #448 as orphans of the removed windowed/ribbon pathways:
`characterize_telemetry_instruments.py`, `characterize_timetag_jitter.py`, `create_physics_regression_fixtures.py`,
`run_regression_matrix.py`. They imported `trajectory_grading` loaders / `windowed_*` modules (all deleted). Their
*capability* — characterizing telemetry instrument noise / time-tag jitter and building physics regression fixtures —
may still be wanted; if so, re-home it against the new `src/preprocessing/trajectory/` loaders + smoother API.
**Importance:** Medium. The capability fed the #447 measurement-model characterization (σ_pos, jitter offset). It is
not lost data (evidence JSONs persist), but the regeneration scripts are gone.
**Evidence:** g3 removal verified all 4 imported deleted modules (g3-review-result.md, per-script grep). They are
cited as live commands in `docs/physics/measurement_model.md` (e.g. `py scripts/characterize_timetag_jitter.py`).
**Acceptance criteria:** Either (a) re-implement the needed characterization scripts against the new loaders/smoother
with a test, or (b) a documented decision that they are obsolete and the doc commands removed.
**Out of scope:** Re-running the full characterization; this is about the tooling, not new measurements.

---

## TR-2 — Validation-breadth follow-up for the windowless trajectory estimator
**Labels:** research hardening, missing test
**What:** #448 shipped the validated estimator + clean-race reproduction (2022 Spain R, 22.77 ms). Extend validation
to: wet sessions, more circuits, explicit pit/in-out-lap filtering robustness, and quali thin-n (the lab saw
47–63 ms on thin quali — small-n, not trajectory error). Explicitly OUT of scope for #448 per the issue + launch order.
**Importance:** Medium-High. The estimator is the Phase-1 input to the #449 force layer; breadth confidence matters
before downstream relies on it across conditions.
**Evidence:** Issue #448 "Done-when" + launch-order Honest-Null clause name this as a tracked follow-up. Lab E12
verdict: quali sessions 47–49 ms (thin-n). spain_reproduction evidence: race clears 22.77 ms.
**Acceptance criteria:** A committed multi-session validation (≥1 wet, ≥2 more dry circuits, quali) reporting held-out
sector residuals + held-out χ² per class, with a documented expected-range table; thin-n behavior characterized.
**Out of scope:** Changing the estimator (only validating it); new estimation theory.

---

## TR-3 — Reconcile docs/physics/measurement_model.md §9/10/11 to the trust-profile
**Labels:** missing doc, structure/constraint mismatch
**What:** The #447 Phase-1 measurement-model contract doc sections 9 (F1 covariance-band), 10 (F3 sector-anchor),
and 11 (traceability) still cite the now-deleted ribbon-grading machinery (`covariance_gate.py`, `sector_anchor.py`,
`cross_residual`) and the retired `trajectory_grading_report.md` v1.0 schema as the implementation context for those
recommendations. The trust-profile (`trajectory/grading.py` + `trajectory_trust_profile.md`) replaces pass/fail
grading, so the F1/F3 recommendations need re-expressing against the new module.
**Importance:** Medium. The contract recommendations are still valid in spirit but reference deleted files; left
as-is they are dead references in a committed physics-contract doc.
**Evidence:** Cartographer reconcile flagged 5 residual refs (lines 396–397, 416, 438, 441, 473, 514–515, 520).
g3 fixed only the footer dead-links.
**Acceptance criteria:** §9/10/11 reference the new `grading.py`/`calibration.py` + `trajectory_trust_profile.md`;
the F1 band + F3 anchor recommendations restated for the trust-profile (or marked superseded with a pointer).
**Out of scope:** Changing the obs-model contract numbers (σ, bands); this is a reference/structure reconciliation.
Crosses into #447/#449 contract territory — Admiral should decide whether to fold into #449 or file standalone.
