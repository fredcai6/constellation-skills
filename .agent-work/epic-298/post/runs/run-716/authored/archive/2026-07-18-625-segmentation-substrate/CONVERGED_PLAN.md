# Converged plan — #625 Phase 1 (post plan-alternatives)

Design-it-twice: 2 candidates run in parallel (constraint: smallest-diff vs most-testable).
Panel-vs-single: **2 candidates, not a 3+ panel** — this is one bounded, already-decomposed
epic issue (not itself spawning new epics or an architecture-touching interface choice), so
scaled down from the "load-bearing → panel(3+)" default; the two constraints (minimal-touch
vs maximal-falsifiability) are the ones that matter most for a validation-substrate issue,
so 2 was judged sufficient. Surfaced here for the plan-approval checkpoint, not decided
silently.

## Recommendation: a named hybrid

Take candidate A's (smallest-diff) file placement discipline — reuse `arcs.py`'s
`_contiguous_runs` directly (generalize its regime-set param rather than duplicating it),
and put the classifier-facing additive methods literally inside `segment_classifier.py`
(the launch order's literal instruction: "Extend `src/physics/segment_classifier.py`") rather
than candidate B's separate `soft_regime.py` adapter that never touches the named file.

Take candidate B's (most-testable) internal discipline: pure-function statistical cores in
dedicated `layer2/` sibling modules (consistent with how `layer2/pooling.py`,
`layer2/estimate_store.py` etc. already separate statistical machinery from the Layer-1
classifier — not new architecture, the existing pattern), synthetic-fixture unit tests per
function, and critically candidate B's F12 **discriminating** test: prove the stability
check can FAIL (two descriptor sets from deliberately shifted generators) as well as pass
(two sets from the same generator) — a check that can only ever pass isn't falsifiable in
practice, only in principle. Also keep B's observability-router idea of a
symbol-resolution test (router entries must resolve to real symbols in the 5 `layer2/*_view.py`
modules) rather than an inert prose table.

Consolidated from B's 9 gates to **4 crew gates** (below) by grouping related pure-function
work into the same gate/module boundary without losing per-function synthetic-fixture test
coverage — 9 gates × 3 crew dispatches each is not a practical Sonnet-tier commander budget
for one issue, and the mission's "smallest reasonable bite" is a per-gate property, not a
gate-count target.

## Gates

**Gate 1 — Straight-arc grouping + descriptor axis (deliverable 2)**
- `src/physics/layer2/arcs.py`: generalize `_contiguous_runs(samples, min_len, regimes)`
  (drop the `_BRAKE_REGIME` hardcode to a param; `identify_braking_arcs` keeps its exact
  public signature, passing `{_BRAKE_REGIME}` internally — zero behavior change). Add
  `StraightArc` dataclass (`sample_indices, length_m, duration_s, top_speed_ms`) +
  `identify_straight_arcs(samples, min_len)` over the three straight regimes.
- `src/physics/layer2/corner_descriptors.py` (new): `bin_row_to_descriptor(mu_lat_p90,
  v_mean) -> (radius, lateral_g)` (`R = v_mean**2 / (mu_lat_p90 * GRAVITY_MS2)`),
  `descriptors_from_frame(df) -> np.ndarray[N,2]` (drops non-positive/NaN `mu_lat_p90` rows).
- Close: synthetic `KinematicSample` sequence (corner→straight→corner) yields correct
  straight-arc length/duration/top_speed; existing `identify_braking_arcs` tests unmodified
  and green; descriptor function unit tests cover nominal/zero-mu/NaN/negative-guard cases.
- Evidence: `py -m pytest tests/unit/physics/layer2/test_arcs.py tests/unit/physics/layer2/test_corner_descriptors.py -v`

**Gate 2 — Soft/fractional property-class membership (deliverable 1)**
- `src/physics/layer2/property_mixture.py` (new): `fit_property_mixture(descriptors,
  k_range, min_support_per_component) -> MixtureFit` (BIC-selected `sklearn.mixture.
  GaussianMixture` over standardized (radius, lateral_g); rejects a k whose smallest
  component's soft weight × N falls below the support floor), `posterior_membership(fit,
  descriptors) -> np.ndarray[N,K]`.
- `src/physics/segment_classifier.py`: additive `soft_class_membership(sample, fit)` method
  — corner samples only, straights return `None`; `_classify_regime`/`_VALID_REGIMES`
  untouched (no regime-tag rename, membership is auxiliary, not a new hard tag).
- Close: synthetic 2-cluster and 3-cluster Gaussian blob tests confirm BIC recovers true k
  when separated and collapses under the min-support floor on a thin blob; membership rows
  sum to 1; a `SegmentClassifier`-level test confirms corners get membership, straights
  get `None`, and all pre-existing `test_segment_classifier.py` cases stay green.
- Evidence: `py -m pytest tests/unit/physics/layer2/test_property_mixture.py
  tests/unit/physics/test_segment_classifier.py -v`

**Gate 3 — F12 falsifiable gate: held-out-circuit stability (deliverable 4, MANDATORY)**
- `src/physics/layer2/mixture_stability.py` (new): `hungarian_match(means_a, means_b)`
  (`scipy.optimize.linear_sum_assignment`), `component_agreement_stat(fit_a, fit_b) -> float`
  (mean Euclidean distance between matched standardized component means),
  `F12_AGREEMENT_THRESHOLD` (a named, pre-registered constant — chosen and frozen in this
  gate BEFORE the real-data run, not tuned after seeing the result),
  `check_holdout_stability(df, ...) -> StabilityResult` (deterministic seeded circuit-level
  split into two non-overlapping halves, fits Gate 2's mixture independently on each,
  returns the statistic + verdict).
- Close: a **discriminating** unit test — two synthetic descriptor sets drawn from the SAME
  generator must PASS (statistic below threshold), two sets from deliberately shifted
  generators must FAIL (statistic above threshold) — proves the check can actually
  distinguish stable from unstable, not merely execute. Then run
  `check_holdout_stability` against the real `data/damage_integrals.db` (absolute path,
  read-only) and record the honest PASS/FAIL verdict with numbers — either outcome closes
  the gate (a FAIL is a complete, reportable finding per Honest-Null Clause, not a blocker).
- Evidence: `py -m pytest tests/unit/physics/layer2/test_mixture_stability.py -v`
  plus a committed real-data run transcript + JSON result under
  `.agent-work/625-segmentation-substrate/artifacts/f12_holdout_stability.json`.

**Gate 4 — Per-circuit regime time-share rollup + observability router (deliverables 3, 5)**
- `src/physics/layer2/regime_rollup.py` (new): pure `corner_bin_share(bins_occupied,
  n_bins=32) -> float`, `circuit_time_share(df_for_circuit, fit) -> dict` (corner-share via
  coverage ratio, straight-share = 1 − that, corner sub-shares = Gate 2's posterior
  membership averaged over the circuit's rows, weighted by `n_samples`); thin
  `load_circuit_frame(db_path, gp_name) -> pd.DataFrame` DB reader kept separate from the
  math (unit-testable against a `tmp_path` sqlite fixture, not the real 612k-row store).
- `scripts/build_regime_rollup.py` (new): thin CLI composing the above over every circuit in
  `data/damage_integrals.db`, writing `.agent-work/625-segmentation-substrate/artifacts/
  regime_time_share.csv`.
- `src/physics/layer2/observability_router.py` (new): `ROUTER_ENTRIES: dict[str, list[str]]`
  mapping each property-class label / straight-regime to the `layer2/*_view.py`
  view(s)/parameter(s) it evidences (braking_view, lateral_view, traction_view,
  power_drag_view, coast_view) — a unit test resolves every referenced view/parameter name
  against the real modules (`import` + `hasattr`), catching doc drift automatically.
- Close: synthetic-fixture exact-value tests for `corner_bin_share`/`circuit_time_share`;
  DB-fixture smoke test for `load_circuit_frame`; router symbol-resolution test; script run
  against the REAL store produces one row per circuit with shares summing to ~1 and the
  Monza-vs-Monaco sanity ordering (corner-share Monza < Monaco) holds — necessary, not
  sufficient, alongside Gate 3's falsifiable check. This gate's integrate step ALSO runs the
  full closing checks: `py -m pytest tests/unit/physics -q` (full-suite regression) and a
  grep-based check that no new module imports `evo_predictor`/`latent_power`/
  `compound_prior` (`constraint:physics_region_no_evo_import`) — folded into this gate's
  integrate rather than a separate gate, since both are cheap command postconditions with no
  new code of their own.
- Evidence: `py -m pytest tests/unit/physics/layer2/test_regime_rollup.py
  tests/unit/physics/layer2/test_observability_router.py -v`;
  `py C:/Programs/f1-625/scripts/build_regime_rollup.py --db
  C:/Programs/f1Brainz/data/damage_integrals.db` transcript + output CSV;
  `py -m pytest tests/unit/physics -q` (full-suite green);
  `grep -rn "evo_predictor\|latent_power\|compound_prior" src/physics/layer2/property_mixture.py
  src/physics/layer2/mixture_stability.py src/physics/layer2/regime_rollup.py
  src/physics/layer2/corner_descriptors.py src/physics/layer2/observability_router.py` (expect
  zero matches).

## Untaken roads
- A 3-candidate panel (vs 2) — skipped: this issue is a single bounded, already-scoped
  Phase-1 issue inside a confirmed epic decomposition, not an architecture-spawning choice;
  2 constraints (touch-minimizing vs falsifiability-maximizing) span the axis that matters
  most for a validation substrate.
- B's fully-isolated `soft_regime.py` adapter (never touching `segment_classifier.py`) —
  skipped in favor of A's literal-file-match to the launch order's wording; the statistical
  core still lives in a separate testable module (`property_mixture.py`), so testability is
  not materially sacrificed.
- A 9-gate maximally-testable decomposition — skipped as impractical crew-dispatch overhead
  for one commander wave; consolidated to 4 gates while keeping every pure function its own
  synthetic-fixture test.

## Cold critic findings and dispositions

Cold critic (no authoring context, read `MISSION_FRAME.md` + this file + `arcs.py`/
`segment_classifier.py`/`physics_data_models.py` only) returned 6 findings. All triaged
within delegated latitude (plan-refinement, not a scope/architecture decision) — none floated.

1. **[CRITICAL, testability]** "corner-share via coverage ratio, straight-share = 1 − that"
   cannot be a TIME-share when the source (`grip_bin_obs`) is corner-gated only. **EDIT,
   accepted, verified against source** (`grip_bin_obs.py:38,42`: rows exist only for bins
   where `a_lat > CORNER_GATE_MS2` samples clear `_MIN_BIN_SAMPLES=5` — confirmed by direct
   re-read, not taken on the critic's word). Bins are exactly 1/32 of each lap's own total
   *distance* (`grip_bin_obs.py:37`, uniform arc-length slices) — so bin-occupancy-fraction
   IS a legitimate **arc-length distance-share**, not a fabrication. But it is NOT a time
   share: since `dt = ds/v` and corners are where speed is lowest, distance-share
   systematically **understates** true time-share for corner-heavy sections. Fix: Gate 4's
   rollup relabels the primary quantity `corner_distance_share` (not `time_share`) with an
   explicit docstring/output caveat stating the understatement direction — the "regime
   time-share rollup" deliverable name (mission's own wording) stays, the computed column is
   honestly scoped as its distance-share proxy, per the project's data-authority tenet
   (silent wrongness is a named failure mode, ORCHESTRATOR_CONTEXT.md).
2. **[MAJOR, testability]** bin-occupancy called "diversity/cardinality, not
   time/distance-share." **Partial REJECT, partial fold into #1.** Bins are uniform-distance
   by construction (`grip_bin_obs.py:37`), so occupancy-fraction tracks arc-length correctly
   (a long sweeping corner legitimately occupies more bins/more distance-share — that is
   correct behavior for a distance metric, not the cardinality error the critic describes).
   The real gap is time-vs-distance, already fixed by #1's relabeling.
3. **[MAJOR, testability]** single deterministic circuit-split risks a lucky/unlucky
   partition flipping the F12 verdict. **EDIT, accepted in full.** Gate 3 now runs the
   held-out stability check across 5 seeded circuit-splits (not 1), reporting the
   statistic's distribution (mean, range, count PASS/FAIL) alongside a single headline
   verdict — cheap at 22-circuit/2-cluster-fit scale, materially strengthens the mandatory
   gate.
4. **[MAJOR, testability]** `min_support_per_component` has no pre-registered value, unlike
   `F12_AGREEMENT_THRESHOLD`'s explicit "frozen before the real-data run" discipline —
   inconsistent standard. **EDIT, accepted.** Gate 2 pre-registers
   `MIN_COMPONENT_WEIGHT_FRAC = 0.05` (no fitted component may hold <5% of pooled weight) as
   a named constant chosen before the real fit, same discipline as F12's threshold.
5. **[MAJOR, simplicity/underbuilt]** router's only check is symbol existence
   (`import`+`hasattr`), proving nothing about whether the mapping is semantically true.
   **Partial EDIT, partial REJECT with reason.** A full numerical sensitivity/identifiability
   proof per basis parameter is Phase 2/4-scale work (out of this substrate phase's budget
   and stated deliverable — the router documents observability routing, it does not itself
   re-derive Phase 3's basis fit). Accepted fix: every router entry must additionally cite
   the exact existing code (file:line) showing that view/session-runner already consuming
   that regime (e.g. `session_braking.py` filtering on `straight_brake`) — grounds each
   entry in verifiable current code, not just a resolvable name, without overbuilding a new
   statistical analysis this phase doesn't need.
6. **[MINOR, intent-fit]** Gate 3's FAIL verdict (if it occurs) doesn't propagate into Gate
   4's CSV artifact — a downstream reader can't tell if the numbers sit inside a
   stability-confirmed or known-unstable regime. **EDIT, accepted, cheap.** Rollup script
   output includes a metadata header/companion note citing the F12 verdict + artifact path.

## Plan-approval checkpoint
Satisfied via `user-decision` citing `LAUNCH_ORDER:Mission` (delegated mode, no reachable
human; Admiral ratifies).
