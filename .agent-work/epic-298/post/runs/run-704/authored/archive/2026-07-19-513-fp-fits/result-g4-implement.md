# Implementation Result

Status values follow `skills/workbench/references/status-model.md`.

## Assigned gate
`g4` (513-fp-fits — representativeness weighting, execute.json gate `g4-implement`)

## Completed slice
New `src/physics/layer2/fp_representativeness.py`: a continuous per-observation representativeness
weight `w in [0,1]` computed EMERGENTLY from an FP lap's own properties — never a session label.
Public surface:
- `ObservationFeatures` (frozen dataclass): `fuel_proximity`, `compound_softness`,
  `run_purpose_score`, `track_evolution_score`.
- `observation_features(latent: FpLapLatent, *, quali_fuel_kg, track_evolution,
  session_max_track_evolution=None) -> ObservationFeatures`.
- Four pure per-feature functions: `fuel_proximity`, `compound_softness`, `run_purpose_score`,
  `track_evolution_score` (all independently testable, all None/unknown-safe, none raises on an
  unrecognized input).
- `WeightParams` (frozen dataclass of named coefficients) + `DEFAULT_WEIGHT_PARAMS` (hand-set,
  flagged tunable) + `observation_weight(features, *, params=DEFAULT_WEIGHT_PARAMS) -> float` — a
  logistic sigmoid over a linear combination of the four features.

## Scope
**Files changed:**
- `src/physics/layer2/fp_representativeness.py` (new, 348 lines)
- `tests/unit/physics/layer2/test_fp_representativeness.py` (new, 432 lines)

**Specific exclusions touched:** no. Did not touch `session_estimator.py`, the views, or
`estimate_store`; did not wire into #628 `driver_utility`; no `data/*.db` read, written, or
committed (synthetic `FpLapLatent` instances only, built in-test via a local `_latent()` helper); no
weighting coefficients fit on real data (`DEFAULT_WEIGHT_PARAMS` is hand-set only).

## Behavior changed
Yes — new capability. No existing module was modified; nothing downstream consumes this yet (G5/G6
are the wiring gates), so no existing behavior changed.

## Map Impact
- **Structural anchors touched:** `struct:physics.layer2` — new `fp_representativeness.py`, consumes
  `fp_lap_latent.FpLapLatent` (import only, `fp_lap_latent.py` itself untouched).
