# Archive result — `epic-568-codex-tier-local`

**Session:** `constellation/epic-568-codex-tier-local/archive/commander/attempt-1`
**Launch order:** `.agent-work/epic-568/LAUNCH_ORDER-wave2-archive-codex.md` (frozen, 2026-08-14)
**Date:** 2026-08-14

## Verdict

**`archive` did NOT complete. The lease is NOT released.** Nothing was mutated.

The refusal is not the gate's. Every archive postcondition is now factually satisfiable, and I
verified each one at source. The run stopped because **this session's spine MCP door is bound to the
wrong spine and cannot be retargeted from inside the session.** The launch order requires
"Spine interaction is MCP-only", so there is no sanctioned path from here to the engine.

This is the Honest-Null Clause case: a reason the order did not anticipate. Reporting and stopping,
per instruction. No gate was forced and no spine state was hand-edited.

## The blocker

`.mcp.json` binds the door from the environment:

```json
"SPINE_FILE": "${SPINE_FILE:-examples/mcp-interactive-demo/spine.json}"
```

This session was launched with `SPINE_FILE`, `SPINE_SESSION`, and `SPINE_ENGINE` all **unset**, so
the door fell through to the default. `scripts/mcp_spine_server.py:146` resolves `SPINE` once at
module import, so the binding is fixed for the life of the server process.

`spine_status` from this session therefore reports a foreign spine:

```
ACTIVE g1 [pending] — Create .../epic-418-followon/commander-424/crew-plans/scratch-mcp/...notes.txt
```

That is `work_id: scratch-mcp-424`, the interactive demo spine — not
`epic-568-codex-tier-local`. Calling `spine_lease claim` or `spine_advance` from this session would
act on the demo spine. I did not call them.

There is no retargeting tool. `spine_open` creates a spine that does not exist yet; `spine_close`
acts only on the bound spine; no verb rebinds. Editing the repo-root `.mcp.json` to hardcode a path
was rejected: that file is outside my ownership and two other Commanders share this checkout, so the
edit would corrupt their door bindings.

I also rejected the engine CLI fallback that the archive imperative itself names
(`<engine> release --session-id ...`). Two independent reasons point the same way: my frozen order
says MCP-only, and `scripts/checklist_engine.py` is a serialized lane held by two other Commanders
right now, so invoking it could run a mid-edit engine against my spine.

## Archive verification (all read-only, all measured at source)

| Cond | Statement | Measured | Status |
|---|---|---|---|
| `p1` | workflow feedback recorded | already satisfied in spine | met |
| `c1` | episode captured AND git-tracked | `verify_episode_captured.py ... --phase archive` exits 0; 3 episodes: `-001`, `-002`, `-003` | **passes** |
| `c2` | branch committed and pushed | `HEAD == origin/epic-568-codex-tier-routing == a34cf500` | **true, attestable** |
| `c2b` | PR OPEN or MERGED | check command run verbatim, exits 0 | **passes** |
| `c3` | lease released | last action, not reached | not reached |
| `c4` | staged diff carries no suspicious artifacts | staged diff empty; work-area move lands under `.agent-work/**`, an allow_glob | **would pass** |

Worktree is clean apart from two untracked work-area directories
(`.agent-work/epic-568-codex-tier-local/`, `.agent-work/epic-568-codex-tier-routing/`). `.agent-work`
is **not** gitignored here, so the archive move commits normally.

Spine: 9 of 10 gates `complete`; `archive` is `blocked`. Lease `constellation/epic-568-codex-tier-local`
is still `active`, last heartbeat `2026-08-14T17:39:45Z` — the dead predecessor's, as the order said.

## Floated to the Admiral

**1. The dispatch environment, not the gate, is the blocker.** One Admiral action clears it: relaunch
this crew with the door bound. Values verified against this worktree:

```
SPINE_FILE=/home/tommy/projects/constellation-skills/.worktrees/epic-568-codex-tier-routing/.agent-work/epic-568-codex-tier-local/spine.json
SPINE_SESSION=constellation/epic-568-codex-tier-local/archive/commander/attempt-1
SPINE_ENGINE=/home/tommy/projects/constellation-skills/scripts/checklist_engine.py
```

The relaunched session takes the lease over with `spine_lease claim force=true` plus a reason, which
stamps `previous_session_id` and `takeover_reason` — that is takeover, not recreation, as ordered.
`SPINE_SESSION` must carry the crew name for that stamp to be right.

**2. PR #579 is MERGED, not OPEN. The launch order is out of date here.** The order states it is OPEN
and directs me to report that it "remains OPEN and unmerged". At source:

```
state: MERGED   mergedAt: 2026-08-14T23:32:12Z   mergeCommit: e0c998b6
```

It was squash-merged, so `a34cf500` is not itself an ancestor of `origin/main`, but `e0c998b6` is.
The merge landed after the order was frozen. This does **not** block anything — `c2b` accepts OPEN or
MERGED and passes on the merged state. It only means the required closing note in the Return Shape is
now false, and the merge decision the order reserved to the Admiral has already been exercised.

**3. Reconciled, not disputed: `a34cf500`.** The Admiral-authored mechanical `map/INDEX.md`
regeneration sits on top of `247ffa1f` exactly as the order describes. Verified present, left alone,
not reverted or re-attributed.

## Not done

No push, no PR creation, no PR modification. No edit to `scripts/checklist_engine.py` or
`scripts/hooks/spine_rail.py`. No spine mutation of any kind. The work-area move to
`.agent-work/archive/<date>-epic-568-codex-tier-local/` was deliberately left undone — it belongs
inside the gated archive step, and doing it now would move this file out from under the Admiral.
