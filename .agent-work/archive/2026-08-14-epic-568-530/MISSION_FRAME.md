# Mission Frame

## Intent

Correct the spine-rail binding's worktree attribution for a resolved spine in a
linked worktree. This is a small mechanical correction; the architecture map is
unparseable, so this frame is cut from the declared substitute `README.md`.

## Affected Capabilities

- Binding records preserve the owning worktree of each resolved spine so shared
  session Stop and SessionStart guards distinguish parent and child runs.

## Examples / Events

- A child claims `.agent-work/child/spine.json` after `cd` into a linked
  worktree while its hook payload still names the main checkout as `cwd`.
- A parent Stop must block for its own active spine, but not for the child's
  active foreign-worktree spine; after parent release it remains non-blocking.

## Structural Anchors

- `README.md` — declared degraded-map substitute; no citable architecture
  packet currently covers `scripts/hooks/spine_rail.py`.

## Governing Constraints / Assumptions

- The resolved absolute spine path is the source of truth for its owning
  worktree; hook payload `cwd`, observed `cd`, and `--worktree` text are not.
- The helper accepts only an absolute `.agent-work/<work-id>/<name>.json`
  path. Malformed or out-of-layout paths produce no attribution and must never
  fall back to `cwd`.
- Release target resolution stays unchanged.
- Store locking, identity unification, reaping, and all #441 behavior remain
  out of scope.

## Decision Anchors & Decision Pressure

- Source of truth: derive the recorded worktree from validated `abs_spine`.
  @grade: settled/measured · leans g1-implement
- Scope: support JSON checklists below `.agent-work/<work-id>/`.
  @grade: settled/human · leans g1-implement
- Serialization: do not implement #441 locking, identity unification, or
  reaping.
  @grade: settled/human · leans g1-implement

## Claims / Evidence Surfaces

- A real git main plus linked-worktree test makes the pre-fix binding record the
  deliberately wrong payload `cwd`, then proves the corrected record names the
  child worktree and drives production Stop and SessionStart handlers.
- Negative helper cases prove malformed and out-of-layout paths are refused.
- `pytest -q tests/test_spine_rail.py` protects the rail's focused behavior.

## Map Confidence / Staleness / Disputes

- The repository map is `DEGRADED-UNPARSEABLE`; `README.md` is hash-pinned in
  `map-orientation.json`. Missing citable coverage for the rail is escalated to
  the Admiral and is not silently trusted.

## Out of Scope

- Binding-store transactionality, liveness/reaping policy, schema migration,
  release behavior, and #441's broader store work.
