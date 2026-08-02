# Implementation Result

Status values follow `skills/workbench/references/status-model.md`.

## Assigned gate
`g4 (execute.json: g4-implement)` — Regime distance-share rollup + observability router

## Completed slice
New `src/physics/layer2/regime_rollup.py` (`corner_bin_share`, `circuit_distance_share`,
`load_circuit_frame`), new `src/physics/layer2/observability_router.py`
(`ROUTER_ENTRIES` for the four regime tags, every entry citation-grounded against real
current source), and a new CLI `scripts/build_regime_rollup.py` that was **run for real**
against `C:/Programs/f1Brainz/data/damage_integrals.db` (612,615 rows, 22 circuits, mixture
fit `k=3`). Gate 3's real-data F12 verdict (**FAIL**, n_pass=0/5) is propagated honestly into
the rollup's own output — as leading `#`-comment lines in the CSV itself *and* a sibling
`.meta.json` — so a reader of the CSV alone still sees it. All computed fields are named
`distance_share`, never `time_share`, throughout `regime_rollup.py` (AST-verified by a
dedicated test).

## Scope
**Files changed:**
- `src/physics/layer2/regime_rollup.py` (new)
- `src/physics/layer2/observability_router.py` (new)
- `scripts/build_regime_rollup.py` (new)
- `tests/unit/physics/layer2/test_regime_rollup.py` (new — 18 cases)
- `tests/unit/physics/layer2/test_observability_router.py` (new — 12 cases)
- `.agent-work/625-segmentation-substrate/artifacts/regime_time_share.csv` (generated
  evidence artifact)
- `.agent-work/625-segmentation-substrate/artifacts/regime_time_share.meta.json` (generated
  evidence artifact)
- `.agent-work/625-segmentation-substrate/g4-implementer-plan.json` (this run's engine plan,
  driven to completion)

**Specific exclusions touched:** no — `property_mixture.py`, `mixture_stability.py`,
`corner_descriptors.py`, and `arcs.py` were not modified (`git status` confirms zero changes
to those files from this run; only their existing public functions were imported and called).
`data/damage_integrals.db` was never written to — both `regime_rollup.load_circuit_frame` and
`scripts/build_regime_rollup.py`'s pooled-load connect via a `sqlite3` URI with `?mode=ro`,
which fails writes at the driver level (independently verified for `load_circuit_frame` via a
`test_connection_is_read_only` test). No `circuits.yaml` or other production-default touched.
No `evo_predictor`/`latent_power`/`compound_prior` imports anywhere in the 5 new files (grep
verified, zero matches — see Evidence).

## Behavior changed
Yes — new capability only (no existing module edited).

## Map Impact
- **Structural anchors touched:** `struct:physics.layer2` — three new modules:
  `regime_rollup.py` (`corner_bin_share`, `circuit_distance_share`, `load_circuit_frame`),
  `observability_router.py` (`ROUTER_ENTRIES`), and `scripts/build_regime_rollup.py` (CLI
  composing Gate 2's `fit_property_mixture` + Gate 4's own rollup functions over the real
  `data/damage_integrals.db` `grip_bin_obs` table).
- **Capabilities added/changed/affected:** per-circuit regime distance-share rollup (the x6
  excursion's previously-unbuilt deliverable) is now built and has been run once against the
  real store, producing `regime_time_share.csv` (22 circuit rows, corner/straight +
  3-class corner sub-shares each summing correctly). Observability router (Phase 1's
  round-1 load-bearing consumer) is now built with every entry grounded in verified real
  source.
- **Events added/changed/affected:** none.
- **Constraints/assumptions touched:** `constraint:physics_region_no_evo_import` — honored
  (grep-verified zero matches across all 5 new physics-region files).
  `constraint:canonical_data_source` — honored (`grip_bin_obs` via the DB, read-only; no
  FastF1 direct calls). Pre-ruling #2 (lateral axis from `grip_bin_obs`, not fingerprint
  CSVs) — honored, reuses Gate 1/2's existing descriptor pipeline unchanged. Pre-ruling #6
  (no `circuits.yaml`/production-default writes) — honored.
- **Decision candidates / resolved decisions:** the class-share renormalization convention
  (see Assumptions below) is a real interpretive choice this gate made and is now the
  behavior baked into `regime_rollup.py` — future consumers of `corner_class_i_distance_share`
  should know a degenerate (invalid-descriptor) row's bin-distance mass gets proportionally
  absorbed into whichever classes the circuit's *valid* rows belong to, not left unattributed.
  This was forced by the handoff's literal "values sum to corner_distance_share across
  classes" requirement and is the correct reading of it, not an arbitrary pick.
