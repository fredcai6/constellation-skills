# Review Result

## Assigned Gate
`g2` (issue #667, epic #659 — "the join": season-capable bounded-validation harness)

## Result
`APPROVE`

## Handoff compliance
PASS. The harness runs the g1 join over a real bounded slice, composing each circuit's #664
field-reference `.fingerprint` × each driver's #666-fit cells via `join_weekend_prior` for BOTH
channels (`utilization`, `energy`), and emits an honest-σ summary that surfaces thin/unresolved
exposure. It is season-capable (circuit list is a `build_summary(...)` argument) and partial-slice
tolerant. Every close-criterion below verified independently against source and by reproduction — not
trusted from the implementer's claim.

## Close-criterion verdicts (each verified independently)
- **Seam composition** — PASS. Fits cells via `fit_driver_fingerprints(... map_version=None,
  allow_unverified=True)` into a `tempfile.mkdtemp` scratch `DriverFingerprintStore`; reads
  composition via `ReferenceUtilizationStore.get(...).fingerprint`; reads cells via
  `store.get_fingerprint(driver, era, vocabulary, channel, DEFAULT_WHAT_MEASURE)` where
  `DEFAULT_WHAT_MEASURE == "deficit"` (verified in `address.py`); runs `join_weekend_prior` for both
  `FINGERPRINT_CHANNELS`; records `corner_share`, `mean`, `scale` (`prior.prior.scale`), `nu`,
  `thin_classes`, `weight_on_thin`, `resolved_mask`, `fully_thin`, per-cell `status`/`support_n`.
- **Vocabulary alignment** — PASS. The SAME `ClassVocabulary` object is passed to both
  `_fit_all_drivers` and `_prior_record`/`join_weekend_prior`, so `vocabulary_version` matches and the
  join does not refuse. `class_ids` are DERIVED from the DB: `reference_laps.class_ids_json` filtered
  to `severity:%`; `vocabulary_id` is the shared prefix (`severity:2023:v1`). Not hardcoded.
- **Composition passthrough** — PASS. The WHOLE `.fingerprint` dict (including the non-severity
  `straight`/`braking_zone` keys) is passed as `composition`; `join_weekend_prior` itself selects the
  severity classes (`comps = [composition[cid] for cid in vocabulary.class_ids]`). Not pre-filtered
  or renormalized before the join.
- **Season-capable + partial-tolerant** — PASS. Circuit list is a `build_summary` arg (default
  Monaco/Spain/Great Britain/Belgium). A circuit with no field row is skipped with a printed `[skip]`
  note and recorded in `circuits_skipped`, never crashing. Confirmed on the real DB, which holds only
  Great Britain: Monaco/Spain/Belgium skipped cleanly, 8 priors produced over Great Britain.
- **Tests** — PASS. The synthetic smoke test has NO skipif — it always runs (builds a temp own-DB and
  asserts both channels produce a resolved prior + populated thin surfacing). The real-slice test uses
  a per-function `@pytest.mark.skipif(not _REAL_SLICE_DB.exists())` — note this is per-function, so
  the synthetic test runs even when the real DB is absent (a better choice than the reference file's
  module-level `pytestmark`). Skip-clean behavior demonstrated with an identical-decorator throwaway on
  an absent path → SKIPPED, body never runs.
- **No committed data/*.db; temp DBs only; .pth insert; join untouched** — PASS. Scratch store lives
  in `tempfile.mkdtemp` (outside the repo); `git status` shows no `.db`; editable-.pth `sys.path`
  insert is at the top of the script; the join module is not in g2's file set (imported read-only).
- **simplification_limits** — PASS on both files (exit 0).

## Scope drift
None. Only the two NEW named files. The real slice DB is opened read-only (`mode=ro`), never copied
or committed. Offline/DB-only (no FastF1). The join module (`src/physics/fingerprint/join.py`) is a
separate untracked g1 artifact, imported read-only, not in g2's file set.

## Evidence verdict
Required evidence present and independently reproduced (see pasted output). Test-after mode is
appropriate — the join's correctness is gated by g1's T7 invariants; this file exercises the harness
on data. Synthetic ALWAYS-runs; real-slice skips cleanly when absent.

## map_version structural finding — adjudication
CONFIRMED SOUND. On disk, `map_version` is per-circuit — verified directly:
`reference_laps` / `driver_class_observables` carry `map_version = "2023-Great Britain-Q:v1"` (the
circuit name is embedded). The harness therefore fits each driver ONCE season-wide (`map_version=None`
→ the fit applies no map_version filter, pooling all in-cutoff rows) into the temp store, and only the
composition is per-circuit: the join re-weights those season-pooled cells by THIS circuit's
corner-severity mix, recording the circuit's `map_version` as the prior's provenance. That is exactly
the intended per-weekend prior — season-pooled driver capability × circuit-specific corner-severity
composition. (On the current slice only Great Britain is present, so season-pool == GB, but the
structure is correct for when more circuits land.) I agree with the implementer's reading.

## Code/doc quality
Clean, minimal, well-decomposed. Fails visibly (`ReferenceLapNotFound` when no field rows), no hidden
fallback. Fowler pass driven over both files; `verify_fowler_pass.py` exit 0 (12 smells; 10 absent;
`long-parameter-list` OVERRIDDEN citing the surrounding fit/join kw-only seam convention +
global-crew.md "match surrounding conventions"; `data-clumps` FLAGGED as a minor non-blocking
observation — the (driver,circuit,channel) triple recurs but is the intended flat per-prior JSON
identity and is already partly factored by the `_key()` helper).

## Map impact verdict
- Evidence supports claimed change: yes — harness runs green on the real GB slice (8 priors) and the
  reproduced numbers match the implementer's (VER util `mean=2.693`, `scale=1.368`, `nu=4.0`).
- Constraints not violated: yes — offline/DB-only, temp-DB-only, no `data/*.db`, seams consumed as-is.
- Notes match the diff: yes — new script + test only; the `map_version` per-circuit note matches disk.
- Decision candidates surfaced: yes — the season-wide-fit / per-circuit-composition choice is called
  out as a within-authority structural decision; join module untouched.
- Durable context routed: adequate for a demonstration harness; no interface/contract change.

## Reconciliation check
No architecture divergence — consumes #664/#666/#667 seams as-is, no contract change.

## Blockers
- none.

## Out-of-scope observations
- The emitted JSON summary (`.agent-work/667-join/artifacts/join_bounded_summary.json`) is NOT
  auto-gitignored in this worktree (`git check-ignore` exits 1). It is currently unstaged and the
  harness writes to `.agent-work/` (a local scratch path, not a committed source path), so this is not
  a blocker — but the commander should ensure it is not `git add`-ed at integration.
- g3/full-season run (Monaco/Spain/Belgium) is blocked only on those circuits' `reference_laps` +
  `driver_class_observables` rows being built into the slice DB; the harness already runs the whole
  season the moment they are present (circuit list is an argument). Not this gate's work.
- Minor (data-clumps observation): a `(driver, circuit, channel)` value object could bundle the triple
  if the record set grows; trivial, non-blocking.

## Reproduced evidence (pasted)

pytest (verbose, showing both selected and their run/skip state):
```
tests/unit/physics/fingerprint/test_join_bounded_validation.py::test_synthetic_smoke_both_channels_prior_and_thin_surfacing PASSED [ 50%]
tests/unit/physics/fingerprint/test_join_bounded_validation.py::test_real_slice_surfaces_thin_exposure PASSED [100%]
============================== 2 passed in 0.62s ==============================
```

skip-clean demonstration (identical skipif decorator on an absent DB path):
```
claude/skip_demo_test.py::test_real_slice_would_skip_when_absent SKIPPED [100%]
SKIPPED [1] ... real bounded slice DB not present at Z:\definitely\not\here\reference_utilization_run.db -- this test exercises REAL data
============================= 1 skipped in 1.51s ==============================
```

simplification_limits:
```
PASS (2 files checked)
exit: 0
```

harness real-slice run (load-bearing) + emitted summary:
```
  [skip] no reference_laps field row for circuit 'Monaco' -- skipped
  [skip] no reference_laps field row for circuit 'Spain' -- skipped
  [skip] no reference_laps field row for circuit 'Belgium' -- skipped
join_bounded_summary: 8 priors over 1 circuit(s) (skipped 3); thin exposure -> 0 weight_on_thin, 0 thin_classes, 0 fully-thin
circuits_processed: ['Great Britain']   circuits_skipped: ['Monaco', 'Spain', 'Belgium']   n_priors: 8
vocab: severity:2023:v1 k=4 ['...:c0','...:c1','...:c2','...:c3']
sample prior VER/util: corner_share=0.42174..., mean=2.6932..., scale=1.3682..., nu=4.0,
  thin_classes=[], weight_on_thin=0.0, resolved_mask=[True,True,True,True], fully_thin=False,
  map_version='2023-Great Britain-Q:v1', vocabulary_version='severity:2023:v1'
thin_resolved_cells_near_floor: 8 entries, all severity:2023:v1:c1 (support_n≈3.558 — honest thin signal)
```

DB shape confirming map_version is per-circuit:
```
reference_laps: year=2023 gp_name='Great Britain' session_type='Q' map_version='2023-Great Britain-Q:v1' (reference_id Ferrari / Red Bull Racing / __field__)
driver_class_observables: gp_name='Great Britain' map_version='2023-Great Britain-Q:v1'
```

## Workflow Feedback
- **Handoff gaps:** The handoff was thorough and its close criteria mapped cleanly to verifiable
  checks. It did not state whether the real-slice DB would be present in this environment — it was, so
  both tests ran; I had to separately demonstrate the absent-DB skip path to satisfy the "skips cleanly
  when absent" criterion. A one-line "the archived slice DB IS present in the review env; verify the
  skip path synthetically" would have pre-empted that step.
- **Context rediscovered:** None material. `DEFAULT_WHAT_MEASURE == "deficit"` and
  `FINGERPRINT_CHANNELS == (utilization, energy)` had to be confirmed in `address.py` to validate the
  seam calls, but that is ordinary verification, not a handoff gap.
- **Instructions improvised around:** None. The engine, survey template, and Fowler rail covered the
  review cleanly.
- **What would have made this easier:** Confirm the JSON-output gitignore status in the handoff (the
  implementer already flagged it) so the reviewer need not re-derive it.

## Return status
`complete`
