# Implementation Result

Status values follow `skills/workbench/references/status-model.md`.

## Assigned gate
g4 (sigma-honesty wiring + explicit-unknown semantics -- Tier-1 #2 wiring / #506 + Tier-1 #3)

## Completed slice
All four close-criteria items landed:
1. Replaced the static `SYSTEMATIC_FLOOR` dict + `_apply_floor` in `estimate_store.py` with a
   guarded per-session call into G1's `systematic_budget()`, folded in quadrature into every
   covered axis's stored `{axis}_sigma` (cda incl. `power_drag_area_m2`, p_max, a_b, b_b, a_t,
   b_t, A0, A2 -- 8 of the 9 tracked axes; theta_R has no stored value/sigma column at all, see
   below). The SHARED component is persisted per axis in a new `{axis}_shared_sigma` column (9
   new nullable columns, additive schema).
2. Added a `shared_floor` arg to `pooling.pool_random_effects` (absolute units, floors
   `sigma_mu` in quadrature after DerSimonian-Laird shrinkage) and threaded it NON-OPTIONALLY
   through `pool_driver.pool_store` (derived per constructor+param from the median of the
   store's `{axis}_shared_sigma` column; gracefully 0.0, never omitted, when the store has no
   shared-sigma data for that param).
3. Real explicit-unknown status: `_axis_statuses()` computes `resolved`/`unresolved` per axis
   from the actual session inputs (view presence, PowerDrag degeneracy); `theta_R_status` is
   ALWAYS `unresolved` (never a fitted value). Added `normalize_axis_status()` (NULL -> treated
   as `unresolved`) and `effective_axis_sigma()` (the real consumer contract: an unresolved axis
   is widened to at least `UNRESOLVED_AXIS_SIGMA_FRAC` of its own magnitude, synthesizing a
   reserved-wide sigma from a caller-supplied reference value when no stored point value exists
   at all -- e.g. theta_R).
4. Characterized weekend_state gate decisions before/after on the REAL stored
   `physics_estimates.db` (1562 Q ok rows): **zero decision flips across all 11 F6 axes, verdict
   unchanged (PASS 9/11 both before and after)**. See "Weekend-state decision stability" below.

## Scope
**Files changed:**
- `src/physics/layer2/estimate_store.py` -- SYSTEMATIC_FLOOR/`_apply_floor` retired; new
  `_session_systematic_budgets`, `_floor_with_budget`, `_floor_constant_rel`,
  `normalize_axis_status`, `effective_axis_sigma`, `_axis_statuses`; every field-builder
  (`_drag_area_fields`, `_braking_fields`, `_traction_fields`, `_power_drag_fields`,
  `_lateral_fields`) threaded through `budgets`; 9 new `{axis}_shared_sigma` `EstimateRecord`
  fields; `record_from_estimate` wires the budget + status computation.
- `src/physics/layer2/pooling.py` -- `pool_random_effects` gains `shared_floor` (default 0.0,
  bit-identical to pre-G4 behavior).
- `src/physics/layer2/pool_driver.py` -- `_PARAMS` carries the shared_sigma column name; new
  `_shared_floor_for_param`; `pool_store`'s per-constructor loop derives + passes the floor at
  every call; `ParamPool` gained a `shared_floor: float = 0.0` provenance field.
- `tests/unit/physics/layer2/test_estimate_store.py` -- 3 new shared_sigma schema tests, 2 new
  systematic-wiring tests (with-rho real-budget vs no-rho fallback), 3 new status-predicate
  tests, 6 new property tests for `effective_axis_sigma`/`normalize_axis_status`; reconciled 4
  pre-existing tests whose magic-number assumptions the sigma-meaning change invalidated (named
  below).
- `tests/unit/physics/layer2/test_pooling.py` -- 4 new shared_floor tests (zero-reproduces-old,
  plateau-vs-shrink, negative-rejected).
- `tests/unit/physics/layer2/test_pool_driver.py` -- `_rec()` extended with optional
  shared_sigma kwargs; 3 new tests (legacy-graceful-zero, real-floor-derivation, invariant).
