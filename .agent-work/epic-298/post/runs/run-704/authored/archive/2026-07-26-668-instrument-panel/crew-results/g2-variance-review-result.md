# Review Result

Status values follow `skills/workbench/references/status-model.md`.

## Assigned Gate
`g2-variance-review` (#668 instrument panel, epic #659)

## Result
`APPROVE`

## Handoff compliance
The handoff asked for Instrument 1 — the variance-decomposition instrument: a pure
`decompose_segment_time_variance(values, drivers, classes) -> VarianceShares` splitting
segment-time variance into car-reference / driver-utilization / residual shares via the
additive `TwoWayPool` arithmetic in `src/physics/layer2/pooling.py`, driver-utilization
exposed as a floor, no interaction term, TDD synthetic-recovery tests. The delivered diff
does exactly this: `src/physics/instrument_panel/variance_decomposition.py` wraps
`fit_two_way(values, teams=drivers, circuits=classes)` unmodified and returns
`VarianceShares(car_reference_share=pool.frac_circuit, driver_utilization_share=pool.frac_team,
residual_share=pool.frac_resid, driver_utilization_is_floor=True, n=pool.n)`. 7
synthetic-recovery tests, TDD (RED observed via `ModuleNotFoundError` before the module
existed, per implementer's evidence). All assigned criteria satisfied.

## Scope drift
None. `git status --porcelain` (in the worktree) shows only new untracked paths:
`.agent-work/668-instrument-panel/**` (workflow artifacts), `src/physics/instrument_panel/**`
(new package), `tests/unit/physics/instrument_panel/**` (new tests). `git diff` on
`src/physics/layer2/pooling.py` is empty — confirmed byte-for-byte unmodified by reading the
file directly (its `fit_two_way`/`TwoWayPool` match the handoff's cited field names and
signature exactly: `frac_team`, `frac_circuit`, `frac_resid`, `var_team`, `var_circuit`,
`var_resid`, `grand_mean`, `predict`). No `#660/#664/#666/#667` producer module touched. No
`f1_data_*.db` present or written. No interaction term added — `fit_two_way`'s own arithmetic
(`y = μ + team_effect + circuit_effect + residual`) has none, and the new module adds no model
on top of it (5-line pass-through). All specific exclusions respected.

## Evidence verdict
Both LOAD-BEARING evidences reproduced myself, not accepted on the report's word:
- `pytest tests/unit/physics/instrument_panel/test_variance_decomposition.py -q` →
  **7 passed in 0.49s** (matches implementer's claim exactly).
- `pyright src/physics/instrument_panel/variance_decomposition.py` → **0 errors, 0 warnings,
  0 informations** (matches claim exactly).

Beyond the required evidence, I independently verified the axis-mapping falsifiability claim
by writing a standalone scratch script (outside the repo, read-only, not committed) that reuses
the tests' exact generative model directly against `fit_two_way`:
- **Correct mapping** (as shipped): pure-car signal (`a=1,b=0`) → `car_reference_share=0.999`,
  `driver_utilization_share=0.000`; pure-driver signal (`a=0,b=1`) → `car_reference_share=0.000`,
  `driver_utilization_share=0.997`. Matches the shipped tests' `<0.1` thresholds.
- **Swapped mapping** (`car_reference<-frac_team`, `driver_utilization<-frac_circuit`) on the
  identical synthetic data: pure-car signal gives swapped `driver_utilization_share=0.999` (the
  shipped test asserts `<0.1` — **would FAIL**); pure-driver signal gives swapped
  `car_reference_share=0.997` (shipped test asserts `<0.1` — **would FAIL**). Confirms 2 of the 7
  tests genuinely falsify a swapped mapping, not just superficially exercise the code path.
- **Hardcoded-share stand-in** (e.g. `driver_utilization_share` fixed at 0.33 across the `b`
  sweep): fails `test_driver_utilization_share_rises_monotonically_with_b`'s
  `shares[-1] > shares[0] + 0.1` assertion. Hardcoding is independently caught.
- Confirmatory sum/bounds evidence (`car_reference_share + driver_utilization_share +
  residual_share ≈ 1.0`, each in `[0,1]`) is exercised via `_assert_valid_shares` on **every one**
  of the 7 tests, not a single spot example as the handoff's confirmatory bar required at minimum.

As additional (non-required) diligence: ran the reused seam's own test suite together with the
new module — `pytest tests/unit/physics/layer2/test_pooling.py
tests/unit/physics/instrument_panel/ -q` → **22 passed in 0.56s** — confirming the read-only
reuse of `pooling.py` disturbs nothing in its own contract. A full `tests/unit/physics/` region
run (per the project's per-region-verification rule) was attempted but stalled indefinitely
inside an unrelated pre-existing file (`tests/unit/physics/layer2/test_damage_tractability.py`)
well past 2 minutes with zero new progress; I stopped it rather than let it block this review —
see Out-of-scope observations. This is unrelated to the reviewed diff (that file's suite runs
independently of `instrument_panel`, and `git diff` confirms nothing in `layer2/` changed).

Also reproduced `py -m src.utils.simplification_limits --paths src/physics/instrument_panel
tests/unit/physics/instrument_panel` myself → `PASS (4 files checked)`.

## Code/doc quality
Minimal and maintainable: a single 5-line pass-through function and a 5-field frozen
`VarianceShares` dataclass, matching the neighboring `src/physics/layer2/` house style (frozen
dataclass return, explicit docstring). No module-level mutable state, no DB singleton, no
caching — none of the project's structure/state review blockers apply. The 35-line module
docstring is substantive, not filler: it documents the non-obvious one-directional
floor-vs-non-floor asymmetry (why `driver_utilization_share` can only understate, never
overstate, given no interaction term) that is not inferable from the trivial code alone.

**Fowler refactoring pass** — recorded to `fowler_pass_g2.json`, cleared
`scripts/verify_fowler_pass.py` (exit 0, `smells=12, flagged=[], overridden=[]`). All 12
baseline smells (long method, large class, duplicated code, feature envy, data clumps,
primitive obsession, long parameter list, shotgun surgery, divergent change, message chains,
speculative generality, comments-as-deodorant) visited and verdicted **absent** — the module is
a deliberately thin, single-purpose wrapper with no design smell worth raising, and the
(values, drivers, classes) parameter clump exactly mirrors the wrapped `fit_two_way` signature
by design rather than being an un-refactored smell.

## Map impact verdict
- **Evidence supports claimed change:** yes — the capability claim (driver-utilization /
  car-reference variance sizing) matches the function's actual, verified behavior.
- **Constraints not violated:** yes — `constraint:lowest-dimensionality` (no interaction term)
  and `constraint:no-frame-kill` (driver share = floor, explicit field) both verified in code,
  not merely asserted.
- **Notes match the diff:** yes — the listed structural anchors (`pooling.py` read-only,
  `instrument_panel/` new) match `git status`/`git diff` exactly.
- **Decision candidates surfaced:** n/a — the axis mapping and no-interaction rule were already
  pinned by commander authority upstream (launch order + #665/#675 convention); the implementer
  correctly did not re-litigate them, and correctly said so rather than silently following.
- **Durable context routed:** yes — no durable context was dropped; the one out-of-scope finding
  (region-suite hang) is routed to Triage below.

## Reconciliation check
No divergence from the recorded architecture needing Commander reconciliation. This is a
net-new, self-contained package with no existing contract changed.

## Blockers
- none

## Out-of-scope observations
- **Triage candidate (flagged in the engine via `flag-candidate`, id `tc1`):**
  `tests/unit/physics/layer2/test_damage_tractability.py` (or a fixture it shares) stalls the
  full `python -m pytest tests/unit/physics/ -q` region run indefinitely with zero new output
  past 2 minutes — observed independently of, and unrelated to, this diff (`git diff` on that
  file/directory is empty). This silently defeats the project's per-region-verification rule for
  the whole physics region on any future physics change, not just this one. Worth a Triage
  ticket.

## Workflow Feedback

- **Handoff gaps:** none of substance. One small friction: the handoff's "Survey State Location"
  path (`.agent-work/668-instrument-panel/g2-variance-review/review.json`) differs in shape from
  where crew-results/crew-handoffs live (`.agent-work/668-instrument-panel/crew-handoffs/` and
  `crew-results/`) — a reviewer has to notice the survey lives at a third, sibling location
  rather than infer it from the other two directory names. Not ambiguous once read carefully,
  just worth naming explicitly as "a third directory, not nested under crew-results/."
- **Context rediscovered:** none beyond ordinary source-verification (reading `pooling.py`
  directly to confirm the handoff's cited field names/signature, per CREW_CONTEXT's "verify a
  cited seam against source" rule) — this was already anticipated by the handoff and by the
  implementer's own result.
- **Instructions improvised around:** the project's CREW_CONTEXT per-region-verification rule
  ("run the focused region suite for every source change") nominally calls for the full
  `tests/unit/physics/ -v` run for a physics-region touch, but that run stalls on an unrelated
  pre-existing file. I substituted a narrower, still-meaningful regression check — the reused
  seam's own suite (`test_pooling.py`) plus the new module's suite, both green together — and
  reported the stall as an out-of-scope finding rather than let it block this review or silently
  skip region verification.
- **What would have made this easier:** nothing needed for this handoff specifically; at the
  epic level, a known-good/fast physics-region test command (or a documented skip-list for the
  hanging file) would remove this friction for every future physics-touching review.

## Return status
`complete`
