# Agent Feedback Log

Unified, append-only retrospective across Constellation runs in this repo. Each Commander run appends one entry at the `feedback` step, just before archive/commit. Purpose: capture where the workflow, skills, templates, or context made the work harder than it needed to be, so the doctrine improves over time.

This is workflow-improvement signal, not project truth. It accumulates across work-ids and is **never** archived or moved with a single run — it lives at the root of the agent work area and persists.

Newest entries on top.

---

## `2026-07-10` — `issue-106`

**Run shape:** `commander (delegated)` · full spine (init→archive), execute.json = 12 gates (5 deliverable classes: design/runner-core/live-wiring/scenarios/acceptance) all closed · subagents: 3 design-it-twice candidates + 1 cold plan critic + 4 implementer/reviewer crews (session tier); live pilot launched sonnet (one tier down).

**Instruction adherence:** fully followed, with sanctioned latitude decisions.
- Ran the runner-contract design gate as a 3-agent design-it-twice, converged to a hybrid (Candidate C skeleton + B's structural T3) under inherited latitude; recorded the comparison.
- Delegated `user-decision` checkpoints satisfied by citing the launch order (understand/plan/triage/review). Live-acceptance taken to the launch order's honest-null path when the environment blocked it.
- Feedback/lessons written to the WORKTREE `.agent-work/` and verify scripts run with `--root` (the known git-common-dir gap the launch order flagged).

**Friction / unclear:**
- **Late feasibility discovery (the load-bearing one):** the understand-step feasibility probe checked `claude --version` and `claude -p "say ok"` (both passed), so the run committed to a live-acceptance plan. But the real blocker — a headless `claude -p` is permission-denied ALL file creation, so it can produce no deliverables — only surfaced at g5 after the whole harness was built. A trivial headless FILE-WRITE probe at understand would have surfaced the honest-null 4 gates earlier. → distilled to a lesson (below).
- `verify_agent_feedback.py` / `verify_lessons_applied.py` resolve the durable trio to the MAIN checkout via git-common-dir; ran both with `--root <worktree>` per the launch order. Recurring engine gap across under-epic commanders (already an epic-level ACTION-NEEDED).

**Crew-reported friction:**
- g2 implementer: importing `install_constellation` via importlib needed `sys.modules` pre-registration before `exec_module` (Python 3.14 dataclass KW_ONLY probe dereferences `sys.modules[cls.__module__]`) — import-only, source untouched.
- g2 + g4 reviewers: the "SPECIFIC REVIEW FOCUS / CENTRAL DECISION" framing turned a hard judgment call into a contract-citation exercise; both recommended carrying the resulting biting-check constraint verbatim into g4/g5 (done). Good pattern — a two-interpretation fork with the contract text cited lets a cold reviewer rule crisply.
- g3 implementer/reviewer: the `subprocess.run` vs `Popen` agent-free-guard trap was correctly called in the handoff and correctly resolved; real-launch (not just fake) timeout/spawn tests made the LaunchOutcome claim independently checkable.

**What worked:**
- The cold plan critic caught two BLOCKERs (infra-fence for environment flake; the live path being tested-only-at-g5) that materially hardened the plan before any code — high leverage, folded in before freeze.
- Design-it-twice via 3 parallel subagents produced genuinely different candidates that converged cleanly; the structural-T3 graft came directly from comparing them.
- Self-testing by construction paid off: running the acceptance FOR REAL is exactly what discovered the harness isn't live-runnable headlessly (tc2/tc3) — a stronger result than a green pilot would have been.

**Improvement signals:**
- A live-acceptance gate for a headless-agent tool must probe the headless AGENT PERMISSION MODEL (can `claude -p` actually write a file?) at the feasibility step, not just CLI presence/auth. → disposition: distilled to a lesson with a target (the commander feasibility-probe habit), applied to this run's context.
- Runner findings tc1 (sentinel-fallback), tc2 (no `--permission-mode` → live false-red), tc3 (infra-fence misses permission-sandbox) → disposition: recommend-and-defer to Admiral (out of issue-filing latitude).

---