- `.agent-work/627-unified-basis/g4-implement/characterize_g4.py` + `scratch/*.db` -- LOCAL ONLY
  (gitignored via the existing `.agent-work/**/scratch/` pattern for the DB copies; the .py
  script itself is untracked and should NOT be committed as part of this gate's diff). Never
  writes `data/*.db` -- confirmed: `physics_estimates.db` mtime unchanged (Jul 16 09:11) after
  every run in this session.

**Specific exclusions touched:** no. `systematic_budget.py` and `weekend_state/*` source were
read-only throughout (only a scratch DB copy was fed into `gate_f6.run_gate(db_path=...)`, an
existing public parameter -- no weekend_state source line changed). G3's cross-view covariance
population (`_fused_cda_fields`/`_cross_view_covariance_fields`) was read but not modified.

## Behavior changed
Yes. `{axis}_sigma` for cda/p_max/a_b/b_b/a_t/b_t/A2 now reflects a real per-session analytic
budget (or, for a_b/b_b/a_t/b_t/A2, a NEW floor where there was none before) instead of the old
blind constant; A0's numeric value is UNCHANGED (0.04 old blind floor == 0.04
`A0_CURVATURE_TERRAIN_BOUND_REL`, verified bit-identical in the characterization run). Pooled
`sigma_mu` now floors at the shared-systematic component when the store has shared_sigma data
for that param (0.0/no-op otherwise). `{axis}_status` is now computed, not a placeholder
constant. See "Weekend-state decision stability" for the measured real-data impact.

## Map Impact
- **Structural anchors touched:** `struct:physics.layer2` -- `estimate_store.py` (SYSTEMATIC_FLOOR
  removed, `record_from_estimate` now status- and budget-aware), `pooling.py::pool_random_effects`
  (new `shared_floor` param), `pool_driver.py::pool_store` (non-optional floor threading).
- **Capabilities added/changed:** data-driven per-session systematic (#506) is now LIVE (not
  just computed-and-discarded as in G1); pooled-sigma_mu shared floor is LIVE; explicit-unknown
  status is LIVE (resolved/unresolved is a real read, not a schema placeholder).
