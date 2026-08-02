Implements the leakage-free walk-forward 2025 backtest from #439: re-train the model at 4 checkpoints through the season, each predicting the next quarter from only prior data, and aggregate a total-season fantasy score.

## What's here (6 commits)
- **Season fantasy aggregator** (`src/fantasy_scoring/season.py`) + baseline: the promoted-gold model scored over all 24 2025 races = **707.0** (no-in-season-retrain reference; lower is better).
- **Leakage-safe in-season as-of cutoff primitives** — `prepare_module_training_data(eval_year_train_through_round, eval_round_range)`; eval-year rounds ≤N join training, eval = an explicit later range. Verified strictly backward-looking (no future round reaches training).
- **Walk-forward orchestrator** (`src/evo_predictor/walkforward/`) + gold-cycle runner cutoff wiring + an **enforced per-race leakage attestation** (aborts if any race's training touched round ≥ that race). Run/verify scripts: `scripts/run_walkforward_backtest.py`, `scripts/verify_walkforward_run.py`.
- **3 run-enabling fixes** surfaced by actually running it end-to-end: explicit period manifests (downstream was scoring the promoted gold, not each period's model); cross-season prior fallback; and period compound priors are **cross-season throughout** (matches promoted gold; leakage-safe — zero 2025 compound data). The dropped per-period *same-season* compound rebuild is noted on #382.

## Safety / scope
- Additive and opt-in: the cutoff is unset by default, so **gold defaults are byte-for-byte unchanged**. Production gold path untouched.
- Leakage is the dominant failure mode and is gated at three layers: as-of cutoff in training-data assembly, strictly-backward-looking form/labels, and the enforced per-race attestation.
- Tests: season aggregation, as-of cutoff invariants, orchestrator wiring (heavy calls mocked), downstream argv, prior build — all green; `simplification_limits` clean on touched paths.

## Status
The full-fidelity 3-period run is executing now; the committed walk-forward report + final season score (vs the 707.0 baseline) land in a follow-up once it completes. Merging the implementation now per request.

Closes #439 (implementation; result report to follow).

🤖 Generated with [Claude Code](https://claude.com/claude-code)
