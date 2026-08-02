# Implementer Handoff — #525 G1 audit (evidence-only)

## Gate
g1-implement (audit) — issue #525, branch `feat/physics-units-audit-525`

## Task
**EVIDENCE-ONLY. Produce no code changes.** Audit the unit convention of every physics
model parameter across all channels, producer→consumer, by reading source directly, and
write two work-area artifacts:

1. `.agent-work/525/AUDIT_MAP.md` — a producer→consumer unit-convention map.
2. `.agent-work/525/AUDIT_DISPOSITIONS.md` — an inventory of overloaded/ambiguous terms,
   each with a fix-local-vs-route-out disposition, **plus** an A-vs-B canonical-lateral
   recommendation with honest blast-radius, **plus** the ρ-in-aero refit-vs-representation
   call.

This is the front-loaded thinking for issue #525: a units-convention audit driven by THREE
units-collision incidents in a month (#518 `p_max` watts→W/kg; #522 lateral g→m/s²; the
two-producer lateral split). The goal is **de-overloading/disambiguation**, not a units
philosophy — find terms that silently mean different things in different places.

## Protected Intent
The audit map must be **complete and accurate against source** — it is the basis on which
the human will rule (at a decide-fix checkpoint) which fixes happen in this run vs route to
separate issues. A missed producer/consumer or a wrong blast-radius would mis-inform that
ruling. Treat the architecture packet as a starting index, **not** ground truth — verify
every convention claim by reading the cited code.

## Test Mode
inspection-only — this gate writes NO code and runs NO tests on src/. (You MAY run small
read-only throwaway probes to confirm a numeric magnitude if useful, but the deliverable is
the two markdown artifacts.)

## Close Criteria
- `AUDIT_MAP.md` covers **every** physics model parameter at **each** producer and **each**
  consumer, with `file:symbol` citations and the **exact formula + unit** each side assumes.
  Channels to cover (find any I missed):
  - **lateral:** A0, A2, ceiling, g_track, k_tire
  - **longitudinal/power:** theta_P, theta_D, theta_R, p_max, CdA
  - **braking:** a_b, b_b
  - **traction:** the traction frontier params
  - **coast:** rolling-resistance + coast-drag params
  - **terrain:** theta, z, banking
- `AUDIT_DISPOSITIONS.md` inventories every **overloaded/ambiguous** term found — at minimum
  the two lateral conventions, ρ-in-aero (`A2·ρ·v²` vs `A2·v²`), the duplicated `G_MS2`
  constant — each with: where it's overloaded, the de-overloading options, and a proposed
  disposition (**fix-local-in-this-run** vs **route-to-separate-issue**), with reasoning.
