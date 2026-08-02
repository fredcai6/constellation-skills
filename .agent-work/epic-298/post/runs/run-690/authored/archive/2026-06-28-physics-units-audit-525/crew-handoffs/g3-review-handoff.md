# Reviewer Handoff — #525 G3 (durable unit-convention doc + AGENT_GUIDE reference)

## Gate
g3-review — issue #525, branch `feat/physics-units-audit-525`. **Docs-only gate.**

## What Was Implemented
A new durable reference doc `docs/architecture/reference/physics-unit-conventions.md` (unit table
+ `_g`/`_ms2` rationale + fit-vs-apply model split + the single conversion boundary), and a
direct reference to it from `docs/AGENT_GUIDE.md` with a review-and-update-in-the-same-gate
mandate. Result: `.agent-work/525/crew-handoffs/g3-implement-result.md`.

## How to Inspect
```bash
git diff HEAD -- docs/   # (the G2 code is already committed at ca4abcfc; G3 docs are uncommitted)
```

## Close Criteria (each a review check)
1. **Doc accuracy vs current code (most important).** The parameter names in the table must
   match the **post-G2 renamed** fields — spot-check several against source:
   `EstimateRecord.lateral_mech_grip_g` (`estimate_store.py`), `LongitudinalParameters.specific_power_w_kg`
   + `BrakingParameters.brake_decel_ms2` (`physics_data_models.py`), `FitRecord.spec_drag_m2_kg`
   (`fit_store.py`), the conversion seam in `car_prior._assemble_lateral`/`_build_longitudinal`,
   `constants.GRAVITY_MS2`. No OLD names (`A0`, `p_max`, `theta_P`) presented as current.
2. **The `_g`/`_ms2` rationale is correct** — producer/store = density/mass-agnostic grip
   coefficient (poolable); consumer = per-session m/s²; one seam at `car_prior`.
3. **The fit-vs-apply split section is accurate** — density (ρ-agnostic fit vs explicit-ρ apply),
   banking (fit normalizes `cosθ` out, apply is flat → cross-ref **#527**), tyre-decay/track-grip
   (apply-only → cross-ref **#511**). Confirm #527 and #511 are the right issues.
3. **AGENT_GUIDE wiring** — `docs/AGENT_GUIDE.md` carries ONE direct reference to the new doc +
   the standing review-and-update mandate; the reference resolves; it stays a thin pointer.
4. **Docs-review blockers** — correct repo/paths/commands; referenced files/issues exist;
   reflects current (post-rename) workflow; `Last verified` present (the doc has `2026-06-27`).
5. **Docs-only** — no `src/` changes in the diff.

## Constraints
Docs describe current truth (post-rename); one job per doc; `py` not `python` in examples.

## Map Anchors (inbound)
- **Structural:** `docs/architecture/reference/physics-unit-conventions.md`, `docs/AGENT_GUIDE.md`.
- **Decision anchors:** `decision:ideal_lap_sim_two_sided_evaluator`,
  `claim:lateral_car_prior_boundary_conversion` (the doc records the sanctioned seam).

## Evidence Produced
Integrate check passes (`physics-unit-conventions` doc exists + referenced from AGENT_GUIDE).
Implementer reports names verified vs code.

## Suggested Model Tier
simple-bounded (Sonnet) — docs accuracy review.

## Stop Conditions
BLOCK if: the doc presents OLD names as current, a cross-ref (#527/#511) is wrong, the AGENT_GUIDE
reference/mandate is missing or doesn't resolve, or a `src/` change slipped in.

## Return Format
REVIEW_RESULT: verdict (APPROVE or BLOCK), per-check findings (1–5, citing the doc lines/source
you verified), blockers, out-of-scope observations, Workflow Feedback.
