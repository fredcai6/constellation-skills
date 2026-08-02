# RESUME — issue-356-utilization-knob (Constellation Commander run)

If context was compacted, re-orient from here.

## Where we are
- Spine: `.agent-work/issue-356-utilization-knob/spine.json` — steps complete through **plan**; active step is **compact**.
- Problem statement (confirmed): `.agent-work/issue-356-utilization-knob/problem-statement.md`
- Frozen gate plan: `.agent-work/issue-356-utilization-knob/execute.json` (e0-context + G1..G6, each implement/review/integrate). **Do not edit mid-run.**
- Interrogation (consolidated): `.agent-work/issue-356-utilization-knob/interrogation.json`
- Branch: `claude/recursing-hofstadter-5c4e0d` (worktree). Work-id: `issue-356-utilization-knob`.

## Engine
`py C:/Users/fredc/.claude/skills/constellation-workbench/scripts/checklist_engine.py --file <checklist.json> <verb>`
Verbs: current, start, advance, record, consolidate, attest (--cond --which), attach (--type --field K=V), reopen, block, flag-candidate.

## Next actions
1. Finish **compact**: reload the `constellation-commander` skill, then `attest compact --cond c1`, `attest compact --cond c2`, `advance compact` (start it first).
2. **execute**: `start execute` (attest p1 first), then drive `execute.json` gate by gate:
   - For each gate gN: fill `IMPLEMENTER_HANDOFF.template.md`, dispatch a **constellation-implementer** subagent (MUST use the superpowers:test-driven-development skill — red-green-refactor, tests first), integrate IMPLEMENTER_RESULT; then `REVIEWER_HANDOFF`, dispatch **constellation-reviewer**, integrate REVIEW_RESULT; then integrate: run the gate's verification command, confirm APPROVE, advance.
   - Templates: `C:/Users/fredc/.claude/skills/constellation-commander/templates/`
3. Remaining spine steps after execute: **reconcile** (cartographer subagent), **triage** (in-context, user approves issues), **review** (run summary, user accepts — run.accept checkpoint), **archive** (commit, push, move work area to `.agent-work/archive/<date>-issue-356-utilization-knob/`).

## Key decisions (locked)
- Core: `src/utils/utilization.py` — resolve_resource_plan / init_worker / run_jobs (ProcessPoolExecutor; n_workers==1 -> in-process).
- Levels background/balanced/max; gold default balanced; RAM auto-cap (mem_per_worker_gb=1.0), not user-facing.
- `--utilization` allowed in gold mode as non-policy hint (never in applied_overrides).
- Determinism: byte-identical at fixed threads regardless of n_workers; tolerance across thread counts.
- `psutil` must be declared in pyproject.toml (G1).
- Keep `utilization` OUT of the gold report schema.
- Human checkpoints: understand.done (done), plan.approved (done), run.accept (pending at review).
