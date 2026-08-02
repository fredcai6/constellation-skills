# Review Result

Status values follow `skills/workbench/references/status-model.md`.

## Assigned Gate
`g4-review` (513-fp-fits — representativeness weighting)

## Result
`APPROVE`

## Handoff compliance
All close criteria in `.agent-work/513-fp-fits/handoff-g4.md` are met and were independently reproduced (not
trusted from the implementer's report):
- `ObservationFeatures` (fuel_proximity, compound_softness, run_purpose_score, track_evolution_score),
  `observation_features(...)`, `WeightParams`/`DEFAULT_WEIGHT_PARAMS`, `observation_weight(...) -> float`
  present exactly as specified in `src/physics/layer2/fp_representativeness.py` (348 lines).
- Weighting form is a transparent logistic sigmoid over a linear combination of the four named features, with
  every coefficient named in `WeightParams` and flagged tunable (G6 fits for real) — inspectable, not a black
  box.
- `w` bounded in [0,1] (in practice the open interval (0,1), a strict subset) for all inputs; nothing is ever
  binary-dropped (no `None`/exclusion path exists in the source).
- `35 passed` reproduced: `py -m pytest tests/unit/physics/layer2/test_fp_representativeness.py -q`.

## Scope drift
None. `git status --short` shows exactly the two allowed new files
(`src/physics/layer2/fp_representativeness.py`, `tests/unit/physics/layer2/test_fp_representativeness.py`)
plus the `.agent-work/` workflow dir. Specific exclusions honored: `session_estimator.py`/views/`estimate_store`
untouched; no `#628 driver_utility` wiring (confirmed by grep — no other `src/` file imports
`fp_representativeness` yet); `git status --short data/` clean (no `data/*.db` touched; tests build synthetic
`FpLapLatent` via a local `_latent()` helper); `DEFAULT_WEIGHT_PARAMS` is hand-set, no fitting code path exists
in the module.

## Evidence verdict
All required evidence reproduced independently at the source, not accepted from the report:
- `py -m pytest tests/unit/physics/layer2/test_fp_representativeness.py -q` → **35 passed** (matches).
- `grep -nE "FP1|FP2|FP3|session_type" src/physics/layer2/fp_representativeness.py` → **empty, exit 1**
  (matches — no session-type string anywhere in the module source).
- `git status --short data/` → **clean**.
- `py -m src.utils.simplification_limits --baseline --paths src/physics/layer2/fp_representativeness.py
  tests/unit/physics/layer2/test_fp_representativeness.py` → **PASS (2 files checked)**.

### THE CENTRAL CHECK (critic F3/F4, calendar-in-disguise guard) — independently re-derived, not trusted

I recomputed `observation_weight`'s sigmoid arithmetic by hand outside the test suite to confirm the emergence
tests are genuine, non-trivial discriminators — not tautologies that would pass under any implementation.

**Test 1 — within-session** (`test_lap3_low_fuel_soft_push_beats_lap18_high_fuel_hard_long_run_same_session`):
`track_evolution_score(35)` with no `session_max_track_evolution` supplied is **identical** for both
observations by construction (`35/(35+40) = 0.46667` for each — confirmed both by the test's own equality
assertion and my independent recompute). The weight gap under `DEFAULT_WEIGHT_PARAMS`
(push = 0.9974 vs long_run = 0.6136) is therefore driven **entirely** by fuel_proximity/compound_softness/
run_purpose_score (0.9975/1.0/1.0 vs 0.0183/0.3/0.2), which genuinely differ — a real, non-tautological
discrimination, not one riding the track-evolution term.

The companion test (`test_within_session_gap_survives_even_if_track_evolution_term_zeroed`) was recomputed
too: zeroing `w_track_evolution` still leaves push = 0.9959 > long_run = 0.499 — the gap survives independent
of any track-evolution contribution.

**Test 2 — cross-session** (`test_fp2_like_push_beats_fp3_like_long_run`): recomputed
`track_evolution_score(8) = 0.16667` vs `track_evolution_score(70) = 0.63636` — the **later/long-run**
observation has the track-evolution **advantage**, exactly as the test's own pre-check assertion (line 361)
states and as I independently confirmed. Despite that, recomputing the full weight gives
`w(earlier_push) = 0.9965 > w(later_long_run) = 0.6482` — the final ranking is **reversed** relative to
track_evolution_score alone. This is precisely the "a track-evolution-only weighting would get this backwards"
property the handoff/critic demanded, and it is asserted **programmatically** (not just claimed in prose) via
the test's own pre-check assertion before the weight comparison runs.

Structural corroboration: `w_track_evolution = 1.0` is deliberately the **smallest** of the four feature
coefficients (`w_fuel_proximity=2.5`, `w_run_purpose=2.5`, `w_compound_softness=1.5`,
`w_track_evolution=1.0`) per the module's own `DEFAULT_WEIGHT_PARAMS` docstring — consistent with, not merely
coincidental to, the emergence property.

**Verdict: the emergence tests are genuine, non-trivial discriminators.** They would fail under a
track-evolution-only (calendar-in-disguise) weighting and pass only because the implementation is truly
multi-feature.

**No BLOCK trigger present:**
- No session-type string in the module (verified by grep, independently reproduced).
- No binary-drop (`observation_weight`'s logistic range is the open interval (0,1); `TestNothingBinaryDropped`
  exercises out/in/thin-long-run cases and all return positive bounded weights; no `None` path in source).
- No Q-session leakage (`track_evolution_score`'s signature is exactly `{track_evolution,
  session_max_track_evolution}`, both plain ints, verified by `inspect.signature` test + manual read;
  `FpLapLatent.fuel_kg_est`/`compound`/`run_purpose` are FP-observed/emergent fields per `fp_lap_latent.py`'s
  own docstring, not Q-derived).
- No real-data fit (`DEFAULT_WEIGHT_PARAMS` is hand-set; the module contains no fitting/optimization code
  path).

## Code/doc quality
Meets inherited + project rules (per-rule sub-checks, all independently verified):
- **Physics-region imports:** only `math`/`dataclasses`/`typing` plus `fp_lap_latent.FpLapLatent`
  (transitively `sqlite3`/`pathlib`/`pandas`/`mass_model`). No `evo_predictor`/`latent_power`/
  `compound_prior`/`fastf1` import anywhere in the chain.
- **Leakage guard (F6):** confirmed as above.
- **Named tunable constants:** `FUEL_SCALE_KG`, `COMPOUND_SOFTNESS_BY_LABEL`, `NEUTRAL_COMPOUND_SOFTNESS`,
  `C_NUMBER_SOFTNESS`, `RUN_PURPOSE_SCORE_BY_LABEL`, `DEFAULT_RUN_PURPOSE_SCORE`,
  `TRACK_EVOLUTION_HALF_SCALE_LAPS`, `NEUTRAL_TRACK_EVOLUTION_SCORE`, `DEFAULT_WEIGHT_PARAMS` — all
  module-scope, each docstring-flagged "Calibration placeholder"/"TUNABLE, not fitted".
- **File size:** 348 / 432 lines, well under 1000; `simplification_limits --baseline` PASS reproduced.
- **CREW_CONTEXT structural rules:** no mutable module-level runtime state (only immutable constants + two
  frozen dataclasses), no DB singleton (module does not touch the DB at all); missingness represented
  intentionally via named fallbacks (`NEUTRAL_COMPOUND_SOFTNESS`, `NEUTRAL_TRACK_EVOLUTION_SCORE`,
  `DEFAULT_RUN_PURPOSE_SCORE`), never silently guessed/zeroed.

### Refactoring pass (Fowler code smells)
Full pass recorded at `.agent-work/513-fp-fits/g4-review/fowler_pass.json`; `scripts/verify_fowler_pass.py`
exits 0 (`smells=12, flagged=[], overridden=['primitive-obsession']`). 11 of 12 baseline smells **absent**.
One **overridden**: `primitive-obsession` (raw `str` compound/run_purpose instead of enums) — logged reason:
this matches the upstream `FpLapLatent.compound`/`.run_purpose` `str` convention, and `fp_lap_latent.py` is
frozen/out-of-scope for this gate per the handoff's Allowed Scope; the module already centralizes all
string-matching into two named lookup tables plus a documented neutral fallback.

## Map impact verdict
- **Evidence supports claimed change:** yes — the produced evidence (35 green tests incl. the two load-bearing
  emergence tests, hand-verified above) backs the claimed capability.
- **Constraints not violated:** yes — physics-region, leakage, emergence, and nothing-binary-dropped
  constraints all independently re-verified.
- **Notes match the diff:** yes — structural/capability/constraint/decision notes in
  `result-g4-implement.md`'s Map Impact section match the actual diff (new file only, import-only dependency
  on `fp_lap_latent.FpLapLatent`, no consumer wiring yet — confirmed by grep, no other `src/` file imports
  `fp_representativeness`).
- **Decision candidates surfaced:** yes — the logistic-sigmoid-vs-geometric-mean form choice and
  `DEFAULT_WEIGHT_PARAMS` coefficients are correctly flagged as G6 fodder.
- **Durable context routed:** yes — no new triage candidates needed; the two named follow-ons (#628 wiring,
  G6 fitting) are already tracked as `execute.json` gates `g5`/`g6`.

## Reconciliation check
No divergence from the recorded architecture requiring Commander reconciliation. `execute.json`'s
`g4-implement` anchors (structural/capability/constraint/decision) match what was actually built.

## Blockers
- none

## Out-of-scope observations
- none

## Workflow Feedback
- **Handoff gaps:** none blocking. One minor pre-existing friction (already flagged by the implementer, worth
  repeating): the handoff's own suggested process-noise docstring wording literally contained the
  `FP1`/`FP2`/`FP3` tokens its own hygiene rule forbids "anywhere in the module" — resolved correctly by the
  implementer via rephrasing, but a future handoff for a similarly self-referential hygiene rule should note
  "applies to docstrings/comments too, phrase required documentation without the literal tokens" up front.
- **Context rediscovered:** none — the handoff, `execute.json` anchors, and `result-g4-implement.md` were
  internally consistent and sufficient to verify without digging elsewhere.
- **Instructions improvised around:** none — the survey engine and Fowler-pass rail ran cleanly end to end
  with no workaround needed.
- **What would have made this easier:** none — the handoff's central-check framing (state the exact property
  the emergence tests must prove, plus the two named test identifiers) made independent hand-verification
  fast and unambiguous; this is a good template for future load-bearing-property review handoffs.

## Return status
`complete`
