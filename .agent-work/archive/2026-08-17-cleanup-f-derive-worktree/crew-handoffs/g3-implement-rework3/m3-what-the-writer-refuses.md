# What the bind-on-resume writer now refuses

Derived from `m3-refusals.txt` (the committed hook and the working tree run
side by side over every reachable cell), not from memory.

## The rule

The bind-on-resume refuses to file a spine path that `session_view_provenance`
already attributes to a **different** binding key than the one it would file it
under (the bare `sid`), and therefore never overwrites that attribution. It is
asked at the write, not at either read.

## The refusal set — one class

| the read's state | what the store attributes the scanned path to | before | after |
|---|---|---|---|
| no binding at all (#261) | nobody | binds | **binds** |
| non-empty view, owns none of it (B4) | a sibling | no bind (reader guard) | no bind |
| **owns an entry whose spine no longer loads** | **a sibling agent's composite key** | **binds** | **REFUSES** |
| owns an entry whose spine no longer loads | nobody (#202's shape) | binds | binds |
| owns an entry whose spine no longer loads | its own bare key | binds | binds |
| 2+ in-tree spines | anyone | no bind | no bind |

**One cell moves.** Every other bind survives, including the two that carry a
regression risk: #261's resumed session, and #202's merge onto an existing
sibling entry.

## Is any legitimate bind refused?

**No, and the reason is structural rather than a survey of cases.** The guard
fires only when the store attributes the scanned path to a binding key in *this
session's own view* that is not the key the write would use. Only keys of the
form `sid` and `sid#<agent_id>` are in that view, so a refusal means: **an agent
sharing this harness session has claimed this exact spine.** A session that had
itself claimed that spine would be the attributed key — the claim writes under
the very key the guard compares against — and the guard passes, as the last row
of the table shows by measurement.

**The one named exception is not new and is already recorded.** `tc5`: when a
path is claimed under *both* a bare key and a composite key, provenance is
last-key-wins, so the session that really did claim it can be attributed to the
other key and lose the re-bind. That loss already happens one branch earlier, at
rework 2's reader guard, and this change neither widens nor narrows it. It is
recorded as `tc5` and wants a decision about which of two keys owns a path both
claimed.

## What the refusal costs the refused session

Nothing it is entitled to. It gets no binding and no resume context — which is
indistinguishable from the hook being absent, and the only thing that context
could have said was another agent's next imperative. Its own Stop still
**blocks**; it is told the gate is foreign-owned and who owns it, with the
imperative withheld (#549). The gate it cannot see was never its own.
