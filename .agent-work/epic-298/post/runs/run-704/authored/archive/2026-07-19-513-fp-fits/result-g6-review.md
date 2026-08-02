# Review Result

## Assigned Gate
`g6` (513-fp-fits) — "held-out gate harness, both channels"

## Result
`APPROVE`

## Rework note (2026-07-19)
The original pass (below) BLOCKED on one finding: `divergent_case_read` at 100 lines / cyclomatic complexity
20, one unit over the project's machine-enforced `simplification_limits` limits under the strict
(non-`--baseline`) check. The implementer extracted `_pooled_normalized_weight_diffs` (41 lines) +
`_fold_divergent_deltas` (34 lines) out of `divergent_case_read` (now 59 lines). Independently re-verified,
not taken on report:
- Re-ran `py -m src.utils.simplification_limits --paths src/physics/layer2/fp_gate.py scripts/fp_representativeness_gate.py tests/unit/physics/layer2/test_fp_representativeness_gate.py` (no `--baseline`, the strict check that originally caught the violation) → **PASS (3 files checked)**, zero violations. AST-confirmed every function in `fp_gate.py` is now well under 99 lines / complexity 19.
- Re-ran the full gate suite → **36 passed** (unchanged from pre-rework).
- Confirmed `tests/unit/physics/layer2/test_fp_representativeness_gate.py` is **byte-identical** (703 lines,
  same as pre-rework) — the fix did not alter test coverage or expectations to paper over a behavior change.
- Read the two extracted helpers line-by-line against the pre-rework inline logic: the split is purely
  mechanical (same pooling/normalization/threshold/per-fold-skip logic, relocated not altered).
- `git status --short data/` still clean; `--baseline --paths` variant still PASSes too.

The Fowler pass record (`g6-review/fowler-pass.json`) was updated (`long-method`: `flagged` → `absent`, with
the resolution documented) and re-verified via `verify_fowler_pass.py` (exit 0). The engine-driven survey
(`g6-review/review.json`) was re-consolidated to `APPROVE` (0 open findings) — see its `consolidation` field
for the full rework summary. Everything below this note is the **original** review pass, preserved for audit
trail; only the verdict and the blocker status have changed.

---

## Original result (superseded by the rework note above)
`BLOCK`