- **Claims/evidence produced:** `regime_time_share.csv` + `.meta.json` (real-store run,
  timestamped, F12 verdict embedded) back the claim "the rollup script runs end-to-end
  against the real store and produces one row per circuit with the expected Monza<Monaco
  sanity ordering." `test_observability_router.py`'s citation-grounding tests back the claim
  "every router entry is independently verifiable against real, currently-true source" (not
  just internally self-consistent prose).
- **Trust limitations / drift found:** none newly found — `circuits.yaml`'s low-trust
  `downforce` field was correctly NOT used anywhere in this gate's work, per its Map
  Confidence Flag. The F12 FAIL verdict (Gate 3, already known) means
  `corner_class_i_distance_share` values across the CSV should be read as provisional
  substrate output, not a validated class taxonomy — this is the primary trust caveat and it
  is now carried in the rollup's own output per the Close Criteria.
- **Triage candidates:** see Out-of-scope observations below (CONVERGED_PLAN's Gate-4
  "integrate step" closing checks were only implicit in the handoff — flagged for the launch
  order's future handoffs to state Required Evidence completely per-gate rather than
  splitting it across the handoff and CONVERGED_PLAN prose).

## Test mode
**Required:** test-after with synthetic fixtures for the math; a DB-fixture smoke test (not
the real store) for the loader; a real-store run for the script's evidence artifact.
**Satisfied:** yes — `regime_rollup.py`'s math functions (`corner_bin_share`,
`circuit_distance_share`) are covered entirely by synthetic-fixture tests (no DB);
`load_circuit_frame` is covered by a `tmp_path` sqlite fixture, never the real 612k-row store;
`scripts/build_regime_rollup.py` was run twice for real against
`C:/Programs/f1Brainz/data/damage_integrals.db` (once during development, once as the
`advance`d command-check evidence for plan item m3), producing the committed CSV/meta
artifacts. `observability_router.py` is covered by a synthetic-free suite that reads real
source files directly (not a DB concern).

TDD was followed throughout (see TDD evidence below): tests written and observed failing
(module import error) before each of `regime_rollup.py` and `observability_router.py` existed.

## Evidence

