# Implementation Result

Status values follow `skills/workbench/references/status-model.md`.

## Assigned gate
`g2` (issue #667, epic #659 — "the join", season-capable bounded-validation harness)

## Completed slice
Built a SEASON-CAPABLE, OFFLINE harness that runs the g1 join on a real bounded slice — reading
#664 `reference_laps` composition × #666-fit fingerprint cells — and emits an honest-σ summary that
surfaces thin exposure. Plus a CI-safe test file (always-run synthetic smoke + skip-if-absent
real-slice). All three implementation gates driven through the engine to done.

## Scope
**Files changed (both NEW, committed-tier, not staged by me):**
- `scripts/join_bounded_validation_667.py`
- `tests/unit/physics/fingerprint/test_join_bounded_validation.py`

**Local-only artifacts written (gitignored/uncommitted, not staged):**
- `.agent-work/667-join/artifacts/join_bounded_summary.json` (harness output)
- `.agent-work/667-join/crew-plans/g2-implement-plan.json` (+ `.journal`) — the engine plan
- this result file

**Specific exclusions touched:** no. No FastF1/online call (offline/DB-only); no `data/*.db`
written (temp fingerprint store lives in a `tempfile.mkdtemp` scratch dir); the join module
(`src/physics/fingerprint/join.py`) was NOT edited; the real slice DB was opened read-only, never
copied or committed.

## Behavior changed
Yes — new demonstration harness + tests only. No production/library behavior changed; the harness
CONSUMES the #664/#666/#667 seams as-is.

Design summary:
- **One DB-derived vocabulary, reused for fit + join.** Severity `class_ids` come from
  `reference_laps.class_ids_json` filtered to `severity:%`; `vocabulary_id` is the shared prefix
  (`severity:2023:v1`), `rules_era = era_key(year)`, `f12_verdict="UNVERIFIED"`, fit called
  `allow_unverified=True`. The SAME `ClassVocabulary` object drives the fit and the join so
  `vocabulary_version` matches (the join refuses a mismatch loudly).
- **Fingerprint is a season product; composition is per-circuit.** Each driver is fit ONCE
  season-wide (`map_version=None`, pooling all circuits up to `as_of_round`) into a TEMP
  `DriverFingerprintStore`; the join re-weights those season cells by each circuit's corner-severity
  composition. `map_version` on disk is PER-CIRCUIT (`2023-Great Britain-Q:v1`), derived from each
  circuit's field-reference row and passed as join provenance.
- **The WHOLE field-reference `.fingerprint` dict is passed as `composition`** (not pre-filtered /
  renormalized) — the join selects `vocabulary.class_ids` from it itself.
- **Season-capable + partial-slice tolerant.** Circuit list is a `build_summary(...)` argument
  (default `[Monaco, Spain, Great Britain, Belgium]`); a circuit with no field-reference row is
  SKIPPED with a printed note and recorded in `circuits_skipped`, never a crash.
- Per `(driver, circuit, channel)` for BOTH channels it records `corner_share`, `mean`, `scale`
  (`prior.prior.scale`), `nu` (`prior.prior.nu`), `thin_classes`, `weight_on_thin`, `resolved_mask`,
  `fully_thin`, and each cell's `status`/`support_n`; a `thin_surfacing` block aggregates thin/
  unresolved exposure (thin_classes, weight_on_thin, fully-thin, near-floor resolved cells) plus an
  honest prose statement.

Real-slice measured result (GB only on disk): 8 priors (4 drivers × 2 channels) over Great Britain;
Monaco/Spain/Belgium tolerated as absent. Example VER utilization prior: `corner_share=0.4217`,
`mean=2.693`, `scale=1.368`, `nu=4.0`. All 4 severity cells resolve at `as_of_round=12`, but `c1` is
honestly thin (support ~3.56 vs ~212 for c0) and is surfaced via `thin_resolved_cells_near_floor`
(8 entries). The synthetic smoke forces `c1` sub-floor so it goes UNRESOLVED, exercising the
`thin_classes` / `weight_on_thin` fat-σ path directly.

## Map Impact
- **Structural anchors touched:** `struct: scripts/join_bounded_validation_667.py` (NEW harness,
  script-level); `struct: tests/unit/physics/fingerprint/test_join_bounded_validation.py` (NEW test).
- **Capabilities added/changed/affected:** `capability: weekend-utilization-prior validated on a
  real bounded slice` — the join now has a runnable, season-capable demonstration over real #664/#666
  stores that emits an honest-σ, thin-surfacing summary.
- **Constraints/assumptions touched:** offline/DB-only honored; #664/#666/#667 seams consumed as-is
  (no edits); temp-DB-only (#656) and no-`data/*.db` (#632) honored; season-capable circuit-list arg
  satisfied.
- **Decision candidates / resolved decisions:** `decision:validation-reads-real-664-666-stores`
  @grade: settled/inherited — implemented as specified. One local structural choice within authority:
  the fingerprint fit is season-wide (`map_version=None`) and the composition per-circuit, because
  `map_version` is per-circuit on disk and the driver fingerprint is a season product the join
  re-weights per circuit. No frozen literal minted; join module untouched.
- **Claims/evidence produced:** harness runs green offline on the real GB slice (exit 0, 8 priors,
  thin surfaced); `pytest` 2 passed; `simplification_limits.py` PASS.

## Test mode
**Required:** `test-after allowed`
**Satisfied:** yes — one ALWAYS-RUN synthetic smoke test (builds a temp own-DB, asserts both channels
produce a prior and thin surfacing is populated) + one skip-if-absent real-slice test (mirrors
`test_bounded_validation.py`'s `pytest.mark.skipif` on the archived DB path).

## Evidence

```bash
"C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe" -m pytest tests/unit/physics/fingerprint/test_join_bounded_validation.py -q
```
```
collected 2 items
tests\unit\physics\fingerprint\test_join_bounded_validation.py ..        [100%]
============================== 2 passed in 0.59s ==============================
```
(The synthetic smoke RAN, not skipped; the real-slice test ran here because the archived DB is
present, and would skip cleanly if absent.)

```bash
"C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe" src/utils/simplification_limits.py --paths scripts/join_bounded_validation_667.py tests/unit/physics/fingerprint/test_join_bounded_validation.py
```
```
PASS (2 files checked)
exit: 0
```

Harness real-slice smoke (load-bearing):
```bash
"C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe" scripts/join_bounded_validation_667.py
```
```
  [skip] no reference_laps field row for circuit 'Monaco' -- skipped
  [skip] no reference_laps field row for circuit 'Spain' -- skipped
  [skip] no reference_laps field row for circuit 'Belgium' -- skipped
join_bounded_summary: 8 priors over 1 circuit(s) (skipped 3); thin exposure -> 0 weight_on_thin, 0 thin_classes, 0 fully-thin -> ...join_bounded_summary.json
```
(At `as_of_round=12` all 4 GB severity cells resolve, so `weight_on_thin`/`thin_classes`/`fully_thin`
are 0 — the thin c1 signal is instead surfaced via 8 `thin_resolved_cells_near_floor` entries, an
honest "resolved-but-thin" reading.)

**Result:** pass (all three checks).

## TDD evidence, if required
Not required (test-after mode). Green observed after writing: `pytest` 2 passed.

## Docs/contracts touched
- none — new script + test only; no interface/contract changes.

## Assumptions
- The default `--db-path` points at the external archived real slice
  (`C:/Programs/f1Brainz/.agent-work/archive/2026-07-26-664-reference-laps/artifacts/reference_utilization_run.db`)
  so `main()` runs out of the box; every parameter (year/session/circuits/drivers/as_of_round/out)
  is overridable on the CLI.
- Fitting season-wide (`map_version=None`) and joining per-circuit is the intended composition
  (per-circuit `map_version` on disk + season-level driver fingerprint). Within stated authority.
- On the real slice, `c1` resolving at `as_of_round=12` (not going unresolved) is a genuine measured
  outcome, not a defect — it clears the 1.0 support floor once Great Britain is visible, but stays
  thin (~3.56) and is reported as such.

## Stop conditions hit
- none. The fit/reference/join seams composed exactly as the handoff described; no scope excess and
  no decision beyond authority was needed.

## Out-of-scope observations
- The commander's g3 step (full 4-circuit run) needs the other three circuits' `reference_laps` +
  `driver_class_observables` rows built into the slice DB; the harness already runs the full season
  the moment they are present (circuit list is an argument).

## Workflow Feedback
- **Handoff gaps:** the handoff specified `build_summary(db_path, *, year, session_type, circuits,
  drivers, as_of_round)` but did NOT name a `db_path` default for `main()`; I defaulted it to the
  archived real-slice path (the only real data available). Minor — worth stating explicitly in future
  handoffs.
- **Context rediscovered:** that `map_version` is PER-CIRCUIT (`2023-Great Britain-Q:v1`), not a
  season-level value, and therefore the fingerprint fit must be season-wide (`map_version=None`) while
  only the composition is per-circuit. The handoff mentioned "season-capable" but not the per-circuit
  `map_version` shape; I had to inspect the real DB to settle it. A one-line note ("map_version is
  per-circuit; fit season-wide with map_version=None, compose per-circuit") would have saved the probe.
- **Instructions improvised around:** none of substance. The `IMPLEMENTER_PLAN` template's `m1`
  TDD-red guidance is a no-op for a test-after run; I collapsed to a single green command postcondition
  per the template's own escape clause.
- **What would have made this easier:** confirm in the handoff that `.agent-work/` is NOT actually
  broadly gitignored in this worktree (`git check-ignore` exits 1 for `.agent-work/667-join/...`;
  only specific subpaths + `.agent-work/**/*.db|*.pkl|*.npz|scratch/` are ignored). The emitted JSON
  summary is therefore not auto-ignored — I left it unstaged (I stage nothing), but the "gitignored —
  local-only" claim in the handoff's Deliverable Path Check is inaccurate for this path.

## Return status
`complete`
