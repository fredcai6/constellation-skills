# Implementer Handoff

## Gate
`g2`

## Task
Sidecar record IO + backtest CLI wiring.

1. **New module `src/evo_predictor/module_record.py`** — the one canonical record format:
   - `write_module_record(output_json_path, *, module_name, task, entity_scope, evidence_source, rows) -> (npz_path, index_path)`
     writes `{stem}.record.npz` + `{stem}.record.json` next to the backtest JSON
     (`backtests/foo.json` → `backtests/foo.record.npz` / `foo.record.json`).
   - npz member keys use **ordinal prefixes** (`ev0000__pi`, `ev0000__sigma_pi`,
     `ev0000__outcome`, `ev0000__pair_index`, `ev0000__features`, `ev0000__dqi`,
     `ev0000__entity_ids`, plus `ev0000__target_mu` / `ev0000__actual_positions` only when
     present). Rationale: real `event_id`s may contain `:` (see the `[_:]` regex at
     module_training_orchestration.py:485) which is hostile inside zip member names on
     Windows tooling — the index maps ordinal ↔ event_id. This deviates deliberately from
     the issue's literal `pi__{event_id}` suggestion; the Commander has approved it.
   - `{stem}.record.json` index is **stdlib-readable** (no numpy): `format_version: 1`,
     module identity (module_name/task/entity_scope/evidence_source), `feature_names`,
     `feature_schema_version`, `source_backtest` (basename), and `events: [...]` — one entry
     per emitted event with `key` (ordinal), `event_id`, `n_entities`, `n_pairs`,
     `entity_ids` (list of str), `has_target_mu`, `has_actual_positions`. Every emitted
     event appears in the index; floats stay binary in the npz.
   - `load_module_record(index_path_or_stem) -> ModuleRecord` (or plain dict structure)
     rehydrating per-event dicts; loading then comparing must reproduce the written arrays
     exactly (`np.array_equal`, including dtype fidelity for float64/int64).
   - Validate on write: rows with inconsistent `feature_names`/`feature_schema_version`
     ⇒ error naming the event; empty rows ⇒ still write a valid empty-index pair.
2. **Wire `cmd_backtest_latent_power_module` (run.py:392)**:
   - Parser (`_add_backtest_latent_power_module_parser`, run.py:651): add
     `--emit-module-record` (`action="store_true"`, default False).
   - In the command: `emit = bool(getattr(args, "emit_module_record", False))`; call
     `evaluate_labeled_batches(..., collect_record=emit)` (G1 param); when emitting, pop
     the `"record"` entry off every per_event row BEFORE building the payload (payload and
     written JSON stay exactly as today), and call `write_module_record` next to
     `args.output`. Records only written when `args.output` is set; if emit is on with no
     `--output`, raise a clear error (records need an anchor path).
   - Module identity for the writer comes from the adapter
     (`get_training_adapter(module_name)`: `.task`, `.entity_scope`, `.evidence_source`).
   - **Reuse guard** (run.py:394-398, env `GOLD_CYCLE_REUSE_EXISTING=1`): when emit is on,
     reuse requires output JSON **and both sidecars** to exist; otherwise fall through and
     recompute (print a `[reuse]`-style line explaining why). Factor the reuse decision
     into a small pure helper so it is unit-testable without a bundle.

## Protected Intent
- Backtest JSON payload and file bytes unchanged in all modes (flag off: trivially; flag
  on: record entries stripped before serialization).
- Flag off (default) ⇒ no `.record.*` files, no behavior change anywhere.
- One canonical record format; no alternates, no compatibility shims.

## Test Mode
Test-led (TDD). Unit tests with synthetic record rows (numpy arrays in the G1 row shape);
no DB or trained bundle needed.

## Close Criteria
- Round-trip: write with ≥2 events (ragged n_entities, one event with `target_mu=None`,
  one with `actual_positions=None`) then load ⇒ exact array equality incl. `sigma_pi`
  matrices and dtypes; index lists every event with correct flags/counts.
- Payload purity: given per_event rows with `"record"` entries, the emitted-payload rows
  deep-equal the same rows without records (test the strip helper directly).
- Reuse-guard helper: (reuse on, emit off, output exists) ⇒ reuse; (reuse on, emit on,
  sidecars missing) ⇒ recompute; (reuse on, emit on, all three present) ⇒ reuse.
- Emit on without `--output` ⇒ error naming the flag dependency.
- Focused evo suite green: `py -m pytest tests/unit/evo_predictor/ -q`.
- `py -m src.utils.simplification_limits --paths src/evo_predictor/module_record.py src/evo_predictor/run.py` passes (strict).

## Allowed Scope
- `src/evo_predictor/module_record.py` (new)
- `src/evo_predictor/run.py` (backtest command + its parser only)
- `tests/unit/evo_predictor/test_module_record.py` (new) and a small run.py-level test file
  if needed

## Specific Exclusions
- `evaluate_labeled_batches` internals (G1 — consume its contract as-is)
- Gold-cycle config / template builders / TOMLs (G3)
- Any docs (G3 documents the contract)
- `details.json`, report schema, fusion code

## Constraints
- `py` not `python`
- Index JSON must be readable with stdlib `json` alone; npz via `np.load(..., allow_pickle=False)`
- No module-level state; match surrounding style
- Sidecar write is atomic-ish: write to temp names then rename, so a crashed run never
  leaves a valid-looking truncated npz (match repo conventions if a helper exists)

## Required Evidence
- Test output for the new files + focused suite
- simplification_limits output
- Assumptions noted in IMPLEMENTER_RESULT

## Verification Commands
```bash
py -m pytest tests/unit/evo_predictor/test_module_record.py -q
py -m pytest tests/unit/evo_predictor/ -q
py -m src.utils.simplification_limits --paths src/evo_predictor/module_record.py src/evo_predictor/run.py tests/unit/evo_predictor
```

## Suggested Model Tier
simple bounded — IO contract fully specified; edge cases enumerated.

## Authority
Decided (Commander + user): sidecar naming, ordinal npz keys + index mapping, index
content set, reuse-guard semantics, no-output error. You must NOT decide alone: format
extensions, compression choices beyond default `np.savez_compressed` vs `np.savez`
(pick `np.savez_compressed`; floats are exact either way), touching excluded files.

## Stop Conditions
Stop and return if: allowed scope must be exceeded, the G1 row contract is missing a field
this gate needs, required evidence cannot be produced, or a decision outside the given
authority is needed.

## Return Format
Return IMPLEMENTER_RESULT: completed slice, files changed, test mode satisfied, evidence
produced, assumptions used, stop conditions hit, out-of-scope observations.

## Working agreement
Work from repo root `C:\Programs\f1Brainz\.claude\worktrees\issue-371-module-record`.
Do not `cd` elsewhere; do not touch `.agent-work/` except to read this handoff and
PROBLEM_STATEMENT.md. Commit nothing — the Commander owns commits.
