# Problem statement — #441 transactional binding store

## Protected intent

Make `.agent-work/.spine-rail-binding.json` a fail-open, serializable shared
store for the three production writers: PostToolUse claim, PostToolUse release,
and SessionStart bind-on-resume. Preserve explicit checklist lease lifecycle;
this issue changes discovery state only.

## Required behavior

- One portable advisory-lock transaction covers load, safe reap, mutation, and
  unique-temp atomic replacement for every writer. Lock acquisition is bounded;
  hook contention or lock failure returns without blocking the host.
- The transaction preserves every independently written binding when real
  spawned processes claim concurrently against the same registry.
- `spine_rail.is_usable_agent_id` is the authoritative predicate for binding
  keys and gauge transcript paths: ASCII letters, digits, `_`, and `-`, length
  1–64. Punctuation, whitespace, wildcard characters, separators, traversal,
  non-strings, empty values, and longer values are rejected consistently.
- A claim binds only an existing, readable JSON checklist at the contained
  `<worktree>/.agent-work/<work-id>/<name>.json` shape. Absolute paths receive
  the same validation as relative paths. Release first resolves the recorded
  target so a moved, archived, or deleted checklist can still remove its own
  entry.
- Safe reap removes malformed or empty records immediately, explicitly released
  checklist targets, and missing targets only after a 24-hour grace measured
  from a parseable `claimed_at`. A missing target with no trustworthy age is
  retained. A readable checklist with an active lease is never reaped by age.
- Existing readers continue to fail open on absent, corrupt, ambiguous, or
  inaccessible state.

## Proof contract

The red/green regression uses the production PostToolUse handler and binding
store path from independent `multiprocessing` spawn processes, synchronizes
their writes to overlap, then proves the final registry is valid JSON and
contains every expected entry. Focused identity, claim-shape, release, reaper,
and SessionStart tests cover the remaining policy branches. Mutation control
must demonstrate that removing the transaction causes the concurrency test to
fail under the same topology.

## Boundaries

No checklist-engine lease behavior, claim/release journaling, child ownership,
actor identity, durable-root liveness, PID inference, historical bulk backfill,
or historical registry mutation. Windows failures may be recorded, but every
non-Windows failure blocks completion.

## Context quality

The architecture map is degraded and has no citable binding-store packet. The
launch order is therefore the governing intent source, while the named source
files confirm its baseline. Reconcile records the map gap; implementation does
not widen to repair the map.
