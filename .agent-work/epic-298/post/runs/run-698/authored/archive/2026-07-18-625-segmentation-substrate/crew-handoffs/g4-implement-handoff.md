# Implementer Handoff

## Gate
g4 (execute.json: g4-implement) — Regime distance-share rollup + observability router

## Task
Build the per-circuit regime distance-share rollup and the observability router, per
CONVERGED_PLAN.md Gate 4 (cold-critic dispositions #1/#2/#5/#6 baked in below). **This gate's
output must honestly propagate Gate 3's real-data F12 verdict, which is FAIL** — the rollup is
still a required deliverable, but its output must not be presented as validated.

## Protected Intent
Never call the computed quantity `time_share` in code, output columns, or docs — it is a
DISTANCE proxy (see Close Criteria). Never let a downstream reader of the rollup CSV miss that
the substrate's own falsifiability check (Gate 3) came back FAIL.

## Test Mode
Test-after with synthetic fixtures for the math; a DB-fixture smoke test (not the real store)
for the loader; a real-store run for the script's evidence artifact.

## Close Criteria
- New `src/physics/layer2/regime_rollup.py`:
  - `corner_bin_share(bins_occupied: set[int] | int, n_bins: int = 32) -> float` — pure,
    `len(bins_occupied)/n_bins` if given a set, or `bins_occupied/n_bins` if given a count;
    your call on the exact parameter type, document it.
  - `circuit_distance_share(df_for_circuit: pd.DataFrame, fit: "MixtureFit") -> dict` — input
    is one circuit's `grip_bin_obs`-shaped rows (columns include `lap_number`, `bin`,
    `mu_lat_p90`, `v_mean`). Compute, per lap, the fraction of the 32 bins occupied
    (`corner_bin_share`), then average across laps for that circuit ->
    `corner_distance_share`. `straight_distance_share = 1.0 - corner_distance_share`. Corner
    sub-shares: apply Gate 1's `corner_descriptors.descriptors_from_frame` to the circuit's
    rows, run Gate 2's `posterior_membership(fit, descriptors)`, average the membership
    columns weighted by each row's `n_samples` (present in `grip_bin_obs`) ->
    `corner_class_{i}_distance_share` for each of `fit.k` classes (values sum to
    `corner_distance_share` across classes). Return a flat dict with these fields PLUS
    `n_laps`, `n_rows`.
  - **NAME THE FIELDS `distance_share`, NEVER `time_share`, anywhere in this module** — cold
    critic finding #1: `grip_bin_obs` is corner-gated-only (no straight-line rows exist in the
    source table), so this is an arc-length distance proxy, not literal lap-time. Bins are
    uniform 1/32-of-lap-distance BY CONSTRUCTION (verified: `grip_bin_obs.py`'s
    `lap_bin_observations`, `dist/total*N_BINS`), so occupancy-fraction IS a legitimate
    distance-share, but it SYSTEMATICALLY UNDERSTATES true time-share for corners (cars are
    slower in corners, so more real time is spent per unit distance there than distance-share
    implies — `dt = ds/v`, lower `v` in corners means MORE time per unit distance). State this
    understatement direction explicitly in the module's docstring.
  - `load_circuit_frame(db_path: str, gp_name: str) -> pd.DataFrame` — thin SQLite reader
    (`SELECT * FROM grip_bin_obs WHERE gp_name = ?`), read-only connection, kept separate from
    the math above (no computation inside this function).
