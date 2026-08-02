# Implementation Result

Status values follow `skills/workbench/references/status-model.md`.

## Assigned gate
`g7-realrun-implement` (#668 instrument panel, epic #659) — **REWORK 1**: the real-data culmination
gate, reopened solely because the project-mandated `py -m src.utils.simplification_limits` gate
failed on `scripts/instrument_panel_668_report.py`.

## Completed slice
Surgical extract-function refactor of `scripts/instrument_panel_668_report.py` ONLY, so the
project's machine-checked complexity/length gate passes, with **zero behavior change**:

1. `instruments_2_3_replication` (cyclomatic complexity 26 → limit 20) split into 5 helpers:
   `_channel_halves_for_partition`, `_partition_verdict_entry`, `_accumulate_partition_r`,
   `_sigma_honesty_checks_for_channel`, `_combine_class_verdict`. The parent function now only
   sequences these calls in the exact same order the inline code previously executed them in.
2. `render_markdown` (125 lines / complexity 20 → limits 100 lines / 20) split into 4 section
   helpers: `_render_header`, `_render_instrument1`, `_render_instruments_2_3`,
   `_render_instrument4`. The parent function now only concatenates their `list[str]` output in
   the same order the inline code previously appended lines in.
3. JSON key-order stabilization (the handoff's "also fix" item): both `json.dumps(...)` emit
   sites in `main()` (stdout print and `REPORT_JSON_PATH.write_text`) now pass `sort_keys=True`.
   Root cause (identified by the g7 reviewer): `compare_channels_by_class`
   (`src/physics/instrument_panel/replication.py`, out of this gate's scope, already approved at
   g3) builds its returned verdicts dict by iterating a plain Python `set`, whose iteration order
   is randomized per-process by CPython's hash seed. Sorting keys at JSON-emit time makes the
   committed `.json` byte-stable across runs without touching that already-approved module or any
   value.
4. Corrected the narrative on WHICH bug g7's history involves (the reviewer's other
   non-blocking observation) — see "Bug-narrative correction" below.

No instrument module (`src/physics/instrument_panel/*.py`), no frozen value
(`src/physics/layer2/frozen_constants.py`), and no report NUMBER or text content changed.
`tests/unit/physics/instrument_panel/test_panel_report.py` was NOT touched (no helper-name
coupling — the tests only call the public functions `run_panel`/`render_markdown`/
`instrument4_whole_lap_calibration`/`enumerate_2v2_partitions`/`instrument4_construction_check`,
none of which were renamed or had their signature changed).

## Scope
**Files changed:**
- `scripts/instrument_panel_668_report.py` (refactor only — helper extraction + `sort_keys=True`)
- `docs/physics/instrument_panel_668_gb2023q_report.json` (regenerated; content unchanged, key
  order stabilized — see Evidence)
- `docs/physics/instrument_panel_668_gb2023q_report.md` (regenerated; byte-identical to the
  pre-refactor file — see Evidence)

**Specific exclusions touched:** no. No instrument module edited (confirmed: `git status` shows
no modification under `src/physics/instrument_panel/`). No frozen value edited (`frozen_constants.py`
untouched by this gate; its pre-existing `M` status traces to the already-approved g3 gate, not to
this diff). No report NUMBER changed (proven by the parsed-JSON deep-equality check in Evidence).
No FastF1 online call (the script still only imports `src.data.database.DatabaseManager` and the
read-only sqlite adapters). `data/f1_data_2023.db` was WAL-touched by the read-only
`DatabaseManager` connections during the verification runs and restored via
`git checkout -- data/f1_data_2023.db`; `git status --porcelain data/` is clean at the end (see
Evidence). No `docs/architecture/*` touched. `tests/unit/physics/instrument_panel/test_panel_report.py`
not touched (not needed — see Completed slice above).

## Behavior changed
No. This is a pure extract-function + refactor-only change: every extracted helper executes the
exact same statements, in the exact same order, on the exact same inputs as the inline code it
replaced — no branch, computation, or ordering was altered. The one intentional observable change
is the committed `.json`'s key order (now alphabetically sorted via `sort_keys=True`), which the
handoff explicitly permits ("byte-identical ... or JSON key-order-only change") as the fix for the
reviewer-identified non-determinism. The rendered `.md` is proven byte-identical (see Evidence).

## Bug-narrative correction
The g7 reviewer flagged (as a non-blocking, out-of-scope observation) that the g7 review handoff's
phrasing — "the implementer fixed a real bug here" — was attached to the **no-leakback** area,
while the implementer's own `why_trail` (`m3-tests-panel-report`) attributes the actual fixed bug
to something unrelated. Recording the correct attribution here, in this result, so it is not lost
again in a future audit:

- **The real bug fixed during the original g7 run:** `instrument4_whole_lap_calibration` was
  iterating the hardcoded module-level `DRIVERS`/`CIRCUITS` tuples instead of the `(driver,
  gp_name)` pairs actually present in its own input rows — an iteration-completeness bug, found
  and fixed while writing `test_panel_report.py`, fixed by iterating `sorted(by_driver_gp)`
  instead. This changed only the row order of the whole-lap comparison table, not any value.
- **No-leakback was NOT the bug that got fixed.** The no-leakback property
  (`instrument4_whole_lap_calibration` calls `score_sector` — which consumes `official_time` —
  only AFTER `compose_sector_predictions` has already fixed the composed prediction) was
  structurally correct from the very first version of the script; it never needed a fix, and
  `test_whole_lap_composed_prediction_is_unaffected_by_official_time` is a genuine
  mutation-resistant confirmatory test of an always-true property, not a regression guard for a
  past leakback defect.

This rework's own change (the refactor) does not touch either of these — it is stated here purely
to close out the reviewer's narrative-correction request against the historical record.

## Map Impact
- **Structural anchors touched:** `scripts/instrument_panel_668_report.py` — internal-only
  restructuring (new private helpers `_channel_halves_for_partition`, `_partition_verdict_entry`,
  `_accumulate_partition_r`, `_sigma_honesty_checks_for_channel`, `_combine_class_verdict`,
  `_render_header`, `_render_instrument1`, `_render_instruments_2_3`, `_render_instrument4`); the
  file's public surface (`run_panel`, `render_markdown`, `instruments_2_3_replication`,
  `instrument4_whole_lap_calibration`, etc.) is unchanged in name and signature.
