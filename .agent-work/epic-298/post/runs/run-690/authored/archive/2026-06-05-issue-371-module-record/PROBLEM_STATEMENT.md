# Problem Statement — issue 371: per-event module record emit

## Confirmed ask

Add a gated emit of per-event module records (outputs + labels + inputs) at the module
backtest seam so fusion experiments A (correlated-covariance), B-cheap (partial pooling),
B-expensive (driver = constructor + residual re-target), and C-gate (interaction headroom)
become offline replays over cached data — no retraining of the 12 modules. The offline
harness itself is OUT of scope (an issue for it already exists; do not file another).

## Protected intent (must not change)

- Flag off (default): zero change to current artifacts — byte-identical backtest JSON and
  details.json, no `.record.*` files, no schema churn, no config-file churn required.
- `evaluate_labeled_batches` stays pure (returns rows; no path knowledge).
- DB-only analysis doctrine untouched (records derive from the existing eval pass).
- `details.json` untouched; gold report schema (`gold_report_schema.py`) untouched.

## Resolved design decisions

1. **Flag home/shape** — `emit_module_record: bool = False` on `GoldCycleRuntimeConfig`
   (`[runtime]`), parsed via `runtime_raw.get("emit_module_record", False)` with type
   validation (the `utilization` optional-key precedent). NOT echoed into
   `build_run_config`/details.json (preserves byte-identity + zero report-schema churn);
   provenance lives in the `.record.json` sidecar. Add `"emit_module_record": "runtime"`
   to the CLI override-section mapping; add explicit `false` to `gold_defaults.toml` for
   discoverability. (Issue text said `GoldCycleDataConfig`; actual pattern home is the
   runtime section — confirmed deviation.)
2. **Coverage (USER)** — uniform contract: flag on ⇒ EVERY `cmd_module_backtest`
   invocation emits records next to its output JSON (mains + LOSO folds + uncertainty-
   calibration backtests). Thread the flag through all three template builders + a
   `--emit-module-record` CLI flag on the module-backtest subcommand.
3. **Seam** — `evaluate_labeled_batches` gains an opt-in collect parameter enriching
   per-event rows in-memory with arrays; `cmd_module_backtest` strips the heavy arrays
   from the JSON payload and spills `{output_stem}.record.npz` + `{output_stem}.record.json`
   next to `args.output`. Evidence-mode eval call sites are untouched (default-off param).
4. **Reuse guard** — the `[reuse]` early-return in `cmd_module_backtest` must require the
   record sidecars to exist when the flag is on; otherwise re-run (no silent absence).
5. **Record content (per module, per event)** — keys: `event_id`, `module_name`, `task`,
   `entity_scope`, `evidence_source`, year/round/gp; outputs: `pi` (n,), `sigma_pi` (n,n);
   labels: `target_mu` (n,) when present, pair `outcome` (pairs,), `actual_positions` (n,);
   inputs: `pair_index` (pairs,2), `features` (pairs,d), `dqi` (pairs,), `entity_ids` (n,).
   npz keyed per event (`pi__{event_id}`, ...) for ragged n; `.record.json` is the
   stdlib-readable index carrying string metadata + usable/missing-label flags.
6. **Verification (USER)** — three tiers: unit tests on synthetic batches (default rows
   unchanged; exact round-trip via `np.array_equal`); one bounded real-data integration
   test (determinism-test mold: cheap modules, 2 years, max_rounds 1, few epochs; backtest
   twice off/on same bundle ⇒ byte-identical JSON, records only flag-on); PLUS one flag-on
   smoke-mode gold cycle run end-to-end with an evidence artifact listing the records
   produced across mains + LOSO + calibration dirs.
7. **Docs** — document the record contract in `docs/evo/` in the same gate (new page or
   section linked from the gold-cycle doc); records are non-committed generated artifacts
   (stay out of git). Forward-compatible note referencing #370's schema slice.

## Constraints from project doctrine

- `py` for all Python invocations; region tests for evo before/after;
  `py -m src.utils.simplification_limits` on touched paths (strict).
- One canonical path: a single record format, no alternate emit modes.
- Local-agent run (numpy/torch env required) — confirmed, we are local.