- New `scripts/build_regime_rollup.py`: thin CLI, `--db` flag (default
  `C:/Programs/f1Brainz/data/damage_integrals.db`), iterates every distinct `gp_name` in
  `grip_bin_obs`, fits Gate 2's `fit_property_mixture` ONCE on the pooled full-dataset
  descriptors (not per-circuit — the mixture defines the shared class vocabulary every
  circuit's sub-shares are expressed in terms of; a per-circuit-only mixture would make
  cross-circuit class labels meaningless), then calls `circuit_distance_share` per circuit
  using that shared fit, writes one row per circuit to
  `.agent-work/625-segmentation-substrate/artifacts/regime_time_share.csv` (the CSV FILENAME
  may keep the mission's own "time_share" wording since that's the deliverable's name in the
  launch order — but the CSV's own column headers must read `corner_distance_share`,
  `straight_distance_share`, `corner_class_N_distance_share`, never `time_share`). **Also**
  read `.agent-work/625-segmentation-substrate/artifacts/f12_holdout_stability.json`
  (Gate 3's committed artifact — it exists in this worktree already) and prepend/attach a
  metadata block to the rollup output (either a leading comment-row in the CSV, or a sibling
  `.agent-work/625-segmentation-substrate/artifacts/regime_time_share.meta.json` — your call)
  stating: the F12 `headline_verdict` (currently `"FAIL"`), a one-line plain-English caveat
  ("this rollup's class-membership substrate did NOT pass its held-out-circuit stability
  check — treat class-level sub-shares as provisional, not validated"), and the path to the
  full F12 artifact. This is critic finding #6 — do not skip it, the FAIL verdict must
  actually be readable from the rollup's own output, not just buried in a different file.
- New `src/physics/layer2/observability_router.py`: `ROUTER_ENTRIES: dict[str, list[dict]]`
  mapping each of the four regime tags (`"corner"`, `"straight_throttle"`, `"straight_coast"`,
  `"straight_brake"`) to a list of entries, each entry `{"view": "<module.ClassName>",
  "citation": "<file>:<line>", "note": "<one-line, what evidence this regime provides that
  view>"}`. Ground EVERY entry in real, currently-true code (verify each citation by reading
  the actual file — do not guess line numbers):
  - `"corner"` -> `lateral_view.LateralView` (cited via `session_lateral.py:61`,
    `corner_parts.append([s for s in samples if s.regime == "corner"])`) AND
    `traction_view.TractionView`/`power_drag_view.PowerDragView` (cited via
    `session_traction.py:24`, `_TRACTION_REGIMES = ("straight_throttle", "corner")` — corner
    samples feed the traction/power-drag throttle-on hump alongside straight_throttle).
  - `"straight_throttle"` -> `traction_view.TractionView`/`power_drag_view.PowerDragView`
    (same `session_traction.py:24` citation as above).
  - `"straight_brake"` -> `braking_view.BrakingView` (cited via `arcs.py`'s
    `_BRAKE_REGIME = "straight_brake"` used by `identify_braking_arcs`, which
    `session_braking.py` composes into `decoupled_braking_input.py:183`,
    `brake = regime == _BRAKE_REGIME`).
  - `"straight_coast"` -> `coast_view.CoastView` — VERIFY this citation carefully:
    `session_coast.py`'s `prepare_coast_samples` does NOT read `SegmentClassifier`'s `regime`
    field at all; it derives its own coast mask directly from raw throttle/brake/speed
    thresholds (`thr < 5.0 & brk < 5.0 & ...`, read the actual current line number). Cite the
    REAL mechanism honestly — if `CoastView`'s regime linkage is indirect/parallel rather than
    a direct `regime == "straight_coast"` filter, say so explicitly in the router entry's
    `note` field rather than fabricating a filter that doesn't exist. This is exactly the kind
    of semantic-grounding check the router exists to make truthful.
  - A unit test resolves EVERY citation's `file:line` by reading that exact file and
    confirming the cited line contains language matching the claimed regime filter (a
    lightweight text-match check, e.g. read the file, split into lines, check the cited
    line number's content contains the expected regime string — this is the "grounds each
    entry in verifiable current code" check per critic finding #5; a full numerical
    identifiability re-derivation is explicitly OUT of this gate's scope, that's Phase 2/4
    work).

## Allowed Scope
`src/physics/layer2/regime_rollup.py` (new), `scripts/build_regime_rollup.py` (new),
`src/physics/layer2/observability_router.py` (new),
`tests/unit/physics/layer2/test_regime_rollup.py` (new),
`tests/unit/physics/layer2/test_observability_router.py` (new),
`.agent-work/625-segmentation-substrate/artifacts/regime_time_share.csv` (generated),
`.agent-work/625-segmentation-substrate/artifacts/regime_time_share.meta.json` (generated, if
you choose the sibling-file approach for the F12-verdict metadata).

## Specific Exclusions
Do not modify `property_mixture.py`, `mixture_stability.py`, `corner_descriptors.py`, or
`arcs.py` (Gates 1-3's files, already reviewed/approved — reuse their public functions
exactly). Do not write to `data/damage_integrals.db`. No `circuits.yaml`/production-default
changes. No `evo_predictor`/`latent_power`/`compound_prior` imports.

## Constraints
- `constraint:physics_region_no_evo_import`, `constraint:canonical_data_source`.
- `distance_share`, never `time_share`, in code/output field names.
- The F12 FAIL verdict must be readable from the rollup's own output artifacts, not only from
  a separate file a reader might not know to check.
- Router citations must be independently verifiable against real source — do not invent a
  line number or a filter that doesn't exist; report the true mechanism even when it's
  indirect (coast_view case above).

## Map Anchors (inbound)
- **Structural:** `struct:physics.layer2` — new `regime_rollup.py`, `observability_router.py`,
  `scripts/build_regime_rollup.py`; `data/damage_integrals.db` `grip_bin_obs` (read-only,
  absolute path); Gate 3's `f12_holdout_stability.json` (already committed in this worktree
  at `.agent-work/625-segmentation-substrate/artifacts/`).
- **Capability:** per-circuit regime distance-share rollup (x6 excursion named this unbuilt);
  observability router (round-1 load-bearing consumer, per DESIGN_SPEC Phase 1).
- **Constraints/assumptions:** `constraint:physics_region_no_evo_import`,
  `constraint:canonical_data_source`.
- **Decision anchors:** pre-ruling #2 (lateral axis from `grip_bin_obs`, not fingerprint
  CSVs); pre-ruling #6 (no `circuits.yaml`/production-default writes).
