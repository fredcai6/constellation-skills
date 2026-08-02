# Review Result

Status values follow `skills/workbench/references/status-model.md`.

## Assigned Gate
g2 — store SCHEMA: `cross_view_covariance` JSON blob + per-axis `{axis}_status` columns + reserved wide-σ sentinel (schema/defaults/migration/round-trip ONLY; #627 unified-basis)

## Result
`APPROVE`

## Handoff compliance
Fully satisfied within allowed scope. `EstimateRecord` gained `cross_view_covariance: Optional[dict] = None` (added to `_JSON_COLUMNS` so it (de)serializes generically through `upsert`/`load`) and 9 `{axis}_status: Optional[str] = "unresolved"` fields for `AXIS_STATUS_NAMES = (cda, p_max, a_b, b_b, a_t, b_t, A0, A2, theta_R)`. `UNRESOLVED_AXIS_SIGMA_FRAC = 1.0` is documented in-module and follows the cited `power_drag_view._CDA_UNKNOWN_SIGMA`/`_PMAX_UNKNOWN_FRAC` pattern (grep-confirmed those constants exist at `power_drag_view.py:36-37`). `error_record(...)` explicitly sets sane defaults for every new field. `_migrate_missing_columns` needed **zero code changes** — it already iterates `EstimateRecord.__dataclass_fields__` generically, so the new columns ALTER-add automatically. No value population, no status resolution anywhere in the diff — verified by reading the full diff and the full file.

## Scope drift
None. `git status --porcelain` shows exactly the two allowed files (`src/physics/layer2/estimate_store.py`, `tests/unit/physics/layer2/test_estimate_store.py`) plus the untracked `.agent-work/627-unified-basis/` workflow directory. No pooling/view/weekend_state edits, no production-default/circuits.yaml/gold change, all new tests use `tmp_path` (no `data/*.db` writes), no evo import (`constraint:physics_region_no_evo_import` respected — import list unchanged: stdlib + numpy/pandas only). Additive-migration-only and sparse-dict-not-dense-matrix constraints both confirmed in the diff.

## Evidence verdict
Required evidence reproduced independently, not just re-read from the report:
- `py -m pytest tests/unit/physics/layer2/test_estimate_store.py tests/unit/physics/weekend_state/ -q` → **122 passed**, exact match to the implementer's claim.
- Independently reproduced the protected BACKWARD-READ intent with a **standalone script** (not the implementer's test): built a minimal legacy `session_estimates` table missing all g2 columns, opened it via `EstimateStore` (triggers `_migrate_missing_columns` on `__init__`), confirmed via `PRAGMA table_info` that `cross_view_covariance` + all 9 `{axis}_status` columns exist post-migration, confirmed `load()` succeeds with **no "no such column" error**, and confirmed the legacy row's new columns read back as Python `None` (NULL backfill from SQLite's bare `ALTER TABLE ADD COLUMN`, not the Python dataclass default `"unresolved"`) — the honest finding the handoff asked to verify, reproduced exactly and correctly framed as benign legacy state (a G4 concern, not a G2 blocker).
- Ran the project's `simplification_limits` check on the touched files at strict `--paths` scope: found 1 pre-existing cyclomatic-complexity violation (`test_fit_quality_metadata_populated_and_round_trips`, complexity 26 > 20), confirmed via `git stash`/re-run A-B test that it **predates this diff** and lives in a function g2 never touched. Not a g2 blocker; routed as triage candidate tc2.

## Code/doc quality
Full Fowler baseline pass run (`r6-fowler`, 12/12 smells visited, `scripts/verify_fowler_pass.py` exit 0): 7 absent, 5 overridden with a logged repo-standard + reason each (large-class and data-clumps against the file's own flat-schema/flat-column conventions; duplicated-code against `error_record`'s pre-existing fully-explicit-kwargs style; primitive-obsession against the file's existing plain-`str`+comment convention for `fit_status`/`support_trust`; speculative-generality against the g2 handoff's own explicit staged-schema-only mandate). 0 flagged — no code-smell defect found. Documentation is dense and matches the file's existing convention for non-obvious cross-gate contracts (e.g. `SYSTEMATIC_FLOOR`, `_RHO_INFLATION`).

## Map impact verdict
- **Evidence supports claimed change:** yes — independently reproduced above.
- **Constraints not violated:** yes — backward-readable store honored and independently reproduced; additive-only migration confirmed by reading the full `_migrate_missing_columns` body.
- **Notes match the diff:** yes — the implementer's structural-anchor notes (`EstimateRecord`, `_JSON_COLUMNS`, `_migrate_missing_columns`, `error_record`) match the actual diff. "Capabilities: none yet observable" is accurate — independently grep-confirmed that `weekend_state/frame.py`, `layer1_physics.py`, `gate_f6.py`, `gate_spec.py` reference only the pre-existing `{axis}_sigma` pattern by name, never `cross_view_covariance` or `{axis}_status`; `frame.py` additionally reads a **different** physical DB via an explicit `SELECT_COLUMNS` allowlist, so it cannot pick up the new columns even implicitly.
- **Decision candidates surfaced:** yes — the `cross_view_covariance` dict shape and the `AXIS_STATUS_NAMES` short-name-to-field mapping are explicitly flagged as the frozen contract G3/G4 build against, not silently decided past the implementer's authority.
- **Durable context routed:** yes — the implementer flagged `scripts/migrate_estimate_store_metadata.py` (a separate standalone migration script with a hardcoded column list) as not including the new g2 columns; independently confirmed by reading the script. Captured mechanically as triage candidate **tc1** in the survey's bubble-up channel (was previously only prose in `IMPLEMENTER_RESULT.md`).

## Reconciliation check
No divergence from recorded architecture requiring Commander reconciliation beyond the two routed triage candidates (tc1, tc2), both non-blocking and out of g2's allowed scope.

## Blockers
- none

## Out-of-scope observations
- **tc1**: `scripts/migrate_estimate_store_metadata.py` is a separate standalone migration path (hardcoded `_NEW_COLUMNS` list, targets `data/physics_estimates.db` directly) that does not yet include the g2 columns. Recommend a follow-on issue to keep it in sync with `EstimateRecord`, or retire it in favor of always constructing an `EstimateStore`.
- **tc2**: `tests/unit/physics/layer2/test_estimate_store.py::test_fit_quality_metadata_populated_and_round_trips` has cyclomatic complexity 26 (limit 20) under the strict `--paths` simplification-limits check. Confirmed pre-existing (identical failure with the g2 diff stashed out) and untouched by g2. The repo's canonical check-in command (`--baseline`) currently only enforces `file_lines` per `config/simplification_baseline.json`, so this violation is invisible to that gate regardless of this diff. Recommend either adding it to the baseline allowlist with a tracked exit condition, or a follow-on simplification issue.

## Workflow Feedback

- **Handoff gaps:** none blocking. One minor ambiguity worth naming: CREW_CONTEXT.md's simplification-limits rule says "Review blocker when skipped or failing on in-scope Python," which read literally could block on ANY pre-existing violation in a touched file, not just violations the diff introduces. I resolved this by A/B-testing with `git stash` (confirming the one violation found predates this diff and lives in an untouched function) and treating it as non-blocking triage rather than a G2 BLOCK — but the rule's wording doesn't itself distinguish "introduced by this diff" from "pre-existing in a touched file." Worth tightening the CREW_CONTEXT wording (e.g. "failing on lines this diff touches") so future reviewers don't have to make that call themselves.
- **Context rediscovered:** none beyond normal reading — the handoff's Map Anchors, evidence command, and stop conditions were all exactly where named.
- **Instructions improvised around:** the `append`/`record` verb sequence (r4a-simplification appended mid-survey) landed at the END of the items list rather than inline after r4-quality — cosmetic only, the engine still visited it before consolidate allowed. Also: a `git stash`/`` `command` `` backtick inside a `record --finding` string got shell-interpreted mid-command (bash backtick expansion), which silently re-stashed the g2 diff for a few seconds before I caught it via `git status`/`git stash list` and restored it with `git stash pop` (confirmed diff `--stat` unchanged, reran the full test suite green afterward — no lasting effect, but worth naming as a live hazard: avoid backticks/literal `git stash` text inside `--finding`/`--reason` string arguments passed through a POSIX shell).
- **What would have made this easier:** none structurally — the handoff was unusually precise (down to naming the exact sentinel pattern to match). The one process improvement is the CREW_CONTEXT wording note above.

## Return status
`complete`
