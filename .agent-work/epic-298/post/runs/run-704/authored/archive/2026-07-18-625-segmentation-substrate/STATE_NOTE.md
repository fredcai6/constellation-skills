# Crash-resume state note — 625-segmentation-substrate

- **step:** execute · gates g1/g2/g3 fully complete (all reviewed APPROVE); g4-implement and
  g4-review both complete and APPROVE; g4-integrate in-progress, waiting on the full physics
  suite regression (c3 postcondition) to finish before the closing `advance g4-integrate`.
  Gate 3's real-data F12 verdict is FAIL (n_pass=0/5) — a genuine, verified, honest finding,
  already propagated into Gate 4's rollup output.
- **slug:** 625-segmentation-substrate, branch feat/625-segmentation-substrate, worktree C:/Programs/f1-625
- **next command:** tail the background suite log, then once green:
  `py C:/Users/fredc/.claude/skills/constellation-workbench/scripts/checklist_engine.py --file .agent-work/625-segmentation-substrate/execute.json advance g4-integrate`
  (session lease on the OUTER spine is `commander-625-segmentation-substrate`; execute.json's
  gate checklist itself carries no separate lease)
- **pid:** background bash task `bfw020uv5` (run_in_background) — the ENGINE's own
  `advance g4-integrate` call (this actually executes c1/c3/c4's postcondition commands,
  including the full-suite regression), log at
  `C:/Users/fredc/AppData/Local/Temp/claude/C--Programs-f1Brainz/cac4681b-3be0-47b5-bcad-8d680b5c633e/scratchpad/g4_integrate_advance.log`.
  A prior manual (non-engine) copy of the full-suite run (`bsxq2adv7`) reached 90% clean
  (zero failures, every actual risk-surface file green incl. `test_segment_classifier.py`)
  before being reaped by the harness for runtime — strong supporting evidence while the
  engine's own authoritative run completes.
- **expected artifact:** `bfw020uv5.output` reaching `g4-integrate -> complete`; then
  `regime_time_share.csv`/`.meta.json` (already committed, Gate 4 evidence).

_Updated: 2026-07-18T08:05:00Z_
