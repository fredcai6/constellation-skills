# Triage Recommendation: 3 minor candidates, self-tracking or low-confidence

## Classification
`cleanup` (candidate 1), `tooling` (candidates 2, 3)

## Source checklist/artifact
- epic-569/w3-promote g7 (candidates 1, 2), commander-session observation this gate (candidate 3)

## Structural anchor
`path: skills/cartographer/templates/CARTOGRAPHER.template.json; skills/scout/templates/SCOUT.template.json; none (candidate 3)`

## Candidates

**1. `CARTOGRAPHER.template.json`'s `packets.c1`/`index-overlays.c1` — re-assessable once
`docs/architecture/` is restored.** Both were declined this wave because the map is currently
DEGRADED-UNPARSEABLE (`docs/architecture/generated/map.json`'s `findings`/`nodes`/`relationships`
all empty, independently confirmed by g7's implementer and reviewer) — a repo-wide, pre-existing
condition this lane did not cause and is out of scope to fix. No action needed until a future wave
restores the map; re-run this lane's own g7 assessment (`.agent-work/w3-promote/notes-1.md` g7
section) at that point rather than re-deriving from scratch.

**2. `SCOUT.template.json`'s `report.c1` report-only status.** Already self-tracking: the named
promotion trigger ("N clean report-only runs through this gate with zero false-refusals, reviewed
at the next Cartographer/Scout-owning wave") is recorded directly in the shipped template's own
`map_check_note` field (`skills/scout/templates/SCOUT.template.json`, `report` task) — a durable,
in-repo artifact a future Cartographer/Scout-owning wave will read directly. No separate issue
needed; filing one would duplicate what the template itself already carries.

**3. A stray `.agent-work/<work-id>/` directory** (the literal, unresolved placeholder string used
as a real path) appeared in this session's worktree, containing duplicated `mechanical/`+`context/`
receipt JSON parallel to the correctly-resolved `.agent-work/w3-promote/mechanical/` and
`.agent-work/w3-promote/context/` directories. Observed once, this session, not reproduced against
a specific harness code path — worth someone tracing (a tool somewhere appears to resolve
`<work-id>` literally instead of substituting the real work-id on at least one call path), but
insufficient evidence this run to name the exact mechanism. Untracked, uncommitted, outside
`.agent-work/w3-promote/`, and not part of this lane's PR — does not affect the deliverable.

## Recommended priority
`low` (all three)

**Reason:** none block anything today; 1 and 2 are self-resolving via existing mechanisms once
their trigger conditions are met, 3 is a single unreproduced observation.

## Related artifacts
- `.agent-work/w3-promote/RESULT.md` §5
- `.agent-work/w3-promote/notes-1.md` g7 section

## Disposition
`recommend-and-defer` (candidate 1 and 3), effectively no-issue-needed (candidate 2 — self-tracking
via `map_check_note`, recorded here for completeness of the triage record rather than as a filing
candidate)

**Detail:** candidate 1 and 3 — issue-filing authority is unclear this run (no explicit
issue-creation authority named in `docs/agents/ORCHESTRATOR_CONTEXT.md` or the launch order); both
are also low-confidence enough (candidate 3 unreproduced, candidate 1 blocked on an unrelated
future map restoration) that filing now would be premature. Candidate 2 needs no issue at all — the
tracking mechanism already lives in the shipped template.

## Issue creation authority
`issue-ready only`
