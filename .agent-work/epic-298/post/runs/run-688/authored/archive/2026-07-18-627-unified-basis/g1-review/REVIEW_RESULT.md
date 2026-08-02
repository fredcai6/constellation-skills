# Review Result

Status values follow `skills/workbench/references/status-model.md`.

## Assigned Gate
`g1 (systematic-budget module — Tier-1 #2 / #506 analytic engine)`

## Result
`APPROVE`

## Handoff compliance
The module `src/physics/layer2/systematic_budget.py` delivers the documented public function
`systematic_budget(params, *, mass_kg, rho, theta_R, cda_pin_sigma) -> dict[str, tuple[shared_rel, session_varying_rel]]`
covering all 8 required axes (cda, p_max, a_b, b_b, a_t, b_t, A0, A2), using analytic (no re-fit)
sensitivities as specified. Verified independently against source, not just against the module's
own docstring claims:

- **Mass 1:1 (CdA, P_max):** `PowerDragView.design()` (power_drag_view.py:203-205) shows both
  design columns scale as `1/mass_kg`; re-derived that the OLS solution therefore scales linearly
  with mass for the joint (unpinned) fit path — the exact path `nuisance_sensitivity.py` uses.
  Matches `MASS_SENS_CDA = MASS_SENS_PMAX = 1.0` exactly.
- **CdA-pin Jacobian (braking/traction):** `cda_frontier_jacobian`'s own docstring
  (braking_view.py:125-158) documents the healthy-fit slope sensitivity `j ≈ rho/(2m)` the module
  reuses directly — not re-derived, correctly cited.
- **theta_R additive intercept:** `theta_R.sigma**2` is added only to `cov[0,0]` in both
  `traction_view.py:154` and `braking_view.py:248` — confirms the module's exact 1:1-intercept /
  0-slope theta_R claim.
- **A0/A2 carry zero of the 4 nuisances:** `lateral_view.py` has zero references to
  `theta_R`/`mass_kg`/`rho` anywhere — provable by inspection, matches the module's claim and is
  the most Protected-Intent-critical assertion ("do NOT reuse the blind 4%").
- **SYSTEMATIC_FLOOR citations** (estimate_store.py:53-57) match the module's "measured 4.3%
  (mass+rho)" / "measured 3.7% (mass-dominated)" / "A0 mass/rho cancel" citations verbatim.

Split rule (SHARED = `quali_mass(year)` model bias + `theta_R=0.15` literal; SESSION-VARYING =
per-session rho + fuel) is documented with rationale in the module docstring as required.

## Scope drift
None. `git status --porcelain` shows exactly 3 untracked files (`systematic_budget.py` + 2 test
files) plus the expected `.agent-work/` workflow dir — no `estimate_store.py`/`pooling.py`/
`pool_driver.py`/view file touched, no `data/*.db` path, no `circuits.yaml`/gold bundle change.
`git check-ignore` exits 1 (not ignored) for all 3 new files. `constraint:physics_region_no_evo_import`
verified by grep: only stdlib `typing`/`__future__` imports, zero `evo` references.

## Evidence verdict
Re-ran both required commands independently:
- `py -m pytest tests/unit/physics/layer2/test_systematic_budget.py -q` → **18 passed**
- `py -m pytest tests/unit/physics/layer2/ -q -k systematic` → **20 passed, 684 deselected**

Both match the pasted IMPLEMENTER_RESULT tails exactly.

