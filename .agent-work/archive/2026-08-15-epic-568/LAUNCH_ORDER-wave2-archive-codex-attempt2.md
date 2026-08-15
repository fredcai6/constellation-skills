# Launch Order: `epic-568-codex-tier-local — archive resume — attempt 2`

**Issued:** 2026-08-15 by `admiral-epic-568` · **Boundary:** `wave-2-gate-refusal` · **Launch:** `epic-568-wave-2-repair`
**Supersedes** `LAUNCH_ORDER-wave2-archive-codex.md`, which was factually wrong on two points. Both
were found by attempt 1 and are corrected below. **Frozen.**

## What attempt 1 got right, and why you are attempt 2

Attempt 1 did not fail. It refused, correctly, and its refusal is the reason this order exists.

It found that `.mcp.json` binds the spine door from `${SPINE_FILE:-examples/mcp-interactive-demo/spine.json}`,
that `scripts/mcp_spine_server.py:146` resolves that path **once at import**, and that its session was
launched with `SPINE_FILE`, `SPINE_SESSION`, and `SPINE_ENGINE` all unset. Its door pointed at the
interactive-demo spine `scratch-mcp-424`. Calling `spine_lease claim` or `spine_advance` from there
would have mutated the **demo** spine. It did not call them. It also declined to edit the shared
`.mcp.json`, which would have corrupted two concurrent Commanders' bindings, and declined the engine
CLI because that order said MCP-only and `checklist_engine.py` was a serialized lane held by others.

Every one of those judgements was right. Nothing was mutated.

## The two corrections to my previous order

1. **PR #579 is MERGED, not OPEN.** `state: MERGED`, `mergedAt: 2026-08-14T23:32:12Z`, squash merge
   commit `e0c998b6`, an ancestor of `origin/main`. It merged after that order froze. The previous
   order's Return Shape told you to close by noting the PR "remains OPEN and unmerged" — that
   sentence would now be false, and you are not to write it. Note that `a34cf500` is **not** an
   ancestor of `main`, because the merge was a squash. Cite `e0c998b6` for this work.
2. **Your door is bound this time.** This dispatch launches through the `cli` backend with `--spine`,
   which binds `SPINE_FILE` and an assignment-keyed `SPINE_SESSION` into your process before your MCP
   servers start. Verify it: `spine_status` must describe `epic-568-codex-tier-local`, not
   `scratch-mcp-424`. **If it still resolves to a foreign spine, stop and report — do not proceed and
   do not fall back.** A third session acting on the demo spine is the failure this order exists to
   prevent.

## Mission

Complete `archive` on `epic-568-codex-tier-local` and release the lease last. Nothing else.

## Prior-Wave Verdicts (pasted)

Attempt 1's verification, which you may rely on rather than redo:

- `c1` passes — `verify_episode_captured.py --phase archive` exits 0, 3 tracked episodes.
- `c2` is true — `HEAD == origin/epic-568-codex-tier-routing == a34cf500`.
- `c2b` passes — its check command run verbatim, exit 0. It accepts MERGED as well as OPEN.
- `c4` would pass — staged diff empty; the work-area move lands under `.agent-work/**`, an allow_glob.
- Only `c3` (lease release) is unreached.
- Spine on disk: 9 of 10 gates complete, `archive` blocked, predecessor lease active at heartbeat
  `17:39:45Z`.

Re-verify what your own postconditions require, but you are not expected to re-derive the above.

## Pre-Rulings

1. **`decision:take-the-lease-over` — settled.** Claim with `force` plus a `reason`, which stamps
   `previous_session_id` and `takeover_reason`. That is a takeover, not a recreation. Do not create a
   new spine.
2. **`decision:publication-is-done` — settled.** Do not push, open, or modify any PR. Do not merge.
3. **`decision:admiral-map-commit-stands` — settled.** `a34cf500` is a legitimate Admiral-authored
   mechanical `map/INDEX.md` regeneration on top of your `247ffa1f`. Reconcile it; do not revert or
   re-attribute it.
4. **`decision:release-is-last` — settled.** Terminal advance does not auto-release. Advance archive,
   then release explicitly as your final act.
5. **`decision:no-shared-config-edits` — settled**, confirming attempt 1's own judgement. Do not edit
   `.mcp.json`. Other Commanders are live.

## Honest-Null Clause

If `archive` refuses for any reason this order has not anticipated, report it and stop. Attempt 1's
refusal was worth more than a forced advance would have been. Do not force a gate, do not hand-edit
spine state, and do not substitute the engine CLI on this dispatch — with the door bound, MCP is
genuinely available, so a fallback would be covering up a real signal.

## File Ownership

Yours: your work-area records under `.agent-work/epic-568-codex-tier-local/` and your episode files.
Not yours: `.mcp.json`, `scripts/checklist_engine.py`, `scripts/hooks/spine_rail.py`. A Commander
holds the `checklist_engine.py` lane right now.

## Workspace

Worktree `.worktrees/epic-568-codex-tier-routing`, branch `epic-568-codex-tier-routing`, spine
`.agent-work/epic-568-codex-tier-local/spine.json`. Yours alone.

## Pre-empted Steps

Everything through `feedback` is complete. Start at `archive`.

## Data Locations

Findings: `.agent-work/epic-568-codex-tier-local/FINDINGS-archive.md`. Attempt 1's record is at
`ARCHIVE_RESULT.md` — read it first.

## Stop Conditions

- `spine_status` does not resolve to `epic-568-codex-tier-local`.
- `archive` refuses for a reason not anticipated here.
- Completing it would require hand-editing spine state, bypassing the engine, or editing shared config.

## Return Shape

Report: what `spine_status` resolved to (name it explicitly — this is the whole point of attempt 2);
whether `archive` completed; whether the lease is released; what archive verification showed; and
anything floated. Do **not** describe PR #579 as open.
