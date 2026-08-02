# Review Result

Status values follow `skills/workbench/references/status-model.md`.

## Assigned Gate
`g4 (issue #662)` — Corner descriptors + turn direction + severity membership; the HIGHEST-RISK gate (#639 a_lateral unit boundary).

## Result
`APPROVE`

## Handoff compliance
All three required deliverables are present in `src/physics/segment_map/derivation/corner_attributes.py`:
`compute_corner_descriptor`, `compute_turn_direction`, `compute_severity_membership`, plus
`fit_era_severity_mixture` and the convenience wrapper `derive_corner_attributes` (explicitly requested
by the handoff "for g5 to persist"). The #639 unit boundary requirement (m/s²→g via `GRAVITY_MS2` at
exactly one documented call site) is satisfied. The pooled-era mixture fit, soft membership invariants,
and turn-direction sign convention are all implemented and tested as specified. Scope was respected.

## Scope drift
None. `git status --short` shows only two new untracked files:
`src/physics/segment_map/derivation/corner_attributes.py` and
`tests/unit/physics/segment_map/derivation/test_corner_attributes.py`. No edits to
`docs/architecture/*`, `segment_map/runtime.py`, `segment_map/from_mixture.py`, `segment_map/identity.py`,
any `layer2/*.py` file, or `frozen_constants.py`. No `SegmentMap` assembly, no store write, no sub-phase
population, no corner-number-marker join — all Specific Exclusions respected. (A pre-existing modified
`data/f1_data_2023.db` binary appears in `git status`; confirmed via `git log` it was last touched by an
unrelated 2026-07-02 fuel-mass commit and is neither read nor written by this gate's code or tests — an
out-of-scope worktree artifact, not a G4 scope breach.)

## Evidence verdict
All required evidence independently reproduced (re-run myself, not trusted from the impl result):
- `pytest tests/unit/physics/segment_map/derivation/test_corner_attributes.py -v` → **14 passed** (identical
  to the claim), including `TestRealDataSmoke::test_pooled_2023_fit_smoke` **genuinely PASSED, not SKIPPED**
  (the real `damage_integrals.db` is present at the MAIN-checkout path and was actually queried).
- The two load-bearing tests isolated (`TestUnitBoundary` + `TestMembershipInvariants`) → **4 passed**.
- `py -m src.utils.simplification_limits --paths src/physics/segment_map/derivation/corner_attributes.py`
  → **PASS (1 files checked)**.
- `grep -n "GRAVITY_MS2"` → import at line 89, **exactly one** executable division at line 185 (all other
  matches are docstring prose); `grep -n "9\.81"` → **no output, exit 1** (no literal anywhere in the file).

**The unit-boundary proof, read line-by-line:** `test_monkeypatched_gravity_scales_lateral_g_by_exactly_one_over_g`
computes `lateral_g_before` with the real `GRAVITY_MS2`, monkeypatches the module-bound `GRAVITY_MS2` to
`2×`, recomputes `lateral_g_after`, and asserts `lateral_g_after == lateral_g_before / 2.0` exactly. This
is genuinely dispositive: a double conversion would produce `lateral_g_before / 4`, a missing conversion
would leave it unchanged at `lateral_g_before`; only a single conversion produces the observed `/2` scaling.
A companion assertion confirms `radius_m` (which never touches `GRAVITY_MS2`) is untouched by the patch.

## Code/doc quality
Minimal, maintainable, matches surrounding conventions. Verified the reference-lap descriptor genuinely
sits on the mixture's own training axis: `radius_m = 1/|κ|` is algebraically identical to
`corner_descriptors.bin_row_to_descriptor`'s `v_mean²/(mu_lat_p90·G)` in steady state (since
`a_lateral_ms2 = v²·|κ|` by construction here, `v²/a_lateral_ms2 = 1/|κ|`) — the module docstring states
this equivalence explicitly. The median-achieved-vs-p90-capability offset on the `lateral_g` axis is
documented inline as a bounded, deferred approximation (not silently ignored, not switched to a
p90-capability descriptor, per the Admiral ruling cited in the handoff).

