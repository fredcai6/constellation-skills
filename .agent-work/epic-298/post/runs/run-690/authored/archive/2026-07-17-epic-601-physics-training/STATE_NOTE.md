# Crash-resume state note - epic-601-physics-training

- **step:** execute - Wave 7 dispatched (3 parallel delegated Commanders + a #560 review subagent)
- **slug:** epic-601-physics-training; Admiral session `admiral-20260716-601-physics` (Claude); main checkout C:\Programs\f1Brainz
- **base:** local `main` 5e8e92d7 (7A/7C); #560 tip ed57bccc (7B). origin/main forked — 7C reconciles, Admiral pushes at wave close.
- **wave 7 commanders (isolated worktrees):**
  - 7A residual screen (go/no-go gate) - C:\tmp\f1brainz-601-7a-residual (wave7a-residual-screen) - LO launch-orders/wave7a-residual-screen.md - expects .agent-work/cmdr-7a-residual-screen/RESULT.md
  - 7B 2026 aero (#483) - C:\tmp\f1brainz-601-7b-aero (wave7b-2026-aero) - LO launch-orders/wave7b-2026-aero.md - expects .agent-work/cmdr-7b-2026-aero/RESULT.md
  - 7C reconcile - C:\tmp\f1brainz-601-7c-reconcile (wave7c-reconcile) - LO launch-orders/wave7c-reconcile.md - expects .agent-work/cmdr-7c-reconcile/RESULT.md
  - #560 review subagent - existing worktree C:\tmp\f1brainz-601-560 (admiral-601-physics-560, ed57bccc) - on APPROVE Admiral merges to local main
- **STATUS 2026-07-16 ~16:15Z:**
  - rev-560: APPROVE (folds into origin/main via normal PR — retracted the "can't PR" ruling)
  - 7C: DONE — `no-fork-shallow-clone-illusion`. Base pivots to `origin/main` (9f014121, strict superset of local main). NO reconcile. local main just 6 behind.
  - 7A: backtest reaped TWICE by agent-idle (children die when the running agent goes idle; run only writes csv at the very end). Admiral now OWNS it as OS-detached compute: parent pid in C:\tmp\f1brainz-601-7a2-residual\.agent-work\cmdr-7a-residual-screen\artifacts\detached.pid (was 7604), parallel plan level=max + effective_seed=0, script self-pins worktree sys.path. Poll bg-task `bkcuixpc6` (DONE→evo_residuals.csv / DEAD / HUNG-deadlock / TIMEOUT). ON DONE: run correlation physics_panel.csv vs evo_residuals.csv (join year,round,canonical_constructor_id), Spearman+Pearson per axis (apex/lateral-grip, drag) per holdout → go/no-go verdict + write RESULT.md. ON HUNG: relaunch sequential-detached (219s/round, proven). Determinism excuse gone → null is real.
  - 7B: DONE — PR #622 (2026 aero + #560 bundled), rev-622 APPROVE, clean 3-way merge to origin/main. HELD for wave-close user checkpoint (merge surfaced).
  - 7A backtest saga: hangs whenever py runs without a console/interactive stdin (explicit bash-bg OR concurrent OR Start-Process-hidden-with-pipes all hung CPU=0; bash-bg also gets REAPED ~10min; the ONE success was a single foreground-auto-bg smoke, 219s). Current attempt: single-process SEQUENTIAL combined driver (run_residuals_combined.py) launched detached via cmd /c "py ... > log 2>&1 < NUL" (file redirect + empty stdin), pid in artifacts/combined.pid (16828). Watchdog btmhc2tcp (~3min): HEALTHY(CPU>25)→chain-poll to completion; HUNG→PIVOT to sampler-free proxy screen (correlate physics_panel vs a data-only baseline residual from DB, no NN sampler) and note it as a weaker-but-sufficient gate, full evo A/B deferred to Wave 8.
  - PIVOTED: real backtest is unrunnable headless here (hangs CPU=0 every mode; loky/console deadlock — see triage-candidates/wave7a-backtest-blocker.md). Gate now runs as SAMPLER-FREE PROXY screen via `cmdr-7a3` (physics_panel vs a data-only prior-form baseline residual, pure pandas). Expects .agent-work/cmdr-7a-residual-screen/RESULT.md in C:\tmp\f1brainz-601-7a2-residual. Verdict rules: proxy-signal→GO Wave8 (real A/B confirmatory); proxy-null→lean no-go but not definitive (proxy≠full-evo; frac_team≤3% prior).
- **WAVE-CLOSE package pending (present to user):** (1) merge PR #622 (2026 aero + #560) to origin/main [surfaced]; (2) Wave-8 go/no-go from 7a3 proxy verdict; (3) note real-A/B backtest blocker (triage) needs an issue before Wave 8; (4) fast-forward local main to origin/main is user's call.
- **next command:** await poll br3y2v3fa + 7B; adjudicate; then wave-close: rebase #560/7B onto origin/main, open PRs, integrate; fast-forward of local main is user's call (dirty checkout).
- **pid:** detached backtest 10936; poll br3y2v3fa; 7B subagent
- **expected artifact:** artifacts/evo_residuals.csv then 7A RESULT.md; 7B RESULT.md + PR

_Updated: 2026-07-16, Wave 7 launch_
