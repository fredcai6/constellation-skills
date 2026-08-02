# Triage Recommendations — issue #446 follow-ups

Six candidates surfaced during the run. None are in-scope for #446 (harness + strawman only).
Recommendation: the Admiral decides filing — tc1 and tc6 fold naturally into the **Phase 0b**
child of epic #445 (do NOT file as standalone), tc3/tc4/tc5 are small data/physics-region hygiene
items that can be one consolidated issue or folded into existing data-layer work. Filed nothing
autonomously (Commander under an Admiral-run epic; issue creation floated).

---

## tc1 — Anchor s_finish fixed at 0.0m reference
- **Labels:** research hardening, unresolved decision
- **What:** The sector-anchor gate fixes the start/finish anchor at s=0.0m as the arc-length
  reference and co-estimates s1/s2/s3. For circuits with an ambiguous start/finish loop position
  this may need to be a free parameter too.
- **Evidence:** `sector_anchor.py`; g1 implementer note + g1 review.
- **Acceptance:** Phase 0b decides whether s_finish stays fixed or becomes free; if free, the
  gate's identifiability (1 extra dof vs lap-closure) is checked.
- **Route:** FOLD INTO Phase 0b (anchor calibration is explicitly a 0b task). Not standalone.

## tc6 — Covariance gate band too loose (HEADLINE 0b input)
- **Labels:** research hardening, unresolved decision
- **What:** Gate (b) currently uses reduced-chi-square band [0.01, 100]; the strawman passes it in
  all 3 sessions despite chi-squares 0.60-11.14, so (b) does not yet discriminate. Tighten toward
  ~[0.5, 2.0] once the honest covariance model exists.
- **Evidence:** `.agent-work/issue-446/VERDICT.md`; g3 reports (chi-sq 11.14 / 3.07 / 0.60); g3 review confirmed.
- **Acceptance:** Phase 0b sets the band against a characterized error model so gate (b)
  discriminates honest from dishonest covariance.
- **Route:** FOLD INTO Phase 0b (this is the harness's primary feed into 0b's gate design). Not standalone.

## tc2 — scipy.optimize dependency in preprocessing
- **Labels:** dependency cleanup
- **What:** `trajectory_grading` introduces `scipy.optimize` (anchor co-estimation), consistent with
  existing `loess_bootstrap.py`/`spline_basis.py` scipy usage. Confirm scipy is an accepted
  preprocessing-region dependency / pin it.
- **Evidence:** `sector_anchor.py`; g1 triage note.
- **Acceptance:** scipy confirmed in deps (pyproject) or pinned; no action if already declared.
- **Route:** Small hygiene — fold into a data/physics-region cleanup issue or close if scipy is
  already a declared dep (likely; verify).

## tc3 — FastF1 pos_data decimetre convention undocumented
- **Labels:** missing doc
- **What:** FastF1 `pos_data` X/Y are in DECIMETRES (verified ratio ~10 vs FastF1 Distance);
  the 0.1→metres scale is currently only in `strawman_candidate.py`. Document the convention in
  physics/architecture docs so future estimators don't re-derive or mis-scale it.
- **Evidence:** g2 review (measured 6941.6m vs FastF1 6949.5m on Spa).
- **Acceptance:** decimetre convention + scale documented in a physics/preprocessing doc.
- **Route:** Small doc item — candidate for one consolidated data/physics hygiene issue.

## tc4 — GP-name divergence (DB 'Belgium' vs event 'Belgian Grand Prix')
- **Labels:** cleanup, dependency cleanup
- **What:** The runner needs a `gp_name_in_db` param because the DB GP name differs from the FastF1
  event name. A data-layer GP-name lookup/normalization table would remove per-call params.
- **Evidence:** g2 implementer + review.
- **Acceptance:** a single canonical GP-name normalization in the data layer; callers stop passing
  ad-hoc name overrides.
- **Route:** Data-region cleanup — fold into data-layer work or one consolidated hygiene issue.

## tc5 — offline_mode() version guard swallows on FastF1 < 3.0
- **Labels:** bug (latent), dependency cleanup
- **What:** The offline guard silently swallows on FastF1 < 3.0; pin/assert the FastF1 version or
  fail loudly so an old FastF1 can't silently allow a network attempt.
- **Evidence:** g2 review.
- **Acceptance:** FastF1 version asserted/pinned; offline guarantee fails loudly if unavailable.
- **Route:** Small hygiene — fold into the consolidated data/physics issue.

---

## Recommended disposition (for the Admiral)
- **Phase 0b epic child:** tc1 + tc6 (anchor calibration + covariance-band tightening) — these ARE
  Phase 0b work; record them in the 0b plan, do not file standalone.
- **One consolidated "trajectory-grading harness hygiene" issue (optional):** tc2 + tc3 + tc4 + tc5
  — small data/physics-region doc/dep/cleanup items. Low priority; can wait.
- Commander filed nothing. Awaiting Admiral approval on what to file vs fold.
