# Implementer Handoff — #525 G3 (durable unit-convention doc + AGENT_GUIDE reference)

## Gate
g3-implement — issue #525, branch `feat/physics-units-audit-525`

## Task
Promote the #525 audit into a **durable architecture reference doc** capturing the physics
parameter unit conventions **as actually unified in G2** (the rename has landed — use the NEW
names), and wire it into the agent guide. **Docs-only — no `src/` changes.**

Two deliverables:
1. **`docs/architecture/reference/physics-unit-conventions.md`** (new) — the unit-convention map.
2. A **single direct reference** to it from **`docs/AGENT_GUIDE.md`** + a review-and-update mandate.

## Authoritative inputs (READ FIRST)
- `.agent-work/525/AUDIT_MAP.md` — the producer→consumer map (NOTE: it uses the OLD names; the
  rename has since landed — translate to the NEW names by reading the current code).
- `.agent-work/525/NAMING_TABLE.md` — old→new name mapping + the `_g`/`_ms2` rationale.
- The **current code** is ground truth for the new names: `src/physics/physics_data_models.py`
  (the *Parameters dataclasses), `src/physics/layer2/estimate_store.py` (`EstimateRecord`),
  `src/physics/fit_store.py` (`FitRecord`), `src/physics/utilization/car_prior.py`
  (`_assemble_lateral`/`_build_longitudinal` — the conversion seams), `src/physics/constants.py`.
- `.agent-work/525/DECIDE_FIX_DECISIONS.md` — the ratified conventions.

## What the doc must contain
1. **The unit-convention table** — for every physics model parameter (lateral, longitudinal/power,
   braking, traction, coast, terrain): the **new field name**, its **unit**, the **producer**
   (where measured/fit), the **store column** (now migrated to the new name), the **consumer**
   (where applied), and the **canonical form / conversion seam**. Keep it a *short reference
   table*, not prose. Use the post-rename names (`lateral_mech_grip_g`/`_ms2`, `max_power_w`,
   `spec_drag_m2_kg`, `brake_decel_ms2`, etc.).
2. **The `_g` vs `_ms2` rationale** — a short note: the five-view producer/store hold a
   density/mass-agnostic grip *coefficient* (`_g`) because that is what is poolable across
   sessions; the consumer needs a per-session physical acceleration (`_ms2`); the single
   conversion seam is `car_prior._assemble_lateral` (lateral) / `_build_longitudinal`
   (longitudinal). (See NAMING_TABLE.md for the wording.)
3. **The fit-model vs apply-model split** (the key durable insight) — a short section laying out,
   side by side, **what the fit measures** vs **what the sim applies**, so latent divergences are
   visible not hidden:
   - **density:** fit = ρ-agnostic coefficient; apply = explicit ρ (correct factorization).
   - **banking (cosθ):** fit *normalizes it out* (`mu = |a_lat|/(g·cosθ)`); the apply side is
     **flat** (no cosθ re-application) → a known fit/apply asymmetry. **Cross-reference #527.**
   - **tyre-grip decay (`tyre_grip_decay_per_lap`) + `track_grip_mult`:** apply-side-only
     modulations the fit has no equivalent for (currently dormant on the C1 path).
     **Cross-reference #511.**
4. **The single conversion boundary** — state that `car_prior` is the ONE sanctioned place g→m/s²
   (lateral) and watts→W/kg (longitudinal) conversions happen, and the store-column migration
   (`scripts/migrate_physics_store_columns_525.py`) keeps the on-disk stores aligned.

## AGENT_GUIDE wiring
Add to `docs/AGENT_GUIDE.md` ONE direct reference to the new doc, with a standing instruction:
**any work that touches a physics model parameter (adds/renames/repurposes one, or changes a
producer/consumer/store) MUST review and update `docs/architecture/reference/physics-unit-conventions.md`
in the same gate.** Keep it to a short section/bullet — the guide is a thin top-level pointer.

## Close Criteria
- `docs/architecture/reference/physics-unit-conventions.md` exists, reflects the **post-G2 new
  names** (verified against current code, not the old AUDIT_MAP names), and contains the table +
  the `_g`/`_ms2` rationale + the fit-vs-apply split (with #527/#511 cross-refs).
- `docs/AGENT_GUIDE.md` carries one direct reference + the review-and-update mandate.
- The integrate check passes:
  `py -c "import pathlib,sys; ref='physics-unit-conventions'; doc=pathlib.Path('docs/architecture/reference/physics-unit-conventions.md'); g=pathlib.Path('docs/AGENT_GUIDE.md').read_text(encoding='utf-8'); sys.exit(0 if (doc.exists() and ref in g) else 1)"`
- `Last verified` date where `docs/DOCUMENTATION.md` requires it.

## Allowed Scope
`docs/architecture/reference/physics-unit-conventions.md` (new), `docs/AGENT_GUIDE.md`. No `src/`.

## Specific Exclusions
- No code changes. No new src behavior. Do not re-document the OLD names (the rename has landed).
- Do not fix the banking/k_tire model issues here (those are #527/#511) — only *document* them.

## Constraints
- Docs describe current truth (post-rename); one job per doc.
- Reference paths/issues must resolve (#527, #511, the migration script path).
- `py` not `python` in any example commands.

## Map Anchors (inbound)
- **Structural:** `docs/architecture/reference/physics-unit-conventions.md` (new),
  `docs/AGENT_GUIDE.md`, and it documents `struct:physics`/`.layer2`/`.utilization`.
- **Decision anchors:** `decision:ideal_lap_sim_two_sided_evaluator` (the conversion seams);
  `claim:lateral_car_prior_boundary_conversion` (now generalized/sanctioned — the doc records it).

## Required Evidence
The new doc; the AGENT_GUIDE diff; the integrate-check command passing; a note confirming the
names in the doc match current code (spot a couple, e.g. `EstimateRecord.lateral_mech_grip_g`,
`LongitudinalParameters.specific_power_w_kg`).

## Verification Commands
```bash
py -c "import pathlib,sys; ref='physics-unit-conventions'; doc=pathlib.Path('docs/architecture/reference/physics-unit-conventions.md'); g=pathlib.Path('docs/AGENT_GUIDE.md').read_text(encoding='utf-8'); sys.exit(0 if (doc.exists() and ref in g) else 1)"
```

## Suggested Model Tier
simple-bounded (Sonnet) — bounded docs task; the table + the two short rationale sections are
well-specified. Read the current code for the new names.

## Authority
The conventions + names are settled (G2 landed, user-ratified). You author the doc; you do not
change any convention or code.

## Stop Conditions
Stop if: a name in the code doesn't match NAMING_TABLE (report the discrepancy — don't paper over
it); or the doc would require a code change to be accurate.

## Operating Discipline
Your result file IS the deliverable — `.agent-work/525/crew-handoffs/g3-implement-result.md` must
exist with the evidence before you rest.

## Return Format
`IMPLEMENTER_RESULT`: the doc created, the AGENT_GUIDE reference added, the integrate-check result,
name-match confirmation, assumptions, stop conditions, out-of-scope finds, Workflow Feedback.