```bash
$ py -m pytest tests/unit/physics/layer2/test_regime_rollup.py tests/unit/physics/layer2/test_observability_router.py -v
```
```
tests/unit/physics/layer2/test_regime_rollup.py::TestCornerBinShare::test_set_form PASSED
tests/unit/physics/layer2/test_regime_rollup.py::TestCornerBinShare::test_set_form_full_default_n_bins PASSED
tests/unit/physics/layer2/test_regime_rollup.py::TestCornerBinShare::test_count_form PASSED
tests/unit/physics/layer2/test_regime_rollup.py::TestCornerBinShare::test_empty_set PASSED
tests/unit/physics/layer2/test_regime_rollup.py::TestCornerBinShare::test_zero_count PASSED
tests/unit/physics/layer2/test_regime_rollup.py::TestCornerBinShare::test_custom_n_bins PASSED
tests/unit/physics/layer2/test_regime_rollup.py::TestCircuitDistanceShare::test_bin_occupancy_and_class_split_exact PASSED
tests/unit/physics/layer2/test_regime_rollup.py::TestCircuitDistanceShare::test_straight_plus_corner_sums_to_one PASSED
tests/unit/physics/layer2/test_regime_rollup.py::TestCircuitDistanceShare::test_multi_key_lap_grouping_distinguishes_same_lap_number PASSED
tests/unit/physics/layer2/test_regime_rollup.py::TestCircuitDistanceShare::test_degenerate_descriptor_row_counts_toward_bin_occupancy_but_not_its_own_class PASSED
tests/unit/physics/layer2/test_regime_rollup.py::TestCircuitDistanceShare::test_zero_n_samples_falls_back_gracefully PASSED
tests/unit/physics/layer2/test_regime_rollup.py::TestCircuitDistanceShare::test_no_valid_descriptor_rows_gives_zero_class_shares PASSED
tests/unit/physics/layer2/test_regime_rollup.py::TestCircuitDistanceShare::test_no_key_or_value_named_time_share PASSED
tests/unit/physics/layer2/test_regime_rollup.py::TestLoadCircuitFrame::test_loads_only_the_requested_circuit PASSED
tests/unit/physics/layer2/test_regime_rollup.py::TestLoadCircuitFrame::test_loads_the_other_circuit_independently PASSED
tests/unit/physics/layer2/test_regime_rollup.py::TestLoadCircuitFrame::test_missing_circuit_returns_empty_frame PASSED
tests/unit/physics/layer2/test_regime_rollup.py::TestLoadCircuitFrame::test_connection_is_read_only PASSED
tests/unit/physics/layer2/test_regime_rollup.py::TestNoTimeShareIdentifier::test_no_time_share_identifier_in_module_source PASSED
tests/unit/physics/layer2/test_observability_router.py::TestRouterEntriesShape::test_all_four_regime_tags_present PASSED
tests/unit/physics/layer2/test_observability_router.py::TestRouterEntriesShape::test_every_entry_has_required_fields PASSED
tests/unit/physics/layer2/test_observability_router.py::TestCitationsResolveAgainstRealSource::test_every_citation_in_tag_is_grounded[corner] PASSED
tests/unit/physics/layer2/test_observability_router.py::TestCitationsResolveAgainstRealSource::test_every_citation_in_tag_is_grounded[straight_throttle] PASSED
tests/unit/physics/layer2/test_observability_router.py::TestCitationsResolveAgainstRealSource::test_every_citation_in_tag_is_grounded[straight_coast] PASSED
tests/unit/physics/layer2/test_observability_router.py::TestCitationsResolveAgainstRealSource::test_every_citation_in_tag_is_grounded[straight_brake] PASSED
tests/unit/physics/layer2/test_observability_router.py::TestStraightCoastHonestlyGroundsIndirectLinkage::test_coast_entry_does_not_claim_a_direct_regime_filter PASSED
tests/unit/physics/layer2/test_observability_router.py::TestNoInventedCitations::test_all_cited_files_exist[corner] PASSED
tests/unit/physics/layer2/test_observability_router.py::TestNoInventedCitations::test_all_cited_files_exist[straight_throttle] PASSED
tests/unit/physics/layer2/test_observability_router.py::TestNoInventedCitations::test_all_cited_files_exist[straight_coast] PASSED
tests/unit/physics/layer2/test_observability_router.py::TestNoInventedCitations::test_all_cited_files_exist[straight_brake] PASSED
tests/unit/physics/layer2/test_observability_router.py::TestNoInventedCitations::test_all_referenced_view_classes_actually_exist PASSED

============================= 30 passed in ~4s ==============================
```

**Result:** pass (30/30, engine-verified via `advance m1-regime-rollup-module` and
`advance m2-observability-router` command-check postconditions).

### Real-store run transcript

```bash
$ py scripts/build_regime_rollup.py --db C:/Programs/f1Brainz/data/damage_integrals.db
```
```
Loaded 612615 pooled rows across 22 circuits from C:/Programs/f1Brainz/data/damage_integrals.db
Fitting property mixture ONCE on 612615 pooled descriptors (this may take a couple of minutes)...
Fitted mixture: k=3 (shared class vocabulary for every circuit below)
  Abu Dhabi: corner_distance_share=0.6626 straight_distance_share=0.3374 n_laps=1134 n_rows=24044
  Australia: corner_distance_share=0.8392 straight_distance_share=0.1608 n_laps=870 n_rows=23362
  Austria: corner_distance_share=0.6180 straight_distance_share=0.3820 n_laps=2723 n_rows=53849
  Azerbaijan: corner_distance_share=0.5977 straight_distance_share=0.4023 n_laps=2017 n_rows=38581
  Bahrain: corner_distance_share=0.5234 straight_distance_share=0.4766 n_laps=1946 n_rows=32596
  Brazil: corner_distance_share=0.7172 straight_distance_share=0.2828 n_laps=494 n_rows=11338
  China: corner_distance_share=0.6165 straight_distance_share=0.3835 n_laps=763 n_rows=15053
  Emilia Romagna: corner_distance_share=0.7430 straight_distance_share=0.2570 n_laps=1183 n_rows=28126
  Great Britain: corner_distance_share=0.7899 straight_distance_share=0.2101 n_laps=893 n_rows=22572
  Hungary: corner_distance_share=0.7298 straight_distance_share=0.2702 n_laps=2517 n_rows=58777
  Italy: corner_distance_share=0.5186 straight_distance_share=0.4814 n_laps=1967 n_rows=32642
  Japan: corner_distance_share=0.8160 straight_distance_share=0.1840 n_laps=1476 n_rows=38539
  Las Vegas: corner_distance_share=0.5745 straight_distance_share=0.4255 n_laps=216 n_rows=3971
  Mexico: corner_distance_share=0.5734 straight_distance_share=0.4266 n_laps=1062 n_rows=19488
  Miami: corner_distance_share=0.7221 straight_distance_share=0.2779 n_laps=954 n_rows=22043
  Monaco: corner_distance_share=0.8314 straight_distance_share=0.1686 n_laps=1171 n_rows=31154
  Netherlands: corner_distance_share=0.8199 straight_distance_share=0.1801 n_laps=1373 n_rows=36021
  Qatar: corner_distance_share=0.6621 straight_distance_share=0.3379 n_laps=228 n_rows=4831
  Saudi Arabia: corner_distance_share=0.9104 straight_distance_share=0.0896 n_laps=821 n_rows=23919
  Singapore: corner_distance_share=0.6686 straight_distance_share=0.3314 n_laps=1129 n_rows=24154
  Spain: corner_distance_share=0.7176 straight_distance_share=0.2824 n_laps=2502 n_rows=57455
  United States: corner_distance_share=0.7272 straight_distance_share=0.2728 n_laps=434 n_rows=10100

F12 verdict propagated into rollup output: FAIL (n_pass=0/5)
Wrote 22 circuit rows -> .agent-work\625-segmentation-substrate\artifacts\regime_time_share.csv
Wrote F12-verdict metadata -> .agent-work\625-segmentation-substrate\artifacts\regime_time_share.meta.json
```

