# Reviewer Handoff

## Gate
g4 (execute.json: g4-review) — Regime distance-share rollup + observability router

## Survey State Location
`.agent-work/625-segmentation-substrate/g4-review/review.json`

## What Was Implemented
`src/physics/layer2/regime_rollup.py` (`corner_bin_share`, `circuit_distance_share`,
`load_circuit_frame`), `src/physics/layer2/observability_router.py` (`ROUTER_ENTRIES`, every
entry citation-grounded), `scripts/build_regime_rollup.py` (run for real, k=3 fitted on
612,615 pooled rows across 22 circuits), producing `.agent-work/625-segmentation-substrate/
artifacts/regime_time_share.csv` and `.meta.json`, both carrying Gate 3's F12 FAIL verdict.

## How to Inspect the Diff
Worktree `C:/Programs/f1-625` — `git status --porcelain` then `Read` new files directly
(untracked). Gates 1-3 are already approved — review only Gate 4's slice:
`regime_rollup.py`, `observability_router.py`, `scripts/build_regime_rollup.py`, their two
test files, and the two generated artifacts. CONFIRM `property_mixture.py`,
`mixture_stability.py`, `corner_descriptors.py`, `arcs.py` show no NEW diff beyond what Gates
1-3 already introduced (they should be identical to their post-Gate-3 state).

## Task Statement
Build the rollup + observability router per CONVERGED_PLAN.md Gate 4 and the full handoff at
`C:/Programs/f1-625/.agent-work/625-segmentation-substrate/crew-handoffs/g4-implement-handoff.md`,
propagating Gate 3's FAIL verdict honestly into the output.

## Close Criteria
- **`distance_share` naming discipline**: grep/AST-check confirms `time_share` never appears
  as a field/variable name in `regime_rollup.py` or the CSV headers (only the deliverable
  FILENAME `regime_time_share.csv` may carry the word, per the mission's own naming — the
  implementer's test explicitly covers this, re-verify it yourself).
- **F12 FAIL verdict is genuinely readable from the rollup's own output** — open
  `regime_time_share.csv` directly (not the `.meta.json`) and confirm the FAIL verdict, the
  n_pass count, and a plain-English caveat are visible in its own leading lines, without
  needing to already know the meta file exists.
- **Monza-vs-Monaco sanity ordering** holds on the real run (`corner_distance_share` for
  `gp_name="Italy"` (Monza) < `gp_name="Monaco"`) — independently confirm from the committed
  CSV.
- **Observability router citations are genuinely grounded**, not fabricated: spot-check AT
  LEAST the `straight_coast` entry (the handoff flagged this as tricky — `CoastView` does NOT
  filter directly on `regime == "straight_coast"`, it has its own independent coast-detection
  logic) — confirm the router entry states this indirect linkage honestly rather than claiming
  a direct filter that doesn't exist. Spot-check one more entry (your choice) against its cited
  file:line directly.
- **Class sub-shares sum correctly**: for at least 2 real circuit rows, confirm
  `corner_class_0 + corner_class_1 + corner_class_2 ≈ corner_distance_share` (within floating
  rounding) and `corner_distance_share + straight_distance_share ≈ 1.0`.
- **Reuse discipline**: `property_mixture.fit_property_mixture` was reused, not reimplemented
  or modified, for the pooled fit.
- **Read-only DB access**: no writes to `data/damage_integrals.db`.

## Allowed Scope
`src/physics/layer2/regime_rollup.py`, `src/physics/layer2/observability_router.py`,
`scripts/build_regime_rollup.py`, `tests/unit/physics/layer2/test_regime_rollup.py`,
`tests/unit/physics/layer2/test_observability_router.py`,
`.agent-work/625-segmentation-substrate/artifacts/regime_time_share.csv`,
`.agent-work/625-segmentation-substrate/artifacts/regime_time_share.meta.json`.

## Specific Exclusions
`property_mixture.py`, `mixture_stability.py`, `corner_descriptors.py`, `arcs.py` must show no
NEW diff from this gate. No DB writes. No `circuits.yaml`/production-default changes. No
`evo_predictor`/`latent_power`/`compound_prior` imports.

## Constraints the Implementation Must Respect
- `constraint:physics_region_no_evo_import`, `constraint:canonical_data_source`.
- Never `time_share` as a field name (only the CSV filename may carry the word).
- F12 verdict readable from the rollup's own output artifacts.

## Map Anchors (inbound)
- **Structural:** `struct:physics.layer2` — three new modules + one new script; real read
  against `data/damage_integrals.db`.
- **Capability:** per-circuit regime distance-share rollup; observability router (round-1
  load-bearing consumer).
- **Constraints/assumptions:** `constraint:physics_region_no_evo_import`,
  `constraint:canonical_data_source`.
- **Decision anchors:** pre-ruling #2, pre-ruling #6.
- **Evidence expectations:** Monza-vs-Monaco sanity ordering; router citations independently
  verifiable; F12 FAIL propagated honestly, not suppressed or softened.

## Evidence Produced
See `C:/Programs/f1-625/.agent-work/625-segmentation-substrate/crew-handoffs/g4-implement-result.md`
(claimed: 30/30 tests, real-store run with Monza<Monaco, F12 FAIL propagated). This commander
already independently reproduced the 30/30 test result and read the CSV/meta.json content
directly — you should independently reproduce the test run yourself too, and additionally spot
verify at least one router citation against real source with your own eyes. Target
postcondition: `g4-integrate.c1` (test command), `g4-integrate.c2` (this verdict), `g4-integrate.c5`
(artifact/CSV content check).

Note: this gate's Commander-owned integrate step separately runs the FULL physics suite
regression (`py -m pytest tests/unit/physics -q`, ~15+ min) and the 5-file no-evo-import grep
— these are NOT your responsibility to run (they were correctly identified by the implementer
as integrate-step, not implement-step, scope); your review is scoped to Gate 4's own slice.

## Suggested Model Tier
Stronger — composes three prior gates' machinery, plus a genuineness-grounded documentation
deliverable and an honest-propagation requirement.

## Stop Conditions
Stop and return BLOCK if: the diff cannot be accessed, evidence is unreproducible, a router
citation is fabricated/wrong, the F12 verdict is missing or softened in the rollup's own
output, or `time_share` appears as an actual field name.

## Return Format
Return REVIEW_RESULT: verdict (APPROVE or BLOCK), per-check findings, blockers, out-of-scope
observations, workflow feedback. Write it to
`C:/Programs/f1-625/.agent-work/625-segmentation-substrate/crew-handoffs/g4-review-result.md`
before ending your turn, and also return it as your final assistant text response.
