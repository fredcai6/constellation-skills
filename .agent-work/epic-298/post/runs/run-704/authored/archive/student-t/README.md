# Student-t Migration — Working Documents Archive

Design + planning artifacts from the Gaussian → Student-t migration work (2026-05-31).
The code shipped to `main`; these are the working documents, archived here for reference.

## Contents

- `2026-05-31-student-t-migration-design.md` — the design spec (the two-tail aleatoric/epistemic
  framing, fork decisions, acceptance signal, and the running list of open items for later phases).
- `2026-05-31-student-t-phase0-foundation.md` — plan for `src/common/student_t.py` (the
  `predictive_t` foundation: tail rules + `PredictiveT` + factory).
- `2026-05-31-student-t-phase1a-calibration-scoring.md` — plan for `src/calibration/scoring.py`
  (PIT, coverage, CRPS, `summarize_calibration`).
- `2026-05-31-student-t-phase1b-baseline-core.md` — plan for `src/calibration/baseline.py`
  (dual-reference Gaussian-vs-Student-t per-task scoring + `r/σ` dashboard).
- `2026-05-31-student-t-phase1b-wire.md` — plan for `src/calibration/harness.py` + CLI
  (discover bundle, extract live per-task arrays, emit baseline report).
- `sample-baseline-report-eval2025.json` — sample harness output from a smoke run
  (`constructor_quali_power_from_race_weekend`, eval year 2025).

## Status at archive time

Shipped to `main`: Phase 0, Phase 1a, Phase 1b-core, Phase 1b-wire. Full suite green (2539 passed),
pyright clean.

Pending (see the spec's "Open Items"): Phase 2 (route the fantasy sampler through `predictive_t` —
the train/inference consistency leak), Phase 3 (quali `norm.cdf`, tire-wear CIs, viz bands),
Phase 4 (tune formula-vs-hybrid + `tau`; revisit the `HybridRule` floor concern). Smaller follow-ups:
Gaussian-arm vectorization in the harness, `docs/architecture/index.md` update, and promoting the
private `_join_retro_results` import used by the harness.