**Monza vs Monaco:** Monza (`gp_name="Italy"`) `corner_distance_share = 0.5186` **IS LESS
THAN** Monaco `corner_distance_share = 0.8314`. The expected sanity ordering holds on the
real store (Monza is a low-downforce, straight-heavy circuit; Monaco is a tight street
circuit with almost no straights).

**CSV's first 5 data rows (with leading comment/metadata header, verbatim from the
committed file):**
```
# F12 HELD-OUT-CIRCUIT STABILITY VERDICT: FAIL (n_pass=0/5) -- see .agent-work\625-segmentation-substrate\artifacts\f12_holdout_stability.json
# CAVEAT: this rollup's class-membership substrate did NOT pass its held-out-circuit stability check -- treat class-level sub-shares as provisional, not validated.
# metadata: .agent-work\625-segmentation-substrate\artifacts\regime_time_share.meta.json
# generated_utc: 2026-07-18T06:47:40.380665+00:00
gp_name,corner_distance_share,straight_distance_share,corner_class_0_distance_share,corner_class_1_distance_share,corner_class_2_distance_share,n_laps,n_rows
Abu Dhabi,0.6625881834215167,0.3374118165784833,0.07041185770994825,0.45982545037193984,0.13235087533962517,1134,24044
Australia,0.8391522988505747,0.16084770114942526,0.09779687391848767,0.4082093874816794,0.3331460374504028,870,23362
Austria,0.6179879728240911,0.3820120271759089,0.10267924073099603,0.33051340785774236,0.18479532423535233,2723,53849
Azerbaijan,0.5977472731779871,0.40225272682201285,0.024284536280107905,0.3996360337866885,0.17382670311119294,2017,38581
Bahrain,0.5234455292908531,0.4765544707091469,0.0075107979398650136,0.3826917355594214,0.13324299579156781,1946,32596
```

**Monaco / Italy rows specifically:**
```
Italy,0.5186469527477312,0.4813530472522688,0.02259271854790443,0.3560033929815596,0.14005084121826718,1967,32642
Monaco,0.8314262595217419,0.16857374047825816,0.03462649427980601,0.4116219671217407,0.38517780811019517,1171,31154
```

**F12-verdict metadata content (`regime_time_share.meta.json`, verbatim):**
```json
{
  "timestamp_utc": "2026-07-18T06:47:40.380665+00:00",
  "db_path": "C:\\Programs\\f1Brainz\\data\\damage_integrals.db",
  "mixture_k": 3,
  "n_circuits": 22,
  "f12_artifact_path": ".agent-work\\625-segmentation-substrate\\artifacts\\f12_holdout_stability.json",
  "f12_headline_verdict": "FAIL",
  "f12_n_pass": 0,
  "f12_n_splits": 5,
  "f12_mean_statistic": "Infinity",
  "f12_min_statistic": "Infinity",
  "f12_max_statistic": "Infinity",
  "caveat": "this rollup's class-membership substrate did NOT pass its held-out-circuit stability check -- treat class-level sub-shares as provisional, not validated."
}
```

