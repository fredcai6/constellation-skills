# Crash-resume state note — issue-495-fit-robustness

- **step:** execute · gate g3-integrate ADVANCE in background (py -m pytest tests/unit/physics -q). g3-review APPROVE (attempt-2). After g3 closes: execute c1 attest -> spine advance execute -> reconcile (cartographer) -> triage (tc1/tc2/tc3) -> review -> feedback -> archive. ARCHIVE: git add -f reports/physics/495_fit_robustness_validation.md (/reports gitignored; P0/P1a force-tracked). Crews session-limit was at 12:10pm PT (now lifted).
- **slug:** issue-495-fit-robustness · branch fix/495-fit-robustness · worktree C:/Programs/f1Brainz (main checkout — data lives here: data/telemetry_store.db, data/telemetry cache, data/physics_fits.db)
- **next command:** python C:/Users/fredc/.claude/skills/constellation-workbench/scripts/checklist_engine.py --file .agent-work/issue-495-fit-robustness/execute.json current ; drive g2-implement -> g2-review -> g2-integrate -> g3 validation
- **pid:** none — crews are Agent-tool subagents (foreground/blocking), recorded in crew-runs.json via run_crew.py pure registry funcs (no claude CLI binary in this harness)
- **expected artifact:** .agent-work/issue-495-fit-robustness/g2_implementer_result.md (then g2_review_result.md)

_Updated: 2026-06-28T16:00:00Z_
