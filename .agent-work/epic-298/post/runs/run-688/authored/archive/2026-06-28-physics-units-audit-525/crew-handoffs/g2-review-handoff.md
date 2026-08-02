# Reviewer Handoff — #525 G2 (unify + label + guard)

## Gate
g2-review — issue #525, branch `feat/physics-units-audit-525`

## What Was Implemented
The ratified #525 G2 scope (convention B, m/s² at consumer; consumer + live sim path
UNTOUCHED). 20 files, +261/−234. Mostly labelling + constant dedup + the friction_coupling
removal + one new output-level guard. See `.agent-work/525/DECIDE_FIX_DECISIONS.md` (ratified
scope) and `.agent-work/525/crew-handoffs/g2-implement-result.md` (the implementer's evidence).

## How to Inspect the Diff
```bash
git diff main...feat/physics-units-audit-525 -- src/ tests/
git log --oneline main..feat/physics-units-audit-525
```

## Task Statement
Nine in-scope items (full detail in `g2-implement-handoff.md`): OT-1 lateral A0/A2 suffix +
headers + promote `car_prior._assemble_lateral` to the sanctioned seam; OT-2 ρ label-only
(KEEP explicit, no removal); OT-3 one `GRAVITY_MS2`; OT-4 one `MASS_KG`; OT-5 longitudinal
label-only (keep conversion at car_prior); OT-7 one density fallback = 1.225; friction_coupling
verify-then-remove; OT-6 comment-fix only; the output-level guard.

## Close Criteria (each a review check — verify against the diff + source)
1. **No-regression / convention B honored:** confirm the lateral/longitudinal **consumer
   formulas are UNCHANGED** (`physics_data_models.lateral_capability`, `drag_acceleration`,
   `physics_simulator._compute_speed_caps`) — only docstrings/headers added, no math edits.
   Confirm **no ρ removal** and **no refit**. The C1 utilization numbers must not move.
2. **Rename consistency (no half-renamed seam):** every renamed field/column
   (`p_max`→`p_max_w`, `cda*`→`cda_m2`, `theta_P`→`theta_P_w_per_kg`, the lateral A0/A2
   suffixes) is updated consistently across producer→store→consumer and all readers/tests.
   Grep for the OLD names to confirm no stragglers (`git grep -n "DEFAULT_RHO"`,
   `git grep -n "\.theta_P\b"`, etc.).
3. **friction_coupling removal correctness:** verify it was genuinely **never invoked**
   (only instantiated) before removal — grep `\.friction_coupling\.` across src/ and confirm
   no call sites existed; confirm no dangling import/reference remains (`git grep -ni
   "friction_coupling\|FrictionCoupling"` → only expected absence). If the implementer's
   "never called" claim is wrong (a real call site existed), BLOCK.
4. **Constant dedup correctness:** `GRAVITY_MS2`/`MASS_KG`/density consolidations are
   **value-identical** (9.81, 808.0; density 1.20→**1.225** is the one intended value change —
   confirm it only affects the fallback path and any asserting test was updated). Confirm
   `braking_fit.G_MS2` is retired correctly (deprecated alias OR removed — and `car_prior`
   imports the new constant). No `# TODO(#525)` left (`git grep -n "TODO(#525)" src/`).
5. **Guard meaningfulness (scrutinize — this is the point of the run):**
   - It exercises the REAL path (car_prior → CapabilityEnvelope → PhysicsSimulator). ✓ confirm.
   - The **A0-at-boundary assert `[20,60] m/s²`** is the meaningful teeth (g-unit A0 ~3.2 fails
     it) — confirm it genuinely catches a #522-class g→m/s² mismatch.
   - The **top-speed band `[250,500]` km/h** passes a 436 km/h synthetic-Monza value. Confirm
     (a) 436 is the CURRENT value (consumer untouched, so unchanged from pre-G2 — not a new
     regression), and (b) the band still catches both historical bug classes (#522 ~100-150
     km/h < 250; #518 745 km/h > 500). Flag if the band is so wide it's vacuous for a ~1.2×
     (density) error — note whether the A0/corner asserts cover that gap.
   - Verify the **red-on-break demonstration** is genuine (the implementer says bypassing the
     conversion makes `20.0 <= 3.2` fail). 
   - Minor: the test docstring says "300–360 km/h" but the assert is `[250,500]` — a doc
     inconsistency worth a note (not necessarily a BLOCK).
   - Confirm it is NOT a per-param band-test matrix and uses NO units library.
6. **Suite green:** re-run `py -m pytest tests/unit/physics/ tests/known_answer/test_published_f1_data.py tests/property/test_physics_properties.py -q` and confirm GREEN.
7. **Scope:** physics-region only (no evo import); no shim/alias/dual-path; only the ratified
   items touched; braking/traction/coast/terrain math untouched except constant imports.

## Allowed Scope (of the implementation)
`src/physics/**`, `tests/unit/physics/**`, `tests/known_answer/test_published_f1_data.py`,
`tests/property/test_physics_properties.py`, `src/physics/__init__.py`, new
`src/physics/constants.py`.

## Constraints the Implementation Must Respect
- `constraint:physics_region_no_evo_import`; consumer formulas unchanged; no refit; no ρ
  removal; `k_tire` value unchanged (comment only); renames consistent.

## Map Anchors (inbound)
- **Structural:** `struct:physics`, `struct:physics.layer2`, `struct:physics.utilization`,
  the guard in `tests/known_answer/`.
- **Decision anchors:** `decision:ideal_lap_sim_two_sided_evaluator` (Review Trigger fires —
  the lateral conversion is promoted/labelled; flag for reconcile);
  `claim:lateral_car_prior_boundary_conversion` (now the sanctioned seam, not a TODO patch).

## Evidence Produced
Implementer reports: suite 639 passed / 6 skipped; guard red-on-break shown; simplification
limits clean; friction verdict = never-invoked-removed. **Re-verify the suite yourself.**

## Suggested Model Tier
stronger (Opus) — verifying rename consistency across producer/consumer, the friction-removal
safety, and (especially) the guard's genuine bite are judgment calls; a half-renamed seam or a
vacuous guard is the failure a green suite won't show.

## Stop Conditions
BLOCK if: a consumer formula/ρ/refit was changed; a rename is half-applied; friction_coupling
was actually called (removal unsafe); a constant dedup changed a value unintentionally; the
guard doesn't genuinely catch a units mismatch or isn't green; or any out-of-scope change.

## Return Format
Return REVIEW_RESULT: verdict (APPROVE or BLOCK), per-check findings (1–7, each citing the
source/diff you verified + the suite result you re-ran), blockers, out-of-scope observations,
and Workflow Feedback (`none` needs a run-specific reason).
