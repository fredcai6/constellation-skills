# Reviewer Handoff

## Gate
`g3` — `finish_work` composition + dispose + CLI. Final gate of 3; g1 (verify+close) and g2 (reap+child-release) are already reviewed and integrated.

## Survey State Location
`.agent-work/epic-567-door/cmdr-g/g3-review/review.json`.

## What Was Implemented
- `finish_work(spine_path, *, root, session_id, today, tree_clean, episodes_captured, why=None, push=True, open_pr=False) -> dict` — composes, in this load-bearing order: `done_refusal` (refuse-and-stop) → `_release_child_plans` (children first) → `_advance_and_release` (top-level release) → `force_reap` (after every release) → `close_work` (unmodified archive move) → optional `git push` → optional `open_pr`. Never raises for a normal closeout refusal.
- `open_pr(work_id, branch, *, root, title=None, body=None) -> str | None` — a separate helper, not called by default (`open_pr=False`); writes the PR body via a temp file and `gh pr create --body-file` (never `--body`).
- `scripts/spine_done_cli.py` (new file) — thin CLI over `finish_work`.
- 15 new tests: refusal-stage coverage, a spy-based composition-order test, the #552 lease-proof end-to-end test, `open_pr` behavior, and fresh-process CLI smoke tests.

**One deliberate deviation from the handoff to verify:** the implementer's own report says `finish_work`'s signature adds `tree_clean: bool, episodes_captured: bool` as required keyword parameters — the handoff's headline signature line omitted them, but its own step 2 and CLI section both require them. Confirm this is a genuine, unavoidable gap in the handoff (not an implementer error) by reading the handoff yourself, and confirm the added parameters are actually wired to `done_refusal`'s call.

## How to Inspect the Diff
Uncommitted working tree in `/home/tommy/projects/constellation-skills/.worktrees/567-g-closeout-lease`. `git status --porcelain` then `git diff -- scripts/spine_lifecycle.py tests/test_spine_lifecycle.py`; `scripts/spine_done_cli.py` is new (appears in `git status`, not `git diff --name-only`).

## Task Statement
Compose g1+g2's already-shipped primitives into one call per `.agent-work/epic-567-door/cmdr-g/crew-handoffs/g3-implementer-handoff.md`.

## Close Criteria
- **Composition order is exactly right** — re-run `TestFinishWorkCompositionOrder` yourself and read the spy assertion: `["release_child_plans", "advance_and_release", "force_reap", "close_work"]`. This ordering is the actual point of both cold critiques (PLAN_CRITIQUE.md/PLAN_CRITIC.md finding 2) — verify the SOURCE calls them in this order, not just that the test (which could itself be wrong) passes.
- **The #552 lease-proof end-to-end test is real** — re-run `TestFinishWorkLeaseProofEndToEnd` yourself, read the test body, and confirm it genuinely builds a parent+child fixture with BOTH leases active before the call and asserts BOTH are gone after, with the child physically present in the archive directory reading `released`. This is the launch order's Return Shape item 5 — the single most important thing this whole lane produces.
- `finish_work` never raises for a normal closeout refusal at any composed step — re-run `TestFinishWorkRefusals` and confirm each refusal case returns a structured dict, not an exception.
- `open_pr` is never called unless `open_pr=True` — confirm via the `TestOpenPr` off-by-default test, and confirm (by reading source) `open_pr`'s PR body write uses `--body-file`, never `--body`.
- Fenced files empty diff: `git diff --stat -- scripts/checklist_engine.py scripts/mcp_spine_server.py scripts/hooks/spine_rail.py`.
- `done_refusal`, `_engine_call`, `_advance_and_release`, `force_reap`, `_release_child_plans`, `close_work`/`closeout_refusal` are unmodified — `finish_work` composes them, does not alter their behavior.
- **Fresh-process CLI validation is genuine, not simulated in-process** — confirm `TestSpineDoneCli` actually spawns a `python3` subprocess (`subprocess.run`), and independently run the CLI yourself against a throwaway fixture (not this worktree's own `.agent-work`) to confirm it works outside the test harness too.
- Full suite green (pre-change: 119, this is the terminal gate — should not add MORE tests unless you find a genuine gap).

## Allowed Scope
`scripts/spine_lifecycle.py` (`finish_work`, `open_pr`), `tests/test_spine_lifecycle.py`, `scripts/spine_done_cli.py` (new).

## Specific Exclusions
`scripts/checklist_engine.py`, `scripts/mcp_spine_server.py`, `scripts/hooks/spine_rail.py` — must show empty diff. g1/g2's functions and `close_work`/`closeout_refusal` must be unmodified.

## Constraints the Implementation Must Respect
- Never run `finish_work` or the CLI against a live spine file — every test fixture (including the CLI smoke tests) must build under `tmp_path` or an explicitly throwaway repo, never `.agent-work/epic-567-door/{,cmdr-g/}{spine,execute}.json`.
- `open_pr` must never construct a `gh pr create --body <string>` call — only `--body-file`.

## Map Anchors (inbound)
- **Structural:** `scripts/spine_lifecycle.py` — `close_work` (:384+, unmodified), the g1/g2 primitives (read their docstrings directly — they are the authoritative contract `finish_work` composes).
- **Capability:** mechanical-closeout-one-verb — #574's full contract sketch, steps 1-5, now reachable via one call.
- **Constraints/assumptions:** `decision:pr-opening-question-is-not-yours` — floated, not ruled; `open_pr` off by default.
  `@grade: settled/human · leans g3-implement`
- **Decision anchors:** `decision:new-rot-first-old-rot-maybe` — the 41 pre-existing stale leases are explicitly out of scope; confirm `finish_work` makes no attempt to sweep them (it shouldn't, and the implementer's report says it doesn't — verify this by reading, not trusting).
- **Evidence expectations:** the lease-proof test IS the claim/evidence this whole gate exists to produce — treat it as the single highest-priority thing to independently reproduce.

## Evidence Produced
See `.agent-work/epic-567-door/cmdr-g/crew-handoffs/g3-implementer-result.md` in full (thorough: composition-order spy test, lease-proof test body and output, two forms of fresh-process CLI evidence including a standalone manual run). The Commander independently re-ran the full suite (119 passed), the fenced-file diff (empty), the lease-proof test alone, and confirmed the new CLI file is tracked and not gitignored, before dispatching you. Re-verify independently.

## Suggested Model Tier
Sonnet — bounded; this is the terminal gate of a well-specified 3-gate sequence, and its one genuinely hard thing to verify (composition order + the lease-proof mechanism) is mechanically checkable against source and tests.

## Stop Conditions
BLOCK if: the composition order in source doesn't match children→top-release→reap→archive; the lease-proof test doesn't genuinely exercise both leases going to zero; `open_pr` is called by default anywhere; a fenced file shows non-empty diff; the CLI smoke test is not a genuine subprocess spawn.

## Return Format
Return `REVIEW_RESULT` to `.agent-work/epic-567-door/cmdr-g/crew-handoffs/g3-reviewer-result.md` before ending your turn.
