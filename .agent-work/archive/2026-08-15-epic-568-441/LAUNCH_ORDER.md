# Launch order — #441 transactional binding store

## Mission

Make the shared spine binding registry safe under concurrent hook writers, unify usable agent-id validation across rail and gauge consumers, constrain claim targets to valid JSON checklists, and reap only provably dead binding entries. Build directly on reviewed #530 without changing checklist lease lifecycle.

## Prior-wave verdicts

Base `065445de` contains reviewed #530 commit `97eb5d34`, which derives binding worktree ownership from the validated absolute spine path; its focused rail suite passed 111 tests with 1 skip and independent APPROVE. Measurement found all binding writers currently perform unlocked read-modify-write and fixed `.tmp` replacement can lose updates. Claim/release live in `handle_post_tool_use`; SessionStart is a third writer. Gauge and rail use divergent agent-id predicates. The live registry measured 17 entries: 15 missing targets, 1 released target, 1 active target.

## Pre-rulings

- decision:transaction-boundary — one shared portable advisory-lock transaction must cover read, safe reap, mutation, and unique-temp atomic replacement for claim, release, and SessionStart writers.
  @grade: settled/human · leans execute
- decision:active-retention — never reap a readable active lease by age in this issue; no historical bulk backfill or lifecycle inference. Safe reap is limited to malformed/empty records, missing targets after a bounded grace, and explicitly released targets.
  @grade: settled/human · leans execute
- decision:identity — move the stricter gauge allowlist into one authoritative rail helper and make both rail binding keys and gauge consumption use it; reject punctuation, whitespace, wildcards, and ids longer than 64 consistently.
  @grade: settled/measured · leans execute
- decision:claim-validation — claims require an existing `.json` checklist at the contained `.agent-work/<work-id>/<name>.json` shape established by #530; release first resolves the recorded target and retains moved/deleted compatibility.
  @grade: settled/human · leans execute
- decision:no-engine-lifecycle — explicit lease release remains mandatory. Claim/release journaling, child ownership, actor identity, durable-root liveness, and PID-less worktree freedom are separate lifecycle waves.
  @grade: settled/human · leans execute

## Honest-null clause

If a production multiprocess regression cannot lose updates on the reviewed base, return the exact scheduling/topology tested and continue only with independently red identity/path/reaper defects; do not manufacture concurrency machinery.

## Inherited latitude

Choose the smallest stdlib portable lock implementation and bounded acquisition behavior that fails open for hooks. Prefer OS advisory locks (`fcntl`/`msvcrt`) with crash release; float if platform behavior requires a stale lockfile policy or if active-lease retention must change.

## File ownership

Sole writer for `scripts/hooks/spine_rail.py`, `scripts/hooks/gauge_writer_hook.py`, focused `tests/test_spine_rail.py`, `tests/test_gauge_writer_hook.py`, and worktree-local `notes-1.md`. Expand only for a directly required shared test helper and float first.

## Workspace

`/home/tommy/projects/constellation-skills/.worktrees/epic-568-441`, branch `epic-568/441-binding-store`, base `065445de`, created with `git worktree add -b epic-568/441-binding-store .worktrees/epic-568-441 065445de`. First verify isolation with `python /home/tommy/.claude/skills/constellation-admiral/scripts/verify_worktree_isolation.py --here /home/tommy/projects/constellation-skills/.worktrees/epic-568-441`.

## Inherited context

Drive `.agent-work/epic-568-441/spine.json` only through `scripts/mcp_spine_server.py` over stdio as session `constellation/epic-568-441`; no checklist-engine CLI and no reading/hand-editing engine JSON. Acceptance requires a real spawn-safe multiprocessing test using production handler/store paths and independent processes against one registry; final JSON must parse and retain every expected entry. Run on Linux now and preserve Windows-compatible test structure; Windows CI failures are allowed to remain recorded, while every non-Windows failure blocks.

## Pre-empted steps

Admiral established context, measured the overlap, ruled lifecycle policy, serialized this work after #530, and ratified this launch order. Cite it at delegated checkpoints.

## Data locations

All inputs are tracked in this isolated worktree. No historical binding registry is to be mutated by tests or migration.

## Budget

- Model tier: `gpt-5.6-sol`, high reasoning.
- Session: high-risk cross-platform concurrency change; float lifecycle ambiguity immediately.

## Stop conditions

Stop for active-lease reaping, engine lifecycle/journal changes, child semantics, actor/PID liveness, inability to build a discriminating production multiprocess test, or any non-Windows regression.

## Return shape

Write a durable result before returning. Include isolation, red/green and mutation-control proof, exact lock/reaper semantics, changed files/tests, blast-radius count, remaining platform risks, spine status, and READY-FOR-REVIEW or FLOAT.
