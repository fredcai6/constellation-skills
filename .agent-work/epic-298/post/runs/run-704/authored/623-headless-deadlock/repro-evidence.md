# #623 — headless deadlock: pre-fix reproduction evidence

All runs: cwd=`C:/Programs/f1-623` (fixed-code worktree, `git rev-parse --abbrev-ref HEAD` =
`fix/623-headless-deadlock`), pre-fix tree (HEAD `c62a6430`, no changes yet), launched via
PowerShell `Start-Process -WindowStyle Hidden` (genuinely detached, no console/window
attached to the child), `-RedirectStandardOutput`/`-RedirectStandardError` to log files.

Command (1 race, Bahrain 2024):
```
py -m src.evo_predictor.run sampled-backtest \
  --sampled-runtime-manifest reports/evo/gold_cycle_260612_054059_2018thru2024.sampled_runtime_manifest.json \
  --year 2024 --seed 12345 --max-rounds-per-year 1 --race Bahrain \
  --db-path data/f1_data_2024.db --compound-prior-root params/gold/compound_prior \
  --output <out>.json
```

## Attempt 1 — solo detached run

Launched 15:00:25. Log reached `race 1/1 - round 1 Bahrain (elapsed 0m, ETA ~0m)` immediately,
then **completed** at 15:04:10 (total 4m), valid output JSON written (`aggregate_metrics`
present, `per_race` count 1). CPU/WorkingSet polled every 30s throughout — did NOT hang.

This attempt did **not** reproduce the deadlock — noted honestly; see Attempt 2.

## Attempt 2 — two concurrent detached processes (Bahrain + Saudi Arabia)

Launched two `Start-Process -WindowStyle Hidden` children at 15:05:25 (matches the issue's own
repro matrix: "two concurrent processes"). The second (Saudi Arabia) crashed within seconds on
an unrelated PowerShell arg-splitting artifact (`--race "Saudi Arabia"` got split into two argv
tokens by `-ArgumentList`, producing an argparse error) — **not** related to #623, a shell
quoting mistake on my part, and it exited immediately.

The first (Bahrain, PID 31024) — the exact same command as Attempt 1, same manifest, same DB,
same seed — **deadlocked**: log froze at
`race 1/1 - round 1 Bahrain (elapsed 0m, ETA ~0m)` (printed 15:05:25) and CPU time / working
set stayed completely flat (`CPU=0.15625` core-seconds, `WS=16MB`) across 26 consecutive 30s
polls (13 minutes wall-clock, 15:05:25 -> 15:18:33), while the log line never advanced past
race 1 and no output file was ever written. Killed manually (`Stop-Process -Force`) at 15:18:33
rather than left running — this is the reproduced deadlock signature from #623 ("hangs with 0%
CPU at the first race... CPU=0 at race 1 start means the process blocks acquiring a backend
resource before any NN compute").

## Interpretation

The deadlock is real and reproduces in this exact worktree/environment, but is **not
deterministic on every detached launch** — it reproduced on the second attempt (running
alongside a very-short-lived second process) but not the first (solo). This is consistent
with the diagnosis's account: a lazily-initialized native thread-pool whose init path is
console-handle-dependent is a race, not a guaranteed-every-time hang — timing/scheduling
(including a second process briefly sharing the machine at process-start time) can tip it
either way. This does not weaken the recommended fix; it explains why the issue's own report
needed multiple repro attempts across several launch styles to characterize it, and why a
single clean interactive run was the only reliably-successful mode observed.