- **Constraints/assumptions touched:** "pooling cannot average away a shared bias" (#506 core) --
  now enforced end-to-end and demonstrated on real data (Part A below), not just a design intent.
- **Decision candidates:** (1) the cda/p_max fallback-when-budget-unavailable path (rho/mass
  missing) uses a documented 0.04 constant split shared/session via
  `MASS_SHARED_VARIANCE_FRACTION` rather than the real per-session number -- production always
  supplies rho/mass (verified: `estimate_batch.run_estimate_batch` always passes both), so this
  fallback is test-only in practice; flagging for architecture review whether it's worth keeping
  vs. making rho/mass required kwargs. (2) `_shared_floor_for_param`'s median-across-sessions
  representative floor (vs. e.g. max, or a fixed-point single-session lookup) is a judgment call
  documented in the docstring, not measured against alternatives.
- **Claims/evidence produced:** pooled sigma_mu(CdA/P_max) floored by shared systematic on REAL
  RBR 2023 Q data (Part A, real numbers below); weekend_state decision stability on REAL 1562-row
  season data (Part B, zero flips).
- **Triage candidates:** the `_FALLBACK_SYSTEMATIC_REL`/`_floor_constant_rel` fallback paths in
  `estimate_store.py` are currently exercised only when a caller omits rho/mass (test-only) --
  worth a follow-on issue to either (a) make rho/mass required kwargs of `record_from_estimate`
  (closing the fallback path entirely, since production always has them) or (b) add an explicit
  provenance flag distinguishing a fallback-floored row from a real-budget-floored row in the
  store, since today they are indistinguishable downstream (both just look like a finite sigma).

## Test mode
**Required:** test-after (property test + pooled-floor test explicitly required)
**Satisfied:** yes -- property test (`effective_axis_sigma` unresolved-vs-resolved, 6 variants)
and pooled-floor test (`test_pooled_sigma_mu_shrinks_without_floor_but_plateaus_with_floor`,
`test_pool_store_derives_shared_floor_from_stored_shared_sigma_column`) both present and green.

## Evidence

```bash
cd /c/Programs/f1-627
py -c "import src.physics.layer2.pooling as m; print(m.__file__)"
# C:\Programs\f1-627\src\physics\layer2\pooling.py -- worktree isolation confirmed
py -m pytest tests/unit/physics/layer2/ tests/unit/physics/weekend_state/ -q
```

**Result:** PASS -- `835 passed, 2 warnings in 3228.36s (0:53:48)` (the wall time is high because
several other agent sessions were running concurrently against the same machine during this
run -- no test in this suite is individually slow; `test_estimate_store.py`/`test_pooling.py`/
`test_pool_driver.py` alone run in under 4 seconds combined when isolated, see below). Zero
failures, zero errors. The 2 warnings are pre-existing (`test_regime_capability_dashboard.py`
pandas `FutureWarning`, unrelated to this change).

Isolated confirmation of the three directly-edited test files (fast, run repeatedly during
development):
```
tests/unit/physics/layer2/test_estimate_store.py: 48 passed in 3.49s
tests/unit/physics/layer2/test_pooling.py:         15 passed in 1.46s
tests/unit/physics/layer2/test_pool_driver.py:      8 passed in 2.60s
```

## Pooled-floor before/after (real numbers, RBR 2023 Q, 22 sessions)

Real per-session (value, sigma) pulled from `C:/Programs/f1Brainz/data/physics_estimates.db`
(read-only), fit-only sigma reconstructed by analytically backing out the OLD blind floor from
the stored (already-floored) sigma column, NEW sigma recomputed via the real per-session
`systematic_budget()` call using each row's own stored `mass_kg_assumed`/`rho`. Shared floor =
median of the derived shared component across RBR's 22 sessions.

**CdA** (`drag_area_closed_m2`, shared_floor = 0.0532 m^2):

| n sessions | sigma_mu WITHOUT floor | sigma_mu WITH floor |
|---|---|---|
| 2  | 0.1409 | 0.1506 |
| 5  | 0.0663 | 0.0858 |
| 10 | 0.0433 | 0.0690 |
| 17 | 0.0396 | 0.0663 |
| 22 | 0.0399 | 0.0665 |

Without the floor, sigma_mu keeps drifting toward/below 0.04 as n grows (n=17: 0.0396, BELOW the
0.0532 shared floor -- an honest-sounding but overconfident number). With the floor, sigma_mu
plateaus at ~0.065-0.067 from n~=10 onward and never drops below the derived shared component,
at any n.

**P_max** (`max_power_w`, shared_floor = 18,840 W):

| n sessions | sigma_mu WITHOUT floor | sigma_mu WITH floor |
|---|---|---|
| 2  | 25,389 | 31,617 |
| 5  | 20,647 | 27,908 |
| 10 | 11,777 | 22,184 |
| 17 | 8,152  | 20,532 |
| 22 | 7,311  | 20,222 |

Same pattern: unfloored sigma_mu drops to 7,311 W by n=22 (well below the 18,840 W shared
systematic), while the floored value plateaus around 20,200-20,500 W from n~=10 onward.

Full script + raw output: `.agent-work/627-unified-basis/g4-implement/characterize_g4.py`
(local-only, not committed).

## Weekend-state decision stability

Ran `gate_f6.run_gate(db_path=...)` (the frozen F6 held-out gate) against two SCRATCH sqlite
copies of the real `physics_estimates.db` (never the tracked file itself, never `weekend_state/*`
source): an OLD copy byte-identical to production, and a NEW copy with every axis's `_sigma`
column recomputed via the same fit-only-reconstruction + G1-budget-recompute method as Part A,
applied to all 1562 real Q `ok` rows across the full store (not just RBR).

| axis | OLD beat | NEW beat | flip? |
|---|---|---|---|
| drag_area_closed_m2 | True | True | |
| brake_decel_ms2 | True | True | |
| brake_aero_decel_per_m | True | True | |
| traction_accel_ms2 | True | True | |
| traction_aero_accel_per_m | True | True | |
| max_power_w | False | False | |
| power_drag_area_m2 | True | True | |
| lateral_mech_grip_g | True | True | |
| lateral_aero_grip_g | True | True | |
| coast_rolling_decel_ms2 | True | True | |
| coast_drag_area_m2 | False | False | |

**TOTAL FLIPS: 0 / 11 axes. Verdict unchanged: PASS (9/11 covered beats) both before and after.**

This is consistent with expectation: A0 (`lateral_mech_grip_g`) is numerically IDENTICAL old vs
new (0.04 old blind floor == 0.04 `A0_CURVATURE_TERRAIN_BOUND_REL`, by construction). The other
axes' sigma DID shift (braking/traction/A2 gained a new nonzero floor where there was none;
cda/p_max moved from the blind 4% to the real per-session mass/rho-derived number), but every
shift stayed well inside the F6 gate's existing bootstrap noise margins -- a benign shift, not a
coincidence of zero movement. `max_power_w` and `coast_drag_area_m2` were already
`DID-NOT-BEAT-FLOOR` before this change and remain so after; nothing here should be read as this
gate "fixing" those two axes.

Timing: recompute of all 1562 rows' new sigma took 0.8s; `run_gate` itself took ~35s (old) / ~26s
(new) -- both well within a bounded budget, no live physics fit was needed for this evidence.