- **Capabilities added/changed/affected:** new capability — a continuous per-observation
  representativeness weight, ready to feed the G6 held-out gate and the #628 driver-utility product
  (neither wired here; both named follow-ons per the handoff's Specific Exclusions).
- **Constraints/assumptions touched:**
  - `constraint:physics_region_no_evo_import` — honored (only stdlib `math`/`dataclasses`/`typing`
    plus `fp_lap_latent.FpLapLatent`).
  - Emergence (critic F3) — honored; see Evidence below.
  - Leakage (critic F6, "no Q-session input into track_evolution") — honored; see Evidence below.
  - "Nothing binary-dropped" — honored; `observation_weight` is a logistic, range is the open
    interval (0,1), a strict subset of the required [0,1]; no code path returns `None` or excludes
    an observation.
- **Decision candidates:** the weighting FORM is a **logistic sigmoid over a linear combination**
  of the four named features (vs. the handoff's other suggested option, a weighted geometric mean).
  Chosen for: (a) unconditional (0,1) boundedness without a manual clamp; (b) a coefficient of zero
  cleanly means "feature ignored" (geometric mean needs a zero *exponent*, awkward to default); (c)
  well-understood monotonicity properties for the emergence proof. `DEFAULT_WEIGHT_PARAMS` (bias=-1.0,
  w_fuel_proximity=2.5, w_compound_softness=1.5, w_run_purpose=2.5, w_track_evolution=1.0) is a
  DECISION-CANDIDATE for G6: `w_track_evolution` was deliberately set to the SMALLEST coefficient so
  that observation-level representativeness can structurally outweigh a track-evolution advantage —
  this is a design choice, not a fitted result, and G6 may find different coefficients fit the data
  better (as long as they still pass the emergence tests, which are architecture-level, not
  coefficient-level).
- **Claims/evidence produced:** see Evidence section — 35/35 tests green, including a
  by-hand-computed proof that the emergence tests are non-trivial discriminators (a track-evolution-
  only weighting would get the cross-session case backwards).
- **Triage candidates:** none from this slice — the module is intentionally self-contained per the
  handoff's Allowed Scope (no wiring, no fitting).

## Test mode
**Required:** `test-first (TDD)`
**Satisfied:** yes, with one adaptation — see Workflow Feedback. All feature functions, the weight
form, and the emergence/leakage/no-drop guards were test-specified in a single up-front test file
before `fp_representativeness.py` existed (collective RED = `ModuleNotFoundError` on import), then
implemented together as one module pass (the weight form is tightly coupled to
`ObservationFeatures`, so a per-function red/green split would have meant stubbing the whole
dataclass first anyway).

## Evidence

```bash
$ cd /c/Programs/f1-513 && PYTHONPATH=/c/Programs/f1-513 py -m pytest tests/unit/physics/layer2/test_fp_representativeness.py -q
============================= test session starts =============================
platform win32 -- Python 3.14.3, pytest-9.0.2, pluggy-1.6.0
collected 35 items
tests\unit\physics\layer2\test_fp_representativeness.py ................ [ 45%]
...................                                                      [100%]
============================= 35 passed in 1.33s ==============================
```

```bash
$ py -m src.utils.simplification_limits --baseline --paths src/physics/layer2/fp_representativeness.py tests/unit/physics/layer2/test_fp_representativeness.py
PASS (2 files checked)
```

```bash
$ git status --short data/
(no output -- clean)
```

**Result:** pass.

### The two emergence tests (critic F3, load-bearing)

1. `TestEmergenceWithinSession::test_lap3_low_fuel_soft_push_beats_lap18_high_fuel_hard_long_run_same_session`
   — constructs both observations at an IDENTICAL `track_evolution=35` (same session), asserts their
   `track_evolution_score` fields are equal, then asserts `observation_weight(push) >
   observation_weight(long_run)`. PASSED. A companion test
   (`test_within_session_gap_survives_even_if_track_evolution_term_zeroed`) re-runs the same pair
   with `w_track_evolution=0.0` and shows the gap survives — proving the discrimination comes from
   fuel/compound/purpose, not a residual track-evolution term.
2. `TestEmergenceAcrossSessionsRepresentativenessBeatsRecency::test_fp2_like_push_beats_fp3_like_long_run`
   — an "FP2-like" push (`track_evolution=8`) vs an "FP3-like" long-run (`track_evolution=70`); the
   test first asserts the long-run has the `track_evolution_score` ADVANTAGE, then asserts
   `observation_weight(earlier_push) > observation_weight(later_long_run)` anyway. PASSED. No
   session-type string appears anywhere in the test's construction — only the two track_evolution
   ints, chosen to stand in for "earlier/greener" vs "later/more-rubbered-in".

**Non-triviality check (by hand, not itself a test):**
```
track_evolution_score(8)  = 0.16666...   # FP2-like push
track_evolution_score(70) = 0.63636...   # FP3-like long-run
A track-evolution-ONLY weighting would rank the long-run HIGHER (0.636 > 0.167) --
i.e. it would get this pair BACKWARDS. observation_weight must and does override
that ranking via fuel_proximity/compound_softness/run_purpose_score.
```
This confirms test 2 is a real discriminator, not one that would pass under any implementation.

### Module-source hygiene test
`test_no_session_type_string_in_module_source` scans `fp_representativeness.py`'s raw source text
for `FP1`/`FP2`/`FP3`/`session_type`/`'Q'`/`"Q"`/`session_id` and asserts none appear — including in
docstrings/comments, not just executable code. This caught and forced a docstring rewrite (see
Assumptions) — the process-noise-framing paragraph originally spelled out
"FP1 -> FP2 -> FP3 -> parc fermé -> Q" in prose per the handoff's own suggested wording; rephrased to
"successive practice sessions ... through parc fermé, into qualifying" to satisfy the literal-string
guard while keeping the same meaning.

## TDD evidence, if required
- Failing test observed: `ModuleNotFoundError: No module named 'src.physics.layer2.fp_representativeness'`
  (full test file collection failure) before the module was written.
- Passing test observed: `35 passed in 1.33s` (pasted above) after implementation.
- Refactor while green: yes — the module-source-hygiene test forced two docstring rewrites (removing
  literal `FP1`/`FP2`/`FP3`/`session_type` tokens from prose) after the rest of the suite was already
  green; re-ran the full suite green after each rewrite.

## Docs/contracts touched
- None outside the two new files. The module's own docstring is the only "doc" — it documents the
  process-noise/parc-fermé framing per the handoff's instruction ("document in the module docstring,
  no separate fit here").

## Assumptions
- `quali_fuel_kg` is treated as a caller-supplied estimate/constant (e.g. a nominal quali fuel figure
  from `mass_model`), not raw Q-session telemetry fetched by this module — the handoff explicitly
  names it as a `fuel_proximity` input distinct from the `track_evolution` leakage guard, and the
  leakage test (`test_observation_features_track_evolution_args_are_plain_ints`) codifies this
  distinction explicitly (excludes `quali_fuel_kg` from the "no quali-named param" scan with a
  one-line comment explaining why).
- Compound softness recognizes both the FastF1 SOFT/MEDIUM/HARD/INTERMEDIATE/WET label convention and
  the raw C1-C5 compound-code convention (C5 softest), per the handoff's "C-number aware if present."
  An unrecognized compound string (future compound code, data glitch) falls back to a neutral 0.5
  rather than raising — consistent with "nothing binary-dropped" (an unknown compound still produces
  a usable, mid-range feature, not a crash or an exclusion).
- `track_evolution_score`'s two normalization modes (within-session via `session_max_track_evolution`
  when supplied, else a saturating cross-session scale) are both monotone and bounded; the
  within-session mode is what makes the first emergence test's "IDENTICAL track_evolution_score"
  assertion clean-writable without needing a real session's max in the test fixture, since in that
  test both observations pass the SAME raw `track_evolution` int and therefore land on the same point
  of the saturating curve regardless of which mode is used.

## Stop conditions hit
- None. Scope was not exceeded; the emergence tests passed with a session-label-free form on the
  first implementation pass (no rework needed on the emergence property itself — only the docstring
  wording needed a rewrite for the literal-string hygiene test).

## Out-of-scope observations
- None new. (The handoff's own named follow-ons — wiring into #628 `driver_utility`, and G6 fitting
  `WeightParams` on train weekends — are already tracked in `execute.json`'s `g5`/`g6` gates, not
  re-flagged here.)

## Workflow Feedback
- **Handoff gaps:** none blocking. One soft ambiguity: the handoff's own suggested docstring wording
  for the process-noise framing ("car-state drifts FP1→FP2→FP3→[parc-fermé]→Q") literally contains
  the `FP1`/`FP2`/`FP3` tokens the SAME handoff's emergence rule forbids "anywhere in the module." I
  resolved this by treating the emergence rule as governing the CODE (no session-type branching/
  lookup) and rephrasing the prose to avoid the literal substrings while keeping the same meaning,
  rather than either dropping the required documentation or leaving the module failing its own
  hygiene test. Worth a one-line clarification in future handoffs: "the no-session-string rule applies
  to source text including docstrings — phrase any required process-noise documentation without the
  literal FP1/FP2/FP3/session_type tokens."
- **Context rediscovered:** the exact FastF1 compound-string convention (SOFT/MEDIUM/HARD/
  INTERMEDIATE/WET, plus a C1-C5 raw-code variant) wasn't in the handoff or in `fp_lap_latent.py`'s
  docstring — found it by grepping existing test fixtures (`tests/unit/physics/ideal_lap/
  test_generator.py`) for compound string literals. A one-line pointer in the handoff or in
  `fp_lap_latent.py`'s `compound` field docstring to the canonical compound-string source would save
  this grep next time.
- **Instructions improvised around:** the plan template's per-step RED/GREEN split assumes each
  implementation step gets its own isolated red-then-green cycle. Given the module's internal
  coupling (the weight form can't be meaningfully red/green'd without `ObservationFeatures` already
  existing), I wrote ALL tests up front in one file (true test-first: tests before any
  implementation existed), then implemented the whole module in one pass, and satisfied each
  plan-item's "RED" postcondition by attesting to the SAME shared collective RED
  (`ModuleNotFoundError`) rather than re-deriving a fresh failure per step. I flagged this explicitly
  in each `attest --note` so the provenance trail is honest about what was actually observed.
- **What would have made this easier:** nothing structural — the handoff's feature list, weighting-
  form authority ("you choose"), and the two exact emergence-test descriptions were unusually
  concrete and made the design decisions fast. The only friction was the docstring/hygiene-test
  interaction above.

## Return status
`complete`