## Handoff compliance
Full handoff compliance on every substantive close criterion, independently reproduced (not taken on the
implementer's word):

- **ANTI-RIG (the most important check): GENUINE.** Traced `observation_features()`
  (`src/physics/layer2/fp_representativeness.py:277-308`) — it is computed ONLY from
  `(latent.fuel_kg_est, latent.compound, latent.run_purpose, track_evolution, session_max_track_evolution)`.
  In `_build_null_weekends` (test file), every observation — near AND far, all 4 cars — shares
  `compound=MEDIUM, run_purpose=push, fuel_kg_est=15.0=quali_fuel_kg, track_evolution=None(→neutral 0.5)`:
  an IDENTICAL features tuple. `learned_weight()` therefore returns the SAME scalar for every observation
  under ANY fitted `WeightParams`, which mathematically forces the LEARNED arm's per-car weighted mean to
  collapse to the plain unweighted mean — **regardless of what `fit_weight_params` converges to**. This is a
  structural proof, not an empirical accident; the harness cannot be gamed into always passing. CLOCK
  genuinely wins in this fixture because it reads real signal (`hours_to_q` 1.0 near vs 20.0 far×2) that the
  fixture deliberately withholds from the LEARNED arm. Reproduced: 36/36 tests pass including the NULL
  fixture, which asserts `verdict == "HONEST_NULL"` and neither bootstrap favors learned.
- **LEAKAGE (F6): structurally guarded.** `fit_weight_params(train_weekends, ...)` closes over no other
  data source; `run_lowo` excludes the held-out weekend from `train` before calling it. Both dedicated
  shuffle tests (direct call + through `run_lowo`'s own fold loop) pass, confirming byte-identical fitted
  params after shuffling held-out Q targets.
- **DIVERGENT-CASE normalization (F4):** `_min_max_normalize` is applied identically/symmetrically to both
  `norm_learned` and `norm_clock` over the same pooled observation set — an arm-agnostic fix for a genuine
  scale mismatch (clock = unbounded exponential decay vs learned = bounded logistic), not an unfair
  advantage for either side. The implementer's documented TDD RED (a false `HONEST_NULL` on the raw-scale
  diff) substantiates this was a real bug, not an invented departure.
- **No session-type hardcoding:** `clock_weight`/`learned_weight` source-scanned — `session_type` absent
  from both. The only use of `session_type` is in `build_gate_observations`'s leakage-guarded
  track-evolution session-max bucketing, not a weighting decision.
- **Protocol faithfulness:** LOWO (`run_lowo`), paired bootstrap (`paired_bootstrap`, 10k default), the
  divergent-case read (`divergent_case_read`), emergence audit (`emergence_audit`), sandbagging demo
  (`sandbagging_demo`) — all present and match GATE_PROTOCOL.md sections 1/4/5/6/7/8. Both channels
  (PRIMARY grip / SECONDARY power) reported honestly; SECONDARY never silently evidential below
  `min_distinct_sigma`.
- **No real telemetry/DB/compute:** confirmed — every fixture is synthetic, constructed in-test.

## Scope drift
None. `git status --short` shows exactly the 3 claimed new files
(`src/physics/layer2/fp_gate.py`, `scripts/fp_representativeness_gate.py`,
`tests/unit/physics/layer2/test_fp_representativeness_gate.py`) plus `.agent-work/` workflow artifacts.
`git diff --stat` against the frozen upstream G2/G4/G5 modules (`fp_representativeness.py`,
`fp_lap_latent.py`, `mass_model.py`) is empty — `learned_weight` reuses
`fp_representativeness.observation_weight` verbatim, unmodified. The throwaway
`scripts/_g6_smoke_extractor.py` used for the CLI smoke run is confirmed absent from the worktree (genuinely
deleted). No `data/*.db` touched. No imports from `src/evo_predictor`, `src/latent_power`,
`src/compound_prior`, or `fastf1` in `fp_gate.py`.

## Evidence verdict
All 3 handoff verification commands independently re-run from a fresh shell (not trusted from the report):
- `pytest tests/unit/physics/layer2/test_fp_representativeness_gate.py -q` → **36 passed in 3.88s**.
- `py -m src.utils.simplification_limits --baseline --paths <3 files>` → **PASS (3 files checked)**.
- `git status --short data/` → **clean (no output)**.

TDD evidence (RED→GREEN per m1-m6, including the genuine m4 logic-bug RED, not just import-error REDs) is
consistent with the diff.

## Code/doc quality
Mostly strong — dense, protocol-traceable docstrings matching the surrounding `fp_representativeness.py`
convention; no mutable module-level state; randomness via explicit `np.random.default_rng(seed)`; no
`print()` outside the CLI; descriptive validation exceptions. **One real defect found (see Blockers):**
re-running `py -m src.utils.simplification_limits --paths <3 files>` **without** `--baseline` — the
invocation `docs/agents/CREW_CONTEXT.md` documents as "strict on changed trees" — surfaces:

```
src/physics/layer2/fp_gate.py divergent_case_read: cyclomatic_complexity=20 (limit: <20)
src/physics/layer2/fp_gate.py divergent_case_read: function_lines=100 (limit: <100)
```

AST-confirmed: `divergent_case_read` spans `fp_gate.py:560-659`, exactly 100 lines. The handoff's own
verification command (`--baseline --paths <files>`) passes only because `--baseline` narrows the checked
metrics to `file_lines` only (per `config/simplification_baseline.json`'s `baseline_metrics: ["file_lines"]`)
— a materially weaker check than the project's documented strict standard for touched files.
`CREW_CONTEXT.md` states this is a review blocker when failing on in-scope Python.

## Map impact verdict
- **Evidence supports claimed change:** Yes — `evaluate_gate`/`secondary_power_gate` are real, tested,
  callable functions matching the diff.
- **Constraints not violated:** Yes — leakage, divergent-case normalization, emergence, and honest
  both-channel reporting all independently re-verified, not just taken on the implementer's word.
- **Notes match the diff:** Yes — structural anchors (`struct:physics.layer2` new `fp_gate.py`,
  `struct:physics` new `scripts/fp_representativeness_gate.py`) match `git status`.
- **Decision candidates surfaced:** Yes — `DEFAULT_L2_PENALTY=1e-3` and the min-max normalization fix are
  both correctly flagged as decision-candidates for G7/Ship review, with honest rationale; both are
  genuinely load-bearing (without L2 shrinkage, Nelder-Mead saturates on clean synthetic data; without
  normalization, the POSITIVE fixture false-NULLs).
- **Durable context routed:** Yes — the implementer's trust-limitation claim (real FP laps will resolve
  `fp_mass_sigma_kg` to the constant `FP_FUEL_INTERCEPT_SIGMA_KG=15.0`, likely forcing
  `CONFOUNDED_NOT_EVIDENTIAL` on the real G7 batch) was independently grep-verified accurate
  (`fp_lap_latent.py:353` → `mass_model.py:334`, no explicit `fuel_sigma_kg` passed). Routed as a
  reviewer-confirmed triage candidate (`tc1` in `g6-review/review.json`) so Commander/Triage tracks the
  SECONDARY-channel follow-on.

## Reconciliation check
None. `SPLIT_HASH=f1725bd81cd3eefa` in `fp_gate.py` matches `GATE_PROTOCOL.md` exactly. No divergence from
the recorded architecture requiring Commander reconciliation.

## Blockers
- **`divergent_case_read` exceeds the project's own machine-enforced simplification limits** (100 lines vs
  `MAX_FUNCTION_LINES=99`; cyclomatic complexity 20 vs `MAX_CYCLOMATIC_COMPLEXITY=19`), confirmed by running
  the strict (non-`--baseline`) `simplification_limits --paths` check that `CREW_CONTEXT.md` documents as
  the standard for touched files — a review blocker per that doc when failing on in-scope Python. Marginal
  (1 unit over on each metric) and trivially fixable (extract the per-fold divergent-metric computation,
  roughly lines 620-641, into a small helper), with no effect on the harness's correctness or anti-rig
  properties, all of which are independently verified sound. Fix, then re-run
  `py -m src.utils.simplification_limits --paths src/physics/layer2/fp_gate.py scripts/fp_representativeness_gate.py tests/unit/physics/layer2/test_fp_representativeness_gate.py`
  (no `--baseline`) to confirm PASS before re-submitting.

