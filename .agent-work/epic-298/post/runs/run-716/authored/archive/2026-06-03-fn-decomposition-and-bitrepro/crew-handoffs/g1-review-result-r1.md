# REVIEW_RESULT — g1 (decompose evo over-limit functions) — round 1

Verdict: **BLOCK** (single precise fix)

## Blocker
- `src/evo_predictor/run.py` cmd_train_latent_power_module: validation ORDER inverted during extraction.
  - Original: compound-prior requirement check + `_compound_prior_artifacts(...)` load ran BEFORE the
    `--retro-root is required` check.
  - New: the retro_root check was hoisted ABOVE `_resolve_compound_normalizers(...)`.
  - Observable divergence: a compound-needing module invoked with BOTH --retro-root and --compound-prior-root
    missing now surfaces the retro-root error first (was: compound-prior error first); also changes a
    filesystem-I/O short-circuit. Invisible to tests (cmd_train body is mocked) — diff is the guarantee.
  - FIX: restore original ordering — move the retro_root read + `--retro-root` check back to AFTER
    `_resolve_compound_normalizers(...)` and the data-prep calls (its original position).

## Verified PASS (no other divergence)
- _build_parser: all 6 subparsers, every arg/choices/default/required/action/nargs/help byte-identical.
- _parse_and_validate: every validation branch + message byte-identical; same GoldCycleConfig.
- _gold_preflight_coverage: same 19-key per-year dict + order + SQL + lap-schema logic.
- cmd_train other helpers (_resolve_compound_normalizers body, _build_latent_power_config, _join_retro_batches,
  _build_training_diagnostics) byte-identical.
- 127 tests pass; --paths PASS (3 files); helpers module-level/private; no new mutable module-level state.

## Out-of-scope (handled by Commander)
- Stray uncommitted edit to the #356 archived spine.json -> committed separately as housekeeping.
