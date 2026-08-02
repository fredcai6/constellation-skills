# Decisions Log — Issue #382 (for Admiral)

## D0 — No nested-subagent tool available → in-context role discipline [cheap+reversible, LOGGED]
This environment exposes no general-purpose subagent/Task dispatch tool (verified: ToolSearch for Task/subagent returns only TaskStop/EnterWorktree; no agent-spawn). The engine reference explicitly covers this: "If your environment has no nested subagents, keep the orchestration (Commander) in the one human-reachable context and dispatch only the leaf workers." Here even leaf-worker dispatch is unavailable.
**Default taken:** execute the implementer and reviewer roles IN THIS CONTEXT by loading the respective constellation skills, preserving role discipline — separate implement vs review passes, each with its own handoff file and its own evidence, driven through execute.json's gates. The standing order "pass model: sonnet on every dispatch" is recorded in each handoff as the intended tier; it cannot be enforced without a dispatch tool. Logged for Admiral; reversible (no artifact depends on it).

## D1 — §7 / gate findings / gate script NOT on main [LOGGED, mild flag]
§7 of prediction_ceiling_and_priorities.md, compound_crossover_gate_findings.md, and scripts/fit_compound_crossover_gate.py live ONLY on un-merged branch `claude/compound-regime-feasibility` (8 ahead / 24 behind main, no PR). My branch is from origin/main and lacks them.
**Default taken:** append a NEW self-contained §7.5-followup subsection (#382) that stands alone; vendor the pooled-FE cross-check method into my own diagnosis script so the PR is self-contained against main. Do NOT port the whole feasibility §7 (would collide when that branch merges). Do NOT rewrite. Admiral reconciles at merge. Reversible.

## D2 — Do not flip production config defaults [LOGGED, scope guard]
Root-cause points at production defaults (ridge_alpha=1.0, sparse_prior_strength=1.0, monotone-γ isotonic projection). Flipping any is a production-behavior change gold artifacts + sibling #380's consumption depend on → out of default scope.
**Default taken:** identify + MEASURE + RECOMMEND the lever; do not change src/compound_prior behavior. If the Admiral wants the fix applied, that's a follow-up with its own gold-cycle evidence (Brier). Reversible.

## D3 — Reproduce production degeneracy from committed gold artifacts + solver ablation [cheap+reversible]
The committed gold artifacts at params/gold/compound_prior/{year}/compound_prior_summary.json ARE the production degenerate output (confirmed: β jagged/wrong-signed C1, γ_C1..C4 identical plateau). Diagnosis reads these directly (no refit needed to confirm) and re-runs the production solver internals on DB-extracted observations only to ABLATE levers (ridge α sweep, monotone on/off, collinearity). DB-only; canonical data constraint respected.