**Key judgment — fallback validation adequacy (the reviewer's central charge):**

The live perturbation re-run genuinely stalled (plausible, specific evidence in IMPLEMENTER_RESULT:
CPU-sampling data across two independent ~10min/~4min attempts, consistent with the known
concurrent-agent contention in this session). The implementer invoked the handoff-sanctioned
fallback. Split assessment:

1. **Adequate — independently closed-form-tested:** mass 1:1 sensitivity, the CdA-pin Jacobian for
   braking/traction, theta_R's exact additive-intercept form, and A0/A2's provable-zero null. These
   are genuinely derived from source (verified above), not merely asserted, and the unit tests
   exercise the actual implementation behavior (e.g. `test_cda_mass_sensitivity_is_one_to_one`
   checks the coded 1/mass scaling, not just the constant's value).

2. **Not adequate — back-solved, not closed-form:** `THETA_SENS_CDA_REL`, `RHO_SENS_PMAX_REL`,
   `THETA_SENS_PMAX_REL` have **no clean closed form by the module's own admission** and are
   algebraically back-solved from the single pre-existing `SYSTEMATIC_FLOOR` reference number
   (4.3%/3.7%). Independently recomputed the derivation arithmetic myself:
   `sqrt(4.3² − (100·20/808)² − 1.5²)/100 = 0.0318012` (literal: `0.031801` ✓) and
   `sqrt(3.7² − (100·20/808)²)/√2/100 = 0.0194463` (literal: `0.019446` ✓) — no transcription bug,
   but **no unit test recomputes this formula against the literal** (a cheap, currently-missing
   regression guard). More materially: theta_R's CdA contribution is ~55% of the CdA total's
   variance, and the P_max rho/theta_R split is an explicitly-admitted arbitrary 50/50 (one
   equation, two unknowns) — so the **SHARED-vs-SESSION split** for CdA/P_max, which is the
   Protected-Intent-critical "must be computed, not guessed" deliverable, rests on channel
   attribution that is **not independently validated**, only the *total* is anchored to a real
   (if old) historical measurement.

**Verdict on this judgment:** adequate to pass g1's own close criteria. The reproduction claim is
not "ONLY" a bare constant-equals-constant assertion — the mass and rho-width channels are
genuinely computed from real per-session inputs (`quali_mass(2023)=808`, real measured Monza
rho=1.148028) and real documented sensitivity magnitudes. The gap is extensively self-disclosed in
three places (module docstring, IMPLEMENTER_RESULT Map Impact, and a named triage candidate), and
the fallback path was explicitly pre-authorized by the handoff for exactly this scenario. But this
is a **load-bearing gap that G4 must not silently inherit as validated fact** — see triage
candidate below.

## Code/doc quality
- ASCII-safe: byte-level ascii-decode verified clean on all 3 files.
- `py -m src.utils.simplification_limits --paths <3 files>` → PASS.
- Module-level state is immutable float/tuple constants only — matches CREW_CONTEXT's
  "module scope in `src/` is for immutable constants/config only."
- No `print()`/mutable state/DB singleton in the production module (print is confined to the test
  file's `if __name__=="__main__"` manual harness, which CREW_CONTEXT sanctions).
- Validation errors name field + expectation + actual value, matching project convention.
- Physics truth-anchoring: L1 (analytical, mass/theta_R) and L2 (invariant/known-answer, A0/A2
  null) are met at the highest applicable level for the closed-form axes.

## Map impact verdict
- **Evidence supports claimed change:** yes, verified independently above.
- **Constraints not violated:** yes — `constraint:physics_region_no_evo_import` grep-confirmed.
- **Notes match the diff:** yes — additive-only new module under `struct:physics.layer2`, no
  existing behavior changed (confirmed via `git status`).
- **Decision candidates surfaced:** yes — `MASS_SHARED_VARIANCE_FRACTION=0.8` and the 3 back-solved
  constants are correctly flagged as decision/triage items rather than silently baked in as fact.
- **Durable context routed:** yes, and reinforced here — flagged `tc1` on the survey independently
  of the implementer's own note (see below), since it gates whether G4 can trust the CdA/P_max
  shared/session split.

## Reconciliation check
No divergence from recorded architecture. Purely additive, standalone module; not wired into
estimate_store/pooling/pool_driver/views (explicitly G4's job, confirmed untouched).

## Blockers
- none

## Out-of-scope observations
- **Triage candidate (flagged as `tc1` on the review survey):** re-run `run_live_monza_perturbation_validation`
  (or `scripts/nuisance_sensitivity.py` directly) on Monza (Italy) RBR 2023 Q once concurrent-agent
  contention has cleared, to independently confirm/replace `THETA_SENS_CDA_REL`,
  `RHO_SENS_PMAX_REL`, `THETA_SENS_PMAX_REL` before G4 wires `systematic_budget()` into
  estimate_store/pooling. Also confirm `MASS_SHARED_VARIANCE_FRACTION=0.8` at architecture review.
  Already self-flagged by the implementer; independently confirmed here as load-bearing and
  should gate G4's trust in the CdA/P_max split, not be silently inherited.
- **Fowler pass (`r6-fowler`, record at `.agent-work/627-unified-basis/g1-review/FOWLER_PASS.json`,
  `verify_fowler_pass.py` exit 0):** 3 non-blocking quality flags —
  1. *duplicated-code* — `_cda_pmax_budget` repeats a small mass-split+combine pattern for cda and
     p_max; a helper would DRY it, but current form is small/readable.
  2. *primitive-obsession* — public return type is a bare `tuple[float, float]` for
     `(shared_rel, session_varying_rel)` instead of a `NamedTuple`, risking an index-order mistake
     at the G4 call site; inconsistent with the module's own sibling types (`ParamPrior`) which ARE
     typed. Recommend a `NamedTuple` before G4 locks in the tuple-index convention.
  3. *speculative-generality* — `theta_R` kwarg is accepted+validated but its point value is unused
     in the magnitude computation (documented as "for future support"); mild tension with the
     project's no-speculative-abstraction doctrine.
  None are correctness defects.

## Workflow Feedback

- **Handoff gaps:** none material — the handoff's explicit pre-authorization of the fallback path
  ("If telemetry is genuinely unreachable, attest that instead...") combined with its precise
  framing of "acceptable IF independently unit-tested against its closed form" gave a clear,
  actionable bar to judge against. One small gap: the bar assumes every frozen constant HAS a
  closed form to test against, but the module's own docstring is explicit that
  `THETA_SENS_CDA_REL`/`RHO_SENS_PMAX_REL`/`THETA_SENS_PMAX_REL` have **no clean closed form by
  design** — the handoff's phrasing doesn't anticipate "there is no closed form, only a back-solve
  from history," which is a subtly different (and harder to adjudicate) case than "the closed form
  exists but wasn't tested." Naming that third case explicitly in a future handoff would sharpen
  the reviewer's bar.
- **Context rediscovered:** none — the handoff's Map Anchors and the implementer's own
  IMPLEMENTER_RESULT were unusually thorough (exact source-line citations for every claim), so
  independent verification against source was fast and did not require rediscovering anything not
  already pointed to.
- **Instructions improvised around:** none — the constellation-reviewer skill's engine-drive loop,
  the REVIEW_SURVEY template, and the Fowler-pass rail all applied cleanly to this gate with no
  workarounds needed.
- **What would have made this easier:** the handoff's Verification Commands section could have
  named the two commands to independently recompute (e.g. the `sqrt(4.3² − mass_rel² − 1.5²)`
  arithmetic) as an expected reviewer due-diligence step — I did this ad hoc via `py -c`, but a
  named one-liner in the handoff would make it reproducible/citable evidence rather than an
  improvised check.

## Return status
`complete`