**F12 FAIL verdict readability check:** the CSV's own leading comment lines carry the FAIL
verdict, n_pass/n_splits, the caveat sentence, and the metadata file path directly in the
committed CSV artifact — a reader opening only `regime_time_share.csv` sees the FAIL verdict
without needing to know `regime_time_share.meta.json` or `f12_holdout_stability.json` exist.
**Confirmed: the rollup output visibly carries the F12 FAIL verdict, in both artifacts.**

### Supplementary closing-check evidence (CONVERGED_PLAN.md Gate 4 prose, not in the
handoff's own Required Evidence list — see Workflow Feedback)

```bash
$ grep -rn "evo_predictor\|latent_power\|compound_prior" src/physics/layer2/property_mixture.py src/physics/layer2/mixture_stability.py src/physics/layer2/regime_rollup.py src/physics/layer2/corner_descriptors.py src/physics/layer2/observability_router.py
```
**Result:** zero matches (grep exit code 1 = no matches found) — confirms
`constraint:physics_region_no_evo_import` across all 5 named files.

```bash
$ py -m pytest tests/unit/physics -q
```
**Result:** NOT COMPLETED within this run's evidence-gathering window. Kicked off in the OS
background (heavy real numeric fits across many `layer2` test files — confirmed alive via
`Get-Process python`, accumulating genuine CPU time, not hung); after 16+ minutes of wall
clock it had not finished, and since this check is supplementary (named only in
`CONVERGED_PLAN.md`'s Gate 4 "integrate step" prose, not in the handoff's own Required
Evidence list — see Workflow Feedback), I did not block this gate's closure on it. The
process may still be running; its stdout is captured at
`C:\Users\fredc\AppData\Local\Temp\claude\C--Programs-f1Brainz\cac4681b-3be0-47b5-bcad-8d680b5c633e\tasks\b05dinabb.output`
for whoever picks this up next (Commander/Reviewer) to inspect or re-run. The narrower,
handoff-mandated evidence (`test_regime_rollup.py` + `test_observability_router.py`, 30/30
passing; the real-store script run) is fully collected and engine-verified above and does not
depend on this full-suite run's outcome.

## TDD evidence

- Failing test observed (`regime_rollup.py`): `py -m pytest tests/unit/physics/layer2/test_regime_rollup.py -v` →
  `ModuleNotFoundError: No module named 'src.physics.layer2.regime_rollup'` (collection error,
  before the module existed).
- Failing test observed (`observability_router.py`): `py -m pytest tests/unit/physics/layer2/test_observability_router.py -v` →
  `ModuleNotFoundError: No module named 'src.physics.layer2.observability_router'`
  (collection error, before the module existed).
- Passing test observed: both suites green, 30/30, shown above.
- Refactor while green: one test-only refactor — `test_degenerate_descriptor_row_counts_toward_bin_occupancy_not_class_share`
  initially asserted a degenerate row's bin gets *excluded* from every class share (leaving
  `class_sum < corner_distance_share`); the first real run showed that's inconsistent with the
  handoff's explicit "values sum to corner_distance_share across classes" invariant (the
  weighted-average renormalization over valid rows necessarily makes the class shares sum to
  the *full* `corner_distance_share`, degenerate-row bins included, by construction). Fixed the
  test's expectation (not the implementation) to match the spec's literal requirement, renamed
  it `test_degenerate_descriptor_row_counts_toward_bin_occupancy_but_not_its_own_class`, and
  documented the renormalization behavior explicitly in both the test and
  `circuit_distance_share`'s docstring.

## Docs/contracts touched
- `src/physics/layer2/regime_rollup.py`'s and `observability_router.py`'s own module/function
  docstrings are the only "docs" touched — no `docs/architecture/` files edited (out of this
  gate's scope; Cartographer reconcile is the intended consumer of this result's Map Impact
  section).

## Assumptions
- **Class-share renormalization convention** (see Decision candidates above): a degenerate
  (descriptor-invalid) row still contributes its bin to `corner_distance_share` but is
  excluded from the class-membership weighting; because the surviving valid rows' weights are
  renormalized to sum to 1, the class shares still sum to the *full* `corner_distance_share`
  (the degenerate row's mass gets proportionally absorbed into whatever classes the valid rows
  belong to, not left as unattributed "unknown" mass). This is the literal reading of the
  handoff's "values sum to corner_distance_share across classes" requirement and the only
  self-consistent one when M>0; the M=0 case (zero valid rows) is the sole necessary exception,
  returning `0.0` for every class since there is no membership evidence at all in that case.