One point worth recording precisely: `compute_corner_descriptor`/`compute_turn_direction` use
`radius_m = 1/abs(kappa)`, whereas `soft_class_membership`'s literal quoted formula is
`radius = 1.0/sample.curvature` (no `abs`). This is **not** a divergence bug — it is required because
`ReferenceLap.curvature` is **signed** (`build_ribbon`'s `kappa = dphi/ds`), whereas
`KinematicSample.curvature` (`soft_class_membership`'s only real caller, via `SegmentClassifier._get_curvature`)
is **unsigned** (a cross-product-norm magnitude), so `soft_class_membership` never needed an explicit `abs`
in practice. Taking `abs(kappa)` here is the correct adaptation to keep `radius_m > 0` for the mixture's
`log10(radius)` fit space; the module correctly recovers the sign separately for `turn_direction`. This
reasoning is not spelled out verbatim in the module's own docstring (it documents the "signed curvature"
fact but not explicitly *why* `abs()` is required relative to `soft_class_membership`'s literal formula) —
flagged as a documentation quality nit, not a defect.

Fowler code-smell pass (`r6-fowler`, `verify_fowler_pass.py` exit 0, 12/12 smells rendered):
- **flagged**: `duplicated-code` — the degenerate-apex guard (`abs(kappa) <= _DEGENERATE_CURVATURE_EPS`)
  is repeated verbatim in both `compute_corner_descriptor` and `compute_turn_direction`. Non-blocking: both
  call the same deterministic `_corner_apex_indices`, so the duplication cannot desync; a shared
  apex-filtering helper would remove it in a future pass.
- **overridden**: `primitive-obsession` (raw numpy arrays over value objects) — subordinate to
  `runtime.py`'s documented flat-parallel-array architecture, which `SegmentMap.build` requires verbatim.
- **overridden**: `speculative-generality` (`derive_corner_attributes` has no caller in this diff) —
  subordinate to the handoff's explicit statement that g5 (the next gate in this epic) is the named
  consumer, not a hypothetical one.
- All other baseline smells (long-method, large-class, feature-envy, data-clumps, long-parameter-list,
  shotgun-surgery, divergent-change, message-chains, comments-as-deodorant): **absent**.

## Map impact verdict
- **Evidence supports claimed change:** yes — `claim:unit-boundary-fires-once` and
  `claim:membership-invariants` are both backed by tests I independently re-ran and by direct code
  inspection (single call site at line 185; `np.zeros` init + `finite_rows`-only assignment for membership).
- **Constraints not violated:** yes — `decision:a-lateral-g-boundary`, `decision:severity-refit-consume-k4`,
  `decision:dormant-subphase` all honored and independently confirmed (pooled-year filter with no
  session_type filter; k_range=(2,4) default; zero sub-phase code).
- **Notes match the diff:** yes — the claimed `DEFAULT_GRIP_BIN_DB_PATH` precedent
  (`layer2_evolution.py`'s `DB_PATH`) was independently confirmed byte-for-byte
  (`DB_PATH = Path("C:/Programs/f1Brainz/data/damage_integrals.db")` at `layer2_evolution.py:77`).
- **Decision candidates surfaced:** n/a — no new authority-requiring decision arose in this gate; all
  three governing decisions were already Admiral-ratified per the handoff.
- **Durable context routed:** yes — the cross-worktree `grip_bin_obs`/`damage_integrals.db` data-store
  dependency is correctly flagged as a repo-wide pre-existing pattern worth Cartographer's attention, not
  new debt introduced here.

## Reconciliation check
No divergence from recorded architecture requiring Commander reconciliation. The one cross-cutting note
(grip_bin_obs lives only in the untracked `damage_integrals.db`, not in this worktree's per-year DBs) is
pre-existing repo structure already surfaced by the implementer, not introduced by this gate.

## Blockers
- none

## Out-of-scope observations
- Minor doc-quality nit: the module docstring documents that `ReferenceLap.curvature` is signed, but does
  not explicitly connect that fact to *why* `radius_m` needs `abs(kappa)` where `soft_class_membership`'s
  quoted literal formula does not use `abs` — worth one clarifying sentence in a follow-up pass, not blocking.
- Minor Fowler observation: duplicated degenerate-apex guard between `compute_corner_descriptor` and
  `compute_turn_direction` (see Code/doc quality) — a candidate for a small DRY cleanup in g5 or a later pass,
  not blocking.
- The pre-existing cross-worktree `grip_bin_obs`/`damage_integrals.db` dependency (already noted by the
  implementer) is worth a durable Cartographer note if one does not already exist, since g5/g6 will hit the
  same "which DB" ambiguity.

## Workflow Feedback
- **Handoff gaps:** none load-bearing. The handoff's Required Evidence/Verification Commands section scopes
  evidence to the single new test file + simplification check; I additionally attempted a broader
  `pytest tests/unit/physics/ -q` sanity sweep per `CREW_CONTEXT.md`'s "Run the focused region suite for
  every source change" rule, but it did not finish within this review's time budget. I judged this
  acceptable to not block on: `corner_attributes.py` is a brand-new file with zero existing callers and
  modifies no existing file, so it structurally cannot regress any other physics test — the handoff's own
  narrower evidence bar is sufficient for this diff's actual blast radius. Worth a one-line handoff note in
  future high-risk gates: "new-file-only diffs may skip the full region sweep; state the blast-radius
  reasoning" would save a reviewer having to make that call ad hoc.
- **Context rediscovered:** the fact that `soft_class_membership`'s literal quoted formula uses
  `radius = 1.0/sample.curvature` (no `abs`) while `corner_attributes.py` uses `abs(kappa)` required tracing
  `SegmentClassifier._get_curvature` (cross-product-norm, always non-negative) to confirm this is not a
  divergence bug but a correct, required adaptation for `ReferenceLap`'s signed curvature. A one-line
  pointer in the handoff or the module docstring ("soft_class_membership's real caller only ever supplies
  non-negative curvature, which is why it doesn't need an explicit abs()") would have saved this trace.
- **Instructions improvised around:** none beyond what the implementer already reported (their TDD
  single-pass-vs-three-slices note, which I confirmed did not compromise the per-slice evidence chain).
- **What would have made this easier:** a one-line "blast radius" note in the handoff (new-file-only vs.
  touching shared code) so a reviewer doesn't have to independently judge whether a broader region sweep is
  warranted on a high-risk gate.

## Return status
`complete`
