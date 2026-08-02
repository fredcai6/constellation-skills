# Reviewer Handoff

## Gate
`g2`

## What Was Implemented
New src/evo_predictor/module_record.py (write_module_record, load_module_record,
strip_record_from_rows, should_reuse_backtest; ordinal npz keys ev0000__*, stdlib-readable
.record.json index, savez_compressed, temp+rename writes). run.py backtest command wired:
--emit-module-record parser flag, emit-without-output error, reuse guard via
should_reuse_backtest, collect_record=emit, record strip before payload, sidecar spill next
to args.output. New tests/unit/evo_predictor/test_module_record.py (22 tests).

PROVENANCE WARNING: module_record.py and the test file were written by a first implementer
whose session died mid-gate; a second implementer "audited" them and completed the run.py
wiring. That audit is NOT independent — treat the inherited module and tests as unreviewed
code. Read every line of module_record.py against the contract.

## How to Inspect the Diff
Repo root: C:\Programs\f1Brainz\.claude\worktrees\issue-371-module-record
- `git diff src/evo_predictor/run.py` (vs HEAD 5c832fe)
- Untracked new files: src/evo_predictor/module_record.py, tests/unit/evo_predictor/test_module_record.py — read in full.

## Task Statement
Original implementer handoff (read it): .agent-work/issue-371-module-record/crew-handoffs/G2_IMPLEMENTER_HANDOFF.md
Frozen intent: .agent-work/issue-371-module-record/PROBLEM_STATEMENT.md

## Close Criteria (each is a review check)
- Round-trip: ≥2 events, ragged n_entities, one target_mu=None, one actual_positions=None ⇒ exact array equality incl. (n,n) sigma_pi and dtype fidelity (incl. outcome's actual dtype, often float32 — must NOT be coerced to float64).
- Index: stdlib-json readable (no numpy types leak into json.dump), format_version 1, module identity fields, feature_names/feature_schema_version, source_backtest basename, events[] each with key/event_id/n_entities/n_pairs/entity_ids/has_target_mu/has_actual_positions; every emitted event listed.
- npz: ordinal-prefixed member keys; loads with allow_pickle=False (verify entity_ids handling doesn't require pickle).
- Validation: inconsistent feature_names/feature_schema_version across rows ⇒ error naming the event; empty rows ⇒ valid empty-index sidecar pair.
- Atomicity: both sidecars written to temp names then renamed; no path where a partial file keeps the final name.
- Payload purity: strip_record_from_rows output deep-equals rows minus "record"; written backtest JSON identical with/without emit.
- run.py wiring: flag defaults False; emit on + no --output ⇒ clear error naming the dependency; module identity sourced from get_training_adapter(module_name) (.task/.entity_scope/.evidence_source); reuse guard — (reuse on, emit off, output exists) reuse; (reuse on, emit on, sidecars missing) recompute with explanatory [reuse] line; (reuse on, emit on, all three present) reuse.
- JUDGMENT CALL for you: the writer path silently excludes per_event rows lacking a "record" key (implementer assumption: G1 guarantees all rows carry it when collect_record=True). Weigh whether silent exclusion could mask a G1 regression (record emitted for a strict subset of scored events with no error). If you judge it unsafe, BLOCK with a concrete fix proposal (e.g., raise on missing record when emit on); if acceptable, record the rationale.
- Flag off (default): zero behavior change anywhere in the backtest command path.
- Scope: ONLY module_record.py (new), run.py (backtest command + parser only), test_module_record.py (new). Exclusions untouched: evaluate_labeled_batches internals, gold_cycle config/builders/TOMLs, docs, details.json/report schema/fusion.
- Focused evo suite green: `py -m pytest tests/unit/evo_predictor/ -q` (expect ~1240 passed).
- `py -m src.utils.simplification_limits --paths src/evo_predictor/module_record.py src/evo_predictor/run.py tests/unit/evo_predictor/test_module_record.py` ⇒ PASS, and no dir-wide violation names a G2 symbol.

## Constraints the Implementation Must Respect
- `py` not `python`; no module-level state; one canonical record format (no alternate modes); index readable with stdlib json alone.

## Evidence Produced (verify, don't trust)
- 22/22 test_module_record.py; full suite 1240 passed; simplification PASS on the three touched files. Re-run all three commands yourself.

## Suggested Model Tier
stronger scrutiny than G1 — inherited unreviewed code plus an IO contract with atomicity and dtype edge cases.

## Stop Conditions
Stop and return BLOCK if: the diff cannot be accessed, evidence is absent or unverifiable, or a policy decision is required before a verdict is possible.

## Return Format
Return REVIEW_RESULT: verdict (APPROVE or BLOCK), per-check findings, blockers, out-of-scope observations.

## Working agreement
Work from repo root C:\Programs\f1Brainz\.claude\worktrees\issue-371-module-record. Read-only on src/; you may run tests/commands (you may write throwaway scripts under a temp dir to probe round-trip behavior). Do not modify code; do not commit.