## Docs/contracts touched
- None. `{axis}_sigma` column names are unchanged (only their meaning tightens, per the
  handoff's explicit constraint) -- no consumer contract signature changed.

## Assumptions
- `_session_systematic_budgets`'s guard requires braking/traction/PowerDrag/cda_closed all
  present plus rho+mass_kg non-None; verified these are ALWAYS present in the production ingest
  path (`estimate_batch.run_estimate_batch` always supplies `rho`; braking/traction/power_drag
  are non-optional owned views, only lateral/coast are ever `None`). The fallback-constant path
  is therefore expected to be test-only in practice, not a live production behavior -- flagged
  as a decision candidate above (Map Impact) for whether it's worth closing off entirely.
- `_shared_floor_for_param`'s per-constructor MEDIAN of stored `{axis}_shared_sigma` values is
  the chosen "representative shared sigma" (handoff said "median/representative... your call,
  document it"); a max or a fixed single-session lookup were the alternatives considered and
  rejected as either too conservative (max, could be dominated by one degenerate session) or too
  fragile (single lookup, no session to prefer without an explicit canonical-session rule).
- The characterization script's "OLD" sigma reconstruction (backing out the retired blind floor
  from the stored, already-floored sigma column) assumes every historical row was written by the
  retired code path (true for 100% of `data/physics_estimates.db`'s current contents, since G4
  is the first gate to change this wiring).
- `ParamPool.shared_floor` was added as a NEW field (default 0.0) purely for evidence/provenance
  transparency in tests and the characterization script; not required by the handoff text but a
  natural, low-cost extension of the "no silent-unfloored path" requirement (a caller can now
  directly read what floor a given pooled param actually got, rather than inferring it from
  `sigma_mu` alone).

## Stop conditions hit
None. No consumer broke unrecoverably; the pooled floor wired non-optionally without needing a
production-default change; weekend_state stayed green with zero decision flips.

## Out-of-scope observations
- See "Decision candidates" / "Triage candidates" in Map Impact above (fallback-path closure,
  provenance flag for fallback-vs-real-budget floored rows).
- `scripts/nuisance_sensitivity.py`'s live Monza re-run (G1's own attempted OPTIONAL carry-
  forward, not this gate's requirement) was NOT re-attempted here -- G1's systematic_budget.py
  module docstring already documents a stall under contention on 2026-07-18, and this gate's own
  entire evidence base was produced analytically from stored data specifically to avoid needing
  a live fit at all (see "Pooled-floor before/after" and "Weekend-state decision stability"
  above) -- not a blocker per the handoff's explicit optional-carry-forward framing.

## Workflow Feedback
- **Handoff gaps:** none material. The handoff's "your call, document it" latitude on
  shared_floor units/derivation and the status predicate was exactly right-sized -- concrete
  enough to start, open enough to make real engineering judgment calls (documented above).
- **Context rediscovered:** the exact production call graph proving `rho`/`mass_kg` are always
  present in `record_from_estimate`'s real callers (`estimate_batch.run_estimate_batch`) wasn't
  named in the handoff or map anchors; had to trace it myself to justify the fallback-path design
  (whether it needed to carry real weight or could stay a documented, rarely-hit safety net).
  Worth adding as a map anchor for the next gate that touches this seam.
- **Instructions improvised around:** m2's OWN postcondition check (`! grep -rn SYSTEMATIC_FLOOR
  src/`), which I authored too broadly in my own plan -- it fails permanently because
  `systematic_budget.py` and `weekend_state/layer1_physics.py` (both explicitly READ-ONLY /
  do-not-change per the handoff's Allowed Scope) legitimately retain historical prose citations
  of the retired symbol name in their own docstrings, and the engine's `rescope` verb only
  applies to a PENDING gate (not the in-progress gate whose check I'd already authored). I waived
  the condition with `--force` (documented reason: manual verification via a live-code-reference-
  only grep, `test_estimate_store.py` green) rather than editing the checklist JSON by hand. This
  is a lesson for future implementer plans: scope a "no dangling importer" grep check to files
  you actually control (or to an import-statement pattern, not a bare string match), never to a
  bare-string whole-`src/`-tree grep when neighboring read-only files are expected to keep citing
  the retired name in prose.
- **What would have made this easier:** an engine verb to correct an in-progress gate's own
  `command` postcondition text (a narrow "amend the check, not the scope" op) would have avoided
  the waive-with-force detour above for what was purely my own check-authoring mistake, not a
  scope or authority question.

## Return status
complete

---

## REWORK (post-review, simplification-limits)

**Reviewer finding:** `py -m src.utils.simplification_limits --paths src/physics/layer2/estimate_store.py`
FAILED -- `estimate_store.py` had grown to 1010 lines (hard limit 1000, a review blocker per
`CREW_CONTEXT.md`) and the check hadn't been run before the original result was filed. The
engineering itself was independently reproduced and accepted by the reviewer (pooled-floor
plateau, weekend_state 0-flip, property-test distinction) -- this was purely a structural
line-count violation.

**Extraction performed:** pure structural split, no logic/defaults/column-name/API change.
Moved every field-flattening helper out of `estimate_store.py` into a new sibling module,
`src/physics/layer2/estimate_store_fields.py`:
- Sigma/covariance primitives: `_sigma`, `_cov_list`, `_inflate`.
- #627 G4 systematic-budget wiring: `_session_systematic_budgets`, `_floor_with_budget`,
  `_floor_constant_rel`, `_FALLBACK_SYSTEMATIC_REL`/`_FALLBACK_SHARED_REL`/`_FALLBACK_SESSION_REL`,
  `_RHO_INFLATION`, `_THETA_R_LITERAL`.
- #627 G4 explicit-unknown status: `normalize_axis_status`, `effective_axis_sigma`,
  `UNRESOLVED_AXIS_SIGMA_FRAC`, `_axis_statuses`.
- Per-view field builders: `_drag_area_fields`, `_braking_fields`, `_traction_fields`,
  `_power_drag_fields`, `_lateral_fields`, `_coast_fields`.
- #627 G3 cross-view fusion: `_cda_jacobian_cross_terms`, `_fused_cda_inputs`,
  `_fused_cda_fields`, `_cross_view_covariance_fields`.
- Fit-quality/support-trust: `_fit_quality`, `_degrade_trust`, `_support_trust_profile`,
  `_TRUST_RANK`.

`estimate_store.py` keeps the module docstring, `_JSON_COLUMNS`/`_CROSS_VIEW_COVARIANCE_KEYS`/
`AXIS_STATUS_NAMES`/`_PK`, the `EstimateRecord` dataclass, `record_from_estimate`,
`error_record`, and the `EstimateStore` class -- and re-imports everything it calls (plus every
name an EXTERNAL caller imports by name from `estimate_store`, e.g. `regime_readiness.py`
imports `estimate_store._cov_list` directly; several tests import `_sigma`/`_THETA_R_LITERAL`/
`UNRESOLVED_AXIS_SIGMA_FRAC`/`effective_axis_sigma`/`normalize_axis_status`) from
`estimate_store_fields.py`, so every existing import path (public or "private") is unchanged.
Verified: `import src.physics.layer2.estimate_store as es; import
src.physics.layer2.regime_readiness as rr; ... es._cov_list is rr._cov_list` -> `True`.

New line counts: `estimate_store.py` 438, `estimate_store_fields.py` 635 (both well under 1000).

**Environment note (worktree torn down mid-rework):** partway through this rework, the assigned
worktree `C:/Programs/f1-627` was removed from disk by a concurrent process (the Admiral's
post-merge cleanup) -- the #627 epic, including this exact extraction, was independently
merged to `f1Brainz` `main` as commit `70ada70e` (G4) and folded into the epic merge commit
`59c2bc1f` (`#627 (+#506) Phase 3 ... (#645)`, now on `origin/main`). Both required verification
commands below were re-run and pasted against the CURRENT authoritative location,
`C:/Programs/f1Brainz` (main, `59c2bc1f`), since the original worktree no longer exists.

### 1. Simplification limits (all three touched files)

```
$ py -m src.utils.simplification_limits --paths src/physics/layer2/estimate_store.py src/physics/layer2/pooling.py src/physics/layer2/pool_driver.py
PASS (3 files checked)
```
(exit code 0)

### 2. Full required test suite

```
$ py -m pytest tests/unit/physics/layer2/ -q
... 745 passed, 2 warnings in 3686.25s (1:01:26)

$ py -m pytest tests/unit/physics/weekend_state/ -q
... 90 passed in 69.21s (0:01:09)
```
Combined: **835 passed, 0 failed** (split into two invocations purely to work around this
shared environment's background-task time ceiling under heavy concurrent-agent contention --
same 835/835 total the pre-rework IMPLEMENTER_RESULT reported combined). The 2 warnings are the
same pre-existing, unrelated `test_regime_capability_dashboard.py` pandas `FutureWarning` noted
above.

Also independently re-confirmed the four directly-edited/consumer test files in isolation:
`test_estimate_store.py` (48), `test_pooling.py` (15), `test_pool_driver.py` (8),
`test_regime_readiness.py` (21, the `_cov_list` re-export consumer) -- 92 passed in 12.30s.

`git status --short data/` shows only pre-existing untracked `-shm`/`-wal` SQLite journal
sidecar files (0-byte `-wal`, i.e. no pending write); `physics_estimates.db` itself is untouched
(same size/mtime as before this rework). No `data/*.db` was written or committed.

### Return status (rework)
complete
