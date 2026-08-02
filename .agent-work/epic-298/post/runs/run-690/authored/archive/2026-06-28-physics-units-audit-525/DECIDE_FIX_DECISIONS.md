# Decide-fix checkpoint — ratified decisions (#525)

Date: 2026-06-27. Authority: human (user). Basis: G1 audit (`AUDIT_MAP.md` +
`AUDIT_DISPOSITIONS.md`), APPROVED by Opus review.

## D1 — Canonical lateral convention: **B (m/s² at the consumer)**
The shared `LateralParameters` consumer and the live `sim_evaluator`/`fit_batch` path stay
**untouched** (both already m/s²; reviewer independently confirmed the live path does not
route through `car_prior`/the g-unit store). The g→m/s² conversion already at
`car_prior._assemble_lateral` is **promoted to the one sanctioned, labelled seam** (retire
the `# TODO(#525)`). Convention A (g-units everywhere) rejected: it would move the proven
sim path + blessed fixtures = full numeric re-baseline, too much risk for an alignment run.

## D2 — ρ-in-aero: **keep ρ explicit at the consumer; de-overload by LABELLING (no removal)**
Overriding the audit's "drop ρ" sub-suggestion. Aero grip genuinely scales with ρ·v²; the
consumer's `A2·ρ·v²` is physically correct and the legacy producer already matches it.
Removing ρ would make the parameter density-blind (the altitude/temperature trap) or force a
legacy refit. Confirmed pure-representation/no-refit. Fix = **name it honestly**: the
five-view `A2` is a session-ρ-folded grip slope; `car_prior` un-folds it (`/air_density`) to
the ρ-independent coefficient the consumer wants. Label both; delete nothing.

## In-scope for G2 (ratified)
- **OT-1** lateral → adopt B: unit-suffix `A0`/`A2` (g-unit producer/store vs m/s² consumer)
  + co-located unit headers; promote `car_prior._assemble_lateral` to the sanctioned seam.
- **OT-2** ρ → label per D2 (five-view A2 ρ-folded vs canonical ρ-independent), keep explicit.
- **OT-3** gravity → one `GRAVITY_MS2 = 9.81` in a neutral home; retire the mis-homed
  `braking_fit.G_MS2` and the ≥8 scattered `9.81`/`_G` literals (import the constant).
- **OT-4** `MASS_KG` → single definition (`longitudinal_fit`); `session_fit` imports it.
- **OT-5** longitudinal store → **label only**: suffix `p_max_w`/`cda_m2` (store) +
  `theta_P_w_per_kg` (consumer) + headers. **Keep the conversion at `car_prior`** (do NOT
  relocate to the store-write — no de-overload gain, touches the batch/store schema).
- **OT-7** air-density fallback → one constant, value **1.225** (ISA standard); retire the
  `session_fit.DEFAULT_RHO=1.20` divergence. (Moved in-scope per user.)
- **friction_coupling.py removal** → it is superseded-but-LIVE (imported+instantiated in
  `parameter_estimator.py`, re-exported in `__init__.py`, 3 test imports). **Verify it is
  never actually invoked, THEN remove** the instantiation + import + export + its dedicated
  test + the two test references. **STOP and route out if it turns out to be actually called**
  (do not rip out live behavior under a units run). (Moved in-scope per user.)
- **OT-6 comment-fix only** → fix `car_prior.py:57` (falsely claims `k_tire=0.0` "matches the
  single-session convention" — single-session is `0.01`). Do NOT change the `k_tire` value.
- **The one output-level guard** → extend `tests/known_answer/test_published_f1_data.py`:
  ideal-lap top speed + a representative corner cap must land in a physical band (green now,
  fails on a #518/#522-class mismatch). No per-param band matrix, no units library.

## Routed out
- **OT-6 value unification** (k_tire `0.0` vs `0.01` decay) → **modelling decision**, would
  shift C1 numbers. Posted as a comment on **#511** (grip-evolution state) at discovery time.
  No new issue.
- Triage candidates tc1 (OT-6)/tc2 (OT-7)/tc3 (friction_coupling) are now all resolved within
  this run (OT-6→#511 comment + G2 comment-fix; OT-7→G2; friction→G2) — record at triage,
  do not file as separate issues.

## G3 (unchanged)
Durable doc `docs/architecture/reference/physics-unit-conventions.md` + one direct reference
from `docs/AGENT_GUIDE.md` with the review-and-update-in-the-same-gate mandate.