- **Evidence expectations:** Monza-vs-Monaco sanity ordering (`corner_distance_share` Monza
  < Monaco) on the real store — necessary, not sufficient, alongside Gate 3's (FAILED)
  falsifiable check; router citations resolve to real, currently-true code.
- **Map confidence flags:** `circuits.yaml`'s `downforce` is low-trust — do NOT use it to
  validate or cross-check the rollup.

## Deliverable Path Check
All five new paths verified via `git check-ignore -v <path>`, all exited 1 (not ignored) —
run this yourself before starting to reconfirm, paths may have shifted.

## Required Evidence
- `py -m pytest tests/unit/physics/layer2/test_regime_rollup.py tests/unit/physics/layer2/test_observability_router.py -v` — full output, all PASS.
- Real-store run transcript: `py scripts/build_regime_rollup.py --db C:/Programs/f1Brainz/data/damage_integrals.db` — paste the stdout and the resulting CSV's first few rows plus Monza/Monaco rows specifically, and the F12-verdict metadata content.
- State plainly whether Monza's `corner_distance_share` < Monaco's on the real run.
- State plainly that the rollup output visibly carries the F12 FAIL verdict.

## Verification Commands

```bash
cd /c/Programs/f1-625
py -m pytest tests/unit/physics/layer2/test_regime_rollup.py tests/unit/physics/layer2/test_observability_router.py -v
py scripts/build_regime_rollup.py --db C:/Programs/f1Brainz/data/damage_integrals.db
```

Note: fitting the mixture ONCE on the pooled full dataset (612,615 rows) may take a couple of
minutes — this is expected, not a hang.

## Suggested Model Tier
Stronger — composes three prior gates' real statistical machinery plus a genuineness-grounded
documentation deliverable.

## Authority
CONVERGED_PLAN.md Gate 4 (with cold-critic dispositions #1/#2/#5/#6 baked in) governs this
gate's shape. The F12 FAIL verdict from Gate 3 is a FACT you propagate, not a result you
adjust, hide, or editorialize past "provisional, not validated."

## Stop Conditions
Stop and return if: `data/damage_integrals.db` unreachable; Gate 1/2/3's public functions
don't match what's described here (report the actual signatures); a router citation cannot be
honestly grounded in real code (report which entry and why, do not fabricate).

## Return Format
Return IMPLEMENTER_RESULT: completed slice, files changed, test mode satisfied, evidence
produced (including the FULL real-store run output and F12-verdict propagation confirmation),
assumptions used, stop conditions hit, out-of-scope observations, workflow feedback. Write it
to `C:/Programs/f1-625/.agent-work/625-segmentation-substrate/crew-handoffs/g4-implement-result.md`
before ending your turn, and also return it as your final assistant text response.
