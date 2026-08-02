# Agent feedback (staged, fenced)

## 670-season-run — 2026-07-27 (delegated Commander under LAUNCH_ORDER-670)

**Work id:** 670-season-run (epic #659 Wave 6, Build-1 culmination — full-2023 season run + held-out diagnostic).
Drove the spine end-to-end through the engine; execute.json gate-by-gate; crews via `run_crew.py --backend external` + Agent-tool subagents + `--verify-result` (no headless CLI here); all four `user-decision` checkpoints satisfied by citing the launch order; no engine step improvised or hand-edited.

**Friction / unclear**
- The held-out diagnostic's handoff mandated **log-score as the PRIMARY metric**, but that metric turned out confounded by the landed #666 fit's σ (grip term `g_sigma_onesided` ~1e9), making it vacuous (coverage 1.0) for the fingerprint arms. The crew's judgment to lead with the σ-robust |resid| point metric + caveat + a triage candidate was the right escape — but the handoff was slightly wrong for the data.
- The **round-1 no-prior crash** was invisible until the real run: E's car ceiling needs `round_idx < R`, so round 1 (no prior) yields no severity classes and crashes inside `run_circuit`. The synthetic-runner unit tests never exercised a real E-empty round, and the season-runner handoff did not name this strictly-pre early-round-park property up front.
- The **composition-source leakage question** (is W's field-composition strictly-pre?) needed an Admiral adjudication rather than being decidable from the launch order alone; floated for awareness and endorsed as track-geometry.

**Crew-reported friction**
- A crew noted `src/data/database.py` is now the package `src/data/database/` (getters in `_metadata_session.py`) — a map-anchor drift the G1 handoff's file reference predated; flagged for #671.
- Reviewers had to inspect UNTRACKED new scripts directly (not `git diff main...HEAD`); handoffs called this out and it went smoothly, but it is a recurring friction for new-file gates in a linked worktree.
- No crew hit a blocking handoff gap; all 6 dispatches (G1 impl/rev ×2 incl. rework, G3 impl/rev, G4 impl/rev) returned clean with independently-reproduced evidence.

**Improvement signals**
- **Smoke an EARLY/edge item (expected to park), not just a mid-season happy-path round**, before launching a long detached batch — my GB round-10 smoke passed but could not catch the round-1 crash (GB has 9 prior rounds).
- **Real-data batch-runner handoffs should mandate per-item fault isolation up front** (one item's failure parks + continues, never kills the batch) and name the strictly-pre early-item-park property.
- **Detached-process liveness must use PowerShell `Get-Process` CPU (or the result artifact), never git-bash `tasklist`/`ps`** — my first watcher false-"died" on a live PID; reinforces crew-idle-strands-deliverable.
- The review tier earned its keep on the leakage-critical G4: leakage guards counterfactual-proven, σ-artifact magnitude spot-checked, every numeric claim re-reproduced.

None of the above bullets is a bare "none" — every signal section carries a real, run-specific observation.