## Out-of-scope observations
- Minor duplicated all-NaN `BootstrapResult` construction: inlined in `paired_bootstrap`'s empty-input
  branch (`fp_gate.py:519-522`) instead of reusing the existing `_nan_bootstrap()` helper. Cosmetic, no
  behavioral risk.
- A `(value_attr, target_attr)` parameter pair recurs identically across 5 function signatures
  (`fit_weight_params`, `_weekend_metric`, `run_lowo`, `divergent_case_read`, `evaluate_gate`) — a
  PRIMARY-vs-SECONDARY channel selector. A small `ChannelSpec` type would remove the repetition; low cost
  today, flagged as a future simplification candidate, not a blocker.
- `tc1` (routed via the engine's `flag-candidate`): the SECONDARY channel's real-world evidential value is
  gated on `fp_lap_latent.extract_fp_lap_latent` ever supplying a non-constant `fuel_sigma_kg` — independently
  confirmed accurate. Worth tracking as a named follow-on so G7 isn't surprised by an expected
  `CONFOUNDED_NOT_EVIDENTIAL` result.

## Reproduced evidence (this review's own commands)
```
cd /c/Programs/f1-513 && PYTHONPATH=/c/Programs/f1-513 py -m pytest tests/unit/physics/layer2/test_fp_representativeness_gate.py -q
=> 36 passed in 3.88s

cd /c/Programs/f1-513 && PYTHONPATH=/c/Programs/f1-513 py -m src.utils.simplification_limits --baseline --paths src/physics/layer2/fp_gate.py scripts/fp_representativeness_gate.py tests/unit/physics/layer2/test_fp_representativeness_gate.py
=> PASS (3 files checked)

cd /c/Programs/f1-513 && git status --short data/
=> (clean, no output)

cd /c/Programs/f1-513 && PYTHONPATH=/c/Programs/f1-513 py -m src.utils.simplification_limits --paths src/physics/layer2/fp_gate.py scripts/fp_representativeness_gate.py tests/unit/physics/layer2/test_fp_representativeness_gate.py
=> FAIL (2 violations, 3 files checked)
   src/physics/layer2/fp_gate.py divergent_case_read: cyclomatic_complexity=20 (limit: <20)
   src/physics/layer2/fp_gate.py divergent_case_read: function_lines=100 (limit: <100)
```

Full engine-driven survey (7 checks incl. the required Fowler pass, all visited, consolidated BLOCK) at
`.agent-work/513-fp-fits/g6-review/review.json`; Fowler smell record (rail-verified,
`verify_fowler_pass.py` exit 0) at `.agent-work/513-fp-fits/g6-review/fowler-pass.json`.

## Workflow Feedback

- **Handoff gaps:** the handoff's verification command bundled `--baseline --paths <files>`. Reading
  `simplification_limits.py`'s `verify_simplification_limits()` shows `--baseline` narrows the checked
  metrics to whatever `config/simplification_baseline.json`'s `baseline_metrics` lists (here: `file_lines`
  only), silently dropping the `function_lines`/`cyclomatic_complexity` checks for ALL files, not just
  grandfathered ones. `CREW_CONTEXT.md` separately documents a plain `--paths <touched>` (no `--baseline`)
  invocation as "strict on changed trees" — the handoff's combined-flags command is neither of the two
  documented commands and is materially weaker than the "strict" one. This let a real, marginal
  function-length/complexity violation through the implementer's own reported evidence undetected.
- **Context rediscovered:** had to read `simplification_limits.py`'s `verify_simplification_limits()`
  function body and `config/simplification_baseline.json` directly to learn that `--baseline` changes
  *which metrics* run repo-wide, not just which paths are skipped — this isn't obvious from the CLI's
  `--help` text or from CREW_CONTEXT.md's one-line description alone.
- **Instructions improvised around:** none — the skill's evidence-verification doctrine ("verify claimed
  side-effects against the world... a claim you cannot reproduce is a defect") directly motivated
  re-running the check in the project's own documented "strict" form rather than stopping at the handoff's
  literal command, which is what surfaced the blocker.
- **What would have made this easier:** future G6-class handoffs should specify the plain `--paths <touched>`
  (no `--baseline`) simplification_limits invocation for the review's own reproduction step, since that is
  the one CREW_CONTEXT.md itself calls "strict on changed trees" and the one that actually catches
  function-length/complexity regressions on freshly authored code — `--baseline` is for the repo-wide
  check-in.

## Return status
`complete`
