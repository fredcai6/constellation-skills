# Triage candidate: every launch order's first instruction requires a sticky `cd`, and an agent that cannot make one stick never reaches step one

**Status:** not filed. Held to closeout per the epic's standing ruling.
**Found by:** the Admiral of epic-567-door, autopsying lane A's death, 2026-08-16.
**Pairing suggestion:** #535 (reveal the spec through the spine, not the launch order) — this is #535's death shape with a specific mechanical trigger #535 does not name. #535 is already a member of epic #567 and is forecast as wave-2 lane F, so this belongs on it.

## What happened

Lane A (Opus, the epic's anchor lane) ran **47 minutes and wrote zero bytes** — nothing in its worktree, nothing in the main checkout, no work area, no lease, no spine. Two liveness probes and one direct Admiral query produced no write. It was killed and relaunched.

Its final output, captured at kill: **"The bash cwd resets between calls. Let me use EnterWorktree."**

It was not thinking hard and it was not looping on the mission. It was stuck on shell working-directory mechanics, never established a cwd it trusted, and therefore never executed the first line of its launch order.

## Why the launch-order template makes this fatal rather than annoying

`fleet-doctrine.md` and the `LAUNCH_ORDER` template both open every dispatch with, in substance:

> First step, before any git operation: **`cd` into that worktree**, then run `verify_worktree_isolation.py --here <path>` — it must exit 0.

And the template's own note explains, correctly, that the order matters and that passing the path to git instead (`git -C <path>`) **disarms the check**, because it compares the worktree to itself. So the instruction deliberately depends on ambient cwd, and deliberately forbids the obvious workaround.

For an agent that cannot make `cd` stick, that combination is a closed door at line one:

- it cannot satisfy `--here`, because that asserts about ambient cwd;
- it is explicitly told not to use `git -C`, the workaround it would otherwise reach for;
- the check is framed as a gate it must pass and paste before proceeding.

The relaunch resolved it in one sentence by pre-authorizing the fallback: run `cd` as its own single Bash call, and if that still does not stick, work from absolute paths and record that `--here` was unusable. The relaunched agent was writing within minutes.

## Why this is a fleet defect, not a lane defect

Nothing carries the workaround to the next dispatch. The Admiral improvised it, by hand, per dispatch, having just been burned — which is the same criticism #535 makes of the bootstrap-floor workaround it was filed about:

> But it is a workaround, applied by hand, per dispatch, by an Admiral who happened to have just been burned.

The pattern is identical, one level down: the expensive part is not the mission, it is arriving.

## Two smaller observations from the same autopsy

- **The isolation gate cannot distinguish "not isolated" from "not arrived yet."** `--here` returns `fatal: not a git repository` for both, and the template has to spend a paragraph of prose warning readers about it. A check whose failure mode needs a paragraph to disambiguate is worth reshaping.
- **Zero-writes is a better liveness signal than the harness's status, and nothing computes it.** The Admiral had to build the probe inline. `git status --porcelain` empty across a whole worktree, sustained past a threshold, distinguished a stuck agent from a working one when `ListAgents` said only `running`. Its first version of that probe was itself a check that could not fail — it globbed tracked archive `spine.json` files and reported "spine exists" for all four lanes.

## What would close it

An agent's first action is one that cannot fail for an environmental reason, and arriving in a worktree is either mechanically guaranteed or explicitly optional with a stated fallback. `EnterWorktree` — the tool lane A named in its dying words — may already be that mechanism, in which case the defect is that no launch order mentions it.