- **Capabilities added/changed/affected:** none — same capability (the g7 real-data report), same
  output, now passing the project's simplification-limits gate.
- **Constraints/assumptions touched:** none newly touched; `constraint:db-only` / DB-blob-guard
  re-confirmed honored during this rework's verification runs (see Evidence).
- **Decision candidates / resolved decisions:** none.
- **Claims/evidence produced:** `claim:simplification-limits-pass` (PASS output below);
  `claim:report-still-reproduces` (byte-diff + deep-equal evidence below, plus `--check-reproduce`).
- **Trust limitations / drift found:** none newly found.
- **Triage candidates:** none newly raised (this rework closes the g7 review's sole blocker).

## Test mode
**Required:** test-after / evidence-only (pure refactor gate; no new pure-algorithm behavior;
handoff explicitly frames this as "surgically refactor ... NO behavior change").
**Satisfied:** yes — the existing `test_panel_report.py` suite (57 tests total across the
`instrument_panel` package) passes unmodified against the refactored script, and the byte/deep-equal
diff evidence below independently proves output identity beyond what the tests alone assert.

## Evidence

```bash
cd C:/Programs/f1brainz-wt/epic659-668
"C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe" -m src.utils.simplification_limits --paths scripts/instrument_panel_668_report.py
```
**Result:** pass — `PASS (1 files checked)`. Both previously-flagged violations are gone:
`instruments_2_3_replication` cyclomatic complexity now well under 20; `render_markdown` now well
under both the 100-line and 20-complexity limits.

```bash
"C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe" scripts/instrument_panel_668_report.py
```
**Result:** pass — runs to completion, regenerates both report files.

**Reproduce-diff proof (LOAD-BEARING):**
- `.md`: `diff <pre-refactor .md backup> docs/physics/instrument_panel_668_gb2023q_report.md` →
  **empty diff, exit 0** — byte-identical.
- `.json`: raw byte-diff shows ONLY key-order differences (values never differ — confirmed line by
  line: every changed line pair is the identical `"key": value,` text relocated, never a changed
  value). Independently confirmed with a recursive Python deep-equality walk comparing the
  pre-refactor committed JSON against the freshly-regenerated JSON:
  `parsed dict equal: True`, zero `DIFF at <path>` lines emitted by a full recursive key/value
  walk (not just top-level `==`).

```bash
"C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe" scripts/instrument_panel_668_report.py --check-reproduce
```
**Result:** pass — `REPRODUCE CHECK: PASS -- two runs produced identical output`.

```bash
"C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe" -m pytest tests/unit/physics/instrument_panel/ -q
```
**Result:** pass — `57 passed` (includes the 8 `test_panel_report.py` tests, unmodified, run
against the refactored script; and the 49 tests of the four already-built instrument modules,
confirming no regression).

```bash
"C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe" -m pyright scripts/instrument_panel_668_report.py tests/unit/physics/instrument_panel/test_panel_report.py
```
**Result:** pass — `0 errors, 0 warnings, 0 informations`.

```bash
git status --porcelain data/          # before restore: " M data/f1_data_2023.db"
git checkout -- data/f1_data_2023.db  # DB-BLOB-GUARD remedy
git status --porcelain data/          # after restore
```
**Result:** pass — empty output after restore (clean; the DB was WAL-touched by the read-only
`DatabaseManager` connections opened during this rework's verification runs, never
staged/committed).

## Docs/contracts touched
- `docs/physics/instrument_panel_668_gb2023q_report.md` — regenerated, byte-identical to the
  pre-refactor version (evidence above).
- `docs/physics/instrument_panel_668_gb2023q_report.json` — regenerated; content unchanged, key
  order now alphabetically stable via `sort_keys=True` (evidence above).

## Assumptions
- **`sort_keys=True` is the intended fix for the reviewer's JSON-non-determinism observation.**
  The handoff names this exact remedy ("sort keys on emit so re-runs are byte-stable"); applied it
  at both `json.dumps` call sites in `main()` (stdout print and file write) for consistency, rather
  than only the file write, since the handoff's own Evidence commands print JSON to stdout too.
- **No test file change needed.** `test_panel_report.py` only calls this script's public,
  unrenamed functions, so the "only if a test needs a trivial update for extracted helper names"
  allowance in the handoff's Allowed Scope did not need to be exercised.

## Stop conditions hit
None. The limits gate passes cleanly after the refactor; output stayed identical (modulo the
explicitly-permitted JSON key-order stabilization); no instrument-module or frozen-value change
was needed.

## Out-of-scope observations
None beyond the bug-narrative correction recorded above (which the handoff explicitly asked this
gate to fix, not a new finding).

## Workflow Feedback
- **Handoff gaps:** none of substance. The handoff's Verification Commands block gives
  `py -m src.utils.simplification_limits scripts/instrument_panel_668_report.py` as a bare
  positional argument, but the tool's actual CLI (`src/utils/simplification_limits.py`) defines no
  positional argument — only `--paths` (plus `--baseline`/`--json`/`--file-lines-only`). Running the
  handoff's literal command form fails with `unrecognized arguments`. I ran the equivalent working
  form (`--paths scripts/instrument_panel_668_report.py`), which is also what the g7 reviewer used
  and what `CREW_CONTEXT.md`'s own example (`py -m src.utils.simplification_limits --paths
  <touched>`) documents. A future handoff copying this verification command should include the
  `--paths` flag.
- **Context rediscovered:** the "which bug" narrative correction required reading both the prior
  `g7-realrun-implement-result.md` (which already correctly attributes the fix to the hardcoded
  `DRIVERS`/`CIRCUITS` iteration bug in its own "Test mode / Satisfied" section) and the
  `g7-realrun-review-result.md`'s Out-of-scope observation (which pins the mismatch specifically to
  the *review handoff's* wording, not the implement-result). The rework handoff's "a doc/narrative
  nit in the result file" phrasing pointed at "the result file" without specifying which of the two
  result files (implement vs. review) or the review handoff carried the actual nit; I resolved this
  by recording the correct, disambiguated narrative directly in this (implement) result file, since
  that is the artifact this gate owns and rewrites.
- **Instructions improvised around:** none — the refactor was a mechanical extract-function split;
  no design decision was needed since the target complexity/length reduction was achievable with a
  straightforward decomposition along the code's own existing comment-delimited sections
  (per-partition build / sigma-honesty / per-class combine for instruments_2_3_replication;
  per-instrument-section for render_markdown).
- **What would have made this easier:** fixing the `simplification_limits` verification command's
  missing `--paths` flag in the handoff template used for this project's gates going forward, so
  future implementers don't have to independently discover the CLI's actual argument shape.

## Return status
`complete`
