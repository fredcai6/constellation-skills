# Implementer Handoff — g2 (season-capable bounded-validation harness)

## Gate
`g2` (issue #667, epic #659 — "the join", validation harness)

## Task
Build `scripts/join_bounded_validation_667.py`: a SEASON-CAPABLE, OFFLINE harness that runs the g1
join (`src.physics.fingerprint.join.join_weekend_prior`) on a real bounded slice — reading #664
`reference_laps` composition × #666-fit fingerprint cells — and emits an honest-σ summary. Plus a
CI-safe test `tests/unit/physics/fingerprint/test_join_bounded_validation.py`.

## Protected Intent
Demonstrate the join produces honest σ on REAL data — especially thin-cell fat-σ surfaced via
thin_classes/weight_on_thin. A measured thin/unresolved result is a COMPLETE outcome, reported with
real numbers, never dressed up. The harness must be season-capable (circuit list is an ARGUMENT,
not hardcoded) so #670 can run the full season later.

## Test Mode
`test-after allowed` (the harness is a demonstration; the join's correctness is already gated by
g1's T7 invariants). Ship one always-run synthetic smoke test + one skip-if-absent real-slice test.

## Close Criteria
- `scripts/join_bounded_validation_667.py` — a `build_summary(db_path, *, year, session_type,
  circuits, drivers, as_of_round) -> dict` (or similar) that, per (driver, circuit, channel) for
  BOTH channels ("utilization","energy"):
  1. Fits the #666 fingerprint cells via `fit_driver_fingerprints(...)` into a TEMP store (temp dir,
     NEVER a committed `data/*.db`).
  2. Reads the circuit's #664 field-reference composition via `ReferenceUtilizationStore.get(year,
     gp_name, session_type, map_version).fingerprint`.
  3. Reads the k fingerprint cells via `store.get_fingerprint(driver, era, vocabulary, channel,
     "deficit")`.
  4. Runs `join_weekend_prior(composition, cells, vocabulary, as_of_round=..., map_version=...)`.
  5. Records per prior: corner_share, prior.mean, prior scale (`prior.prior.scale`), nu
     (`prior.prior.nu`), thin_classes, weight_on_thin, resolved_mask, and each cell's status/support.
- Emit the summary as JSON to a path UNDER `.agent-work/` (gitignored — local-only) and print a
  one-line human summary.
- `main()` defaults the (year, session_type, circuits, drivers, as_of_round) to the launch order's
  bounded slice (2023, "Q", ["Monaco","Spain","Great Britain","Belgium"], ["VER","PER","LEC","SAI"],
  as_of_round=12) BUT accepts overrides — and TOLERATES a circuit whose rows are absent from the DB
  (skip it with a printed note, do not crash) so it runs against a partial slice.
- Tests: (a) an always-run SYNTHETIC smoke test that builds a tiny TEMP own-DB (one `reference_laps`
  field row via `ReferenceUtilizationStore.write` + a handful of `driver_class_observables` rows via
  `write_class_observables`), runs the harness, and asserts both channels produce a prior and thin
  surfacing is populated; (b) a skip-if-absent REAL-slice test (mirror
  `tests/unit/physics/fingerprint/test_bounded_validation.py`'s `pytest.mark.skipif` on the DB
  path) that runs the harness end-to-end on the real DB and asserts it surfaces thin exposure.

## Allowed Scope
- CREATE `scripts/join_bounded_validation_667.py`, `tests/unit/physics/fingerprint/test_join_bounded_validation.py`.
- Consume as-is: `fit_driver_fingerprints` (`src.physics.fingerprint.fit`), `DriverFingerprintStore`
  (`.../store`), `ReferenceUtilizationStore` + `DriverClassObservableRow`
  (`src.physics.utilization.reference_utilization_store`), `ClassVocabulary` + `era_key`
  (`.../vocabulary`), `join_weekend_prior` (`.../join`).
- MIRROR `scripts/fingerprint_bounded_validation.py` for shape (READ it first).

## Specific Exclusions
- Do NOT run any FastF1 online call. Offline / DB-only.
- Do NOT regenerate segment maps or telemetry (that is the #664/#666 build, out of scope here —
  the harness CONSUMES a pre-built own-DB).
- Do NOT commit or write any `data/*.db`. Temp DBs only in tests (#656). Do NOT edit the join module.

## Constraints
- **Editable-.pth worktree trap:** this is a bare script — add
  `_REPO_ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(_REPO_ROOT))` at the top
  (mirror `fingerprint_bounded_validation.py` lines 27-29) so `src.*` resolves to THIS worktree.
- **Vocabulary construction (season-capable, DERIVED not hardcoded):** read the weekend's severity
  class_ids from the DB — the `reference_laps` `class_ids_json` filtered to `severity:%` gives the
  canonical order; build `ClassVocabulary(vocabulary_id=<the severity version prefix, e.g.
  "severity:2023:v1">, rules_era=era_key(year), k=len(sev_classes), class_ids=tuple(sev_classes),
  f12_verdict="UNVERIFIED", f12_provenance="#667 bounded validation")` and pass
  `allow_unverified=True` to `fit_driver_fingerprints` (a bounded slice's taxonomy is not F12-PASS).
  Use the SAME `vocabulary` object for the fit and the join so `vocabulary_version` matches (the join
  refuses a mismatch loudly).
- **Composition selection:** the field-reference `.fingerprint` dict has straight/braking_zone +
  severity keys; the join itself selects `vocabulary.class_ids` from it — pass the WHOLE fingerprint
  dict as `composition`, do NOT pre-filter or renormalize it.
- READ the real signatures before writing: `fit_driver_fingerprints` (fit.py ~line 306),
  `ReferenceUtilizationStore.get`/`.write`/`.write_class_observables`/`DriverClassObservableRow`
  (reference_utilization_store.py), `join_weekend_prior` (join.py).

## Map Anchors (inbound)
- **Structural:** `scripts/join_bounded_validation_667.py` (NEW); `test_join_bounded_validation.py` (NEW).
- **Capability:** weekend-utilization-prior validated on a real bounded slice.
- **Constraints:** offline/DB-only; reuse #664/#666 seams as-is; season-capable (circuit list arg).
- **Decision:** `decision:validation-reads-real-664-666-stores` @grade: settled/inherited.

## Deliverable Path Check
- **Committed** — `scripts/join_bounded_validation_667.py` (`git check-ignore` exit 1). New file.
- **Committed** — `tests/unit/physics/fingerprint/test_join_bounded_validation.py`. New file.
- **Local-only** — the emitted JSON summary under `.agent-work/667-join/...` (gitignored); your
  IMPLEMENTER_RESULT at `.agent-work/667-join/crew-results/g2-implement-result.md`.

## Required Evidence (load-bearing: the synthetic smoke; confirmatory: real-slice if present)
- `py -m pytest tests/unit/physics/fingerprint/test_join_bounded_validation.py -q` green (paste output).
  The synthetic smoke MUST run (not skip); the real-slice test skips cleanly if the DB is absent.
- If you want to smoke the real path, the on-disk real slice (GB only, read-only) is at
  `C:/Programs/f1Brainz/.agent-work/archive/2026-07-26-664-reference-laps/artifacts/reference_utilization_run.db`
  — do NOT copy it into the repo; do NOT commit it. (The full 4-circuit run is the commander's g3
  step, pending an Admiral scope ruling — you only need the harness + tests to work.)

## Verification Commands
```bash
"C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe" -m pytest tests/unit/physics/fingerprint/test_join_bounded_validation.py -q
"C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe" src/utils/simplification_limits.py --paths scripts/join_bounded_validation_667.py tests/unit/physics/fingerprint/test_join_bounded_validation.py
```

## Suggested Model Tier
`stronger — multi-seam offline harness with a subtle vocabulary/composition alignment`

## Authority
Decided: consume #664/#666 seams as-is; season-capable (circuit-list arg); offline/DB-only; use the
same vocabulary for fit+join. You choose local structure/naming. Do NOT change the join module or
mint frozen literals — STOP and return if either seems needed.

## Stop Conditions
Stop and return if: the fit/reference seams don't compose as described (report the real signatures);
allowed scope must be exceeded; a decision outside this authority is needed.

## Return Format
Return IMPLEMENTER_RESULT (write to `.agent-work/667-join/crew-results/g2-implement-result.md`):
completed slice, files changed, test mode satisfied, evidence (paste pytest + simplification),
assumptions, stop conditions hit, out-of-scope observations, workflow feedback.