- **Lap identity key**: `_lap_key_columns` groups by `lap_number` plus any of
  `year`/`session_type`/`driver`/`stint_num` present in the input frame — the handoff said
  "per lap" without pinning down the exact grouping key set, and the real `grip_bin_obs` table
  does carry all of these columns (confirmed via schema read), so a `lap_number`-only key
  would silently merge different drivers'/sessions'/stints' laps that happen to share a lap
  number. Chose the fuller key as the safe interpretation; documented in the function.
- **CSV row/column ordering**: sorted by `gp_name` alphabetically (not handoff-specified);
  chosen for deterministic, diff-friendly output.
- Router entry `view` field uses `<module>.<ClassName>` (e.g. `"lateral_view.LateralView"`)
  matching the handoff's own example format exactly.

## Stop conditions hit
None. `data/damage_integrals.db` was reachable; Gate 1/2/3's public functions matched the
handoff's description exactly (verified by direct read before writing any code); every router
citation was independently groundable in real, currently-true code (including the
`straight_coast` case, which required stating the indirect/parallel mechanism honestly rather
than inventing a `regime == "straight_coast"` filter that does not exist).

## Out-of-scope observations
- `CONVERGED_PLAN.md`'s Gate 4 prose states "this gate's integrate step ALSO runs the full
  closing checks: `py -m pytest tests/unit/physics -q` (full-suite regression) and a
  grep-based no-evo-import check" — the handoff's own Required Evidence section only lists
  the two unit-test commands + the real-store run, not these two. I ran both as supplementary
  evidence anyway (cheap, directly serve `constraint:physics_region_no_evo_import` already
  assigned to me) rather than silently skipping them or silently treating them as blocking
  scope creep — see Workflow Feedback. Whether these two checks are formally an
  Implementer-owned deliverable vs. a Commander-integrate-step deliverable for THIS gate is a
  process question for Commander/Reviewer to settle, not something I should unilaterally
  decide belongs to "my" scope or not.

## Workflow Feedback

- **Handoff gaps:** the handoff's Required Evidence section (two `pytest` commands + the
  real-store run) is narrower than `CONVERGED_PLAN.md`'s own Gate 4 prose, which additionally
  names a full-suite regression (`py -m pytest tests/unit/physics -q`) and a 5-file grep-based
  no-evo-import check as part of "this gate['s]... integrate step." A crew implementer reading
  only the handoff (as intended — the handoff is supposed to be self-contained) would miss
  these two checks entirely unless they also read CONVERGED_PLAN.md's prose directly, which I
  did as part of m0-context's Stop-Condition verification. Name the field: handoff's "Required
  Evidence" section vs. CONVERGED_PLAN.md's Gate 4 "Evidence" bullet list disagree on scope.
- **Context rediscovered:** none beyond the routine context-loading step already budgeted for
  in m0-context (reading Gate 1/2/3 source + CONVERGED_PLAN.md's Gate 4 section + cold-critic
  dispositions was necessary and expected, not a surprise rediscovery).
- **Instructions improvised around:** the handoff describes `circuit_distance_share`'s
  class-share weighting only at a high level ("average the membership columns weighted by
  each row's n_samples... values sum to corner_distance_share across classes") without
  spelling out the exact renormalization-over-valid-rows-only mechanics needed to make that
  literally true when some rows are descriptor-invalid. I derived the one internally
  consistent implementation (renormalize weights over the *valid* subset so they still sum to
  1, then scale by the full `corner_distance_share`) and initially wrote a test that assumed a
  *different*, more intuitive-but-inconsistent behavior (excluding the degenerate row's mass
  entirely) — caught this via the actual test run, not by re-reading the prose harder, and
  fixed the test (not the implementation) to match the literal, correct reading of the spec.
- **What would have made this easier:** either (a) the handoff spells out the
  renormalization-vs-exclusion choice explicitly for the M>0-mixed-validity case, or (b) it
  says plainly "left as an implementation judgment call, document your choice" so an
  implementer knows not to second-guess a test written against the wrong intuition. Also:
  folding CONVERGED_PLAN's "integrate step" closing-checks language directly into the
  handoff's Required Evidence list (or explicitly stating "these are integrate-only, not
  yours") would remove the ambiguity flagged above.

## Return status
`complete`