- A **canonical lateral convention recommendation**: A (unitless/g-coefficient canonical
  everywhere — consumer moves to g-units, both producers feed g-units) vs B (m/s² canonical
  at the consumer — producers normalize up to it). Include an **honest blast-radius**:
  enumerate every file and test touched, and **independently confirm** whether the live
  `sim_evaluator` / `fit_batch` path consumes the lateral consumer (this is the fact whose
  from-memory version got #522's first fix BLOCKED — verify it from source, don't assume).
- A **ρ-in-aero disposition**: is unifying the density treatment a pure
  representation/conversion change, or does it require **re-deriving a fitted parameter**
  (a refit)? If a refit, say so explicitly — that triggers a stop-and-route decision.

## Allowed Scope
Read-only across `src/physics/**` (especially the seams below), `tests/` (to see what
re-baselines on a convention change), and the architecture packet. **Write only** the two
`.agent-work/525/*.md` artifacts + your result file. **No edits to `src/` or `tests/`.**

## Specific Exclusions
- No code fixes, no renames, no test edits — those are G2 (after the human ratifies scope).
- Do not pick the canonical convention as a decision — **recommend** it; the human rules at
  the checkpoint.
- No re-fitting and no proposing to re-fit as in-scope — if ρ needs a refit, flag it for
  routing out.

## Constraints
- EVIDENCE-ONLY: no `src/`/`tests/` edits this gate.
- Stay physics-region; do not introduce or propose any evo-region coupling
  (`constraint:physics_region_no_evo_import`).
- Cite `file:symbol` (and line where practical) from source for **every** convention claim.
- `py` is the launcher on this machine, never `python`.

## Map Anchors (inbound)
- **Structural seams to start from (verify + expand from source):**
  - `src/physics/layer2/lateral_view.py` — `LateralView`: convention **B** producer. Fits
    A0/A2 as **dimensionless g-unit grip coefficients**; `a_lat = (A0 + A2·v²)·g`, no ρ.
  - `src/physics/lateral_envelope.py` — `LateralEnvelopeFit`: convention **A** producer
    (legacy single-session), m/s², `default_A0≈30`, density-explicit aero `A2·ρ·v²`.
  - `src/physics/physics_data_models.py` — `LateralParameters.lateral_capability` (the
    SHARED consumer, ~line 237), `LongitudinalParameters`, `BrakingParameters`,
    `TractionParameters`, `PhysicsParameterSet`. Document what units each field is read as.
  - `src/physics/physics_simulator.py` — `PhysicsSimulator._compute_speed_caps` /
    `_gsat_ceiling` (consume lateral params); how it reads A0/A2 and whether it applies ρ.
  - `src/physics/utilization/car_prior.py` — `_assemble_lateral` (the #522 g→m/s² boundary
    conversion: `A0·G`, `A2·G/air_density`, Jacobian `diag(G, G/air_density)`) and
    `_build_longitudinal` (the #518 `p_max/MASS_KG` watts→W/kg conversion). These are the
    localized patches #525 may retire/generalize.
  - `src/physics/braking_fit.py` — `G_MS2` constant (and `MASS_KG` in
    `src/physics/longitudinal_fit.py`): confirm the `G_MS2` duplication the issue cites.
  - `src/physics/layer2/estimate_store.py` — the five-view store schema: which columns
    (A0/A2/p_max/…) in which units. Convention B's store-write boundary.
  - `src/physics/sim_evaluator.py`, `src/physics/fit_batch.py`, `src/physics/session_fit.py`
    — convention-A consumers; **confirm from source** whether they read `LateralParameters`.
  - `src/physics/capability_envelope.py` — `CapabilityEnvelope.from_parameters`: how params
    flow into the gg-v envelope.
- **Capability:** physics parameter measurement / capability API; ideal-lap simulation;
  driver utilization (C1).
- **Constraints:** `constraint:physics_region_no_evo_import`; physics change needs explicit
  units/bounds (this audit feeds an L1–L4-evidenced change in G2).
- **Decision anchors:** `decision:ideal_lap_sim_two_sided_evaluator` (records both car_prior
  boundary conversions); `claim:lateral_car_prior_boundary_conversion` (the exact surface
  G2 retires/generalizes — read `docs/architecture/overlays/constraints.yml` for its text).
- **Map confidence flags:** the physics packet was reconciled in #522 (high confidence) but
  treat source as ground truth.

## Required Evidence
The two artifacts (`AUDIT_MAP.md`, `AUDIT_DISPOSITIONS.md`), plus an `IMPLEMENTER_RESULT`
file at `.agent-work/525/crew-handoffs/g1-implement-result.md` summarizing findings, the
A/B recommendation + blast-radius, the ρ call, and any channel you found beyond my list.

## Verification Commands
```bash
# evidence-only gate; the deliverables are the markdown artifacts. Confirm they exist:
py -c "import pathlib,sys; sys.exit(0 if (pathlib.Path('.agent-work/525/AUDIT_MAP.md').exists() and pathlib.Path('.agent-work/525/AUDIT_DISPOSITIONS.md').exists()) else 1)"
# confirm you changed NO tracked src/tests:
git status --porcelain src/ tests/
```

## Suggested Model Tier
stronger (Opus) — the canonical-convention recommendation, the blast-radius, and the ρ
refit-vs-representation judgment are genuinely analytical and load-bearing for the human's
checkpoint ruling.

## Authority
- You **recommend**; you do not decide the canonical convention or what's in-scope — the
  human rules at the decide-fix checkpoint.
- North-star framing (de-overload, not unitless-dogma; stop-and-evaluate if a fix needs a
  refit; nominal cleanup is fine in G2 but NOT this gate) is set by the user (see
  `.agent-work/525/PROBLEM_STATEMENT.md`).

## Stop Conditions
Stop and return if: you cannot read a cited seam, the audit would require a code change to
answer a question, or you hit a decision outside "recommend, don't decide."

## Operating Discipline
Your **result file is the deliverable** — you are not done until
`.agent-work/525/AUDIT_MAP.md`, `.agent-work/525/AUDIT_DISPOSITIONS.md`, and the result
file all exist on disk. Do not go idle with them unwritten.

## Return Format
Return `IMPLEMENTER_RESULT`: artifacts produced, the A/B recommendation + blast-radius, the
ρ disposition, overloaded-term inventory summary, any channels beyond my list, assumptions,
stop conditions hit, out-of-scope observations, and **Workflow Feedback** (what in this
handoff made the work harder than it needed to be; `none` requires a run-specific reason).
