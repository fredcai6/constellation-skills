# Mission Frame

No docs/architecture map exists for this repo (skill-source repo; `map/INDEX.md` is an
unfilled template, `map/ids.jsonl` is empty; this lane does not regenerate it, per the
launch order's map-index-is-Admiral-owned ruling). Per this template's own instruction
("Skip or shrink this frame for a trivial local/mechanical change where the map adds
nothing"), this frame is shrunk to Intent + Out of Scope; there is no map inventory to cite
structural/decision/claim anchors against. `map_orient.py`'s DEGRADED substitutes already
carried the orientation this run needed (`.agent-work/567-f/map-orientation.json`): `README.md`
and `skills/commander/references/crew-dispatch.md`.

## Intent

Measure whether `scripts/run_crew.py`'s spine-only dispatch, `spine_open`'s spec compilation,
and `spine_bind` already deliver #535 ("dispatch should start with 'start the spine with this
identifier,' not the launch order"), and build only what the measurement shows is genuinely
missing, confined to `scripts/run_crew.py` (the one file this lane owns).

**Measurement outcome** (full detail: `.agent-work/567-f/notes-1.md`): the concrete mechanism
#535 names is already shipped and this very Commander session is live proof of it (dispatched
via `run_crew.py --backend cli --spine <this spine>`, door resolved to its own spine, identity
derived from `work_id`, no caller-supplied identifier). No code change to `scripts/run_crew.py`
is warranted. Two real, adjacent gaps exist but sit outside this lane's file ownership /
latitude and are floated to the Admiral rather than built: (1) the `ExternalBackend` (the
Agent-tool-harness dispatch path) refuses spine-only by design, blocked by a harness
constraint (the `Agent` tool takes no env-injection parameter) that no change inside
`run_crew.py` can close; (2) Commander-level mission content (this launch order's own Mission/
Pre-Rulings/Latitude/File-Ownership) has no spine-carried representation -- `spine_open`'s spec
compilation covers only `implementer`/`reviewer` gate plans -- and closing that would touch
`skills/**` templates fenced to lane D1 this wave.

## Out of Scope

- Reopening the identity-trade decision that keeps session identity derived from the spine's
  own work id (forbidden per the launch order).
- Any edit inside `skills/**` (except `skills/workbench/**`), `specs/**`, or
  `scripts/mcp_spine_server.py` -- fenced to other lanes this wave.
- Building a fix for the `ExternalBackend`/harness-constraint gap or the Commander-level
  spec-compilation gap -- both are architecture-level and floated, not built, this run.
