# Crash-resume state note — w2-reindex

- **step:** execute · about to start gate g1-implement (precommit library, index-snapshot mechanism, fail-open shim) — plan step is complete; execute.json is authored and frozen at `.agent-work/w2-reindex/execute.json`
- **slug:** w2-reindex, branch epic-569/w2-reindex, worktree /home/tommy/projects/569-w2-reindex
- **next command:** no detached process launched yet. Resume by reading `mcp__spine__spine_status`'s `current`, then dispatch g1-implement's implementer per `execute.json`'s g1-implement.constraints (the full pinned specification — index-snapshot build, unique tempfile worktree paths, per-subprocess timeouts, plain-file-I/O copy-back, fail-open with one-line stderr diagnostic) via `python scripts/run_crew.py --parent <own SPINE_SESSION> --model sonnet ...` per `references/crew-dispatch.md`
- **pid:** none — foreground (no background process outstanding)
- **expected artifact:** `.agent-work/w2-reindex/crew-handoffs/g1-implement-implementer-result.md` (does not exist yet)

Context: a HARD context-band trip fired at the `execute` step boundary (CONTEXT 26% >= hard). A refresh-request is filed against `execute` (why_ref w-4). Read MISSION_FRAME.md, PLAN_ALTERNATIVES.md, and PLAN_CRITIC.md (including its Commander disposition section) before dispatching g1 — they carry the full reasoning behind execute.json's pinned gate specifications; do not re-derive them.

_Updated: 2026-08-22T17:38:46Z_
