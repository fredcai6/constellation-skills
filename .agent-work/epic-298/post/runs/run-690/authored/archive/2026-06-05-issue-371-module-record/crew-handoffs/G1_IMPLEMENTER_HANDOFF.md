# Implementer Handoff

## Gate
`g1`

## Task
Add an opt-in, default-off record-collection parameter to `evaluate_labeled_batches`
(`src/evo_predictor/module_training_orchestration.py:509`). When enabled, each `per_event`
row gains a `"record"` entry — an in-memory dict of numpy arrays + metadata captured from
objects already in scope in the loop:

- `pi` (n,) — `pred.latent_power` (detach→cpu→numpy, float64)
- `sigma_pi` (n,n) — `pred.sigma_pi` (same treatment; the full matrix line 543 currently
  discards). If a prediction object lacks `sigma_pi`, treat as a hard error when collecting
  (records without covariance are useless to the consumer) — name the module/event in the message.
- `target_mu` (n,) or None — `batch.target_mu` (None-safe; row records label availability)
- `outcome` (pairs,) — `batch.outcome`
- `actual_positions` (n,) or None — from `_actual_positions_from_diag(item)` aligned to
  `batch.entity_ids` order (positions for entities missing from the diag map: NaN)
- `pair_index` (pairs,2) int64 — `batch.pair_index`
- `features` (pairs,d) — `batch.features`
- `dqi` (pairs,) — `batch.dqi`
- `entity_ids` (n,) — `tuple(batch.entity_ids)` (strings; keep as list/tuple, not ndarray)
- `feature_names` — `item.feature_names`; `feature_schema_version` — `item.feature_schema_version`
- `event_id` — `batch.event_id` (year/round are parseable downstream via the existing
  `re.match(r"(\d{4})[_:](\d+)", ...)` convention at module_training_orchestration.py:485;
  do NOT duplicate parsing here — store raw event_id, plus gp/round metadata only if it is
  already present in `item.diagnostics`)

Events skipped by the existing numerical-error guard (lines 535-539) produce no record —
unchanged behavior, the skip already logs.

## Protected Intent
- Default-off call returns rows **byte-identical** to today: same keys, same values, no
  `"record"` key anywhere, aggregate metrics unchanged.
- The function stays **pure**: no filesystem knowledge, no paths, no writes. It returns rows.
- No change to `details.json`, schema, or any writer in this gate.

## Test Mode
Test-led (TDD): write the failing tests first against the new parameter, then implement.
Existing pattern to follow: `tests/unit/evo_predictor/test_evaluate_labeled_batches.py`
(`_FakeModule` / `_FakePrediction` / `_labeled_batch_result` synthetic-batch helpers).
Note `_FakePrediction` lacks `sigma_pi` — your fakes for collect-on tests must provide an
(n,n) tensor there; also extend with a fake whose prediction lacks `sigma_pi` to prove the
hard-error path.

## Close Criteria
- Default (no new argument / explicit off): output deep-equals the pre-change output for
  the same synthetic inputs (assert no `"record"` key in any row).
- Collect-on: every non-skipped event row carries a `"record"` dict whose arrays are exactly
  equal (`np.array_equal` / `torch.equal` pre-conversion) to the values the fakes produced,
  including the full `sigma_pi` matrix.
- `target_mu=None` event still yields a record with `target_mu is None` and everything else
  populated.
- Missing `sigma_pi` on the prediction object with collect on ⇒ raises with module/event
  named; collect off ⇒ unaffected.
- `actual_positions` absent from diagnostics ⇒ record carries None (event remains usable
  for outputs/inputs).
- Numerical-error skip path: skipped events produce neither metrics row nor record (extend
  a fake to raise `torch.linalg.LinAlgError` on one event).
- Focused evo suite green: `py -m pytest tests/unit/evo_predictor/ -q`.
- `py -m src.utils.simplification_limits --paths src/evo_predictor/module_training_orchestration.py` passes (strict).

## Allowed Scope
- `src/evo_predictor/module_training_orchestration.py` (the `evaluate_labeled_batches`
  function and module-local helpers you add beside it)
- `tests/unit/evo_predictor/test_evaluate_labeled_batches.py` and/or a new
  `tests/unit/evo_predictor/test_evaluate_labeled_batches_record.py`

## Specific Exclusions
- `cmd_module_backtest` / `run.py` (G2)
- Any npz/json writing (G2)
- Gold-cycle config or template builders (G3)
- `fusion.py`, report schema, docs

## Constraints
- `py` not `python` for all commands
- Parameter naming: `collect_record: bool = False` (keyword-only preferred to match the
  function's style if applicable)
- Keep tensor→numpy conversion inside the collect branch only — zero overhead when off
- Match surrounding code style/comment density; no module-level state

## Required Evidence
- Test run output (the new tests + the focused file) pasted in IMPLEMENTER_RESULT
- simplification_limits output for the touched paths
- Brief note of any assumptions

## Verification Commands
```bash
py -m pytest tests/unit/evo_predictor/test_evaluate_labeled_batches.py tests/unit/evo_predictor/test_evaluate_labeled_batches_record.py -q
py -m pytest tests/unit/evo_predictor/ -q
py -m src.utils.simplification_limits --paths src/evo_predictor/module_training_orchestration.py tests/unit/evo_predictor
```
(Adjust the second test path if you extend the existing file instead of adding a new one.)

## Suggested Model Tier
simple bounded — the seam is one function, contract fully specified, strong existing test pattern.

## Authority
Decided (Commander + user): param shape (opt-in bool, default off), record field set,
purity requirement, hard-error on missing sigma_pi when collecting, store-raw-event_id.
You must NOT decide alone: adding fields beyond the contract, changing existing row/metric
shapes, touching files outside Allowed Scope.

## Stop Conditions
Stop and return if: allowed scope must be exceeded, a specific exclusion must be touched,
required evidence cannot be produced, `pred.sigma_pi` turns out not to exist on the real
`LatentPowerPrediction` (verify at `src/evo_predictor/module_runtime.py:~106` first), or a
decision outside the given authority is needed.

## Return Format
Return IMPLEMENTER_RESULT: completed slice, files changed, test mode satisfied, evidence
produced, assumptions used, stop conditions hit, out-of-scope observations.

## Working agreement
Work from repo root `C:\Programs\f1Brainz\.claude\worktrees\issue-371-module-record` (this
worktree IS the repo). Do not `cd` elsewhere; do not touch `.agent-work/` except to read
this handoff and PROBLEM_STATEMENT.md. Commit nothing — the Commander owns commits.
