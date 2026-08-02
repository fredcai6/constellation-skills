# Review Result

## Assigned Gate
`g2 — Offline loaders + strawman candidate + runner (review)`

## Result
`APPROVE`

## Handoff compliance
All handoff deliverables present and verified: `offline_loader.py`, `db_truth_loader.py`,
`strawman_candidate.py`, `runner.py` in `src/preprocessing/trajectory_grading/`;
integration test `tests/integration/test_trajectory_grading_runner.py` (19 tests on 2023
Belgium Q). All close criteria from `g2-review.md` satisfied: `get_telemetry` confined to
strawman, offline loader raises on cache miss, DB read-only via `mode=ro` URI, arc-length
scaling verified independently, strawman docstring states it is the artifact under study,
runner produces schema-valid GradingReport JSON, all three primitives produce output.

## Scope drift
Diff touches only allowed scope: `src/preprocessing/trajectory_grading/` (4 new modules),
`tests/integration/` (1 new test file), `.agent-work/issue-446/crew-handoffs/` (handoff +
plan docs — agent infrastructure). No g1 pure-core changes, no `windowed_estimator`, no
`physics`, no `evo`/`latent`/`compound`. Specific exclusions honoured.

## Evidence verdict
Evidence is independently verified and sufficient:
- `py -m pytest tests/integration/test_trajectory_grading_runner.py -q` → **19 passed in 2.30s** (re-run by reviewer).
- `py -m src.utils.simplification_limits --paths src/preprocessing/trajectory_grading tests/integration/test_trajectory_grading_runner.py` → **PASS (11 files)** (re-run by reviewer).
- `get_telemetry` grep (Python source only, excluding pycache) → confined to `strawman_candidate.py` only (7 references, all in that file).
- Arc-length scaling throwaway script → see rx2 detail below.

Test mode was test-after (not TDD); handoff did not require TDD. Tests are behavior-focused
(schema structure, primitive output presence, no passes/fails asserted for gates, cross-residual
correctly has no 'passed' key).

## Code/doc quality
All four modules use `logging.getLogger(__name__)`, explicit type hints throughout, named
exceptions (`SessionNotCachedError`, `SessionNotFoundError`) with descriptive messages naming
field + expectation. No silent fallbacks in critical paths. `_LapsShim` is a minimal adapter to
avoid storing the full FastF1 Session in `RawSessionStreams` — justified in both modules.
Constants (`_XY_TO_METRES`, `NAIVE_POSITION_VARIANCE_M2`, `_DEFAULT_SPEED_M_PER_S`) are named
at module scope with docstrings. Docs are module-docstring level and thorough.

One minor concern (not blocking): the `session.load()` exception handler in `offline_loader.py`
(line 157) catches a broad `Exception` and only converts to `SessionNotCachedError` when the
message contains `"cache"`, `"network"`, or `"not"`. Other failures (e.g. corrupt cache file)
will propagate as-is, which is acceptable safe behaviour.

## Map impact verdict

- **Evidence supports claimed change:** Yes — 19/19 integration tests on a real cached session
  prove end-to-end wiring. Arc-length independently confirmed correct.
- **Constraints not violated:** Physics-region isolation maintained (zero evo/latent/compound
  imports). DB-only data access honoured. Offline-only constraint honoured. Raw streams only
  (strawman excepted per pre-ruling 2).
- **Notes match the diff:** Map Impact notes in `g2-implement-RESULT.md` accurately describe
  all four structural anchors touched. Capabilities listed match the diff exactly.
- **Decision candidates surfaced:** DatabaseManager bypass decision is documented with full
  justification in `db_truth_loader.py` module docstring and `g2-implement-RESULT.md`.
- **Durable context routed:** Three triage candidates flagged (decimetre unit convention, GP
  name divergence, offline_mode version guard) — appropriately routed.

## Reconciliation check
No divergence from g1 architecture. The `__init__.py` was intentionally not extended (g2
modules not exported from package init per handoff scope). Map anchors `struct:preprocessing.
trajectory_grading`, `struct:fastf1_api`, `struct:sqlite_db`, `struct:data` updated correctly.
No docs/contracts need immediate update beyond the triage candidates below.

## Blockers
- none

## Out-of-scope observations

1. **FastF1 pos_data X/Y unit convention (Triage):** The `_XY_TO_METRES = 0.1` constant is
   documented in `strawman_candidate.py` but not in architecture docs or any contract file.
   Other harness modules that eventually work with raw pos_data will need to know this.
   Recommend: add to architecture index / `struct:fastf1_api` notes.

2. **GP name divergence in DB (Triage):** FastF1 uses "Belgian Grand Prix"; DB stores "Belgium".
   The `gp_name_in_db` runner parameter works around this, but other GP names likely have
   similar mismatches. A lookup table or data layer note would prevent per-session discovery
   loops for future work.

3. **`fastf1.Cache.offline_mode()` version guard (Triage):** The `AttributeError` on FastF1 <
   3.0 is silently swallowed (best-effort). In production usage an explicit version check and
   hard failure would be safer. Low priority given FastF1 3.8.1 is installed.

## Arc-length scaling — detailed evidence

Throwaway script (created and deleted, not committed) loaded 2023 Belgium Q from the offline
cache at `C:/Programs/f1Brainz/outputs/cache`. Driver 1 (VER) fastest lap, 397 pos_data points.

| Scale hypothesis | Computed arc | Expected |
|---|---|---|
| raw (no scale) | 69,415.7 | would be ~70 km — wrong |
| × 0.1 (decimetres) | **6,941.6 m** | Spa 7004 m — correct |
| × 1.0 (metres assumed) | 69,415.7 m | would be ~70 km — wrong |
| × 0.01 (centimetres) | 694.2 m | would be ~700 m — wrong |

FastF1 `Distance` column (from `get_telemetry`) = 6,949.5 m.
Ratio raw_arc / ff1_dist = 9.9885 ≈ 10 — confirms X/Y are in decimetres.

**`_XY_TO_METRES = 0.1` is correct.**

## Workflow Feedback

- **Handoff gaps:** The handoff's close criteria were precise and independently verifiable —
  well formed. The arc-length check instruction ("e.g. sanity-check…Spa is ~7004 m") was
  exactly what was needed and made the check unambiguous.

- **Context rediscovered:** The `db_truth_loader.py` module docstring includes a comment "We
  still import ``DatabaseManager`` from ``src.data.database`` for nothing" — but inspecting
  the file, `DatabaseManager` is not actually imported at all. The comment is misleading (a
  leftover from a draft decision) but harmless. This was cross-checked by reading the full
  import block.

- **Instructions improvised around:** The skill template says the engine reference lives at
  `references/checklist-engine.md` but that file was absent in the installed skill at
  `C:\Users\fredc\.claude\skills\constellation-reviewer\references\`. The engine Python
  source was read directly as a substitute. This is a misfit in the skill's file layout, not
  a gap in what I needed to do.

- **What would have made this easier:** The handoff's "Verify independently" instruction for
  arc-length was clear. The only friction was the BOM encoding issue when creating the survey
  JSON via PowerShell (Out-File writes UTF-16 LE with BOM by default; the engine's
  `read_text(encoding="utf-8")` rejects this). Workaround: `[System.IO.File]::WriteAllText`
  with explicit `UTF8Encoding($false)`. This is a Windows-specific gotcha worth noting in
  engine docs.

## Return status
`complete`
