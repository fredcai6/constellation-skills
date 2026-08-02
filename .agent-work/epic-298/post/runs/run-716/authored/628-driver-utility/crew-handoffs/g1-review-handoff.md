# Reviewer Handoff — G1 (observable module + resumable batch CLI)

## Gate
`g1-review`. Worktree **C:/Programs/f1-628** only. DBs read-only in MAIN checkout C:/Programs/f1Brainz/data/.

## What was implemented
- `src/physics/utilization/driver_utility_observable.py` — pure `compute_regime_deficits` computing per-regime
  absolute deficit `g = mean(v_ideal - v_real)` over the 4 masks (reuses `_build_regime_masks`).
- `scripts/build_driver_utility_observables.py` — resumable batch CLI (one strictly_pre ceiling + one
  simulate_lap per constructor-round; lean `fit_best_lap_trace` for v_real; idempotent skip-if-present;
  round-with-no-causal-history writes an error row).
- `tests/unit/physics/test_driver_utility_observable.py` — 8 unit tests.
- Implementer result: `.agent-work/628-driver-utility/crew-results/g1-implement-result.md`.

## How to inspect the diff
`cd /c/Programs/f1-628 && git status && git diff -- src/physics/utilization/driver_utility_observable.py scripts/build_driver_utility_observables.py tests/unit/physics/test_driver_utility_observable.py`
(The three files are untracked/new — inspect them directly; `data/driver_utility_observables.db` is an
untracked scratch DB and must NOT be in the diff/staged.)

## Task statement being verified
Produce the per-driver per-axis ABSOLUTE-deficit observable against a strictly_pre CAUSAL ceiling, with NO
`observed ÷ capability` division anywhere (the load-bearing F4 check).

## Close criteria (verify each, re-running the numbers)
- Re-run `py -m pytest tests/unit/physics/test_driver_utility_observable.py -q` → all pass.
- **F4 (load-bearing):** grep the two new source files → NO `v_real/v_ideal`, `/ v_ideal`, or
  `observed/capab*` division. The metric must be a SUBTRACTION, not a ratio.
- `_build_regime_masks` is REUSED from `regime_utilization` (not reinvented).
- The ceiling is built with `strictly_pre=True` in the CLI.
- v_real comes from `fit_best_lap_trace` (lean; NOT the full `fit_session_full` MAP fit).
- CLI is genuinely idempotent/resumable (a re-run adds 0 rows) and one ceiling+sim is shared across a
  constructor's two drivers (not recomputed per driver).
- Synthetic behavior: driver-at-ceiling → g≈0; corner-slow → g>0 on corner axes, ≈0 on straight.
- `git status data/` shows only the untracked scratch DB; nothing under data/ is staged.

## Allowed scope / exclusions
Review only the three new files + the result. Do not review G2/G3 (not built). Out-of-scope finds → note as
triage candidates, do not fix.

## Map anchors (inbound)
Inherits g1-implement anchors — the F4 no-division check is the load-bearing review check;
`decision:c1_driver_utilization_design` (strictly_pre is the falsifiable-gate refinement).

## Required evidence
Paste: the pytest re-run output, the F4 grep result, and your confirmation that the ceiling+sim is shared and
the CLI is idempotent (cite the lines).

## Verification commands
```bash
cd /c/Programs/f1-628 && py -m pytest tests/unit/physics/test_driver_utility_observable.py -q
cd /c/Programs/f1-628 && grep -nE "v_real ?/ ?v_ideal|/ ?v_ideal|observed ?/ ?cap" src/physics/utilization/driver_utility_observable.py scripts/build_driver_utility_observables.py || echo NO-RATIO-OK
cd /c/Programs/f1-628 && git status --porcelain data/
```

## Return format
Return REVIEW_RESULT with an explicit verdict line `verdict: APPROVE` or `verdict: BLOCK`, the re-run
evidence, any findings (severity-ranked), and workflow feedback. BLOCK if the F4 no-division check fails or
any close criterion is unmet.
