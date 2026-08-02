# Implementer Handoff

## Gate
g4 (σ-honesty wiring + explicit-unknown semantics — Tier-1 #2 wiring / #506 + Tier-1 #3)

## Task
Wire G1's `systematic_budget` into the store (replacing the static `SYSTEMATIC_FLOOR`), add a shared-systematic
floor to the pooled σ_μ (so pooling cannot claim sub-% season knowledge — the #506 core), and make the
explicit-unknown status real (resolved/unresolved per axis, reserved wide-σ for unresolved).

## Protected Intent
Honest σ over optimistic σ. The SHARED systematic is common-mode across a year's sessions → pooling CANNOT average
it away, so the pooled σ_μ must carry it as a floor. An unresolved axis must be distinguishable from a
confident-≈0 measured axis. The Phase-2 `weekend_state` consumers (read value/`{axis}_sigma` by name) must stay green.

## Test Mode
test-after allowed; add a property test + a pooled-floor test.

## Close Criteria
1. **Replace SYSTEMATIC_FLOOR with G1 per-session budget.** In `estimate_store.py`: each stored `{axis}_sigma`
   folds the per-session systematic TOTAL (fit-σ ⊕ systematic, from `systematic_budget(...)`) in quadrature —
   REPLACING the flat `SYSTEMATIC_FLOOR` dict + `_apply_floor`. Persist the SHARED component per axis in a new
   `{axis}_shared_sigma` slot (so pooling can floor on it). Before removing `SYSTEMATIC_FLOOR`, grep the tree for
   every importer/user of the symbol and migrate them (do not leave a dangling import). A0/A2 use G1's
   curvature/terrain-bounded systematic, not the blind 4%.
2. **Shared-systematic floor on pooled σ_μ.** In `pooling.py::pool_random_effects` add a `shared_floor` arg (per-
   param shared σ, absolute or relative — your call, document it); after the DerSimonian-Laird σ_μ is computed,
   floor it: `sigma_mu = sqrt(sigma_mu**2 + shared_floor**2)`. Thread it through `pool_driver.py::pool_store`:
   `pool_store` MUST always pass the per-param shared floor (derive it from the store's `{axis}_shared_sigma`
   column — e.g. the median/representative shared σ for that param across the pooled sessions). The floor must be
   wired NON-OPTIONALLY at the `pool_store` site (add a test that the wired path floors and that the floor is
   non-None there) — no call site may silently regress to unfloored. The floor is WITHIN-YEAR (matches
   `pool_store`'s `load(year=...)` within-year pooling); document cross-year mass-model drift as out-of-scope
   (handled separately by `fit_drift`).
3. **Explicit-unknown status (real).** Set `{axis}_status='resolved'` when the axis was genuinely measured this
   session (finite, non-degenerate σ from real data); `'unresolved'` for: `theta_R` (only a cold constant, never
   measured into the basis — always unresolved), a degenerate PowerDrag CdA/P_max (`power_drag_degenerate`), and
   any absent (None) lateral/coast view (→ A0/A2/coast axes unresolved). An unresolved axis persists the RESERVED
   wide σ (the G2 `UNRESOLVED_AXIS_SIGMA_FRAC` sentinel), NOT a confident ≈0. Treat a NULL status (legacy-row
   backfill, G2 finding) as `unresolved` on read.
4. **weekend_state decision stability.** The `{axis}_sigma` numeric distribution now shifts (per-session
   systematic replaces flat 4%; A0/A2 off the blind 4%). Characterize the weekend_state gate DECISIONS
   (gate_f6/floor/gate_spec) before/after on a fixture or a stored-row load, and confirm no UNINTENDED decision
   flips — OR document the expected/benign shift. This is a real silent-regression path; do not rely on
   test-green alone.

## Demonstration (real numbers, canonical Italy(Monza) RBR 2023 Q)
- Pooled σ_μ for CdA and P_max no longer drops below the shared floor as n grows (before/after: show σ_μ with n
  sessions WITHOUT the floor shrinking toward 0, vs WITH the floor plateauing at the shared systematic ~4.3%
  CdA / ~3.7% P_max). Use a stored `physics_estimates.db` season load
  (`C:/Programs/f1Brainz/data/physics_estimates.db`) if present; bounded timeout, document the path used.
- OPTIONAL (carry-forward G1 tc1): if a real Monza fit is feasible without stalling, re-attempt the live
  perturbation validation of the 3 back-solved systematic constants (THETA_SENS_CDA_REL, RHO_SENS_PMAX_REL,
  THETA_SENS_PMAX_REL). If it stalls again, note it — not a blocker for this gate.

## Property/unit tests (tests/unit/physics/layer2/)
- PROPERTY: `theta_R` reads `unresolved` with the reserved wide σ; a degenerate PowerDrag axis reads `unresolved`;
  an absent lateral view → A0/A2 `unresolved`; a genuinely-measured CdA reads `resolved` with a finite (not
  reserved-wide) σ — assert the unresolved σ is NUMERICALLY distinct (much larger) from the resolved one (the
  "unknown vs confident-zero" distinction is testable, not a comment).
- POOLED FLOOR: `pool_random_effects` with a `shared_floor` never returns σ_μ below the floor, even as n→large
  (σ_μ WITHOUT floor → 0; WITH floor → plateaus at floor). And a `pool_store` test that the shared floor is
  actually passed (no silent-unfloored path).
- Existing estimate_store + pooling + pool_driver + weekend_state tests stay GREEN.

## Allowed Scope
- EDIT `src/physics/layer2/estimate_store.py` (replace SYSTEMATIC_FLOOR wiring; add `{axis}_shared_sigma`; status
  resolution), `src/physics/layer2/pooling.py` (`pool_random_effects` shared_floor), `src/physics/layer2/pool_driver.py`
  (thread the floor). If a new `{axis}_shared_sigma` column is needed, add it to `EstimateRecord` (additive,
  nullable — same migration path as G2).
- EDIT tests under `tests/unit/physics/layer2/`. Pre-authorized to reconcile any existing estimate_store/pooling
  test whose scenario the σ-meaning change invalidates — name it in your result.
- READ-ONLY: `systematic_budget.py` (G1), `weekend_state/*` (confirm consumers; do not change them),
  `power_drag_view.py` (degenerate flag).

## Specific Exclusions
- Do NOT change the cross-view covariance population (G3 — done) beyond reading it if needed.
- Do NOT change production defaults, the production pinning CdA, circuits.yaml, or gold.
- Do NOT change `weekend_state/*` source (only characterize its decisions). No data/*.db writes.

## Constraints
- Honest-wide σ; the pooled σ_μ MUST carry the shared floor (pooling cannot average away a common-mode bias).
- `{axis}_sigma` column names UNCHANGED (only their meaning tightens) — consumers read by name.
- Additive schema migration only. `constraint:physics_region_no_evo_import`. ASCII; `py`.

## Map Anchors (inbound)
- Structural: `struct:physics.layer2` — estimate_store.py (SYSTEMATIC_FLOOR/record_from_estimate),
  pooling.py::pool_random_effects, pool_driver.py::pool_store.
- Capability: data-driven systematic (#506); pooled-σ_μ shared floor; explicit-unknown status.
- Constraint: pooling cannot average away a shared bias (the #506 core).
- Decision anchor: pooled-σ_μ shared-floor mechanism (PLAN_ALTERNATIVES B1 — additive quadrature floor after
  shrinkage; a common-mode bias is rank-1 so the two-level model collapses to this).
- Evidence: pooled σ_μ(CdA/P_max) floored by shared systematic (before/after); unresolved distinguishable from
  confident-zero (property test).
- Map confidence flag: worktree editable-.pth trap.

## Deliverable Path Check
- Committed — estimate_store.py, pooling.py, pool_driver.py, tests (edits, tracked).
- Local-only — any demo/characterization script under `.agent-work/...` (gitignored; state it).

## Required Evidence
- `py -m pytest tests/unit/physics/layer2/ tests/unit/physics/weekend_state/ -q` — full pass; paste tail.
- The pooled-floor before/after (σ_μ shrinking vs plateauing at the shared floor) on CdA/P_max, real numbers.
- The weekend_state decision-stability note (no unintended flips, or the documented benign shift).
- The property-test output (unresolved σ ≫ resolved σ).

## Verification Commands
```bash
cd /c/Programs/f1-627
py -c "import src.physics.layer2.pooling as m; print(m.__file__)"   # assert under C:\Programs\f1-627
py -m pytest tests/unit/physics/layer2/ tests/unit/physics/weekend_state/ -q
```

## Suggested Model Tier
stronger — the pooled-floor honesty (must not shrink below the shared systematic), the SYSTEMATIC_FLOOR
replacement, and the status semantics are load-bearing and interlocking.

## Authority
Tier/scope frozen by the launch order. You decide the shared_floor units + the `{axis}_shared_sigma` derivation +
the status-resolution predicate (document them). You must NOT change production defaults, the pinning CdA, or
weekend_state source. If replacing SYSTEMATIC_FLOOR would break a consumer you cannot keep green additively, STOP
and return that as a blocker (the Commander floats a store-change-breaks-consumer decision).

## Worktree Isolation (CRITICAL)
cwd MUST be `C:/Programs/f1-627`. Assert `py -c "import src.physics.layer2.pooling as m; print(m.__file__)"`
prints under `C:\Programs\f1-627` before any real-data run. Data DBs are absolute paths into
`C:/Programs/f1Brainz/data/` (physics_estimates.db). Do NOT commit data/*.db (`git checkout -- data/` after).

## Stop Conditions
Stop and return (blocker) if: replacing SYSTEMATIC_FLOOR breaks a consumer you cannot keep green additively; the
pooled floor cannot be wired non-optionally; a production default must change; or a decision beyond the documented
ones is needed.

## Return Format
Write `IMPLEMENTER_RESULT` to `.agent-work/627-unified-basis/g4-implement/IMPLEMENTER_RESULT.md` AND deliver a
summary to ShipF-627 (route to team-lead if unaddressable) via SendMessage before ending your turn: completed
slice, files changed, the shared_floor design + status predicate, the pooled-floor before/after (real numbers),
the weekend_state decision-stability note, test tail, assumptions, stop conditions, out-of-scope observations,
workflow feedback.
